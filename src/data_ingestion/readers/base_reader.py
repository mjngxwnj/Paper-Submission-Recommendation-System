from abc import ABC, abstractmethod
from database.mongodb.connection import MongoDBConnector
from integration.airflow.conn_config import get_mongo_conn
import pymongo

class BaseReader(ABC):
    def __init__(self, db: pymongo.database.Database, src: str):
        """
        Base class for MongoDB data loaders.

        Args:
            db (pymongo.database.Database): MongoDB database instance.
            src (str): source identifier.
        """

        self._db = db
        self._src = src

    @abstractmethod
    def read(self) -> list[dict]:
        """
        Abstract method to read data from MongoDB.

        Args:
            data (list[dict]): List of documents to be read.
        """

        pass

