from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

from data_ingestion.scrapers import openAlexScraper, SpringerScraper, ScopusScraper
from data_ingestion.normalizers import OpenalexNormalizer, SpringerNormalizer, ScopusNormalizer
from data_ingestion.transformers import UnifiedTransformer

from integration.secrets import get_api_key
from runners import run_scraper, run_normalizer, run_transformer

from datetime import datetime

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
}

with DAG(
    "test_ai_key",
    default_args = default_args,
    start_date=datetime(2025, 10, 22),
    schedule_interval=None,
    catchup=False
) as dag:
    test = PythonOperator(
        task_id = "test",
        python_callable = get_api_key,
        op_kwargs = {
            'name': "SPRINGER_API_KEY"
        }
    )

