import logging

from integration.secrets import get_api_key
from warehouse.core.session import postgres_session
from warehouse.core.data_access import WarehouseDataAccess

from recommendation_flow.preprocessing.data_processor import DataPreprocessor
from recommendation_flow.preprocessing.data_combiner import DocumentCombiner
from recommendation_flow.embedding.embedding_service import EmbeddingService

def run_embedding() -> None:
  # Configuration
  preprocessor = DataPreprocessor()
  combiner = DocumentCombiner()
  embedding_service = EmbeddingService(
    api_key=get_api_key(),
    batch_size=100
  )

  with postgres_session() as pg_session:
    warehouse_access = WarehouseDataAccess(pg_session)

    # 1. Reading data from warehouse
    logging.info("Step 1: Reading data from warehouse...")
    data = warehouse_access.read(
      table='paper_rcm_feature',
      conditions='vector IS NULL'
    )

    # 2. Preprocessing and Combining text
    logging.info("Step 2: Preprocessing and Combining text...")
    processed_df = preprocessor.transform(data)
    processed_df['combined_text'] = processed_df.apply(combiner.combine_documents, axis=1)

    # 3. Embedding in batches and Updating to database
    logging.info("Step 3: Embedding in batches and Updating...")
    data_to_update = embedding_service.generate_in_batches(processed_df)
    warehouse_access.update(
      table='paper',
      data=data_to_update,
      key='doi',
      update_cols=['vector', 'combined_text']
    )

  logging.info("Embedding pipeline completed successfully.")