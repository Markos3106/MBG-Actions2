import openmeteo_requests

import pandas as pd
import requests_cache, json
from retry_requests import retry
from datetime import datetime

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 41.7281,
	"longitude": 1.824,
	"hourly": "temperature_2m",
	"timezone": "auto",
	"forecast_days": 1
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m

hourly_dataframe = pd.DataFrame(data = hourly_data)
temperaturas = hourly_dataframe["temperature_2m"].tolist()

temp_max = max(temperaturas)
temp_min = min(temperaturas)
temp_mitjana = sum(temperaturas) / len(temperaturas)

resultats = {
    "temperatura_maxima": round(temp_max, 2),
    "temperatura_minima": round(temp_min, 2),
    "temperatura_mitjana": round(temp_mitjana, 2)
}

data_actual = datetime.now().strftime("%Y%m%d")

with open(f"temp_{data_actual}.json", "w") as fitxer_json:
    json.dump(resultats, fitxer_json, indent=4)
    