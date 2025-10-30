from data_ingestion.loaders.base_loader import BaseLoader
from database.mongodb.helpers import insert_many
from typing import Any


class RawPaperLoader(BaseLoader):

    def load(self, data: list[dict[str, Any]]) -> None:
        """
        Insert raw documents into the colllection.
        """

        insert_many(self._collection, data)

