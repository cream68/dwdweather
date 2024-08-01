import polars as pl

def calculate_gradtagzahl(daily_avg_df: pl.DataFrame, heating_indoor_temperature: float, heating_limit: float) -> pl.DataFrame:
    """Calculate the Gradtagzahl for a given heating_limit and heating limit."""
    
    # Calculate degree days where temperature is above the heating_limit
    gradtagzahl_df = daily_avg_df.with_columns(
        pl.when(pl.col("average_temperature") < heating_limit)
        .then(heating_indoor_temperature-pl.col("average_temperature") )
        .otherwise(0)
        .alias("degree_days")
    )
    # Filter for days where temperature is below the heating_limit
    days_below_heating_limit = daily_avg_df.filter(
        pl.col("average_temperature") < heating_limit
    )
    #print(gradtagzahl_df)
   # Group by year and month, then aggregate the data
    monthly_gradtagzahl = gradtagzahl_df.with_columns(
        pl.col("date").dt.truncate("1mo").alias("month")
    ).group_by("month").agg([
        pl.count().alias("total_days_in_month"),
        pl.col("degree_days").sum().round(0).alias(f"G({heating_indoor_temperature}°C / {heating_limit}°C)"),
        pl.col("average_temperature").filter(pl.col("average_temperature") < heating_limit).count().alias("days_below_heating_limit"),
        pl.col("average_temperature").filter(pl.col("average_temperature").round(1) < heating_limit).mean().alias("avg_temp_below_threshold").round(1),
        pl.col("average_temperature").mean().round(1).alias("average_monthly_temperature")
    ]).sort("month")

    # Extract year and month from the 'month' column
    monthly_gradtagzahl = monthly_gradtagzahl.with_columns(
        pl.col("month").dt.year().alias("year"),
        pl.col("month").dt.month().alias("month")
    ).select(["year", "month","total_days_in_month", f"G({heating_indoor_temperature}°C / {heating_limit}°C)","days_below_heating_limit" , "average_monthly_temperature", "avg_temp_below_threshold"])

        # Rename columns with new names
    monthly_gradtagzahl = monthly_gradtagzahl.rename({
        "year": "Jahr",
        "month": "Monat",
        "total_days_in_month": "Tage",
        "average_monthly_temperature": "Außentemperatur",
        "days_below_heating_limit": "Heiztage",
        "avg_temp_below_threshold": "Temperatur an Heiztagen"

    })

    # Create a new 'Datum' column
    monthly_gradtagzahl = monthly_gradtagzahl.with_columns(
    pl.date(
        year=pl.col("Jahr").cast(pl.Int32),
        month=pl.col("Monat").cast(pl.Int32),
        day=pl.lit(1)
    ).alias("Datum")
    )
    monthly_gradtagzahl=monthly_gradtagzahl.select(pl.col("Datum"),pl.col(f"G({heating_indoor_temperature}°C / {heating_limit}°C)"),pl.col("Tage"),pl.col("Außentemperatur"),pl.col("Heiztage"),pl.col("Temperatur an Heiztagen"))
    #print(monthly_gradtagzahl)
    # Reorder columns to place 'Datum' first and drop 'Jahr' and 'Monat'
    
    

    return monthly_gradtagzahl