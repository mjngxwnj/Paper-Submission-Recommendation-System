from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from data_ingestion.loaders.test import test_mongo

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
}

with DAG(
    "test",
    default_args = default_args,
    start_date=datetime(2025, 10, 22),
    schedule_interval=None,
    catchup=False
) as dag:

    test_task = PythonOperator(
        task_id = "test",
        python_callable = test_mongo
    )


