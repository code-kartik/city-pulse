import os
import pandas as pd

def load_transformed_data():
    weather_path = "data/silver/weather_transformed.parquet"
    traffic_path = "data/silver/traffic_transformed.parquet"
    
    if os.path.exists(weather_path) and os.path.exists(traffic_path):
        weather_df = pd.read_parquet(weather_path, engine="pyarrow")
        traffic_df = pd.read_parquet(traffic_path, engine="pyarrow")
        
        gold_df = pd.merge(weather_df, traffic_df, on="datetime", how="inner")

        gold_path = "data/gold/city_pulse.parquet"
        os.makedirs("data/gold", exist_ok=True)

        if os.path.exists(gold_path):
            history_df = pd.read_parquet(gold_path, engine="pyarrow")
            combined_df = pd.concat([history_df, gold_df], ignore_index=True)

            final_df = combined_df.drop_duplicates(subset=["datetime"], keep="last")

        else:
            final_df = gold_df

        final_df.to_parquet(gold_path, engine="pyarrow")
        print("Transformed data loaded into gold layer.")


if __name__ == "__main__":
    load_transformed_data()