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
        """
        Extract unique venues and their corresponding execution datetime.

        Args:
            df (pd.DataFrame): Raw DataFrame containing the target_venue.

        Returns:
            pd.DataFrame: A DataFrame with unique venues standardized into:
                - name: Venue name
        """

        venue_df = df[['target_venue']].dropna(subset=['target_venue'])

        venue_df = venue_df.drop_duplicates(subset=['target_venue'], keep='first')

        venue_df = venue_df.rename(columns={
            'target_venue': 'name'
        })

        return venue_df.where(pd.notna(venue_df), None)


    def _transform_ingestion_source(self) -> pd.DataFrame:
        """
        Produce a static table of ingestion sources with fixed IDs.

        Returns:
            pd.DataFrame: A DataFrame with columns:
                - id (int): Unique ID for the ingestion source
                - name (str): Name of the ingestion source
              (springer=1, openalex=2, scopus=3)
        """

        ingestion_source_df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['springer', 'openalex', 'scopus']
        })

        return ingestion_source_df


    def _explode_keyword(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize, clean, split, and flatten keyword data from the raw dataset.

        Args:
            df (pd.DataFrame): Raw DataFrame containing keyword, doi.

        Returns:
            tuple(pd.DataFrame, pd.DataFrame):
                1. bridge_paper_keyword_df:
                    - paper_doi
                    - name (keyword)
                2. keyword_only:
                    - name (unique keyword list)
        """

        bridge_paper_keyword_df = df[['doi', 'keyword', 'execution_datetime']].dropna(subset=['keyword'])

        def normalize_keywords(x):
            if x is None:
                return []

            if isinstance(x, (list, np.ndarray)):
                return [str(i).strip() for i in x if pd.notna(i)]

            if isinstance(x, str):
                try:
                    parsed = ast.literal_eval(x)
                    if isinstance(parsed, list):
                        return [str(i).strip() for i in parsed if pd.notna(i)]
                except:
                    pass

                if "," in x:
                    return [i.strip() for i in x.split(",") if i.strip()]

                return [x.strip()]

            return [str(x).strip()]

        bridge_paper_keyword_df['keyword'] = bridge_paper_keyword_df['keyword'].apply(normalize_keywords)
        bridge_paper_keyword_df = bridge_paper_keyword_df.explode('keyword')
        bridge_paper_keyword_df.dropna(subset=['keyword'], inplace=True)

        bridge_paper_keyword_df = bridge_paper_keyword_df[
            (bridge_paper_keyword_df['keyword'].str.len() < 100) &
            (bridge_paper_keyword_df['keyword'].str.len() >= 2)
        ]

        bridge_paper_keyword_df = bridge_paper_keyword_df.drop_duplicates(subset=['doi','keyword'], keep='first')

        bridge_paper_keyword_df = bridge_paper_keyword_df.rename(columns={
            'doi': 'paper_doi',
            'keyword': 'name'
        })

        keyword_only = bridge_paper_keyword_df[['name']].drop_duplicates(subset=['name'])

        return bridge_paper_keyword_df, keyword_only


    def _transform_author(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize and explode nested author–ORCID structures into two tables:

        Args:
            df (pd.DataFrame): Raw DataFrame containing `doi`, `author`,
                and `orcid`.

        Returns:
            tuple(pd.DataFrame, pd.DataFrame):
                1. bridge_paper_author_df:
                    - paper_doi
                    - author_id (ORCID)
                2. author_df:
                    - orcid
                    - name (author's name)
        """

        tmp_df = df[['doi', 'author', 'orcid']]

        tmp_df['author'] = tmp_df['author'].apply(lambda x: x if isinstance(x, list) else [])
        tmp_df['orcid'] = tmp_df['orcid'].apply(lambda x: x if isinstance(x, list) else [])

        tmp_df = tmp_df[
            (tmp_df['author'].apply(len) > 0) &
            (tmp_df['orcid'].apply(len) > 0) &
            (tmp_df['author'].apply(len) == tmp_df['orcid'].apply(len))
        ]

        tmp_df = tmp_df.explode(['author', 'orcid'], ignore_index=True)

        tmp_df['author'] = tmp_df['author'].astype(str).str.strip()
        tmp_df['orcid'] = tmp_df['orcid'].astype(str).str.strip()
        tmp_df = tmp_df[(tmp_df['author'] != '') & (tmp_df['orcid'] != '')]

        tmp_df = tmp_df.dropna(subset=['author', 'orcid'])

        bridge_paper_author_df = tmp_df[['doi', 'orcid']].rename(columns={
            'doi': 'paper_doi',
            'orcid': 'author_id'
        })

        author_df = tmp_df[['orcid', 'author']].rename(columns={
            'author': 'name'
        }).drop_duplicates(subset=['orcid'])

        return bridge_paper_author_df, author_df


    def _transform_paper_keyword(self, paper_keyword_df: pd.DataFrame, keyword_df: pd.DataFrame) -> pd.DataFrame:
        """
        Map exploded paper–keyword data to keyword IDs.

        Args:
            paper_keyword_df (pd.DataFrame): Bridge table from `_explode_keyword`.
            keyword_df (pd.DataFrame): Keyword dimension table containing IDs.

        Returns:
            pd.DataFrame: A standardized bridge table:
                - paper_doi
                - keyword_id
        """
        if paper_keyword_df.empty or keyword_df.empty:
            return pd.DataFrame(columns=['paper_doi', 'keyword_id'])
        # Merge to get keyword_id based on keyword name

        paper_keyword_df = paper_keyword_df.merge(
            keyword_df[['name', 'id']],
            on='name',
            how='left'
        )

        # Select and rename columns
        paper_keyword_df = paper_keyword_df[['paper_doi', 'id']].copy()
        paper_keyword_df = paper_keyword_df.rename(columns={'id': 'keyword_id'})

        # Drop rows where keyword_id is NaN (keywords that couldn't be matched)
        paper_keyword_df = paper_keyword_df.dropna(subset=['keyword_id', 'paper_doi'])

        # Convert keyword_id to integer type
        paper_keyword_df['keyword_id'] = paper_keyword_df['keyword_id'].astype(int)

        return paper_keyword_df.where(pd.notna(paper_keyword_df), None)


    def _transform_paper(self, df: pd.DataFrame, venue_df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform raw paper data to match the paper table schema.

        Args:
            df: Raw DataFrame containing paper information
            venue_df: DataFrame containing venue names and their assigned IDs

        Returns:
            DataFrame with paper table structure
        """
        if df is None or df.empty:
            return pd.DataFrame(columns=[
                'doi', 'title', 'abstract', 'abstract_link',
                'open_access', 'publication_day', 'publication_month', 'publication_year',
                'venue_id', 'ingestion_source_id', 'created_at'
            ])

        # Start with base columns
        paper_df = df[[
            'doi', 'title', 'abstract', 'abstractlink',
            'openaccess', 'publication_day', 'publication_month', 'publication_year',
            'target_venue', 'ingestion_source', 'execution_datetime'
        ]].copy()

        # Rename columns to match schema
        paper_df = paper_df.rename(columns={
            'abstractlink': 'abstract_link',
            'openaccess': 'open_access',
            'execution_datetime': 'created_at'
        })

        # Map ingestion_source to ingestion_source_id
        source_mapping = {
            'springer': 1,
            'openalex': 2,
            'scopus': 3
        }
        paper_df['ingestion_source_id'] = paper_df['ingestion_source'].map(source_mapping)

        # Merge with venue_df to get venue_id
        if not venue_df.empty and 'id' in venue_df.columns:
            paper_df = paper_df.merge(
                venue_df[['name', 'id']],
                left_on='target_venue',
                right_on='name',
                how='left'
            )
            paper_df = paper_df.rename(columns={'id': 'venue_id'})
            paper_df = paper_df.drop(columns=['name'], errors='ignore')
        else:
            paper_df['venue_id'] = None

        # Select final columns in correct order
        final_columns = [
            'doi', 'title', 'abstract', 'abstract_link',
            'open_access', 'publication_day', 'publication_month', 'publication_year',
            'venue_id', 'ingestion_source_id', 'created_at'
        ]

        paper_df = paper_df[final_columns]

        # Handle missing values
        paper_df['venue_id'] = paper_df['venue_id'].astype('Int64')  # Nullable integer
        paper_df['ingestion_source_id'] = paper_df['ingestion_source_id'].astype('Int64')
        paper_df['publication_day'] = paper_df['publication_day'].astype('Int64')
        paper_df['publication_month'] = paper_df['publication_month'].astype('Int64')
        paper_df['publication_year'] = paper_df['publication_year'].astype('Int64')

        # Remove duplicates based on DOI, keep first occurrence
        paper_df = paper_df.drop_duplicates(subset=['doi'], keep='first')

        # Convert to object dtype and replace all NaN/NA with None
        paper_df = paper_df.astype(object).where(pd.notna(paper_df), None)

        return paper_df


    def transform_bridges(self,
                          paper_keyword_df: pd.DataFrame,
                          keyword_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        """
        Transform and assemble bridge tables using dimension-resolved keyword IDs.

        Args:
            paper_keyword_df (pd.DataFrame): Bridge table linking papers and keywords.
            keyword_df (pd.DataFrame): Dimension table with keyword IDs.

        Returns:
            dict[str, pd.DataFrame]:
                - paper_keyword: Final bridge table with foreign keys applied.
        """

        if paper_keyword_df is None or paper_keyword_df.empty:
            return {
                'paper_keyword': pd.DataFrame(),
            }

        paper_keyword = self._transform_paper_keyword(paper_keyword_df, keyword_df)

        return {
            'paper_keyword': paper_keyword
        }


    def transform_dimensions(self, df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        """
        Generate all dimension and intermediate bridge tables from raw input.

        Args:
            df (pd.DataFrame): Raw ingestion dataset.

        Returns:
            dict[str, pd.DataFrame]: Dictionary of dimension and bridge tables.
        """

        if df is None or df.empty:
            return {
                'venue': pd.DataFrame(),
                'ingestion_source': pd.DataFrame(),
                'bridge_paper_keyword': pd.DataFrame(),
                'keyword': pd.DataFrame()
            }

        venue = self._transform_venue(df)
        ingestion_source = self._transform_ingestion_source()
        bridge_paper_keyword, keyword = self._explode_keyword(df)
        bridge_paper_author, author = self._transform_author(df)

        return {
            'venue': venue,
            'ingestion_source': ingestion_source,
            'bridge_paper_keyword': bridge_paper_keyword,
            'keyword': keyword,
            'bridge_paper_author': bridge_paper_author,
            'author': author
        }


    def transform_facts(self,
                        paper_df: pd.DataFrame,
                        venue_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        """
        Produce fact tables using resolved dimension IDs.

        Args:
            paper_df (pd.DataFrame): Raw paper data.
            venue_df (pd.DataFrame): Dimension table with venue IDs.

        Returns:
            dict[str, pd.DataFrame]:
                - paper: The fully normalized paper fact table.
        """

        return {
            'paper': self._transform_paper(paper_df, venue_df)
        }



