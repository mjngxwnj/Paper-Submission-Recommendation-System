from data_ingestion.state.base_checkpoint import BaseCheckpoint
from database.mongodb.helpers import upsert_one, read

class CheckpointManager(BaseCheckpoint):

    def __init__(self, db, src: str, collection_name: str = "checkpoints"):
        """
        Args:
            db: Optional MongoDB database/session object
            source (str): Datasource (springer, openalex,...)
            collection_name: Name of collection to store checkpoints
        """

        super().__init__(db, src)
        self._collection_name = collection_name
        self._collection = self._db[self._collection_name]


    def get_checkpoint(self) -> dict:
        """
        Get the last checkpoint for a given source.

        Returns:
            str: Last saved offset.
        """

        checkpoint = read(collection=self._collection, filter={'source': self._src})

        if checkpoint:
            doc = checkpoint[0]
            return {
                "scrape_checkpoint": doc.get("scrape_checkpoint"),
                "last_sync_date": doc.get("last_sync_date")
            }

        return {
            "scrape_checkpoint": None,
            "last_sync_date": None
        }


    def save_checkpoint(self, checkpoint: dict) -> None:
        """
        Save checkpoint for a given source.

        Uses upsert to handle first-time insert or update existing offset.

        Args:
            value (int): Last processed record index / offset
        """

        upsert_one(collection = self._collection,
                   query = {'source': self._src},
                   data = checkpoint)



