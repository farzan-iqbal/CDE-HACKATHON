import pyodbc
import pandas as pd

print("SQL Aggregation Analysis Started.")

# Database Configuration
SERVER = 'DESKTOP-50JD6VE'
DATABASE = 'Banggood_Final'

try:
    # 1. Establish Connection
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'
    conn = pyodbc.connect(conn_str)
    print("Database connection established.")
    
    # Helper function to run SQL and display results
    def run_query(title, sql):
        print(f"\n--- {title} ---")
        # Executes the query on SQL Server and converts result to a Pandas DataFrame
        df = pd.read_sql(sql, conn) 
        print(df)

    # --- Query 1: Product Count per Category ---
    run_query(
        "1. Product Count per Category", 
        "SELECT Category, COUNT(*) as Total_Items FROM Products GROUP BY Category ORDER BY Total_Items DESC"
    )

    # --- Query 2: Average Price per Category ---
    run_query(
        "2. Average Price per Category ($)", 
        "SELECT Category, ROUND(AVG(Price), 2) as Avg_Price FROM Products GROUP BY Category ORDER BY Avg_Price DESC"
    )

    # --- Query 3: Top 5 Products by Estimated Revenue ---
    run_query(
        "3. Top 5 Products by Estimated Revenue", 
        "SELECT TOP 5 Name, Price, Est_Revenue FROM Products ORDER BY Est_Revenue DESC"
    )

    # --- Query 4: Average Rating per Category ---
    run_query(
        "4. Average Rating per Category", 
        "SELECT Category, ROUND(AVG(Rating), 1) as Avg_Rating FROM Products GROUP BY Category ORDER BY Avg_Rating DESC"
    )

    # --- Query 5: Price Category Distribution (Budget vs Standard vs Premium) ---
    run_query(
        "5. Price Category Distribution", 
        "SELECT Price_Category, COUNT(*) as Count FROM Products GROUP BY Price_Category"
    )

    conn.close()
    print("\nPart 5 Analysis Complete. Results displayed above.")

except Exception as e:
    print(f"Error during SQL analysis: {e}")