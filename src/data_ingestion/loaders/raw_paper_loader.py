from data_ingestion.loaders.base_loader import BaseLoader
from database.mongodb.helpers import insert_many
from typing import Any


class RawPaperLoader(BaseLoader):
    def __init__(self, db, src):
        """
        Initialize RawPaperLoader with MongoDB connection & target collection.

        Args:
            collection_name (str): Target collection for raw data storage.
        """

        super().__init__(db, src)
        self._collection = self._db[f"raw_papers_{src}"]


    def load(self, data: list[dict[str, Any]]) -> None:
        """
        Insert raw documents into the colllection.
        """

        insert_many(self._collection, data)






