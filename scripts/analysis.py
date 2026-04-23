import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging
import sys

# 1. BASIC CONFIGURATION: Tells Airflow how to format and display the logs
logging.basicConfig(
    level=logging.INFO,  # INFO level means it will record general progress messages as well as errors
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format: Timestamp - Error/Info Level - Actual Message
    handlers=[
        logging.StreamHandler(sys.stdout)  # IMPORTANT: This line sends all logs directly to the Airflow dashboard console
    ]
)

# 2. LOGGER OBJECT: We will use this 'logger' variable throughout the script to log messages
logger = logging.getLogger(__name__)

# Important for Docker/Linux: Use 'Agg' backend to generate plots without a display screen
plt.switch_backend('Agg')

def generate_insights():
    """Generates visual reports and business insights from the cleaned dataset."""
    logger.info("Starting visual reports generation...")
    
    input_file = "Data/banggood_cleaned.csv"
    
    # Check if data exists
    if not os.path.exists(input_file):
        logger.error(f"Critical Error: {input_file} not found. Please run cleaning script first.")
        return

    df = pd.read_csv(input_file)
    logger.info(f"Dataset loaded successfully. Total rows: {len(df)}")
    
    # Ensure the Graphs directory exists
    os.makedirs("Graphs", exist_ok=True)
    
    # Setting a professional theme for the visualizations
    sns.set_theme(style="whitegrid", palette="viridis")

    # --- 1. Category Distribution Analysis ---
    logger.info("Generating 'Category Distribution' graph...")
    plt.figure(figsize=(12, 6))
    ax = sns.countplot(data=df, x='Category', order=df['Category'].value_counts().index)
    plt.title('Product Inventory Volume by Category', fontsize=14)
    plt.xlabel('Category', fontsize=12)
    plt.ylabel('Number of Products', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("Graphs/1_Category_Count.png")
    plt.close() # Close plot to free up memory

    # --- 2. Revenue Performance: Top 5 Products ---
    logger.info("Generating 'Top 5 Revenue Performance' graph...")
    # Cleaning product names slightly for better display on the Y-axis
    top_rev = df.nlargest(5, 'Est_Revenue').copy()
    top_rev['Name'] = top_rev['Name'].str[:30] + '...' # Truncate long names
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=top_rev, x='Est_Revenue', y='Name', hue='Category')
    plt.title('Top 5 Performance: Estimated Revenue Leaders', fontsize=14)
    plt.xlabel('Estimated Revenue ($)', fontsize=12)
    plt.ylabel('Product Name', fontsize=12)
    plt.tight_layout()
    plt.savefig("Graphs/2_Top_Revenue.png")
    plt.close()

    logger.info(f"Success! Visual reports exported to the /Graphs folder. Total rows processed: {len(df)}")

if __name__ == "__main__":
    generate_insights()