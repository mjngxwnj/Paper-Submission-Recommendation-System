from contextlib import contextmanager
from database.mongodb.connection import MongoDBConnector
from integration.airflow import get_mongo_conn

@contextmanager
def mongo_session():
    """
    Context manager to manage MongoDB connection.

    - Automatically calls MongoDBConnector.
    - Connect to DB and yields the db object.
    - Ensures connection is closed after use.
    """

    client = MongoDBConnector(**get_mongo_conn())
    db = client.connect()
    try:
        yield db

    finally:
        client.close()
