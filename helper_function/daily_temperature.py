from wetterdienst.provider.dwd.observation import DwdObservationRequest
import polars as pl
import streamlit as st
from wetterdienst import Parameter, Resolution

@st.cache_data
def get_daily_temperature(station_df, station_ids, start_date, end_date):
    """Retrieve and calculate the daily temperature from the closest stations"""

    # Initialize the request for daily temperature data
    request = DwdObservationRequest(
        parameter=Parameter.TEMPERATURE_AIR_MEAN_2M,
        resolution=Resolution.DAILY,
        start_date=start_date,
        end_date=end_date
    )
    # Filter by station IDs
    daily_data_result = request.filter_by_station_id(station_id=station_ids)
    daily_data = daily_data_result.values.all().df.drop_nulls()  # Ensure `df` is a DataFrame
    
    # Convert the temperature from Kelvin to Celsius
    daily_data = daily_data.with_columns(
        (pl.col("value") - 273.15).alias("temperature")  # Conversion from Kelvin to Celsius
    )

    # Convert station_df to a DataFrame and rename columns for clarity
    station_df = pl.DataFrame(station_df)
    
    # Join `daily_data` with `station_df` on 'station_id'
    daily_data = daily_data.join(station_df, on="station_id")

    # Calculate weighted temperatures
    daily_data = daily_data.with_columns(
        (pl.col("temperature") * pl.col("weights")).alias("weighted_temperature")
    )

    # Sort the aggregated results by date
    daily_avg_sorted = daily_data.sort("date")
    
    return daily_avg_sorted