import os
import pandas as pd
import pyarrow.parquet as pq

def inspect_gold_layer():
    # Make sure this matches your actual file name!
    file_path = "data/gold/city_pulse.parquet"
    
    if not os.path.exists(file_path):
        print("Gold Parquet file not found. Has the pipeline run yet?")
        return

    print("CITY PULSE: DATA INSPECTION")

    # 1. The Infrastructure View (Physical Size)
    size_kb = os.path.getsize(file_path) / 1024
    print(f"Physical File Size: {size_kb:.2f} KB")

    # 2. The Data Engineer View (Instant Metadata Read)
    parquet_metadata = pq.ParquetFile(file_path).metadata
    print(f"Total Rows: {parquet_metadata.num_rows}")
    print(f"Total Columns: {parquet_metadata.num_columns}")
    
    print("-" * 40)

    print("Data Overview:")

    # 3. The Data Analyst View (Reading the actual data)
    df = pd.read_parquet(file_path)
    
    # THE SAFETY CHECK: Prevents the IndexError!
    if df.empty:
        print("The Parquet file exists, but it has 0 rows (it is empty).")
        print("Wait for the ETL pipeline to successfully fetch and load data.")
    else:
        print("--- FIRST ROW (Oldest) ---")
        print(df.iloc[0].to_dict())
        
        print("\n--- LATEST ROW (Newest) ---")
        print(df.iloc[-1].to_dict())

if __name__ == "__main__":
    inspect_gold_layer()