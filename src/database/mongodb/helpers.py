from pymongo.collection import Collection
from pymongo import ASCENDING
from pymongo.errors import PyMongoError
import logging



def validate_type(value, expected_type, name: str = 'variable'):
    """
    Validate that the value matches the expected type.

    Args:
        value: The value to check
        expected_type: The expected type.
        name (str): Name of the variable, used in error message.
    """

    if not isinstance(value, expected_type):
        raise TypeError(f"{name} must be of type {expected_type}, got {type(value).__name__}")


def insert_one(collection: Collection, document: dict) -> bool:
    """
    Insert a single document into the specified MongoDB collection.

    Args:
        collection (Collection): The MongoDB collection object where document will be inserted.
        document (dict): Document to insert.

    Returns:
        bool: True if insertion acknowledged, otherwise raises error.
    """

    #Validate param type
    validate_type(collection, Collection, "collection")
    validate_type(document, dict, "document")

    try:
        result = collection.insert_one(document)
        if result.acknowledged:
            logging.info("Inserted one document successfully.")

            return True

        logging.warning("Insert_one not acknowledged by MongoDB.")
        return False

    except PyMongoError as e:
        logging.error(f"Failed to insert_one: {e}")
        raise


def insert_many(collection: Collection, documents: list[dict]) -> bool:
    """
    Insert multiple documents into collection.

    Args:
        collection (Collection): The MongoDB collection object where document will be inserted.
        documents (list[dict]): list of documents to insert.

    Returns:
        bool: True if insertion acknowledged, otherwise False.
    """

    #Validate param type
    validate_type(collection, Collection, "collection")
    validate_type(documents, list, "documents")

    try:
        result = collection.insert_many(documents)
        if result.acknowledged:
            logging.info(f"Inserted {len(result.inserted_ids)} documents into "
                         f"collection '{collection.name}' successfully.")

            return True

        logging.warning(f"Insert_many not acknowledged by MongoDB for collection '{collection.name}'.")
        return False

    except PyMongoError as e:
        logging.error(f"Failed to insert_many into collection '{collection.name}': {e}")
        raise


def read(collection: Collection, filter: dict | None = None) -> list[dict]:
    """
    Read documents from a MongoDB collection.

    Args:
        collection (Collection): MongoDB collection object to read from.
        filter (dict, optional): MongoDB filter query. Defaults to None (all documents).

    Returns:
        list[dict]: List of documents retrieved.
    """

    validate_type(collection, collection, "collection")
    if filter is not None:
        validate_type(filter, dict, "filter")

    try:
        cursor = collection.find(filter or {})

        documents = list(cursor)
        logging.info(f"Read {len(documents)} documents from collection '{collection.name}' ")

        return documents

    except PyMongoError as e:
        logging.error(f"Failed to read from collection '{collection.name}': {e}")
        raise


def aggregate(collection: Collection, pipeline: list[dict]):
    """
    Run an aggregation pipeline on a MongoDB collection.

    Args:
        collection (Collection): The MongoDB collection to run the pipeline on.
        pipeline (list[dict]): List of aggregation stages.
    """

    validate_type(collection, Collection, "collectin")
    validate_type(pipeline, list, "pipeline")

    try:
        logging.info(f"Running aggregation on collection {collection.name}...")
        collection.aggregate(pipeline, allowDiskUse = True)
        logging.info(f"Aggregation completed. Data has been upserted successfully from {collection.name}.")

    except Exception as e:
        logging.error(f"Failed to aggregate {collection.name}: {e}")
        raise


def ensure_index(collection: Collection, field: str | None = None, unique: bool = True):
    """
    Ensure that an index exists on a specified field in a MongoDB Collection.

    Args:
        collection (Collection): The MongoDB collection object.
        field (str): The field on which to create the index.
        unique (bool): Whether the index should enforce uniqueness. Default is True.
    """

    validate_type(collection, Collection, "collection")
    validate_type(field, str, "field")
    validate_type(unique, bool, "unique")

    indexes = collection.index_information()

    for index in indexes.values():
        if index['key'][0][0] == field and index.get('unique', False) == unique:
            logging.info(f"Index already exists on '{field}' in collection '{collection.name}'.")
            return

    collection.create_index([(field, ASCENDING)], unique = unique)
    logging.info(f"Created {'unique ' if unique else ''}index on '{field}' in collection '{collection.name}'.")

