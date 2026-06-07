import os
import json
import pandas as pd
import pytz
from datetime import datetime

from logger import setup_logger

logger = setup_logger()

def generalise_timestamp(unix_timestamp):
    """Converts the timestamp to IST and generalizes it to the nearest 15-minute mark."""
    ist = pytz.timezone('Asia/Kolkata')

    if unix_timestamp:
        logger.debug(f"Generalising provided unix timestamp: {unix_timestamp}")
        timestamp = datetime.fromtimestamp(unix_timestamp, tz=pytz.utc).astimezone(ist)
    else:
        logger.info("No unix timestamp provided; using current timestamp.")
        timestamp = datetime.now(ist)

    # Generalize to the nearest 15-minute mark
    generalized_time = timestamp.replace(minute=(timestamp.minute // 15) * 15, second=0, microsecond=0)

    return generalized_time

def transform_weather_data():
    path = "data/bronze/weather_raw.parquet"
    logger.info(f"Starting weather data transformation. Checking path: {path}")
    if os.path.exists(path):
        logger.info("Weather bronze file found. Reading parquet.")
        try:
            bronze_df = pd.read_parquet(path, engine="pyarrow")  # read the parquet file into a pandas DataFrame using pyarrow
        except Exception as e:
            logger.exception(f"Failed to read weather parquet at {path}: {e}")
            return None
        raw_payload = bronze_df["raw_payload"].iloc[0]  # extract the raw JSON payload from the first row of the DataFrame
        logger.debug(f"Raw weather payload: {raw_payload}")
        try:
            weather_data = json.loads(raw_payload)  # parse the raw JSON string into a Python dictionary/object
        except Exception as e:
            logger.exception(f"Failed to parse weather JSON payload: {e}")
            return None
        transformed_data = {
            "datetime": generalise_timestamp(weather_data.get("dt")),
            "temperature": weather_data.get("main", {}).get("temp"),
            "weather_description": weather_data.get("weather", [{}])[0].get("description", "Unknown"),
            "humidity": weather_data.get("main", {}).get("humidity"),
            "pressure": weather_data.get("main", {}).get("pressure"),
            "wind_speed": weather_data.get("wind", {}).get("speed")
        }
        logger.info(f"Transformed weather data: {transformed_data}")
        silver_df = pd.DataFrame([transformed_data])
        os.makedirs("data/silver", exist_ok=True)
        out_path = "data/silver/weather_transformed.parquet"
        try:
            silver_df.to_parquet(out_path, engine="pyarrow")
            logger.info(f"Wrote transformed weather data to {out_path}")
        except Exception as e:
            logger.exception(f"Failed to write transformed weather parquet: {e}")
            return None
        return transformed_data
    else:
        logger.warning("Weather data not found at path: %s", path)
        return None
    
def transform_traffic_data():
    path = "data/bronze/traffic_raw.parquet"
    logger.info(f"Starting traffic data transformation. Checking path: {path}")
    if os.path.exists(path):
        logger.info("Traffic bronze file found. Reading parquet.")
        try:
            bronze_df = pd.read_parquet(path, engine="pyarrow")  # read the parquet file into a pandas DataFrame using pyarrow
        except Exception as e:
            logger.exception(f"Failed to read traffic parquet at {path}: {e}")
            return None
        raw_payload = bronze_df["raw_payload"].iloc[0]  # extract the raw JSON payload from the first row of the DataFrame
        logger.debug(f"Raw traffic payload: {raw_payload}")
        try:
            traffic_data = json.loads(raw_payload)  # parse the raw JSON string into a Python dictionary/object
        except Exception as e:
            logger.exception(f"Failed to parse traffic JSON payload: {e}")
            return None
        flow_segment = traffic_data.get("flowSegmentData", {})
        current_speed = traffic_data.get("flowSegmentData", {}).get("currentSpeed", 1)
        free_flow = traffic_data.get("flowSegmentData", {}).get("freeFlowSpeed", 1)
        congestion_pct = round(max(0, (1 - (current_speed / free_flow)) * 100), 2) 

        transformed_data = {
            "datetime": generalise_timestamp(None),
            "current_speed": current_speed,
            "free_flow_speed": free_flow,
            "congestion_pct": congestion_pct,
            "confidence": flow_segment.get("confidence")
        }

        logger.info(f"Transformed traffic data: {transformed_data}")
        silver_df = pd.DataFrame([transformed_data])
        os.makedirs("data/silver", exist_ok=True)
        out_path = "data/silver/traffic_transformed.parquet"
        try:
            silver_df.to_parquet(out_path, engine="pyarrow")
            logger.info(f"Wrote transformed traffic data to {out_path}")
        except Exception as e:
            logger.exception(f"Failed to write transformed traffic parquet: {e}")
            return None
        return transformed_data
    else:
        logger.warning("Traffic data not found at path: %s", path)
        return None