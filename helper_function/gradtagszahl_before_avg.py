import polars as pl

def calculate_gradtagzahl(daily_avg_df: pl.DataFrame, heating_indoor_temperature: float, heating_limit: float) -> pl.DataFrame:
    """Calculate the Gradtagzahl (GTZ) for each month, then average across years."""

    # Step 1: Aggregate daily_avg_df["weighted_temperature"] by date
    daily_avg_df = daily_avg_df.group_by("date").agg([
        pl.col("weighted_temperature").sum().alias("avg_daily_temperature")
    ])

    # Step 2: Add a column for the day of the year in 'MM-DD' format
    daily_avg_df = daily_avg_df.with_columns(
        pl.col("date").dt.strftime("%m-%d").alias("day_of_year"),
        pl.col("date").dt.year().alias("year")  # Extract year
    )

    # Step 4: Calculate GTZ and heating days
    gradtagzahl_per_year = daily_avg_df.with_columns(
        pl.when(pl.col("avg_daily_temperature") < heating_limit)
        .then(heating_indoor_temperature - pl.col("avg_daily_temperature"))
        .otherwise(0)
        .alias("GTZ"),
        (pl.col("avg_daily_temperature") < heating_limit).cast(pl.Int32).alias("avg_daily_heating_day"),
        pl.when(pl.col("avg_daily_temperature") < heating_limit)
        .then(pl.col("avg_daily_temperature"))
        .otherwise(None)
        .alias("avg_daily_temperature_on_heating_day")
    )

    # Step 5: Extract month and day as integers for sorting
    gradtagzahl_per_year = gradtagzahl_per_year.with_columns([
        pl.col("day_of_year").str.slice(0, 2).cast(pl.Int32).alias("month"),
        pl.col("day_of_year").str.slice(3, 2).cast(pl.Int32).alias("day")
    ])

    
    # Step 6: Sort by month and day to ensure chronological order
    gradtagzahl_per_year = gradtagzahl_per_year.sort(["month", "day"])
  
    # Step 7: Group by year and month to calculate monthly GTZ and other metrics
    monthly_gtz_per_year = gradtagzahl_per_year.group_by(["month", "year"]).agg([
        pl.col("GTZ").sum().round(0).alias("GTZ"),
        pl.col("avg_daily_heating_day").sum().round(0).alias("heating_days"),
        pl.col("avg_daily_temperature").mean().round(1).alias("avg_monthly_temperature"),
        pl.col("avg_daily_temperature_on_heating_day").mean().round(1).alias("avg_monthly_temperature_on_heating_day")
    ])
    
    # Step 8: Aggregate results across years to get the final monthly averages
    final_result = monthly_gtz_per_year.group_by("month").agg([
        pl.col("GTZ").mean().round(0).alias("GTZ"),
        pl.col("heating_days").mean().round(0).alias("heating_days"),
        pl.col("avg_monthly_temperature").mean().round(1).alias("avg_monthly_temperature"),
        pl.col("avg_monthly_temperature_on_heating_day").mean().round(1).alias("avg_monthly_temperature_on_heating_day")
    ]).sort(["month"])
    
    return final_result
