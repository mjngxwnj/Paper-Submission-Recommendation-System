from abc import ABC, abstractmethod
from database.mongodb.helpers import aggregate, ensure_index
import pymongo

class BaseNormalizer(ABC):
    def __init__(self, db: pymongo.database.Database, src: str, target_src: str):
        """
        Base class for MongoDB data normalizer.

        Args:
            db (pymongo.database.Database): MongoDB database instance.
            src (str): source identifier.
            target_src (str): Target source name to upsert normalized data.
        """

        self._db = db
        self._collection_name = src
        self._target_collection_name = target_src

        self._collection = self._db[self._collection_name]
        self._target_collection = self._db[self._target_collection_name]


    @abstractmethod
    def _get_pipeline(self) -> list[dict]:
        """
        Return aggregation pipeline for this source.
        """

        pass


    @abstractmethod
    def _get_index_field(self) -> list[str]:
        """
        Return a list of field names that should have index in target collection.
        """

        pass


    def normalize(self):
        """
        Execute normalization an upsert.
        """
        index_fields_list = self._get_index_field()
        pipeline = self._get_pipeline()

        for field in index_fields_list:
            ensure_index(self._target_collection, field = field, unique = True)

        aggregate(self._collection, pipeline)





