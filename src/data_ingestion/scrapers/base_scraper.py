from abc import ABC, abstractmethod
from typing import Union

class BaseScraper(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def fetch_data(self, api_key: str, checkpoint: Union[int, str]) -> tuple[list[dict], Union[int, str]]:
        """
        Abstract method to fetch data.

        Returns: Raw list of papers (unprocessed).
        """

        pass

