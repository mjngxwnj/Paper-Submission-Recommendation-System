from data_ingestion.transformers import BaseTransformer
import pandas as pd
import numpy as np
from datetime import datetime
import ast
import regex as re

class UnifiedTransformer(BaseTransformer):

    def __init__(self) -> None:
        """
        Define brigde table.
        """


    def _transform_venue(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract unique venues and their corresponding execution datetime"""
        venue_df = df[['target_venue', 'execution_datetime']].dropna(subset=['target_venue'])

        venue_df = venue_df.drop_duplicates(subset=['target_venue'], keep='first')

        venue_df = venue_df.rename(columns={
            'target_venue': 'name',
            'execution_datetime': 'created_at'
        })

        return venue_df.where(pd.notna(venue_df), None)


    def _transform_ingestion_source(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a fixed DataFrame for ingestion sources with specified IDs"""
        ingestion_source_df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['springer', 'openalex', 'scopus']
        })

        return ingestion_source_df


    def _explode_keyword(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract unique keywords and their corresponding execution datetime"""
        bridge_paper_keyword_df = df[['doi', 'keyword', 'execution_datetime']].dropna(subset=['keyword'])

        def safe_literal_eval(x):
            try:
                evaluated = ast.literal_eval(x)
                if isinstance(evaluated, list):
                    return evaluated
                else:
                    return [str(x)]
            except (ValueError, SyntaxError):
                return [str(x)]

        bridge_paper_keyword_df['keyword'] = bridge_paper_keyword_df['keyword'].apply(safe_literal_eval)
        bridge_paper_keyword_df = bridge_paper_keyword_df.explode('keyword')
        bridge_paper_keyword_df.dropna(subset=['keyword'], inplace=True) # Added: Drop rows where 'keyword' is NaN after explode
        bridge_paper_keyword_df = bridge_paper_keyword_df[bridge_paper_keyword_df['keyword'] != ''].copy()

        # Add new cleaning steps: strip, lowercase, and remove punctuation
        bridge_paper_keyword_df['keyword'] = bridge_paper_keyword_df['keyword'].astype(str) # Added: Ensure 'keyword' is string type
        bridge_paper_keyword_df['keyword'] = bridge_paper_keyword_df['keyword'].str.strip()
        bridge_paper_keyword_df['keyword'] = bridge_paper_keyword_df['keyword'].str.lower() # Convert to lowercase

        # Remove punctuation. The regex '[^\w\s]' removes anything that is not a word character (alphanumeric + underscore) or whitespace.
        bridge_paper_keyword_df['keyword'] = bridge_paper_keyword_df['keyword'].apply(lambda x: re.sub(r'\p{P}', '', x)) # Using \p{P} for Unicode punctuation

        bridge_paper_keyword_df = bridge_paper_keyword_df.sort_values(by='execution_datetime')
        bridge_paper_keyword_df = bridge_paper_keyword_df.drop_duplicates(subset=['doi','keyword'], keep='first')

        bridge_paper_keyword_df = bridge_paper_keyword_df.rename(columns={
            'doi': 'paper_doi',
            'keyword': 'name',
            'execution_datetime': 'created_at'
        })

        keyword_only = bridge_paper_keyword_df[['name']].drop_duplicates(subset=['name'])

        return bridge_paper_keyword_df, keyword_only


    def extract_briddges(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return {
                'bridge_paper_keyword': pd.DataFrame(),
                'keyword': pd.DataFrame()
            }

        bridge_paper_keyword, keyword = self._explode_keyword(df)

        return {
            'bridge_paper_keyword': bridge_paper_keyword,
            'keyword': keyword
        }


    def transform_bridges(self, df: pd.DataFrame):
        if df is None or df.empty:
            return {
                'bridge_paper_keyword': pd.DataFrame(),
                'keyword': pd.DataFrame()
            }

        bridge_paper_keyword, keyword = self._explode_keyword(df)

        return {
            'bridge_paper_keyword': bridge_paper_keyword,
            'keyword': keyword
        }


    def transform_dimensions(self, df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        if df is None or df.empty:
            return {
                'venue': pd.DataFrame(),
                'ingestion_source': pd.DataFrame(),
                'bridge_paper_keyword': pd.DataFrame(),
                'keyword': pd.DataFrame()
            }

        venue = self._transform_venue(df)
        ingestion_source = self._transform_ingestion_source(df)
        bridge_paper_keyword, keyword = self._explode_keyword(df)

        return {
            'venue': venue,
            'ingestion_source': ingestion_source,
            'bridge_paper_keyword': bridge_paper_keyword,
            'keyword': keyword
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
