from abc import ABC, abstractmethod

class BaseScraper(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def fetch_data(self) -> list[dict]:
        """
        Abstract method to fetch data.

        Returns: Raw list of papers (unprocessed).
        """

        pass

