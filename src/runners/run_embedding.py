import logging

from integration.secrets import get_api_key
from warehouse.core.session import postgres_session
from warehouse.core.data_access import WarehouseDataAccess

from recommendation_flow.embedding.embedding_service import EmbeddingService
from recommendation_flow.preprocessing.data_processor import DataPreprocessor
from recommendation_flow.preprocessing.data_combiner import DocumentCombiner
from recommendation_flow.preprocessing.document_deduplicator import DocumentDeduplicator

def run_embedding_in_batches() -> bool:
  # Configuration
  preprocessor = DataPreprocessor()
  combiner = DocumentCombiner()
  deduplicator = DocumentDeduplicator()
  embedding_service = EmbeddingService(
    api_key=get_api_key("GOOGLE_API_KEY"),
    batch_size=100
  )

  with postgres_session() as pg_session:
    warehouse_access = WarehouseDataAccess(pg_session)

    # 1. Reading data from warehouse
    logging.info("Step 1: Reading data from warehouse in batches of 100,000 records...")
    data = warehouse_access.read(
    table='paper_rcm_features',
    conditions='embedding IS NULL LIMIT 100000'
    )

    # Break if data is empty
    if data.empty:
        return False

    # 2. Preprocessing and Combining text
    logging.info("Step 2: Preprocessing and Combining text...")
    processed_df = preprocessor.transform(data)
    processed_df['combined_text'] = processed_df.apply(combiner.combine_documents, axis=1)
    processed_df.drop(columns=["keyword"], inplace=True)
    processed_df = deduplicator.deduplicator_by_doi(processed_df)
    
    logging.info(f"Unique documents for embedding: {len(processed_df)}")

    # 3. Embedding in batches and Updating to database
    logging.info("Step 3: Embedding in batches and Updating...")
    data_to_update = embedding_service.generate_in_batches(processed_df)
    warehouse_access.update(
    table='paper',
    data=data_to_update,
    key='doi',
    update_cols=['embedding', 'combined_text']
    )

    logging.info("Embedding pipeline completed successfully.")

    return True


def run_embedding() -> None:
    """
    Run embedding process in batches continuously until no more data to process.
    """
    logging.info("Starting embedding pipeline...")

    while True:
        success = run_embedding_in_batches()
        if not success:
            logging.info("No more records to process. Embedding pipeline finished.")
            break
        else:
            logging.info("Batch processed successfully. Continuing to next batch...")


