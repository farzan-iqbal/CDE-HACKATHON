# 🛒 Banggood E-Commerce Data Pipeline

![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.x-green?logo=apacheairflow)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![Selenium](https://img.shields.io/badge/Selenium-Web%20Scraping-43B02A?logo=selenium)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

> A fully automated, end-to-end ETL data pipeline that scrapes real product data from Banggood.com, cleans and transforms it, loads it into PostgreSQL, runs SQL analytics, and generates visual business insights — all orchestrated by Apache Airflow inside Docker.

---

## 📌 Table of Contents

- [Project Overview](#-project-overview)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Pipeline Stages](#-pipeline-stages)
- [Setup Guide](#-setup-guide)
- [Project Structure](#-project-structure)
- [SQL Analytics](#-sql-analytics)
- [Visual Outputs](#-visual-outputs)
- [Key Learnings](#-key-learnings)

---

## 🎯 Project Overview

This project was built as part of a **Data Engineering Hackathon**. The goal was to design a production-style data pipeline from scratch that could:

- **Extract** real product listings from 5 categories on Banggood.com using Selenium
- **Transform** raw messy data into clean, analysis-ready format
- **Load** structured data into a PostgreSQL database
- **Analyze** data using SQL aggregation queries
- **Visualize** business insights using Python charts

The entire pipeline runs **automatically every day** via an Airflow DAG, containerized with Docker for portability.

---

## 🏗️ Architecture

![Pipeline Architecture](docs/architecture.png)

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Python 3.9** | Core scripting language |
| **Apache Airflow** | Pipeline orchestration & scheduling |
| **Selenium + BeautifulSoup** | Web scraping (headless Chrome) |
| **Pandas** | Data cleaning & transformation |
| **PostgreSQL 13** | Relational data storage |
| **SQLAlchemy** | Database ORM & connection |
| **Matplotlib + Seaborn** | Data visualization |
| **Docker + Docker Compose** | Containerization & deployment |

---

## 🔄 Pipeline Stages

### Stage 1 — Extract (scrape_banggood.py)
- Launches headless Chrome using Selenium inside Docker
- Scrapes **5 product categories**: Automobiles, Electronics, Lights, Sports, Mobile
- Handles lazy loading via scroll simulation
- Extracts: Product Name, Price, Category, URL
- Saves raw data to `Data/banggood_data.csv`

### Stage 2 — Transform (clean_data.py)
- Removes rows with missing Name or Price
- Cleans price strings using Regex: `re.sub(r'[^0-9.]', '', x)` — handles formats like `US$19.99`
- Adds business logic columns:
  - `Price_Category` → Budget / Standard / Premium
  - `Est_Revenue` → Price × Reviews
- Saves clean data to `Data/banggood_cleaned.csv`

### Stage 3 — Load (upload.py)
- Connects to PostgreSQL using SQLAlchemy
- Uploads cleaned DataFrame to `products` table
- Uses `if_exists='replace'` for fresh daily loads

### Stage 4 — Analyze (sql_analysis.py)
- Runs 5 SQL aggregation queries directly against PostgreSQL
- Results logged to Airflow task logs for monitoring

### Stage 5 — Visualize (analysis.py)
- Generates 6 charts saved to `/Graphs` folder covering category distribution, revenue, pricing and ratings

---

## ⚙️ Setup Guide

### Prerequisites
Make sure you have these installed:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)

### Step 1 — Clone the Repository
```bash
git clone https://github.com/farzan-iqbal/CDE-HACKATHON.git
cd CDE-HACKATHON
```

### Step 2 — Start the Containers
```bash
docker-compose up --build
```
This will:
- Build the custom Airflow image with all dependencies
- Start PostgreSQL on port `5432`
- Start Airflow on port `8080`

> ⏳ First build takes 3-5 minutes. Wait for `airflow | Listening at: http://0.0.0.0:8080`

### Step 3 — Open Airflow UI
```
URL:      http://localhost:8080
Username: admin
Password: admin
```

### Step 4 — Run the Pipeline
1. Find the DAG named **`banggood_full_pipeline`**
2. Toggle it **ON** (top left switch)
3. Click **▶ Trigger DAG** to run manually
4. Click on the DAG → **Graph View** to watch each task execute

### Step 5 — View Results
```bash
# See scraped CSV
cat Data/banggood_data.csv

# See cleaned CSV
cat Data/banggood_cleaned.csv

# See generated charts
ls Graphs/
```

To check PostgreSQL directly:
```bash
docker exec -it <postgres_container_id> psql -U airflow -d banggood_db
SELECT COUNT(*) FROM products;
SELECT "Category", COUNT(*) FROM products GROUP BY "Category";
```

### Step 6 — Stop Containers
```bash
docker-compose down
```

---

## 📁 Project Structure

```
CDE-HACKATHON/
│
├── dags/
│   └── banggood_dag.py           # Airflow DAG definition
│
├── scripts/
│   ├── scrape_banggood.py        # Stage 1: Web scraping
│   ├── clean_data.py             # Stage 2: Data cleaning
│   ├── upload.py                 # Stage 3: PostgreSQL upload
│   ├── sql_analysis.py           # Stage 4: SQL queries
│   └── analysis.py               # Stage 5: Visualizations
│
├── Data/
│   ├── banggood_data.csv         # Raw scraped data
│   └── banggood_cleaned.csv      # Cleaned & transformed data
│
├── docs/
│   └── architecture.png          # Pipeline architecture diagram
│
├── Graphs/
│   ├── 1_Category_Count.png      # Category distribution chart
│   ├── 2_Price_Distribution.png  # Price distribution chart
│   ├── 2_Top_Revenue.png         # Top revenue products chart
│   ├── 3_Price_PieChart.png      # Price category pie chart
│   ├── 4_Price_vs_Rating.png     # Price vs rating scatter
│   └── 5_Top_Revenue.png         # Top revenue bar chart
│
├── Dockerfile                    # Custom Airflow image
├── docker-compose.yaml           # Multi-container setup
├── Requirements.txt              # Python dependencies
└── README.md
```

---

## 📊 SQL Analytics

Five business queries run automatically against PostgreSQL:

```sql
-- 1. Product count per category
SELECT "Category", COUNT(*) as total_items
FROM products
GROUP BY "Category"
ORDER BY total_items DESC;

-- 2. Average price per category
SELECT "Category", ROUND(AVG("Price")::numeric, 2) as avg_price
FROM products
GROUP BY "Category"
ORDER BY avg_price DESC;

-- 3. Top 5 products by estimated revenue
SELECT "Name", "Price", "Est_Revenue"
FROM products
ORDER BY "Est_Revenue" DESC
LIMIT 5;

-- 4. Average rating per category
SELECT "Category", ROUND(AVG("Rating")::numeric, 1) as avg_rating
FROM products
GROUP BY "Category"
ORDER BY avg_rating DESC;

-- 5. Price category distribution
SELECT "Price_Category", COUNT(*) as count
FROM products
GROUP BY "Price_Category";
```

---

## 📈 Visual Outputs

### Category Distribution
![Category Count](Graphs/1_Category_Count.png)

### Price Distribution
![Price Distribution](Graphs/2_Price_Distribution.png)

### Top Revenue Products
![Top Revenue](Graphs/2_Top_Revenue.png)

### Price Category Breakdown
![Price Pie Chart](Graphs/3_Price_PieChart.png)

### Price vs Rating
![Price vs Rating](Graphs/4_Price_vs_Rating.png)

### Top 5 Revenue Leaders
![Top 5 Revenue](Graphs/5_Top_Revenue.png)

---

## 💡 Key Learnings

- Orchestrating multi-step pipelines with **Apache Airflow DAGs**
- Running **headless Selenium** inside a Docker container
- **Regex-based data cleaning** for inconsistent price formats
- Connecting Python to **PostgreSQL** using SQLAlchemy
- Using **Docker Compose** to manage multi-service applications
- Designing pipelines with **proper logging and error handling**
