import os
import requests
from extract_data import fetch_and_store_weather_data, fetch_and_store_traffic_data
from transform_data import transform_weather_data, transform_traffic_data
from load import build_gold_layer

def get_target_location():
    """Fetches location from env variables, or falls back to IP Geolocation."""
    
    # 1. Check if we have hardcoded secrets (For GitHub Actions)
    env_lat = os.getenv("TARGET_LAT")
    env_lon = os.getenv("TARGET_LON")
    
    if env_lat and env_lon:
        print(f"Using system coordinates: {env_lat}, {env_lon}")
        return float(env_lat), float(env_lon)

    # 2. If no secrets, dynamically fetch device location (For local testing)
    try:
        print("No coordinates in environment. Fetching device location via IP...")
        response = requests.get("https://ipinfo.io/json", timeout=5)
        data = response.json()
        
        # ipinfo returns a string like "28.6139,77.2090"
        lat, lon = data['loc'].split(',')
        city = data.get('city', 'Unknown City')
        
        print(f"Detected Location: {city} ({lat}, {lon})")
        return float(lat), float(lon)
        
    except Exception as e:
        print(f"IP Geolocation failed: {e}. Defaulting to Delhi.")
        return 28.6139, 77.2090

def run_pipeline():
    print("Starting City Pulse ETL Pipeline...")
    
    # Dynamically grab the coordinates
    LATITUDE, LONGITUDE = get_target_location()

    print("\n--- 1. EXTRACTION (Bronze Layer) ---")
    weather_raw = fetch_and_store_weather_data(LATITUDE, LONGITUDE)
    traffic_raw = fetch_and_store_traffic_data(LATITUDE, LONGITUDE)
    
    if not weather_raw or not traffic_raw:
        print("Extraction failed. Halting pipeline.")
        return

    print("\n--- 2. TRANSFORMATION (Silver Layer) ---")
    weather_clean = transform_weather_data()
    traffic_clean = transform_traffic_data()

    if not weather_clean or not traffic_clean:
        print("Transformation failed. Halting pipeline.")
        return

    print("\n--- 3. LOAD (Gold Layer) ---")
    build_gold_layer()
    
    print("\nPipeline completed successfully.")

if __name__ == "__main__":
    run_pipeline()