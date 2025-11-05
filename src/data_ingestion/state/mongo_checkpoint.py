from data_ingestion.state.base_checkpoint import BaseCheckpoint
from database.mongodb.helpers import upsert_one, read

class MongoCheckpoint(BaseCheckpoint):

    def __init__(self, db, src: str, collection_name: str = "checkpoints"):
        """
        Args:
            db: Optional MongoDB database/session object
            src (str): Datasource (springer, openalex,...)
            collection_name: Name of collection to store checkpoints
        """

        super().__init__(db, src)
        self._collection_name = collection_name
        self._collection = self._db[self._collection_name]


    def get_checkpoint(self) -> str:
        """
        Get the last checkpoint for a given source.

        Returns:
            str: Last saved offset.
        """

        checkpoint = read(collection = self._collection, filter = {'source': self._src})

        return checkpoint[0].get('offset', "") if checkpoint else ""


    def save_checkpoint(self, value: str) -> None:
        """
        Save checkpoint for a given source.

        Uses upsert to handle first-time insert or update existing offset.

        Args:
            value (int): Last processed record index / offset
        """

        upsert_one(collection = self._collection,
                   query = {'source': self._src},
                   data = {'offset': value})



