from wetterdienst.provider.dwd.observation import (
    DwdObservationRequest,
    DwdObservationResolution,
    DwdObservationDataset
)
import polars as pl

def get_closest_stations(plz_coordinates, start_date, end_date, num_stations=3):
    """Get the closest weather stations to the given coordinates"""
    # Initialize the request for temperature data
    request = DwdObservationRequest(
        parameter=["TMK"],
        resolution=DwdObservationResolution.DAILY,
        start_date=start_date,
        end_date=end_date
    )

    # Filter stations by distance
    stations_result = request.filter_by_distance(latlon=plz_coordinates, distance=100, unit="km")
    stations_df = stations_result.df  # This should be an eager DataFrame

    # Ensure 'start_date' and 'end_date' columns are of type Date
    stations_df = stations_df.with_columns([
        pl.col("start_date").cast(pl.Date),
        pl.col("end_date").cast(pl.Date)
    ])
    
    # Filter stations based on the date range
    filtered_stations_df = stations_df.filter(
        (pl.col('start_date') <= start_date.date()) & 
        (pl.col('end_date') >= end_date.date())
    )

    # Sort by distance and get the closest stations
    closest_stations_df = filtered_stations_df.sort("distance").head(num_stations)

    # Calculate distances and weights
    distances = closest_stations_df["distance"].to_numpy()
    sum_distances = distances.sum()
    
    if sum_distances == 0:
        weights = distances
    else:
        weights = 1 / (distances + 1e-5)  # Add small constant to avoid division by zero
        weights /= weights.sum()  # Normalize weights

    # Add weights to DataFrame
    closest_stations_df = closest_stations_df.with_columns([
        pl.Series("weights", weights)
    ])

    return closest_stations_df