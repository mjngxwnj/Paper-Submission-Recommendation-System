from airflow import DAG
from airflow.operators.python import PythonOperator

from data_ingestion.scrapers import openAlexScraper, oxfordScraper, SpringerScraper, ScopusScraper, run_scraper
from data_ingestion.loaders import MongoLoader
from data_ingestion.normalizers import BaseNormalizer, SpringerNormalizer, run_normalizer

from datetime import datetime

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

    scrape_springer_task = PythonOperator(
        task_id = "scrape_springer_task",
        python_callable = run_scraper,
        op_kwargs = {
            'scraper_default': SpringerScraper,
            'loader_default': MongoLoader,
            'batch_num': 1,
            'api_key': "b9ff350eae9f1cf54d61f5a69cf1927d",
            'src': 'springer_test'
        }
    )

    normalizer_springer_task = PythonOperator(
        task_id = "normalizer_springer_task",
        python_callable = run_normalizer,
        op_kwargs = {
            'normalizer_default': SpringerNormalizer,
            'src': 'springer_test',
            'target_src': 'full_papers_test'
        }
    )

    scrape_springer_task >> normalizer_springer_task

#    scrape_openalex_task = PythonOperator(
#        task_id = "scrape_openalex_task",
#        python_callable = run_scraper,
#        op_kwargs = {
#            'scraper_default': openAlexScraper,
#            'loader_default': MongoLoader,
#            'batch_num': 1,
#            'api_key': "",
#            'src': 'openalex'
#        }
#    )
#
#    scrape_scopus_task = PythonOperator(
#        task_id = "scrape_scopus_task",
#        python_callable = run_scraper,
#        op_kwargs = {
#            'scraper_default': ScopusScraper,
#            'loader_default': MongoLoader,
#            'batch_num': 1,
#            'api_key': "58f0c056352500c8175e0418b08a4c4e",
#            'src': 'scopus_test'
#        }
#    )
#
#    scrape_oxford_task = PythonOperator(
#        task_id = "scrape_oxford_task",
#        python_callable = run_scraper,
#        op_kwargs = {
#            'scraper_default': oxfordScraper,
#            'loader_default': MongoLoader,
#            'batch_num': 100,
#            'api_key': "",
#            'src': 'oxford'
#        }
#    )


#    normalizer_sourceA_task = PythonOperator(
#        task_id = "normalizer_sourceA_task",
#        python_callable = run_normalizer,
#        op_args = [SourceANormalizer, "srcA", "full_papers"]
#    )
#
#    normalizer_sourceB_task = PythonOperator(
#        task_id = "normalizer_sourceB_task",
#        python_callable = run_normalizer,
#        op_args = [SourceBNormalizer, "srcB", "full_papers"]
#    )
#
#    scrape_sourceA_task >> normalizer_sourceA_task
#    scrape_sourceB_task >> normalizer_sourceB_task
#
#    test_postgres_connection = PythonOperator(
#        task_id = 'test_postgres_connection',
#        python_callable = run_processing
#    )
