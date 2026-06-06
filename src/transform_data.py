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
            "temperature": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "pressure": weather_data["main"]["pressure"],
            "weather_description": weather_data["weather"][0]["description"],
            "wind_speed": weather_data["wind"]["speed"]
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
        transformed_data = {
            "datetime": generalise_timestamp(traffic_data.get("flowSegmentData", {}).get("currentSpeed", None)),
            "current_speed": traffic_data["flowSegmentData"]["currentSpeed"],
            "free_flow_speed": traffic_data["flowSegmentData"]["freeFlowSpeed"],
            "confidence": traffic_data["flowSegmentData"]["confidence"]
        }
        silver_df = pd.DataFrame([transformed_data])
        os.makedirs("data/silver", exist_ok=True)
        silver_df.to_parquet("data/silver/traffic_transformed.parquet", engine="pyarrow")
        return transformed_data
    else:
        print("Traffic data not found.")
        return None

if __name__ == "__main__":
    weather_data = transform_weather_data()
    traffic_data = transform_traffic_data()
    if weather_data:
        print(weather_data)
    else:
        print("Failed to transform weather data.")
    if traffic_data:
        print(traffic_data)
    else:
        print("Failed to transform traffic data.")