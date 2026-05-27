import requests
import pandas as pd
import json
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def fetch_and_store_weather_data(lat, lon):
    # Fetch data from OpenWeather API
    api_key = os.getenv("OPEN_WEATHER_API_KEY")
    api_endpoint = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"

    response = requests.get(api_endpoint)
    if response.status_code == 200:
        bronze_df = pd.DataFrame({
            "timestamp_now":[datetime.now(pytz.utc)],
            "raw_pyload":[json.dumps(response.json())]
        })
        os.makedirs("data/bronze", exist_ok=True)
        bronze_df.to_parquet("data/bronze/weather_raw.parquet", engine="pyarrow")

        print("Weather data fetched and stored in bronze layer.")
        return response.json()
    else:        
        print(f"Error fetching data: {response.status_code}")
        return None
    
def fetch_and_store_traffic_data(lat, lon):
    api_key = os.getenv("TOMTOM_API_KEY")
    api_endpoint = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?key={api_key}&point={lat},{lon}"
    response = requests.get(api_endpoint)
    if response.status_code == 200:
        bronze_df = pd.DataFrame({
            "timestamp_now":[datetime.now(pytz.utc)],
            "raw_pyload":[json.dumps(response.json())]
        })
        os.makedirs("data/bronze", exist_ok=True)
        bronze_df.to_parquet("data/bronze/traffic_raw.parquet", engine="pyarrow")
        print("Traffic data fetched and stored in bronze layer.")
        return response.json()
    else:
        print(f"Error fetching traffic data: {response.status_code}")
        return None
    
# TODO: Remove function invocation in this file and move it to a separate script (e.g., main.py) to avoid executing it when imported as a module.

if __name__ == "__main__":
    # Example coordinates for a city (e.g., New York City)
    latitude = 40.7128
    longitude = -74.0060
    
    weather_data = fetch_and_store_weather_data(latitude, longitude)
    if weather_data:
        print(weather_data)
    else:
        print("Failed to retrieve weather data.")

    traffic_data = fetch_and_store_traffic_data(latitude, longitude)
    if traffic_data:
        print(traffic_data)
    else:
        print("Failed to retrieve traffic data.")