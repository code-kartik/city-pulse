import os
import json
import pandas as pd
import pytz
from datetime import datetime

def generalise_timestamp(unix_timestamp):
    """Converts the timestamp to IST and generalizes it to the nearest 15-minute mark."""
    ist = pytz.timezone('Asia/Kolkata')

    if unix_timestamp:
        timestamp = datetime.fromtimestamp(unix_timestamp, tz=pytz.utc).astimezone(ist)
    else:
        timestamp = datetime.now(ist)

    # Generalize to the nearest 15-minute mark
    generalized_time = timestamp.replace(minute=(timestamp.minute // 15) * 15, second=0, microsecond=0)

    return generalized_time

def transform_weather_data():
    path = "data/bronze/weather_raw.parquet"
    if os.path.exists(path):
        bronze_df = pd.read_parquet(path, engine="pyarrow")  # read the parquet file into a pandas DataFrame using pyarrow
        raw_payload = bronze_df["raw_payload"].iloc[0]  # extract the raw JSON payload from the first row of the DataFrame
        weather_data = json.loads(raw_payload)  # parse the raw JSON string into a Python dictionary/object
        transformed_data = {
            "datetime": generalise_timestamp(weather_data.get("dt")),
            "temperature": weather_data.get("main", {}).get("temp"),
            "weather_description": weather_data.get("weather", [{}])[0].get("description", "Unknown"),
            "humidity": weather_data.get("main", {}).get("humidity"),
            "pressure": weather_data.get("main", {}).get("pressure"),
            "wind_speed": weather_data.get("wind", {}).get("speed")
        }
        silver_df = pd.DataFrame([transformed_data])
        os.makedirs("data/silver", exist_ok=True)
        silver_df.to_parquet("data/silver/weather_transformed.parquet", engine="pyarrow")
        return transformed_data
    else:
        print("Weather data not found.")
        return None
    
def transform_traffic_data():
    path = "data/bronze/traffic_raw.parquet"
    if os.path.exists(path):
        bronze_df = pd.read_parquet(path, engine="pyarrow")  # read the parquet file into a pandas DataFrame using pyarrow
        raw_payload = bronze_df["raw_payload"].iloc[0]  # extract the raw JSON payload from the first row of the DataFrame
        traffic_data = json.loads(raw_payload)  # parse the raw JSON string into a Python dictionary/object
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

        silver_df = pd.DataFrame([transformed_data])
        os.makedirs("data/silver", exist_ok=True)
        silver_df.to_parquet("data/silver/traffic_transformed.parquet", engine="pyarrow")
        return transformed_data
    else:
        print("Traffic data not found.")
        return None