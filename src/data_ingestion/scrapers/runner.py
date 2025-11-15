import logging

from data_ingestion.state import BaseCheckpoint, CheckpointManager
from data_ingestion.scrapers import BaseScraper
from data_ingestion.loaders import BaseLoader

from database.mongodb.session import mongo_session

from data_ingestion.utils import now, add_execution_metadata

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
        checkpoint : BaseCheckpoint = CheckpointManager(db, src)
        last_checkpoint = checkpoint.get_checkpoint()['checkpoint_scrape']

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
                    execution_datetime = now(),
                    source = src
                )

                loader.load(enriched_data)

                if new_checkpoint is not None:
                    last_checkpoint = new_checkpoint

                logging.info(f"Batch {i+1}/{batch_num} completed, checkpoint: {last_checkpoint}")

            except Exception as e:
                print(f"[Batch {i+1}] Error occurred: {e}. Checkpoint: {last_checkpoint}")

                raise

            finally:

                checkpoint_info = {
                    "checkpoint_scrape": last_checkpoint,
                    "execution_date_new": now(),
                }

                checkpoint.save_checkpoint(checkpoint_info)

                logging.info(f"[Batch {i+1}] Checkpoint saved: {last_checkpoint}")

        logging.info(f"Scrape completed. Final checkpoint: {last_checkpoint}")

