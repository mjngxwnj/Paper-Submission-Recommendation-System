from airflow import DAG
from airflow.operators.python import PythonOperator
from database.mongodb.connection import MongoDBConnector
from integration.airflow import get_mongo_conn
from data_ingestion.scrapers import BaseScraper, SourceAScraper, SourceBScraper
from data_ingestion.loaders import BaseLoader, RawPaperLoader
from datetime import datetime
import time
import logging

def run_scraper(scraper_default: type[BaseScraper], loader_default: type[BaseLoader],
                src: str) -> None:
    mongo_client = MongoDBConnector(**get_mongo_conn())
    db = mongo_client.connect()

    scraper : BaseScraper = scraper_default()
    loader : BaseLoader = loader_default(db, src)

    data = scraper.fetch_data()
    loader.load(data)

    mongo_client.close()


default_args = {
    "owner": "airflow",
    "depends_on_past": False, }

with DAG(
    "test",
    default_args = default_args,
    start_date=datetime(2025, 10, 22),
    schedule_interval=None,
    catchup=False
) as dag:

    scrape_sourceA_task = PythonOperator(
        task_id = "scrape_sourceA_task",
        python_callable = run_scraper,
        op_args = [SourceAScraper, RawPaperLoader, "srcA"]
    )

    scrape_sourceB_task = PythonOperator(
        task_id = "scrape_sourceB_task",
        python_callable = run_scraper,
        op_args = [SourceBScraper, RawPaperLoader, "srcB"]
    )

