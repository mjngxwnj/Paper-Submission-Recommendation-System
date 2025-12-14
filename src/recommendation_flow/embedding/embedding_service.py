import time
import logging
import numpy as np
import pandas as pd
from typing import List

from google import genai
from google.genai import types
from recommendation_flow.utils.helpers import parse_api_keys
from recommendation_flow.utils.status_code import GoogleAPIChecker

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
      model_name (str, optional): Embedding model name. Defaults to "text-embedding-004".
      batch_size (int, optional): Number of documents per batch. Defaults to 200.
      request_per_minute_limit (int, optional): Maximum number of requests allowed per minute. Defaults to 55.
      request_per_day_limit (int, optional): Maximum number of requests allowed per day. Defaults to 1450.
      
    Raises:
      ValueError: If no valid API keys are provided.

    Notes:
      - The service supports multiple API keys, which are parsed and rotated 
        automatically to handle rate limits.
      - The client is initialized upon instantiation to ensure readiness 
        for embedding requests.
    """
    self.api_keys = parse_api_keys(api_key)
    if not self.api_keys:
      raise ValueError("No valid API keys provided.")
    
    self.current_key_idx = 0
    self.model_name = model_name
    self.batch_size = batch_size
    self.rpm_limit = request_per_minute_limit
    self.rpd_limit = request_per_day_limit
    
    self._initialize_client()
  
  # -----------------------------------------------------------------------------------
  def _initialize_client(self):
    current_key = self.api_keys[self.current_key_idx]
    masked_key = f"...{current_key[-4:]}"
    print(f"Initializing GenAI Client with key[{self.current_key_idx}] ({masked_key})")
    
    self.client = genai.Client(api_key=current_key)
  
  # -----------------------------------------------------------------------------------
  def _rotate_key(self) -> bool:
    next_idx = self.current_key_idx + 1
    if next_idx >= len(self.api_keys):
      print("All API keys exhausted - cannot rotate anymore.")
      return False
    
    print(f"Rotating key {self.current_key_idx} to {next_idx}")
    self.current_key_idx = next_idx
    self._initialize_client()
    time.sleep(0.5)
    return True
  
  # -----------------------------------------------------------------------------------
  def _call_embed_api(self, contents, task_type):
    """
    Centralized API call with retry, error handling and key rotation.
    """
    max_attempts = len(self.api_keys) * 2
    
    for attempt in range(max_attempts):
      try:
        res = self.client.models.embed_content(
          model=self.model_name,
          contents=contents,
          config=types.EmbedContentConfig(
            task_type = task_type,
            output_dimensionality=768
          )
        )  
        return res
      
      except Exception as e:
        status = GoogleAPIChecker.extract_staus_code(e)
        print(f"[ERROR] key[{self.current_key_idx}] status={status} error={e}")
        
        # No status -> unknown error -> retry
        if status is None:
          print(f"Unknown Error. Retrying with backoff...")
          time.sleep(1.5)
          continue
        
        # 5xx -> server error -> retry
        if status >= 500:
          print(f"Server Error. Retrying after 2s...")
          time.sleep(2)
          
        # Should rotate or not?
        if GoogleAPIChecker.should_rotate_key(status):
          if self._rotate_key():
            continue
          else:
            raise RuntimeError(f"All API keys exhausted (status {status}).")
        
        raise RuntimeError(f"Client error {status}: {e}")
      
    raise RuntimeError("Max retry limit exceeded.")

  # -----------------------------------------------------------------------------------
  def embed_documents(self, texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for dataset documents (combined_text).
    Task: RETRIEVAL_DOCUMENT

    Args:
      texts (List[str]): List of document texts.

    Returns:
      np.ndarray: 2D array (num_docs, embedding_dim).
    """
    if not texts: 
      return []
    
    contents = [{"parts": [{"text": t}]} for t in texts]
    response = self._call_embed_api(contents, "RETRIEVAL_DOCUMENT")
    return [emb.values for emb in response.embeddings]
  
  # -----------------------------------------------------------------------------------
  def embed_query(self, text: str) -> np.ndarray:
    """
    Generate an embedding for user input combined_text.
    Task: RETRIEVAL_QUERY

    Args:
      text (str): User input string.

    Returns:
      np.ndarray: 1D vector (embedding_dim,).
    """
    contents = [{"parts": [{"text": text}]}]
    response = self._call_embed_api(contents, "RETRIEVAL_QUERY")
    return np.array(response.embeddings[0].values)

  # -----------------------------------------------------------------------------------
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
          sleep_time = 60 - elapsed_time + 0.5
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

      batch_df.loc[:, 'embedding'] = vectors
      results.append(batch_df[['doi', 'combined_text', 'embedding']])
      
      time.sleep(0.1)

    if not results:
      return pd.DataFrame(columns=["doi", "combined_text", "embedding"])

    return pd.concat(results, ignore_index=True)
