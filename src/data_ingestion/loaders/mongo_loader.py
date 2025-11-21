from data_ingestion.loaders.base_loader import BaseLoader
from database.mongodb.helpers import insert_many
from typing import Any
import logging


class MongoLoader(BaseLoader):

    def load_data(self, data: list[dict[str, Any]]) -> None:
        """
        Insert raw documents into the colllection.
        """
        if not data:
            logging.warning("No data to insert into collection.")
            return

        insert_many(self._collection, data)

