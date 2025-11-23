import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime

def log_progress(message):
    """Logs message with timestamp to console and file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")
    try:
        with open('code_log.txt', 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    except: pass

def get_category_data(category, url):
    log_progress(f"Starting scrape for: {category}")
    driver = webdriver.Chrome()
    
    try:
        driver.get(url)
        
        # Scroll down 5 times to handle lazy loading of images/prices
        for i in range(1, 6):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Try primary class, fallback to secondary if needed
        cards = soup.select(".product-item") or soup.select(".p-wrap")
        log_progress(f"Found {len(cards)} items in {category}")
        
        data = []
        for c in cards:
            try:
                link = c.select_one("a")
                # Extract name from title attribute or image alt text
                name = link.get("title") or c.select_one("img").get("alt")
                price = c.select_one(".price, .price-box").get_text(strip=True)
                
                if name:
                    # Fix relative URLs
                    p_url = link.get("href", "")
                    if p_url and not p_url.startswith("http"): 
                        p_url = "https://www.banggood.com" + p_url
                    
                    data.append({
                        "Category": category,
                        "Name": name,
                        "Price": price,
                        "Rating": "N/A", # To be cleaned later
                        "Reviews": "0",  # To be cleaned later
                        "URL": p_url
                    })
            except: continue
            
        return pd.DataFrame(data)
        
    finally:
        driver.quit()

if __name__ == "__main__":
    categories = {
        "Automobiles": "https://www.banggood.com/Wholesale-Automobiles-and-Motorcycles-ca-8001.html",
        "Electronics": "https://www.banggood.com/Wholesale-Consumer-Electronics-ca-4001.html",
        "Lights": "https://www.banggood.com/Wholesale-Lights-and-Lighting-ca-5001.html",
        "Sports": "https://www.banggood.com/Wholesale-Sports-and-Outdoors-ca-6001.html",
        "Mobile": "https://www.banggood.com/Wholesale-Mobile-Phones-and-Accessories-ca-2001.html"
    }

    log_progress("Batch extraction started...")
    
    # List comprehension to run scraping for all categories
    all_dfs = [get_category_data(cat, url) for cat, url in categories.items()]

    # Filter out empty results and save
    valid_dfs = [df for df in all_dfs if not df.empty]
    
    if valid_dfs:
        final_df = pd.concat(valid_dfs, ignore_index=True)
        final_df.to_csv("banggood_data.csv", index=False)
        
        log_progress(f"Data saved with {len(final_df)} total items.")
        print(final_df['Category'].value_counts())
    else:
        log_progress("No data extracted.")