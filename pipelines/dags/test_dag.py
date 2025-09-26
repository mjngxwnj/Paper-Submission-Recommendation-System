from airflow import DAG
from airflow.operators.python import PythonOperator
from data_ingestion.db import b

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
}

with DAG(
    "test",
    default_args = default_args,

) as dag:
    
    def task_run_a():
        b.b()
    
    test_task = PythonOperator(
        task_id = "test",
        python_callable = task_run_a
    )

    task_run_a