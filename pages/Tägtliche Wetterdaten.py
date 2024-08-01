import datetime as dt
import streamlit as st
import pytz  # Make sure to install pytz if not already available
from helper_function.daily_temperature import get_daily_temperature


def convert_to_datetime_with_tz(date):
    # Use UTC timezone for this example
    return dt.datetime.combine(date, dt.time()).replace(tzinfo=pytz.UTC)


# Retrieve values from session state
station_ids = st.session_state.get('station_ids', [])
point_coordinates = st.session_state.get('point_coordinates', (None, None))
num_stations = st.session_state.get('num_stations', 1)

# page
st.title("Durchschnittliche tägliche Temperatur")
st.write(f"Für Ort: **{st.session_state.location}**")

# Define default start and end dates
default_start_date = dt.datetime(2023, 1, 1)
default_end_date = dt.datetime(2023, 12, 31)

# Use st.date_input to select a date range
d = st.date_input(
    "Zeitspanne",
    value=(default_start_date, default_end_date),
    format="MM/DD/YYYY"
)

# Extract start_date and end_date from the selected range
start_date, end_date = d
# Convert dates to datetime with timezone info
start_date = convert_to_datetime_with_tz(start_date)
end_date = convert_to_datetime_with_tz(end_date)

# set session states
stations_df = st.session_state.closest_stations_df
stations_ids = st.session_state.station_ids

daily_avg_temperatures_specific_year = get_daily_temperature(stations_df, stations_ids, start_date, end_date)
# Convert Polars DataFrame to Pandas DataFrame
daily_avg_temperatures_pandas = daily_avg_temperatures_specific_year.to_pandas()

# Ensure the columns are correctly named
# daily_avg_temperatures_pandas should have columns 'date' and 'weighted_temperature'
daily_avg_temperatures_pandas = daily_avg_temperatures_pandas[['date', 'weighted_temperature']]

# Set the 'date' column as the index for the time series plot
daily_avg_temperatures_pandas.set_index('date', inplace=True)
# Plot using Streamlit
st.line_chart(daily_avg_temperatures_pandas)