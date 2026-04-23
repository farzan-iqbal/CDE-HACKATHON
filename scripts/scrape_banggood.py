import time
import pandas as pd
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
import sys

# --- LOGGING CONFIGURATION ---
# This ensures that all script activity is visible in the Airflow Task Logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def get_category_data(category, url):
    """
    Scrapes product data for a specific category using Selenium.
    """
    logger.info(f"Starting scrape for category: {category}")
    
    # Configure Chrome Options for Docker (Headless mode is mandatory)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(7) # Wait for initial page load
        
        # Scroll down to trigger lazy loading of products
        for i in range(1, 4):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Look for product cards using multiple possible CSS selectors
        cards = soup.select(".product-item") or soup.select(".p-wrap") or soup.select(".item")
        logger.info(f"Found {len(cards)} potential items in {category}.")
        
        data = []
        for c in cards:
            try:
                link = c.select_one("a")
                # Extracting Name (Priority: Title attribute -> Image Alt -> Text)
                name = link.get("title") or (c.select_one("img").get("alt") if c.select_one("img") else None)
                
                # Extracting Price
                price_tag = c.select_one(".price, .price-box, .p-price")
                price = price_tag.get_text(strip=True) if price_tag else "N/A"
                
                if name:
                    p_url = link.get("href", "")
                    # Convert relative URLs to absolute URLs
                    if p_url and not p_url.startswith("http"): 
                        p_url = "https://www.banggood.com" + p_url
                    
                    data.append({
                        "Category": category,
                        "Name": name,
                        "Price": price,
                        "URL": p_url
                    })
            except Exception as e:
                # Skip individual item if there's a parsing error
                continue
            
        return pd.DataFrame(data)
        
    finally:
        # Always close the browser to free up container memory
        driver.quit()

def run_scraping():
    """
    Main function to execute the batch scraping process.
    """
    # Dictionary of target categories and their URLs
    categories = {
        "Automobiles": "https://www.banggood.com/Wholesale-Automobiles-and-Motorcycles-ca-8001.html",
        "Electronics": "https://www.banggood.com/Wholesale-Consumer-Electronics-ca-4001.html",
        "Lights": "https://www.banggood.com/Wholesale-Lights-and-Lighting-ca-5001.html",
        "Sports": "https://www.banggood.com/Wholesale-Sports-and-Outdoors-ca-6001.html",
        "Mobile": "https://www.banggood.com/Wholesale-Mobile-Phones-and-Accessories-ca-2001.html"
    }

    logger.info("Batch extraction process initialized...")
    
    # Run scraping for each category
    all_dfs = [get_category_data(cat, url) for cat, url in categories.items()]
    
    # Filter out empty DataFrames
    valid_dfs = [df for df in all_dfs if df is not None and not df.empty]
    
    if valid_dfs:
        final_df = pd.concat(valid_dfs, ignore_index=True)
        output_path = "/opt/airflow/Data/banggood_data.csv"
        
        # Ensure the destination directory exists inside Docker
        if not os.path.exists("/opt/airflow/Data"): 
            os.makedirs("/opt/airflow/Data")
        
        # Save raw data to CSV
        final_df.to_csv(output_path, index=False)
        logger.info(f"SUCCESS: Total {len(final_df)} items saved to {output_path}")
    else:
        # If no data is found, exit with error so Airflow marks task as 'Failed'
        logger.error("FAILED: No data extracted. Potential selector changes or blocking.")
        sys.exit(1)

if __name__ == "__main__":
    run_scraping()