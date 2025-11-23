import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Check if cleaned file exists
if not os.path.exists("banggood_cleaned.csv"):
    print("Error: Input file not found. Run Step 2 first.")
    exit()

# Load data
df = pd.read_csv("banggood_cleaned.csv")
print(f"Data loaded: {len(df)} rows found.")

# Create a folder for the output images
os.makedirs("Graphs", exist_ok=True)

# Set the visual style for graphs
sns.set_style("whitegrid")

# 1. Bar Chart: Number of products per Category
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x='Category', palette='viridis')
plt.title('Total Products per Category')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("Graphs/1_Category_Count.png")
plt.close()

# 2. Histogram: Price Distribution
plt.figure(figsize=(10, 6))
sns.histplot(df['Price'], bins=20, kde=True, color='blue')
plt.title('Price Distribution')
plt.xlabel('Price ($)')
plt.savefig("Graphs/2_Price_Distribution.png")
plt.close()

# 3. Pie Chart: Share of Budget vs Premium products
plt.figure(figsize=(8, 8))
counts = df['Price_Category'].value_counts()
plt.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99'])
plt.title('Price Category Share')
plt.savefig("Graphs/3_Price_PieChart.png")
plt.close()

# 4. Scatter Plot: Correlation between Price and Rating
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='Price', y='Rating', hue='Category', alpha=0.7)
plt.title('Price vs Rating')
plt.savefig("Graphs/4_Price_vs_Rating.png")
plt.close()

# 5. Bar Chart: Top 5 Highest Revenue Products
top_5 = df.nlargest(5, 'Est_Revenue')
plt.figure(figsize=(10, 6))
sns.barplot(data=top_5, y='Name', x='Est_Revenue', palette='magma')
plt.title('Top 5 Estimated Revenue Products')
plt.xlabel('Revenue ($)')
plt.yticks(fontsize=8)
plt.tight_layout()
plt.savefig("Graphs/5_Top_Revenue.png")
plt.close()

print("Analysis complete. Check the 'Graphs' folder.")