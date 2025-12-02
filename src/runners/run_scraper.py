import logging

from data_ingestion.state import BaseCheckpoint, CheckpointManager
from data_ingestion.scrapers import BaseScraper

from database.data_access import MongoDataAccess
from database.session import mongo_session

from data_ingestion.utils import today, add_execution_metadata

def run_scraper(scraper_default: type[BaseScraper],
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
        data_access = MongoDataAccess(db, src)

        #get checkpoint
        checkpoint : BaseCheckpoint = CheckpointManager(db, src)
        last_checkpoint = checkpoint.get_checkpoint()['scrape_checkpoint']

        logging.info(f"Last checkpoint: {last_checkpoint}")

        for i in range(batch_num):

            try:
                if not last_checkpoint:
                    data, new_checkpoint = scraper.fetch_data(api_key = api_key)

                else:
                    data, new_checkpoint = scraper.fetch_data(api_key = api_key, checkpoint = last_checkpoint)

                #add execution metadata
                enriched_data = add_execution_metadata(
                    data = data,
                    execution_datetime = today(),
                    source = src
                )

                data_access.load_data(enriched_data)

                if new_checkpoint is not None:
                    last_checkpoint = new_checkpoint

                logging.info(f"[Batch {i+1}/{batch_num}] completed. Checkpoint: {last_checkpoint}")

            except Exception as e:
                logging.error(f"[Batch {i+1}/{batch_num}] error: {e}. Checkpoint: {last_checkpoint}")

            finally:

                checkpoint_info = {
                    "scrape_checkpoint": last_checkpoint,
                }

                checkpoint.save_checkpoint(checkpoint_info)

                logging.info(f"[Batch {i+1}/{batch_num}] checkpoint saved: {last_checkpoint}")

        logging.info(f"Scrape completed. Final checkpoint: {last_checkpoint}")

