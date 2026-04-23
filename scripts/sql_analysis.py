import pandas as pd
from sqlalchemy import create_engine
import os
import logging
import sys

# 1. BASIC CONFIGURATION: Sends logs to the Airflow console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# 2. LOGGER OBJECT
logger = logging.getLogger(__name__)

def run_sql_analysis():
    logger.info("SQL Aggregation Analysis Started.")

    # --- Database Configuration for PostgreSQL (Docker) ---
    # We use the 'postgres' service name defined in docker-compose
    DB_URL = "postgresql://airflow:airflow@postgres:5432/banggood_db"

    try:
        # 1. Establish Connection using SQLAlchemy
        engine = create_engine(DB_URL)
        logger.info("PostgreSQL database connection established.")
        
        # Helper function to run SQL and display results in logs
        def run_query(title, sql):
            logger.info(f"--- {title} ---")
            # Executes query and converts to Pandas DataFrame
            df = pd.read_sql(sql, engine) 
            # Logs the dataframe cleanly
            logger.info(f"\n{df.to_string(index=False)}\n")

       # --- Query 1: Product Count per Category ---
        run_query(
            "1. Product Count per Category", 
            'SELECT "Category", COUNT(*) as total_items FROM products GROUP BY "Category" ORDER BY total_items DESC'
        )

        # --- Query 2: Average Price per Category ($) ---
        run_query(
            "2. Average Price per Category ($)", 
            'SELECT "Category", ROUND(AVG("Price")::numeric, 2) as avg_price FROM products GROUP BY "Category" ORDER BY avg_price DESC'
        )

        # --- Query 3: Top 5 Products by Estimated Revenue ---
        run_query(
            "3. Top 5 Products by Estimated Revenue", 
            'SELECT "Name", "Price", "Est_Revenue" FROM products ORDER BY "Est_Revenue" DESC LIMIT 5'
        )

        # --- Query 4: Average Rating per Category ---
        run_query(
            "4. Average Rating per Category", 
            'SELECT "Category", ROUND(AVG("Rating")::numeric, 1) as avg_rating FROM products GROUP BY "Category" ORDER BY avg_rating DESC'
        )

        # --- Query 5: Price Category Distribution ---
        run_query(
            "5. Price Category Distribution", 
            'SELECT "Price_Category", COUNT(*) as count FROM products GROUP BY "Price_Category"'
        )
        logger.info("Part 5 Analysis Complete. All results displayed in Airflow logs.")

    except Exception as e:
        logger.error(f"Error during SQL analysis: {e}")

if __name__ == "__main__":
    run_sql_analysis()