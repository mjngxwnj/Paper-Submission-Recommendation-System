from datetime import datetime
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator

from database.mongodb.session import mongo_session
from data_ingestion.normalizers import BaseNormalizer, SpringerNormalizer, run_normalizer


with DAG(
    "normalize",
    start_date=datetime(2025, 10, 22),
    schedule_interval=None,
    catchup=False
):

    normalizer_sourceA_task = PythonOperator(
        task_id = "normalizer_sourceA_task",
        python_callable = run_normalizer,
        op_args = [SpringerNormalizer, "springer_test", "full_papers_test"]
    )

