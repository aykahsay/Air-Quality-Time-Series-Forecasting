import os
from dotenv import load_dotenv
import requests
import pandas as pd
from sqlalchemy import create_engine, text
import logging
from datetime import datetime

# ==============================
# 0️⃣ SETUP LOGGING
# ==============================
log_dir = r"C:\Users\Admin\GitHub\Others\Air-Quality-Time-Series-Forecasting\logs"
os.makedirs(log_dir, exist_ok=True)
log_filename = os.path.join(log_dir, f"nairobi_pm25_etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.info("==== INCREMENTAL ETL PROCESS STARTED ====")

try:
    # ==============================
    # 1️⃣ LOAD ENVIRONMENT VARIABLES
    # ==============================
    env_path = r"C:\Users\Admin\GitHub\Others\Air-Quality-Time-Series-Forecasting\.env"
    load_dotenv(dotenv_path=env_path)

    API_KEY = os.getenv("OPENAQ_API_KEY")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_SERVER = os.getenv("DB_SERVER", "localhost")

    logging.info("Environment variables loaded successfully.")

    # ==============================
    # 2️⃣ CONNECT TO SQL SERVER
    # ==============================
    engine = create_engine(
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
    )

    # Get last datetime from bronze table
    with engine.connect() as conn:
        result = conn.execute(text("SELECT MAX(datetime) FROM bronze.Nairobi_PM25")).scalar()
        last_datetime = result if result is not None else None

    if last_datetime:
        logging.info(f"Last datetime in bronze table: {last_datetime}")
    else:
        logging.info("No previous data found. Full extraction will run.")

    # ==============================
    # 3️⃣ EXTRACT DATA FROM OpenAQ
    # ==============================
    url = "https://api.openaq.org/v3/measurements"
    headers = {"X-API-Key": API_KEY}
    params = {
        "city": "Nairobi",
        "parameter": "pm25",
        "limit": 1000,
        "sort": "asc",
        "order_by": "datetime"
    }
    if last_datetime:
        params["date_from"] = last_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if "results" in data and len(data["results"]) > 0:
        df_raw = pd.DataFrame(data["results"])
        logging.info(f"Extracted {len(df_raw)} new records from OpenAQ API.")
    else:
        logging.info("No new data found.")
        df_raw = pd.DataFrame()

    # ==============================
    # 4️⃣ TRANSFORM DATA
    # ==============================
    if not df_raw.empty:
        df_clean = df_raw.copy()
        df_clean = df_clean[["location", "parameter", "value", "unit", "coordinates", "date"]]
        df_clean["datetime"] = pd.to_datetime(df_clean["date"].apply(lambda x: x.get("utc")))
        df_clean["latitude"] = df_clean["coordinates"].apply(lambda x: x.get("latitude"))
        df_clean["longitude"] = df_clean["coordinates"].apply(lambda x: x.get("longitude"))
        df_clean = df_clean.drop(columns=["date", "coordinates"])
        df_clean = df_clean.rename(columns={"value": "pm25_value"})

        # Remove duplicates based on unique keys: location + datetime + pm25_value
        df_clean = df_clean.drop_duplicates(subset=["location", "datetime", "pm25_value"])
        logging.info("Data transformation and deduplication complete.")

        # ==============================
        # 5️⃣ LOAD DATA INTO SQL SERVER
        # ==============================
        with engine.begin() as conn:
            # Bronze: append raw data
            df_raw.to_sql("Nairobi_PM25", con=conn, schema="bronze", if_exists="append", index=False)

            # Silver: append cleaned, remove duplicates in SQL
            df_clean.to_sql("Nairobi_PM25", con=conn, schema="silver", if_exists="append", index=False)

            # Optional: remove duplicates in silver
            conn.execute(text("""
                WITH cte AS (
                    SELECT *, ROW_NUMBER() OVER (PARTITION BY location, datetime, pm25_value ORDER BY datetime) AS rn
                    FROM silver.Nairobi_PM25
                )
                DELETE FROM cte WHERE rn > 1
            """))
            logging.info("Bronze and Silver tables loaded with duplicates removed.")

        # ==============================
        # 6️⃣ AGGREGATE DATA (Gold)
        # ==============================
        df_gold = df_clean.groupby(pd.Grouper(key="datetime", freq="D")).agg(
            pm25_avg=("pm25_value", "mean"),
            pm25_max=("pm25_value", "max"),
            pm25_min=("pm25_value", "min"),
            count=("pm25_value", "count")
        ).reset_index()

        # Load Gold incrementally: remove overlapping days before insert
        with engine.begin() as conn:
            for day in df_gold['datetime'].dt.date.unique():
                conn.execute(text(f"DELETE FROM gold.Nairobi_PM25_daily_summary WHERE CAST(datetime AS DATE) = '{day}'"))
            df_gold.to_sql("Nairobi_PM25_daily_summary", con=conn, schema="gold", if_exists="append", index=False)
            logging.info("Gold table updated incrementally without duplicates.")

    else:
        logging.info("No new data to transform or load.")

except requests.exceptions.RequestException as e:
    logging.error(f"API request failed: {e}")
except Exception as e:
    logging.error(f"ETL process failed: {e}")
finally:
    logging.info("==== INCREMENTAL ETL PROCESS FINISHED ====")
