from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Default arguments
default_args = {
    'owner': 'farzan_iqbal',
    'depends_on_past': False,
    'start_date': datetime(2026, 4, 20),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG Definition
with DAG(
    'banggood_full_pipeline',
    default_args=default_args,
    description='Automated ETL Pipeline for Banggood Hackathon',
    schedule_interval='@daily',
    catchup=False,
    tags=['hackathon', 'data_engineering']
) as dag:

    # Task 1: Scraping
    scrape_task = BashOperator(
        task_id='run_scraping',
        bash_command='python /opt/airflow/scripts/scrape_banggood.py'
    )

    # Task 2: Cleaning
    clean_task = BashOperator(
        task_id='run_cleaning',
        bash_command='python /opt/airflow/scripts/clean_data.py'
    )

    # Task 3: Upload to Postgres (Screenshot: upload.py)
    upload_task = BashOperator(
        task_id='run_upload_to_db',
        bash_command='python /opt/airflow/scripts/upload.py'
    )

    # Task 4: SQL Analysis (Screenshot: sql_analysis.py)
    sql_analysis_task = BashOperator(
        task_id='run_sql_analysis',
        bash_command='python /opt/airflow/scripts/sql_analysis.py'
    )

    # Task 5: Visualization (Screenshot: analysis.py)
    visuals_task = BashOperator(
        task_id='generate_graphs',
        bash_command='python /opt/airflow/scripts/analysis.py'
    )

    # Workflow Sequence
    scrape_task >> clean_task >> upload_task >> sql_analysis_task >> visuals_task