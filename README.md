# City Pulse: Serverless Data Lakehouse

City Pulse is an automated, zero-infrastructure Data Lakehouse designed to capture, normalize, and store the real-time correlation between micro-climate weather events and urban traffic congestion in Delhi. 

Rather than relying on persistent, high-cost cloud compute clusters, this project utilizes GitHub Actions as a serverless orchestration engine. It executes a Python-native ETL pipeline on a scheduled cron basis, incrementally building a highly compressed, historical dataset via PyArrow.

## Architecture: The Medallion Data Pattern

This pipeline strictly adheres to the Medallion Architecture pattern to ensure data auditability, fault tolerance, and schema enforcement.

* **Bronze Layer (Raw Ingestion):** Extracts live JSON payloads from the OpenWeatherMap API and TomTom Traffic Flow API. Implements a wrapper strategy, saving the unmodified JSON strings directly into Parquet format to isolate the pipeline from unexpected upstream schema changes.
* **Silver Layer (Transformation & Normalization):** Parses nested JSON and enforces strict data typing. Applies **Temporal Normalization** by converting asynchronous API timestamps to IST and flooring them to strict 15-minute intervals to guarantee flawless relational joins. Calculates business logic, including a custom Traffic Congestion Index.
* **Gold Layer (Incremental Aggregation):** Performs an inner join on the Silver weather and traffic tables. Implements **Idempotent Upsert Logic**: reads the historical Parquet ledger, appends the new timestamped data, and applies a `drop_duplicates` constraint to prevent data corruption during overlapping pipeline runs.

## Tech Stack & Tooling
* **Orchestration:** GitHub Actions (Cron scheduling)
* **Processing:** Python (Pandas)
* **Storage:** Local Git LFS (Large File Storage) using `.parquet` columnar format via PyArrow
* **Observability:** Python `logging` module for automated CI/CD failure tracing
* **Presentation:** Streamlit (Decoupled presentation layer)

## Key Data Engineering Features

* **Idempotency & Fault Tolerance:** The pipeline uses fallback methods to handle missing API keys or altered JSON schemas (e.g., dynamically dropping precipitation metrics on sunny days). It can be re-run indefinitely for the same time window without duplicating historical records.
* **Columnar Storage Optimization:** Bypasses CSVs entirely in favor of strict, columnar Parquet files, allowing months of high-frequency data to be stored in just a few megabytes while maintaining millisecond query performance.
* **Centralized Observability:** Implements a hybrid logging utility. It writes to a local `.log` file during local development but routes to standard output (`stdout`) during cloud runs, ensuring pipeline failures are permanently captured in the GitHub Actions console.
* **Decoupled Analytics:** The presentation layer reads strictly from the Gold Parquet ledger. It never pings the source APIs, rendering it completely immune to rate limits, network latency, or upstream outages.

## Running it Locally

### 1. Clone and Install
```bash
git clone [https://github.com/code-kartik/city-pulse.git](https://github.com/code-kartik/city-pulse.git)
cd city-pulse
pip install -r requirements.txt
```
### 2. Set Environment Variables
Create a ```.env``` file in the root directory and add your API keys:
```bash
OPEN_WEATHER_API_KEY=your_key_here
TOMTOM_API_KEY=your_key_here
```
### 3. Run the ETL Pipeline
To manually execute the extraction, transformation, and load sequence:
```bash
python src/main.py
```
### 4. Inspect the Data
To quickly check the metadata and footprint of the Gold layer without loading the full dataset into memory:
```bash
python check_data.py
```
