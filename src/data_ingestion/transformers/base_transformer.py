from abc import ABC, abstractmethod
import pandas as pd

class BaseTransformer(ABC):

    @abstractmethod
    def transform_bridges(self,
                          paper_keyword_df: pd.DataFrame,
                          keyword_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        pass


    @abstractmethod
    def transform_dimensions(self, df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        pass


    @abstractmethod
    def transform_facts(self,
                        paper_df: pd.DataFrame,
                        venue_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        pass
