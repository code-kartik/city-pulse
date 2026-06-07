import requests
import pandas as pd
import json
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

from logger import setup_logger

load_dotenv()  # Load environment variables from .env file
logger = setup_logger()

def fetch_and_store_weather_data(lat, lon):
    logger.info(f"Starting fetch_and_store_weather_data for lat={lat}, lon={lon}")
    # Fetch data from OpenWeather API
    api_key = os.getenv("OPEN_WEATHER_API_KEY")
    if not api_key:
        logger.error("OPEN_WEATHER_API_KEY is not set in environment")
        return None
    api_endpoint = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"

    logger.debug(f"Requesting OpenWeather API: {api_endpoint}")
    try:
        response = requests.get(api_endpoint, timeout=10)
    except Exception as e:
        logger.exception(f"Exception while requesting OpenWeather API: {e}")
        return None

    if response.status_code == 200:
        bronze_df = pd.DataFrame({
            "ingestion_time":[datetime.now(pytz.utc)],
            "raw_payload":[json.dumps(response.json())]
        })
        os.makedirs("data/bronze", exist_ok=True)
        out_path = "data/bronze/weather_raw.parquet"
        bronze_df.to_parquet(out_path, engine="pyarrow")

        logger.info(f"Weather data fetched and stored in bronze layer at {out_path}.")
        return response.json()
    else:        
        logger.error(f"Error fetching weather data: {response.status_code} - {response.text}")
        return None
    
def fetch_and_store_traffic_data(lat, lon):
    logger.info(f"Starting fetch_and_store_traffic_data for lat={lat}, lon={lon}")
    api_key = os.getenv("TOMTOM_API_KEY")
    if not api_key:
        logger.error("TOMTOM_API_KEY is not set in environment")
        return None
    api_endpoint = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?key={api_key}&point={lat},{lon}"
    logger.debug(f"Requesting TomTom API: {api_endpoint}")
    try:
        response = requests.get(api_endpoint, timeout=10)
    except Exception as e:
        logger.exception(f"Exception while requesting TomTom API: {e}")
        return None

    if response.status_code == 200:
        bronze_df = pd.DataFrame({
            "ingestion_time":[datetime.now(pytz.utc)],
            "raw_payload":[json.dumps(response.json())]
        })
        os.makedirs("data/bronze", exist_ok=True)
        out_path = "data/bronze/traffic_raw.parquet"
        bronze_df.to_parquet(out_path, engine="pyarrow")
        logger.info(f"Traffic data fetched and stored in bronze layer at {out_path}.")
        return response.json()
    else:
        logger.error(f"Error fetching traffic data: {response.status_code} - {response.text}")
        return None