from abc import ABC, abstractmethod

class BaseCheckpoint(ABC):

    def __init__(self, db):
        """
        Args:
            db: Optional database/session object (for subclass to use).
        """

        self._db = db


    @abstractmethod
    def get_checkpoint(self, source: str) -> str:
        """
        Load checkpoint.

        Args:
            source (str): Datasource to get checkpoint.

        Returns:
            str: Last stored offset.
        """

        pass


    @abstractmethod
    def save_checkpoint(self, source: str, value: str) -> None:
        """
        Save checkpoint.

        Args:
            source (str): Datasource (springer, openalex,...)
            value (str): Offset or batch index.
        """

        pass


