import datetime as dt
import streamlit as st
import polars as pl
from helper_function.daily_temperature import get_daily_temperature
from helper_function.gradtagszahl_before_avg import calculate_gradtagzahl
from helper_function.sidbar import sidebar

with st.sidebar:
        sidebar()

# Retrieve values from session state
station_ids = st.session_state.get('station_ids', [])
point_coordinates = st.session_state.get('point_coordinates', (None, None))
num_stations = st.session_state.get('num_stations', 1)

# page
st.title("Gradtagzahlrechner")

# set session states
stations_df = st.session_state.closest_stations_df
stations_ids = st.session_state.station_ids

with st.expander("Stationen", expanded=False):
    st.dataframe(stations_df[['station_id', 'name', 'distance', 'weights']])

# inputs
year = st.number_input(label="Jahr", min_value=2000,max_value=2024, value=2023)
heating_indoor_temperature = st.number_input(label="Innentemperatur", min_value=0,max_value=25, value=st.session_state.heating_indoor_temperature)
heating_threshold = st.number_input(label="Heizgrenze", min_value=0,max_value=25, value=st.session_state.heating_threshold)

# update session state
st.session_state.heating_indoor_temperature = heating_indoor_temperature
st.session_state.heating_threshold = heating_threshold

start_date = dt.datetime(year, 1, 1)
end_date = dt.datetime(year, 12, 31)
start_last_20_years = dt.datetime(2004, 1, 1)
end_last_20_years = dt.datetime(2023, 12, 31)

# perform calculations
daily_avg_temperatures_specific_year = get_daily_temperature(stations_df, stations_ids, start_date, end_date)
daily_avg_temperatures_last_20_years = get_daily_temperature(stations_df, stations_ids, start_last_20_years, end_last_20_years)
gradtagzahl_df_specific_year = calculate_gradtagzahl(daily_avg_temperatures_specific_year, heating_indoor_temperature, heating_threshold)
gradtagzahl_last_20_years = calculate_gradtagzahl(daily_avg_temperatures_last_20_years, heating_indoor_temperature, heating_threshold)
# Potsdam
long = 52.4009309
lat = 13.0591397

GTZ_specific_year=gradtagzahl_df_specific_year["GTZ"].sum()
heating_days_specific_year= gradtagzahl_df_specific_year["heating_days"].sum()

GTZ_specific_last_20_years=gradtagzahl_last_20_years["GTZ"].sum()
heating_days_specific_last_20_years= gradtagzahl_last_20_years["heating_days"].sum()

# Rename the columns
gradtagzahl_df_specific_year = gradtagzahl_df_specific_year.rename({
    "month": "Monat",
    "GTZ": f"GTZ {heating_indoor_temperature}/{heating_threshold} ",
    "heating_days": "Heiztage",
    "avg_monthly_temperature": "Außentemperatur",
    "avg_monthly_temperature_on_heating_day": "Außentemperatur an Heiztagen"
})

# Rename the columns
gradtagzahl_last_20_years = gradtagzahl_last_20_years.rename({
    "month": "Monat",
    "GTZ": f"GTZ {heating_indoor_temperature}/{heating_threshold} ",
    "heating_days": "Heiztage",
    "avg_monthly_temperature": "Außentemperatur",
    "avg_monthly_temperature_on_heating_day": "Außentemperatur an Heiztagen"
})

st.metric(label=f"Verhältnis der Gradtagzahlen GTZ {heating_indoor_temperature}/{heating_threshold} für {year} zum 20-Jahres Mittel am gleichen Standort", value=f"{GTZ_specific_year/GTZ_specific_last_20_years:.2f}")
st.metric(label=f"Verhältnis der Heiztage HT {heating_threshold} für {year} zum 20-Jahres Mittel am gleichen Standort", value=f"{heating_days_specific_year/heating_days_specific_last_20_years:.2f}")
st.write(f"**GTZ für Jahr {year}**")
st.write(start_date, " bis ", end_date)
with st.expander(f"Statistik GTZ {heating_indoor_temperature}/{heating_threshold} für {year}", expanded=False):
    st.dataframe(gradtagzahl_df_specific_year)
col1, col2 = st.columns(2)
col1.metric(label="Gradtagzahl ", value=GTZ_specific_year)
col2.metric(label="Heiztage ", value=heating_days_specific_year)

st.write(f"**GTZ 20 jähriges Mittel**")
st.write(start_last_20_years, " bis ", end_last_20_years)
with st.expander(f"Statistik für GTZ {heating_indoor_temperature}/{heating_threshold} für 20-Jahres Mittel ", expanded=False):
    st.dataframe(gradtagzahl_last_20_years)
col1, col2 = st.columns(2)
col1.metric(label="Gradtagzahl ", value=GTZ_specific_last_20_years)
col2.metric(label="Heiztage ", value=heating_days_specific_last_20_years)