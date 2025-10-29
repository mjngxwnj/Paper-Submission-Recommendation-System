from airflow import DAG
from airflow.operators.python import PythonOperator

from database.mongodb.session import mongo_session
from database.mongodb.helpers import ensure_index
from data_ingestion.scrapers import BaseScraper, SourceAScraper, SourceBScraper
from data_ingestion.loaders import BaseLoader, RawPaperLoader
from data_ingestion.normalizers import BaseNormalizer, SourceANormalizer, SourceBNormalizer

from datetime import datetime

def run_scraper(scraper_default: type[BaseScraper], loader_default: type[BaseLoader],
                src: str) -> None:

    with mongo_session() as db:
        scraper : BaseScraper = scraper_default()
        loader : BaseLoader = loader_default(db, src)

        data = scraper.fetch_data()
        loader.load(data)


def run_normalizer(normalizer_default: type[BaseNormalizer], src: str,
                   target_src: str) -> None:

    with mongo_session() as db:
        normalizer : BaseNormalizer = normalizer_default(db, src, target_src)
        normalizer.normalize()


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

    normalizer_sourceA_task = PythonOperator(
        task_id = "normalizer_sourceA_task",
        python_callable = run_normalizer,
        op_args = [SourceANormalizer, "srcA", "full_papers"]
    )

    normalizer_sourceB_task = PythonOperator(
        task_id = "normalizer_sourceB_task",
        python_callable = run_normalizer,
        op_args = [SourceBNormalizer, "srcB", "full_papers"]
    )

    scrape_sourceA_task >> normalizer_sourceA_task
    scrape_sourceB_task >> normalizer_sourceB_task


