import pandas as pd
import os
import logging
import sys
import re # Regular Expression library add ki hai

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_banggood_data():
    input_file = "/opt/airflow/Data/banggood_data.csv"
    output_file = "/opt/airflow/Data/banggood_cleaned.csv"

    logger.info(f"Loading raw data from: {input_file}")

    if not os.path.exists(input_file):
        logger.error("Raw data file NOT found!")
        sys.exit(1)

    try:
        df = pd.read_csv(input_file)
        logger.info(f"Raw rows found: {len(df)}")

        if df.empty:
            logger.error("Raw CSV is empty.")
            sys.exit(1)

        # 1. Drop rows with missing Name or Price
        df = df.dropna(subset=['Name', 'Price'])
        
        # 2. STRONGER PRICE CLEANING (Fixes the 'US19.99' error)
        # Ye line har non-numeric cheez (except dot) ko nikal degi
        df['Price'] = df['Price'].astype(str).apply(lambda x: re.sub(r'[^0-9.]', '', x))
        
        # Convert to float (handles empty strings if any)
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df = df.dropna(subset=['Price']) # Remove if price became NaN

        # 3. Logic Columns
        def categorize_price(p):
            if p < 20: return 'Budget'
            elif p < 100: return 'Standard'
            else: return 'Premium'
        
        df['Price_Category'] = df['Price'].apply(categorize_price)
        
        # Ensure Rating and Reviews are numeric
        if 'Rating' not in df.columns or df['Rating'].dtype == object:
            df['Rating'] = 4.0
        if 'Reviews' not in df.columns or df['Reviews'].dtype == object:
            df['Reviews'] = 10
            
        df['Est_Revenue'] = df['Price'] * df['Reviews']

        # 4. Save Cleaned Data
        df.to_csv(output_file, index=False)
        logger.info(f"SUCCESS: Cleaned {len(df)} rows and saved to {output_file}")

    except Exception as e:
        logger.error(f"Cleaning Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clean_banggood_data()