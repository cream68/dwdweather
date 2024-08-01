import requests
from wetterdienst.provider.dwd.observation import (
    DwdObservationRequest,
    DwdObservationResolution,
    DwdObservationDataset
)

def get_lat_lon_from_nominatim(address):
    """Get latitude and longitude from OpenStreetMap Nominatim API."""
    endpoint = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'addressdetails': 1,
        'limit': 1
    }
    headers = {
        'User-Agent': 'my-weather-app/1.0 (your-email@example.com)'
    }
    
    try:
        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP issues
        
        result = response.json()
        if result:
            location = result[0]
            return float(location['lat']), float(location['lon'])
        else:
            raise ValueError("No results found for the given address.")
    except requests.RequestException as e:
        raise RuntimeError(f"Request failed: {e}")
    except ValueError as e:
        raise ValueError(f"Error processing response: {e}")