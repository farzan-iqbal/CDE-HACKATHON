import pandas as pd
import pyodbc
import os

print("--- Step 4: Loading Data to SQL Server ---")

# Database Configuration
# Ensure this matches your SSMS Server Name
SERVER = 'DESKTOP-50JD6VE'
DATABASE = 'Banggood_Final'
DRIVER = 'ODBC Driver 17 for SQL Server'

input_csv = "banggood_cleaned.csv"

# Check if input file exists
if not os.path.exists(input_csv):
    print("Error: Cleaned CSV file not found. Please run Step 2 first.")
    exit()

try:
    # 1. Connect to Database
    print(f"Connecting to {SERVER}...")
    conn_str = f'DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Connected successfully.")

    # 2. Load Data from CSV
    df = pd.read_csv(input_csv)
    # Replace empty values with None so SQL can handle them
    df = df.where(pd.notnull(df), None)
    print(f"CSV Loaded: {len(df)} rows found.")

    # 3. Insert Data
    print("Inserting data into table...")
    
    # Clear existing data to avoid duplicates
    cursor.execute("TRUNCATE TABLE Products")
    
    # SQL Insert Query
    query = """
    INSERT INTO Products (Category, Name, Price, Rating, Reviews, URL, Price_Category, Est_Revenue)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # Convert DataFrame rows to a list of tuples
    data_list = []
    for i, row in df.iterrows():
        data_list.append((
            row['Category'], 
            row['Name'], 
            row['Price'], 
            row['Rating'], 
            row['Reviews'], 
            row['URL'], 
            row['Price_Category'], 
            row['Est_Revenue']
        ))

    # Execute batch insert
    cursor.executemany(query, data_list)
    conn.commit()
    print("Upload complete.")

    # 4. Validate (Row Count Check)
    cursor.execute("SELECT COUNT(*) FROM Products")
    count = cursor.fetchone()[0]
    print(f"Validation: Total rows in SQL Table = {count}")

    conn.close()

except Exception as e:
    print(f"Error: {e}")