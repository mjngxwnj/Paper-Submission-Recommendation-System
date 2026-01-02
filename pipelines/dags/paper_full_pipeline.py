from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

from data_ingestion.scrapers import openAlexScraper, SpringerScraper, ScopusScraper
from data_ingestion.normalizers import OpenalexNormalizer, SpringerNormalizer, ScopusNormalizer
from data_ingestion.transformers import UnifiedTransformer

from integration.secrets import get_api_key
from runners import run_scraper, run_normalizer, run_transformer, run_embedding

from datetime import datetime

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
}

with DAG(
    "paper_full_pipeline",
    default_args=default_args,
    start_date=datetime(2025, 10, 22),
    schedule="0 9 * * *",
    catchup=False
) as dag:

    scrape_springer_task = PythonOperator(
        task_id = "scrape_springer_task",
        python_callable = run_scraper,
        op_kwargs = {
            'scraper_default': SpringerScraper,
            'batch_num': 1,
            'api_key': get_api_key("SPRINGER_API_KEY"),
            'src': 'springer'
        }
    )

    scrape_openalex_task = PythonOperator(
        task_id = "scrape_openalex_task",
        python_callable = run_scraper,
        op_kwargs = {
            'scraper_default': openAlexScraper,
            'batch_num': 1,
            'api_key': '',
            'src': 'openalex'
        }
    )

    scrape_scopus_task = PythonOperator(
        task_id = "scrape_scopus_task",
        python_callable = run_scraper,
        op_kwargs = {
            'scraper_default': ScopusScraper,
            'batch_num': 1,
            'api_key': get_api_key("SCOPUS_API_KEY"),
            'src': 'scopus'
        }
    )


    normalize_springer_task = PythonOperator(
        task_id = "normalize_springer_task",
        python_callable = run_normalizer,
        trigger_rule = TriggerRule.ALL_DONE,
        op_kwargs = {
            'normalizer_default': SpringerNormalizer,
            'src': 'springer',
            'target_src': 'full_papers'
        }
    )

    normalize_openalex_task = PythonOperator(
        task_id = "normalize_openalex_task",
        python_callable = run_normalizer,
        trigger_rule = TriggerRule.ALL_DONE,
        op_kwargs = {
            'normalizer_default': OpenalexNormalizer,
            'src': 'openalex',
            'target_src': 'full_papers'
        }
    )

    normalize_scopus_task = PythonOperator(
        task_id = "normalize_scopus_task",
        python_callable = run_normalizer,
        trigger_rule = TriggerRule.ALL_DONE,
        op_kwargs = {
            'normalizer_default': ScopusNormalizer,
            'src': 'scopus',
            'target_src': 'full_papers'
        }
    )

    transform_full_papers_task = PythonOperator(
        task_id = "transform_full_papers_task",
        python_callable = run_transformer,
        trigger_rule = TriggerRule.ALL_DONE,
        op_kwargs = {
            'transformer_default': UnifiedTransformer,
            'src': 'full_papers'
        }
    )

    embedding_papers_task = PythonOperator(
        task_id = "embedding_papers_task",
        python_callable = run_embedding,
        trigger_rule = TriggerRule.ALL_DONE
    )

    scrape_springer_task >> normalize_springer_task
    scrape_openalex_task >> normalize_openalex_task
    scrape_scopus_task >> normalize_scopus_task

    [normalize_springer_task, normalize_openalex_task, normalize_scopus_task] >> transform_full_papers_task >> embedding_papers_task

