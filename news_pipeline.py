from airflow import DAG
from airflow.operators.python import PythonOperator  # Fixed deprecated import

from datetime import datetime, timedelta


default_args = {
    'owner': 'your_name',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def run_ingestion():
    """Import and run ingestion inside the function to avoid import issues"""
    import sys
    sys.path.insert(0, '/opt/airflow/scripts')
    from scripts.ingestion import run_ingestion as ingestion_func
    return ingestion_func()


def run_processing():
    """Import and run processing inside the function to avoid import issues"""
    import sys
    sys.path.insert(0, '/opt/airflow/scripts')
    from scripts.processing import process_articles as processing_func
    return processing_func()


with DAG(
    'news_pipeline',
    default_args=default_args,
    description='A pipeline to ingest and process news articles',
    schedule_interval=timedelta(hours=4),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['news', 'mlops'],
) as dag:

    ingest_task = PythonOperator(
        task_id='ingest_articles',
        python_callable=run_ingestion,
    )

    process_task = PythonOperator(
        task_id='process_articles',
        python_callable=run_processing,
    )

    # Set dependencies: process runs after ingest completes
    ingest_task >> process_task

