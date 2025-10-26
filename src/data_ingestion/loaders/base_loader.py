from abc import ABC, abstractmethod
from database.mongodb.connection import MongoDBConnector
from integration.airflow.conn_config import get_mongo_conn

class BaseLoader(ABC):
    def __init__(self, src: str):
        """
        Initialize the base loader with MongoDB connection
        """

        mongo_config = get_mongo_conn()

        self._src = src
        self._client = MongoDBConnector(**mongo_config)
        self._db = self._client.connect()


    @abstractmethod
    def load(self, data: list[dict]) -> None:
        """
        Abstract method to load data into MongoDB.

        Args:
            data (list[dict]): List of documents to be inserted or updated.
        """

        pass


    def close(self):
        """
        Close the MongoDB connection.
        """

        if self._client:
            self._client.close()
            self._client = None
