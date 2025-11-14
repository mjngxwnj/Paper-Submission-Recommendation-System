from airflow import DAG
from airflow.operators.python import PythonOperator

from database.mongodb.session import mongo_session
from database.postgres.session import postgres_session
from database.mongodb.helpers import ensure_index

from data_ingestion.state import BaseCheckpoint, MongoCheckpoint
from data_ingestion.scrapers import BaseScraper, openAlexScraper, oxfordScraper, SpringerScraper, ScopusScraper
from data_ingestion.loaders import BaseLoader, MongoLoader
from data_ingestion.normalizers import BaseNormalizer, SpringerNormalizer

from datetime import datetime
import logging

def run_scraper(scraper_default: type[BaseScraper], loader_default: type[BaseLoader],
                batch_num: int, api_key: str, src: str) -> None:
    """
    Run a scraping job for a given scraper and loader, handling checkpoints and errors.

    This function executes a scraper for a specified number of batches, loads the data into
    the target storage, and manages checkpoints to allow running on a daily schedule.

    Args:
        scraper_default (type[BaseScraper]): The scraper class to instantiate and run.
        loader_default (type[BaseLoader]): The loader class for storing scraped data.
        batch_num (int): Number of batches to scrape in this run.
        api_key (str): API key or authentication token required by the scraper.
        src (str): Source identifier, used by loader and checkpoint.
    """

    with mongo_session() as db:
        scraper : BaseScraper = scraper_default()
        loader : BaseLoader = loader_default(db, src)

        #get checkpoint
        checkpoint : BaseCheckpoint = MongoCheckpoint(db, src)
        last_checkpoint = checkpoint.get_checkpoint()

        logging.info(f"Last checkpoint: {last_checkpoint}")

        for i in range(batch_num):
            try:
                if not last_checkpoint:
                    data, new_checkpoint = scraper.fetch_data(api_key = api_key)

                else:
                    data, new_checkpoint = scraper.fetch_data(api_key = api_key, checkpoint = last_checkpoint)

                loader.load(data)

                if new_checkpoint is not None:
                    last_checkpoint = new_checkpoint

                logging.info(f"Batch {i+1}/{batch_num} completed, checkpoint: {last_checkpoint}")

            except Exception as e:
                print(f"[Batch {i+1}] Error occurred: {e}. Checkpoint: {last_checkpoint}")

                raise

            finally:
                checkpoint.save_checkpoint(last_checkpoint)
                logging.info(f"[Batch {i+1}] Checkpoint saved: {last_checkpoint}")

        logging.info(f"Scrape completed. Final checkpoint: {last_checkpoint}")


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


def run_processing():
    with postgres_session() as cur:
        cur.execute("SELECT 1;")


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
            'batch_num': 25,
            'api_key': "b9ff350eae9f1cf54d61f5a69cf1927d",
            'src': 'springer'
        }
    )

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

    scrape_scopus_task = PythonOperator(
        task_id = "scrape_scopus_task",
        python_callable = run_scraper,
        op_kwargs = {
            'scraper_default': ScopusScraper,
            'loader_default': MongoLoader,
            'batch_num': 100,
            'api_key': "58f0c056352500c8175e0418b08a4c4e",
            'src': 'scopus'
        }
    )

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
