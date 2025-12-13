import pandas as pd

class DocumentDeduplicator:
  """
  Deduplicate documents after combined_text creation.
  Ensures 1 embedding per DOI.
  """
  
  @staticmethod
  def deduplicator_by_doi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only one row per DOI
    Assumes combined_text is identical for the same DOI
    
    Args:
      df (pd.DataFrame): DataFrame with 'doi' and 'combined_text'

    Returns:
      pd.DataFrame: Deduplicated DataFrame
    """
    
    return (
      df
      .drop_duplicates(subset=["doi"])
      .reset_index(drop=True)
    )