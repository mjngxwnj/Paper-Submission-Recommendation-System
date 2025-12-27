import logging
import numpy as np
from google import genai
from google.genai import types
from typing import List, Dict, Any

from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, Computed, ForeignKey, select, desc, func

from .db_service import get_db_session

# ============================= ORM CONFIGURATION ==============================
class Base(DeclarativeBase):
  pass

class Venue(Base):
  __tablename__ = "venue"
  __table_args__ = {"schema": "core"}
  
  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  name: Mapped[str] = mapped_column(String(512))
  
class Paper(Base):
  __tablename__ = "paper"
  __table_args__ = {"schema": "core"}
  
  doi: Mapped[str] = mapped_column(String(255), primary_key=True)
  title: Mapped[str] = mapped_column(Text)
  abstract: Mapped[str] = mapped_column(Text)
  combined_text: Mapped[str] = mapped_column(Text)
  venue_id: Mapped[int] = mapped_column(ForeignKey("core.venue.id"))
  
  embedding = mapped_column(Vector(768))
  tsv = mapped_column(
    TSVECTOR,
    Computed("to_tsvector('english', coalesce(combined_text, ''))", persisted=True)                  
  )
  
  venue = relationship("Venue")

# ============================= EMBEDDING SERVICE ==============================
class EmbeddingService:
  def __init__(
    self,
    api_key: str,
    model_name: str = "text-embedding-004",
  ):
    self.api_key = api_key
    self.model_name = model_name
    self.client = genai.Client(api_key=api_key)
  
  # ----------------------------------------------------------------------------
  def embed_user_query(self, text: str) -> np.array:
    if not text:
      return np.array([])
    
    contents = [{"parts": [{"text": text}]}]
    try:
      response = self.client.models.embed_content(
        model = self.model_name,
        contents=contents,
        config=types.EmbedContentConfig(
          task_type="RETRIEVAL_QUERY",
          output_dimensionality=768
        )
      )
      return np.array(response.embeddings[0].values)
    
    except Exception as e:
      logging.error(f"Error calling embedding API: {e}")
      return []
    
  # ----------------------------------------------------------------------------
  def hybrid_search_rrf(
    self,
    vector_search_query: str,
    keyword_search_query: str,
    filter_top_k: int = 100,
    rrf_k: int = 60,
    final_top_k: int = 10
  ) -> List[Dict[str, Any]]:
    """
    Initialize the Hybrid Search flow.

    Args:
      filter_top_k (int): Number of candidates to retrieve from EACH method (Vector & Keyword).
                          Total candidates before RRF will be <= 2 * filter_top_k.
      rrf_k (int): The smoothing constant 'k' in RRF formula: 1 / (k + rank).
                   Higher values dampen the impact of high rankings.
      final_top_k (int): The final number of recommendations to return to the user.
      
    Return:
      List of top recommended venues coressponding with the rrf scores.
    """
    user_embedding = self.embed_user_query(vector_search_query)
    if user_embedding is None or user_embedding.size == 0:
      return []
    
    results = []
    
    with get_db_session() as session:
      try:
        # SEMANTIC SEARCH CTE (Search by vector)
        distance_col = Paper.embedding.cosine_distance(user_embedding.tolist())
        
        stmt_semantic = (
          select(
            Paper.doi,
            Paper.venue_id,
            func.row_number().over(order_by=distance_col).label("rank_vec")
          )
          .order_by(distance_col)
          .limit(filter_top_k)
          .cte("semantic_search")
        )
        
        # KEYWORD SEARCH CTE (Search by text or full text search)
        ts_query = func.websearch_to_tsquery('english', keyword_search_query)
        rank_col = func.ts_rank(Paper.tsv, ts_query)
        
        stmt_keyword = (
          select(
            Paper.doi,
            Paper.venue_id,
            func.row_number().over(order_by=desc(rank_col)).label("rank_ts")
          )
          .where(Paper.tsv.op('@@')(ts_query))
          .order_by(desc(rank_col))
          .limit(filter_top_k)
          .cte("keyword_search")
        )
        
        # RRF CALCULATION (Combine with 2 CTEs)
        s = stmt_semantic.alias("s")
        k = stmt_keyword.alias("k")
        
        score_vec = func.coalesce(1.0/ (rrf_k + s.c.rank_vec), 0.0)
        score_ts = func.coalesce(1.0 / (rrf_k + k.c.rank_ts), 0.0)
        
        rrf_score_col = (score_vec + score_ts).label("rrf_score")
        final_venue_id = func.coalesce(s.c.venue_id, k.c.venue_id).label("venue_id")
        
        stmt_rrf = (
          select(final_venue_id, rrf_score_col)
          .select_from(s)
          .join(k, s.c.doi == k.c.doi, full=True)
          .subquery("rrf_ranking")
        )
        
        # FINAL QUERY (Join Venue & Sort)
        r = stmt_rrf.alias("r")
        
        final_query = (
          select(
            Venue.name.label("target_venue"),
            r.c.rrf_score
          )
          .select_from(r)
          .join(Venue, r.c.venue_id == Venue.id, isouter=True)
          .order_by(desc(r.c.rrf_score))
          .limit(final_top_k)
        )
        
        rows = session.execute(final_query).all()
        
        for row in rows:
          if row.target_venue:
            results.append({
              "target_venue": row.target_venue,
              "score": float(row.rrf_score)
            })
    
      except Exception as e:        
        logging.error(f"Hybrid Search Error: {e}")

    return results