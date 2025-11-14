from datetime import datetime
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator

from database.mongodb.session import mongo_session
from data_ingestion.normalizers import BaseNormalizer, SpringerNormalizer


def run_normalizer(normalizer_default: type[BaseNormalizer], src: str,
                   target_src: str) -> None:
    """
    Run a normalization job for a given normalizer class, transforming and upserting data
    from a source collection into a target collection.

    Args:
        normalizer_default (type[BaseNormalizer]): The normalizer class to instantiate and run.
        src (str): Source collection name or identifier to normalize data from.
        target_src (str): Target collection name or identifier where normalized data will be stored.
    """

    with mongo_session() as db:
        normalizer : BaseNormalizer = normalizer_default(db, src, target_src)
        normalizer.normalize()

    logging.info(f"Task completed: normalization finished for source {src}.")


with DAG(
    "normalize",
    start_date=datetime(2025, 10, 22),
    schedule_interval=None,
    catchup=False
):

    normalizer_sourceA_task = PythonOperator(
        task_id = "normalizer_sourceA_task",
        python_callable = run_normalizer,
        op_args = [SpringerNormalizer, "springer", "full_papers"]
    )

