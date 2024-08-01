from wetterdienst.provider.dwd.observation import DwdObservationRequest
import polars as pl
import streamlit as st
from wetterdienst import Parameter, Resolution

def get_hourly_temperature(stations_df, start_date, end_date):
    """Retrieve and calculate the hourly temperature from the closest stations"""

    # Initialize the request for hourly temperature data
    request = DwdObservationRequest(
        parameter=Parameter.TEMPERATURE_AIR_MEAN_200,
        resolution=Resolution.HOURLY,
        start_date=start_date,
        end_date=end_date
    )

    # Filter by station IDs
    station_ids =  st.session_state.get('station_ids')
    hourly_data_result = request.filter_by_station_id(station_id=station_ids)
    hourly_data = hourly_data_result.values.all().df.drop_nulls()

    # Convert the temperature from Kelvin to Celsius
    hourly_data = hourly_data.with_columns(
        (pl.col("value") - 273.15).alias("temperature_C")  # Conversion if in Kelvin
    )

    # Join weights with the hourly data based on station_id
    hourly_data = hourly_data.join(stations_df, on="station_id")

    # Calculate weighted temperatures
    hourly_data = hourly_data.with_columns(
        (pl.col("temperature_C") * pl.col("weights")).alias("weighted_temperature")
    )

    # Create a new DataFrame with date, weighted temperature
    new_hourly_data = hourly_data.select(
        pl.col("date"),
        pl.col("value"),
        pl.col("temperature_C"),
        pl.col("weighted_temperature")
    )

   # Aggregate weighted temperatures by date
    hourly_avg = new_hourly_data.group_by("date").agg(
        pl.col("weighted_temperature").sum().alias("average_temperature")
    )

   # Sort the aggregated results by date
    hourly_avg_sorted = hourly_avg.sort("date")

    return hourly_avg_sorted
