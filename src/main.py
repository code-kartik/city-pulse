import os
from logger import setup_logger # Import your new utility
from extract_data import fetch_and_store_weather_data, fetch_and_store_traffic_data
from transform_data import transform_weather_data, transform_traffic_data
from load import load_transformed_data

# Initialize the logger for this script
logger = setup_logger()

def get_target_location():
    env_lat = os.getenv("TARGET_LAT")
    env_lon = os.getenv("TARGET_LON")
    
    if env_lat and env_lon:
        logger.info(f"Using system coordinates: {env_lat}, {env_lon}")
        return float(env_lat), float(env_lon)

    # ... (IP fetch logic here) ...
    logger.warning("No coordinates in environment. Defaulting to Delhi.")
    return 28.6139, 77.2090

def run_pipeline():
    logger.info("Starting City Pulse ETL Pipeline")
    
    LATITUDE, LONGITUDE = get_target_location()

    logger.info("1. EXTRACTION (Bronze Layer)")
    weather_raw = fetch_and_store_weather_data(LATITUDE, LONGITUDE)
    traffic_raw = fetch_and_store_traffic_data(LATITUDE, LONGITUDE)
    
    if not weather_raw or not traffic_raw:
        logger.error("Extraction failed. Halting pipeline.")
        return

    logger.info("2. TRANSFORMATION (Silver Layer)")
    weather_clean = transform_weather_data()
    traffic_clean = transform_traffic_data()

    if not weather_clean or not traffic_clean:
        logger.error("Transformation failed. Halting pipeline.")
        return

    logger.info("3. LOAD (Gold Layer)")
    load_transformed_data()
    
    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    run_pipeline()