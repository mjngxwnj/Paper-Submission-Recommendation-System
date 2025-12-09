import time
import logging
import numpy as np
import pandas as pd
from typing import List

from google import genai
from google.genai import types

class EmbeddingService:
  def __init__(
    self,
    api_key: str,
    model_name: str = "text-embedding-004",
    batch_size: int = 100,
    request_per_minute_limit: int = 55,
    request_per_day_limit: int = 1450
  ):
    """
    Initialize the EmbeddingService with API credentials and configuration.

    Args:
      api_key (str): API key for Google Generative AI.
      model_name (str, optional): Embedding model name. Defaults to "gemini-embedding-001".
      batch_size (int, optional): Number of documents per batch. Defaults to 200.
    """
    self.api_key = api_key
    self.model_name = model_name
    self.batch_size = batch_size
    self.client = genai.Client(api_key=api_key)
    self.rpm_limit = request_per_minute_limit
    self.rpd_limit = request_per_day_limit

  def embed_documents(self, texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for dataset documents (combined_text).
    Task: RETRIEVAL_DOCUMENT

    Args:
      texts (List[str]): List of document texts.

    Returns:
      np.ndarray: 2D array (num_docs, embedding_dim).
    """
    if not texts: return []

    contents = [{"parts": [{"text": t}]} for t in texts]
    try:
      res = self.client.models.embed_content(
        model=self.model_name,
        contents=contents,
        config=types.EmbedContentConfig(
          task_type="RETRIEVAL_DOCUMENT",
          output_dimensionality=768
        )
      )

      vectors = [emb.values for emb in res.embeddings]
      return vectors
    except Exception as e:
      logging.error(f"Error generate embedding, reason {e}")
      return []

  def generate_in_batches(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate embeddings for a full DataFrame in batches and return
    ONE final DataFrame (doi, combined_text, vector).

    Args:
      df (pd.DataFrame): Must contain ['doi', 'combined_text'].

    Returns:
      pd.DataFrame: Full DataFrame with vectors added.
    """
    results = []
    total = len(df)
    
    # Counter for Rate Limit
    min_request_count = 0
    daily_request_count = 0
    start_time = time.time()

    for start_idx in range(0, total, self.batch_size):
      # 1. Check Daily Limit
      if daily_request_count >= self.rpd_limit:
        print(f"Daily Request Limit Reached! Stopping process.")
        break
      
      # 2. Check Minute Limit
      if min_request_count >= self.rpm_limit:
        elapsed_time = time.time() - start_time
        
        if elapsed_time < 60:
          sleep_time = 60 - elapsed_time + 1
          print(f"Rate limit approaching ({min_request_count} reqs in {elapsed_time:.2f}s). Sleeping for {sleep_time:.2f}s...")
          time.sleep(sleep_time)
          
        min_request_count = 0
        start_time = time.time()
      
      # 3. Generate in batches
      end_idx = min(start_idx + self.batch_size, total)
      batch_df = df.iloc[start_idx:end_idx].copy()

      print(f"Processing batch embedding {start_idx} to {end_idx}...")

      vectors = self.embed_documents(batch_df['combined_text'].tolist())
      
      min_request_count += 1
      daily_request_count += 1
      
      # 4. Handle Result
      time.sleep(0.2)

      if len(vectors) != len(batch_df):
        logging.error(f"Vector length mismatch at batch {start_idx}. Skipping update.")
        continue

      batch_df.loc[:, 'vector'] = vectors
      results.append(batch_df[['doi', 'combined_text', 'vector']])
      
      time.sleep(0.1)

    if not results:
      return pd.DataFrame(columns=["doi", "combined_text", "vector"])

    return pd.concat(results, ignore_index=True)

  def embed_query(self, text: str):
    """
    Generate an embedding for user input combined_text.
    Task: RETRIEVAL_QUERY

    Args:
      text (str): User input string.

    Returns:
      np.ndarray: 1D vector (embedding_dim,).
    """
    contents = [{"parts": [{"text": text}]}]

    res = self.client.models.embed_content(
      model=self.model_name,
      contents=contents,
      config=types.EmbedContentConfig(
        task_type="RETRIEVAL_QUERY",
        output_dimensionality=768
      )
    )

    return np.array(res.embeddings[0].values)