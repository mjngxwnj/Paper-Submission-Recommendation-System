from data_ingestion.transformers import BaseTransformer
import pandas as pd
import numpy as np
from datetime import datetime
import ast
import regex as re

class UnifiedTransformer(BaseTransformer):

    def _transform_venue(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract unique venues and their corresponding execution datetime"""
        venues_df = df[['target_venue', 'execution_datetime']].dropna(subset=['target_venue'])

        venues_df = venues_df.drop_duplicates(subset=['target_venue'], keep='first')

        venues_df = venues_df.rename(columns={
            'target_venue': 'name',
            'execution_datetime': 'created_at'
        })

        return venues_df.where(pd.notna(venues_df), None)


    def _transform_ingestion_source(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a fixed DataFrame for ingestion sources with specified IDs"""
        ingestion_source_df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['springer', 'openalex', 'scopus']
        })

        return ingestion_source_df


    def _transform_keyword(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract unique keywords and their corresponding execution datetime"""
        keywords_df = df[['keyword', 'execution_datetime']].dropna(subset=['keyword']).copy()

        def safe_literal_eval(x):
            try:
                evaluated = ast.literal_eval(x)
                if isinstance(evaluated, list):
                    return evaluated
                else:
                    return [str(x)]
            except (ValueError, SyntaxError):
                return [str(x)]

        keywords_df['keyword'] = keywords_df['keyword'].apply(safe_literal_eval)
        keywords_df = keywords_df.explode('keyword')
        keywords_df.dropna(subset=['keyword'], inplace=True) # Added: Drop rows where 'keyword' is NaN after explode
        keywords_df = keywords_df[keywords_df['keyword'] != ''].copy()

        # Add new cleaning steps: strip, lowercase, and remove punctuation
        keywords_df['keyword'] = keywords_df['keyword'].astype(str) # Added: Ensure 'keyword' is string type
        keywords_df['keyword'] = keywords_df['keyword'].str.strip()
        keywords_df['keyword'] = keywords_df['keyword'].str.lower() # Convert to lowercase

        # Remove punctuation. The regex '[^\w\s]' removes anything that is not a word character (alphanumeric + underscore) or whitespace.
        keywords_df['keyword'] = keywords_df['keyword'].apply(lambda x: re.sub(r'\p{P}', '', x)) # Using \p{P} for Unicode punctuation

        keywords_df = keywords_df.sort_values(by='execution_datetime')
        keywords_df = keywords_df.drop_duplicates(subset=['keyword'], keep='first')

        keywords_df = keywords_df.rename(columns={
            'keyword': 'name',
            'execution_datetime': 'created_at'
        })

        return keywords_df


    def transform_dimensions(self, df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        """Phase 1: Transform dimension tables only"""
        return {
            'venue': self._transform_venue(df),
            'ingestion_source': self._transform_ingestion_source(df),
            'keyword': self._transform_keyword(df)
            # 'author': self._transform_author(df)
        }

    # def transform_facts(self, df: pd.DataFrame,
    #                    venue_mapping: dict,
    #                    source_mapping: dict,
    #                    keyword_mapping: dict,
    #                    author_mapping: dict) -> dict[str, pd.DataFrame]:
    #     """Phase 2: Transform fact and relationship tables with resolved IDs"""
    #     return {
    #         'paper': self._transform_paper(df, venue_mapping, source_mapping),
    #         'paper_author': self._transform_paper_author(df, author_mapping),
    #         'paper_keyword': self._transform_paper_keyword(df, keyword_mapping)
    #     }
