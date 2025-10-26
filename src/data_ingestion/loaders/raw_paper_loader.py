from data_ingestion.loaders.base_loader import BaseLoader
from database.mongodb.helpers import insert_many
from typing import Any


class RawPaperLoader(BaseLoader):
    def __init__(self, src: str):
        """
        Initialize RawPaperLoader with MongoDB connection & target collection.

        Args:
            collection_name (str): Target collection for raw data storage.
        """

        super().__init__(src)
        collection_name = "raw_papers_" + self._src
        self._collection = self._db[collection_name]


    def load(self, data: list[dict[str, Any]]) -> None:
        """
        Insert raw documents into the colllection.

        Args:
            data: list[dict[str, Any]]: Raw scraped documents to be inserted.
        """

        try:
            insert_many(self._collection, data)

        finally:
            self.close()





