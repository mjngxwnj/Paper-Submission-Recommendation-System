from abc import ABC, abstractmethod
import pymongo

class BaseLoader(ABC):
    def __init__(self, db: pymongo.database.Database, src: str):
        """
        Base class for MongoDB data loaders.

        Args:
            db (pymongo.database.Database): MongoDB database instance.
            src (str): source identifier.
        """

        self._db = db
        self._collection = self._db[src]


    @abstractmethod
    def load(self, data: list[dict]) -> None:
        """
        Abstract method to load data into MongoDB.

        Args:
            data (list[dict]): List of documents to be inserted or updated.
        """

        pass

