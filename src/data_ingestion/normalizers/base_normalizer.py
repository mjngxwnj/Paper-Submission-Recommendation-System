from datetime import datetime
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
        self._src_collection_name = src
        self._target_collection_name = target_src

        self._src_collection = self._db[self._src_collection_name]
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


    def normalize_data(self, checkpoint: datetime | None = None):
        """
        Execute normalization an upsert.
        """

        index_fields_list = self._get_index_field()

        #ensure index
        for field in index_fields_list:
            ensure_index(self._src_collection, field = field, unique = False)
            ensure_index(self._target_collection, field = field, unique = (field == 'doi'))

        pipeline = []

        #incremental filter if chekcpoint exists
        if checkpoint:
            pipeline.append({
                "$match": {"execution_datetime": {"$gt": checkpoint}}
            })

        pipeline.extend(self._get_pipeline())

        #build pipeline
        aggregate(self._src_collection, pipeline)





