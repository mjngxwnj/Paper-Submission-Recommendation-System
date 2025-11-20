from data_ingestion.transformers import BaseTransformer
import pandas as pd

class UnifiedTransformer(BaseTransformer):

    def _transform_paper(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def _transform_author(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def transform(self, df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        return {
            'papers': self._transform_paper(df),
            'authors': self._transform_author(df)
        }
