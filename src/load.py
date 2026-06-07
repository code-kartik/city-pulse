import os
import pandas as pd

from logger import setup_logger

logger = setup_logger()

def load_transformed_data():
    weather_path = "data/silver/weather_transformed.parquet"
    traffic_path = "data/silver/traffic_transformed.parquet"

    logger.info("Starting load_transformed_data")

    if not os.path.exists(weather_path):
        logger.error("Weather transformed file not found: %s", weather_path)
        return
    if not os.path.exists(traffic_path):
        logger.error("Traffic transformed file not found: %s", traffic_path)
        return

    try:
        weather_df = pd.read_parquet(weather_path, engine="pyarrow")
        traffic_df = pd.read_parquet(traffic_path, engine="pyarrow")
        logger.info("Read weather and traffic data; rows: %d, %d", len(weather_df), len(traffic_df))

        gold_df = pd.merge(weather_df, traffic_df, on="datetime", how="inner")
        logger.info("Merged data; rows: %d", len(gold_df))

        gold_path = "data/gold/city_pulse.parquet"
        os.makedirs("data/gold", exist_ok=True)

        if os.path.exists(gold_path):
            history_df = pd.read_parquet(gold_path, engine="pyarrow")
            combined_df = pd.concat([history_df, gold_df], ignore_index=True)
            final_df = combined_df.drop_duplicates(subset=["datetime"], keep="last")
            logger.info("Appended to existing gold data; final rows: %d", len(final_df))
        else:
            final_df = gold_df
            logger.info("No existing gold file found; creating new with rows: %d", len(final_df))

        final_df.to_parquet(gold_path, engine="pyarrow")
        logger.info("Transformed data loaded into gold layer at %s", gold_path)
        return final_df

    except Exception as e:
        logger.exception("Failed to load transformed data: %s", e)
        raise