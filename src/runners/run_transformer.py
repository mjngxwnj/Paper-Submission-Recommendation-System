import logging

from data_ingestion.state import BaseCheckpoint, CheckpointManager
from data_ingestion.transformers.base_transformer import BaseTransformer
from data_ingestion.utils import today

from database.helpers import read
from database.session import mongo_session
from database.data_access import MongoDataAccess

from warehouse.core.session import postgres_session
from warehouse.core.data_access import WarehouseDataAccess


def run_transformer(transformer_default: type[BaseTransformer], src: str) -> None:

    with mongo_session() as mongo_db, postgres_session() as pg_session:
        transformer : BaseTransformer = transformer_default()
        mongo_access = MongoDataAccess(mongo_db, src)
        warehouse_access = WarehouseDataAccess(pg_session)
        checkpoint : BaseCheckpoint = CheckpointManager(mongo_db, src)

        last_checkpoint = checkpoint.get_checkpoint()['last_sync_date']

        logging.info(f"Last checkpoint: {last_checkpoint}")

        try:
            logging.info(f"Started transforming data from {src} collection in MongoDB to Postgres.")

            #read data from mongodb (full papers)
            data = mongo_access.read_data(last_sync_date = last_checkpoint, as_dataframe = True)

            #transform data
            dimension_data = transformer.transform_dimensions(data)

            venue_data = dimension_data['venue']
            ingestion_source_data = dimension_data['ingestion_source']

            #upsert data in to warehouse
            warehouse_access.upsert(table = 'venue',
                                    data = venue_data,
                                    conflict_keys = ['name'],
                                    overwrite = False)

            warehouse_access.upsert(table = 'ingestion_source',
                                    data = ingestion_source_data,
                                    conflict_keys = ['name'])

            logging.info(f"Normalization for {src} completed.")

            checkpoint_info = {
                "last_sync_date": today()
            }

            checkpoint.save_checkpoint(checkpoint_info)

            logging.info(f"Checkpoint saved: {checkpoint_info}")

        except Exception as e:
            logging.error(f"Normalization for {src} failed: {e}")

        logging.info(f"Normalization finished for source {src}.")

