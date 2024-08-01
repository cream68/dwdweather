import streamlit as st
import datetime as dt
from helper_function.get_coord_from_nominatim import get_lat_lon_from_nominatim
# Input for location

def sidebar():
    st.title("Einstellungen")
    location = st.text_input("Ort", value=st.session_state.location)
    try:
        lat, lon = get_lat_lon_from_nominatim(location)
        point_coordinates = (lat, lon)
        st.session_state.point_coordinates = point_coordinates  # Update session state
        st.write(f"Latitude: {lat}, Longitude: {lon}")
    except (ValueError, RuntimeError) as e:
        st.error(str(e))
        return

    # Date range selection
    start_date = st.date_input("Start Date", value=st.session_state.start_date.date())
    end_date = st.date_input("End Date", value=st.session_state.end_date.date())

    # Convert dates from Streamlit to datetime
    start_date = dt.datetime.combine(start_date, dt.datetime.min.time())
    end_date = dt.datetime.combine(end_date, dt.datetime.max.time())

    # Number of stations input with a slider
    num_stations = st.slider("Anzahl an Stationen", min_value=1, max_value=10, value=st.session_state.num_stations)

    # Update session state
    st.session_state.start_date = start_date
    st.session_state.end_date = end_date
    st.session_state.num_stations = num_stations
    st.session_state.location = location
    return st.session_state