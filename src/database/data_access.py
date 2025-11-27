import logging
import pymongo
import pandas as pd
from datetime import datetime

from database.helpers import read as mongo_read, insert_many


class MongoDataAccess:
    def __init__(self, db: pymongo.database.Database , collection_name: str) -> None:
        """
        Initialize MongoDataAccess with database and collection.

        Args:
            database (Database): MongoDB database instance.
            collection_name (str): Name of the collection to operate on.
        """
        self._db = db
        self._collection_name = collection_name
        self._collection = self._db[self._collection_name]


    def set_collection(self, collection_name: str) -> None:
        self._collection_name = collection_name
        self._collection = self._db[self._collection_name]


    def read_data(self,
             last_sync_date: datetime | None = None,
             as_dataframe: bool = False,
             sync_date_field: str = "execution_datetime") -> list[dict] | pd.DataFrame:
        """
        Read documents from the configured collection.

        Args:
            last_sync_date (datetime):
                + If provided, only documents with
                  execution_datetime > last_sync_date are returned (incremental load).
                + If None, the full collection is returned.
            as_dataframe (bool): When True returns a pandas.DataFrame,
                otherwise returns list[dict].

        Returns:
            List of documents as list[dict] or pd.DataFrame depending on as_dataframe.
        """
        filter = {}
        if last_sync_date is not None:
            filter = {sync_date_field: {"$gt": last_sync_date}}

        documents : list[dict] = mongo_read(self._collection, filter = filter)

        if as_dataframe:
            df = pd.DataFrame(documents) if documents else pd.DataFrame()
            logging.info(f"Returned DataFrame with {len(df):,} rows")
            return df

        logging.info(f"Returned {len(documents):,} documents as list[dict]")
        return documents


    def load_data(self, data: list[dict]) -> None:
        """
        Insert raw documents into the colllection.
        """
        if not data:
            logging.warning("No data to insert into collection.")
            return

        insert_many(self._collection, data)






