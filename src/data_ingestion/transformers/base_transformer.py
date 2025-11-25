from abc import ABC, abstractmethod
import pandas as pd

class BaseTransformer(ABC):

    @abstractmethod
    def transform_dimensions(self, df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        pass
