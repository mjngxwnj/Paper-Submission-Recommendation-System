import logging

from data_ingestion import normalizers
from data_ingestion.state import BaseCheckpoint, CheckpointManager

from data_ingestion.normalizers import BaseNormalizer
from database.mongodb.session import mongo_session
from data_ingestion.utils import today

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
        checkpoint : BaseCheckpoint = CheckpointManager(db, src)
        last_checkpoint = checkpoint.get_checkpoint()['last_sync_date']

        logging.info(f"Last checkpoint: {last_checkpoint}")

        try:
            logging.info(f"Normalization for {src} started.")

            normalizer.normalize_data(last_checkpoint)

            logging.info(f"Normalization for {src} completed.")

            checkpoint_info = {
                "last_sync_date": today()
            }

            checkpoint.save_checkpoint(checkpoint_info)

            logging.info(f"Checkpoint saved: {checkpoint_info}")

        except Exception as e:
            logging.error(f"Normalization for {src} failed: {e}")

        logging.info(f"Normalization finished for source {src}.")
