from abc import ABC, abstractmethod

class BaseCheckpoint(ABC):

    def __init__(self, db, src: str):
        """
        Args:
            db: Optional database/session object (for subclass to use).
        """

        self._db = db
        self._src = src


    @abstractmethod
    def get_checkpoint(self) -> str:
        """
        Load checkpoint.

        Returns:
            str: Last stored offset.
        """

        pass


    @abstractmethod
    def save_checkpoint(self, value: str) -> None:
        """
        Save checkpoint.

        Args:
            value (str): Offset or batch index.
        """

        pass


