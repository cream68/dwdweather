import polars as pl

def calculate_gradtagzahl(daily_avg_df: pl.DataFrame, heating_indoor_temperature: float, heating_limit: float) -> pl.DataFrame:
    """Calculate the Gradtagzahl for a given heating_limit and heating limit."""

    # Calculate degree days where temperature is below the heating_limit

    # 1. Aggregate all daily_avg_df["weighted_temperature"] by date
    daily_avg_df  = daily_avg_df.group_by("date").agg([
        pl.col("weighted_temperature").sum().alias("avg_daily_temperature")
    ])

     # Step 2: Calculate the average temperature for each day across all years
    daily_avg_df = daily_avg_df.with_columns(
        pl.col("date").dt.strftime("%m-%d").alias("day_of_year")
    )

    avg_temp_across_years = daily_avg_df.group_by("day_of_year").agg([
        pl.col("avg_daily_temperature").mean().alias("avg_daily_temperature_across_years"),
    ])

    filtered_df = avg_temp_across_years.filter(
    pl.col("day_of_year").str.starts_with("07-")
)

    filtered_df.write_parquet("juli_df.parquet")

    # Step 3: Calculate GTZ and heating days
    gradtagzahl_across_years = avg_temp_across_years.with_columns(
        pl.when(pl.col("avg_daily_temperature_across_years") < heating_limit)
        .then(heating_indoor_temperature - pl.col("avg_daily_temperature_across_years"))
        .otherwise(None)
        .alias("GTZ"),
        (pl.col("avg_daily_temperature_across_years") < heating_limit).cast(pl.Int32).alias("avg_daily_heating_day_across_years"),
        pl.when(pl.col("avg_daily_temperature_across_years") < heating_limit)
        .then(pl.col("avg_daily_temperature_across_years"))
        .otherwise(None)
        .alias("avg_daily_temperature_on_heating_day_across_years")
    )


    # Step 4: Extract month and day as integers for sorting
    gradtagzahl_across_years = gradtagzahl_across_years.with_columns([
        pl.col("day_of_year").str.slice(0, 2).cast(pl.Int32).alias("month"),
        pl.col("day_of_year").str.slice(3, 2).cast(pl.Int32).alias("day")
    ])
    
    # Step 5: Sort by month and day to ensure chronological order
    gradtagzahl_across_years = gradtagzahl_across_years.sort(["month", "day"])
    
    # Step 6: Group by month for aggregation
    gradtagzahl_across_years = gradtagzahl_across_years.group_by("month").agg([
        pl.col("GTZ").sum().round(0).alias("GTZ"),
        pl.col("avg_daily_heating_day_across_years").sum().round(0).alias("heating_days"),
        pl.col("avg_daily_temperature_across_years").mean().round(1).alias("avg_monthly_temperature"),
        pl.col("avg_daily_temperature_on_heating_day_across_years").mean().round(1).alias("avg_monthly_temperature_on_heating_day")
    ])

    return gradtagzahl_across_years

