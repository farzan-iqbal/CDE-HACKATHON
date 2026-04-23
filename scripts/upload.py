import pandas as pd
from sqlalchemy import create_engine
import os
import logging
import sys

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_to_postgres():
    logger.info("--- Step 3: Loading Data to PostgreSQL ---")
    
    # Forcefully using the absolute path in Docker
    input_file = "/opt/airflow/Data/banggood_cleaned.csv"
    db_url = "postgresql://airflow:airflow@postgres:5432/banggood_db"

    # 1. Check if file exists before trying to read it
    if not os.path.exists(input_file):
        logger.error(f"FILE NOT FOUND: I am looking here -> {input_file}")
        # Debug: list everything in the Data folder
        try:
            logger.info(f"Files found in Data folder: {os.listdir('/opt/airflow/Data')}")
        except:
            logger.error("Data folder itself is missing!")
        sys.exit(1)

    try:
        # 2. Read CSV (Checking if it's empty)
        df = pd.read_csv(input_file)
        if df.empty:
            logger.error(f"FILE IS EMPTY: {input_file} has no data.")
            sys.exit(1)

        # 3. Connection and Upload
        engine = create_engine(db_url)
        logger.info(f"Connecting to Postgres and uploading {len(df)} rows...")
        
        # 'replace' clears the old table and puts fresh data
        df.to_sql('products', engine, if_exists='replace', index=False)
        logger.info("SUCCESS: Data successfully uploaded to 'products' table.")

    except Exception as e:
        logger.error(f"Postgres Upload Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    upload_to_postgres()