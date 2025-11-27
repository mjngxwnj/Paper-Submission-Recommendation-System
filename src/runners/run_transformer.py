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


            # ======================== DIMENSION ============================
            #transform dimension data
            dimension_data = transformer.transform_dimensions(data)

            venue_data = dimension_data['venue']
            ingestion_source_data = dimension_data['ingestion_source']
            keyword_data = dimension_data['keyword']
            bridge_paper_keyword_data = dimension_data['bridge_paper_keyword']
            author_data = dimension_data['author']
            bridge_paper_author_data = dimension_data['bridge_paper_author']

            #upsert data into warehouse
            warehouse_access.upsert(table = 'venue',
                                    data = venue_data,
                                    conflict_keys = ['name'],
                                    overwrite = False)

            warehouse_access.upsert(table = 'ingestion_source',
                                    data = ingestion_source_data,
                                    conflict_keys = ['name'])

            warehouse_access.upsert(table = 'keyword',
                                    data = keyword_data,
                                    conflict_keys = ['name'],
                                    overwrite = False)

            warehouse_access.upsert(table = 'author',
                                    data = author_data,
                                    conflict_keys = ['orcid'],
                                    overwrite = False)


            # ========================= FACT ==============================
            #read dimension data again from warehouse after filtering
            venue_warehouse_data = warehouse_access.read(table = 'venue')

            #transform fact data
            fact_data = transformer.transform_facts(data, venue_warehouse_data)
            paper_data = fact_data['paper']

            #upsert data into warehouse
            warehouse_access.upsert(table = 'paper',
                                    data = paper_data,
                                    conflict_keys = ['doi'],
                                    overwrite = True)


            # ========================= BRIDGE ==============================
            keyword_warehouse_data = warehouse_access.read(table = 'keyword')
            #transform bridge data
            bridge_data = transformer.transform_bridges(bridge_paper_keyword_data, keyword_warehouse_data)

            paper_keyword_data = bridge_data['paper_keyword']

            #upsert data into warehouse
            warehouse_access.upsert(table = 'paper_keyword',
                                    data = paper_keyword_data,
                                    conflict_keys = ['paper_doi', 'keyword_id'])

            warehouse_access.upsert(table = 'paper_author',
                                    data = bridge_paper_author_data,
                                    conflict_keys = ['paper_doi', 'author_id'])

            logging.info(f"Normalization for {src} completed.")

#            checkpoint_info = {
#                "last_sync_date": today()
#            }
#
#            checkpoint.save_checkpoint(checkpoint_info)
#
#            logging.info(f"Checkpoint saved: {checkpoint_info}")

        except Exception as e:
            logging.error(f"Normalization for {src} failed: {e}")
            raise

        logging.info(f"Normalization finished for source {src}.")

