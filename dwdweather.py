import datetime as dt
import polars as pl
import streamlit as st
import pandas as pd
from helper_function.closest_stations import get_closest_stations
from helper_function.sidbar import sidebar

# Constants
DEFAULT_LOCATION = "St. Laurentius Rheinhausen"
START_DATE = dt.datetime(2023, 1, 1)
END_DATE = dt.datetime(2023, 12, 31)

def main():

    with st.sidebar:
        st.session_state=sidebar()

    # Initialize session state if not already set
    if 'location' not in st.session_state:
        st.session_state.location = DEFAULT_LOCATION
    if 'start_date' not in st.session_state:
        st.session_state.start_date = START_DATE
    if 'end_date' not in st.session_state:
        st.session_state.end_date = END_DATE
    if 'num_stations' not in st.session_state:
        st.session_state.num_stations = 1
    if 'point_coordinates' not in st.session_state:
        st.session_state.point_coordinates = (None, None)
    if 'station_ids' not in st.session_state:
        st.session_state.station_ids = []


    # Get the closest weather stations to the point coordinates
    closest_stations = get_closest_stations(st.session_state.point_coordinates, st.session_state.start_date, st.session_state.end_date, st.session_state.num_stations)

    # Convert to Pandas DataFrame for plotting
    closest_stations_df = closest_stations.to_pandas()

    # Save station IDs to session state
    st.session_state.closest_stations_df = closest_stations_df
    st.session_state.station_ids = closest_stations[['station_id']].to_pandas()['station_id'].tolist()

    # Prepare data for mapping
    print(st.session_state.point_coordinates[0])
    user_location_df = pd.DataFrame({'latitude': [st.session_state.point_coordinates[0]], 'longitude': [st.session_state.point_coordinates[1]], 'color': '#0000ff'})
    closest_stations_df['color'] = '#ff0000'  # Red for closest stations
    
    # Combine data for map plotting
    st.title("Wetterstationen")
    map_data = pd.concat([closest_stations_df[['latitude', 'longitude', 'color']], user_location_df], ignore_index=True)

    # Plot map with custom colors
    st.map(map_data, latitude='latitude', longitude='longitude', color='color')

    st.title("Nächste Station(en):")
    st.dataframe(closest_stations[['station_id', 'name', 'distance', 'weights']])

    # Get hourly average temperatures for the closest stations
    #daily_avg_temperatures = get_daily_temperature(closest_stations_df, start_date, end_date)

    # Check if daily_avg_temperatures is not empty and plot
    #if not daily_avg_temperatures.is_empty():
    #    daily_avg_df = daily_avg_temperatures.to_pandas()
    #    st.line_chart(daily_avg_df.set_index("date")[["average_temperature"]])
    #    st.dataframe(daily_avg_df)
    #else:
    #    st.write("No daily temperature data available.")

if __name__ == "__main__":
    main()