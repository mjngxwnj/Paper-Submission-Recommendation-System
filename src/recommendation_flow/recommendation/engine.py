from typing import List, Dict, Any
from integration.secrets import get_api_key
from src.warehouse.core.session import postgres_session

from recommendation_flow.preprocessing.data_processor import DataPreprocessor
from recommendation_flow.preprocessing.data_combiner import DocumentCombiner
from recommendation_flow.embedding.embedding_service import EmbeddingService

class RecommendationEngine:
  """
  Core engine for retrieving and ranking research papers based on user queries.
  
  This class implements a Hybrid Search strategy combining:
  1. Semantic Search (Vector Similarity via HNSW)
  2. Keyword Search (BM25/TF-IDF via Postgres Full Text Search)
  
  The results are merged and re-ranked using Reciprocal Rank Fusion (RRF) algorithm.
  Final results are enriched with metadata (Venue Name) via SQL Joins.
  """
  def __init__(self, filter_top_k: int = 100, rrf_k: int = 60, final_top_k: int = 10):
    """
    Initialize the recommendation engine configuration.

    Args:
      filter_top_k (int): Number of candidates to retrieve from EACH method (Vector & Keyword).
                          Total candidates before RRF will be <= 2 * filter_top_k.
      rrf_k (int): The smoothing constant 'k' in RRF formula: 1 / (k + rank).
                   Higher values dampen the impact of high rankings.
      final_top_k (int): The final number of recommendations to return to the user.
    """
    self.filter_top_k = filter_top_k
    self.rrf_k = rrf_k
    self.final_top_k = final_top_k
    self.processor = DataPreprocessor()
    self.combiner = DocumentCombiner()
    self.embedding = EmbeddingService(api_key=get_api_key("GOOGLE_API_KEY"))
    
  # ----------------------------------------------------------------------------
  def search(
    self, 
    user_title: str, 
    user_abstract: str, 
    user_keyword: str
  ) -> List[Dict[str, Any]]:
    processed_query = self.processor.process_user_input(
      title=user_title,
      abstract=user_abstract,
      keyword=user_keyword
    )
    
    vector_search_query = self.combiner.combine_user_query(
      title=processed_query["title"],
      abstract=processed_query["abstract"],
      keyword=processed_query["keyword"],
      task="VECTOR_SEARCH"
    )
    
    keyword_search_query = self.combiner.combine_user_query(
      title=processed_query["title"],
      abstract=processed_query["abstract"],
      keyword=processed_query["keyword"],
      task="KEYWORD_SEARCH"
    )
    
    embed_query = self.embedding.embed_query(vector_search_query).tolist()
    
    results = []
    
    try:
      with postgres_session() as cur:
        sql = """
        WITH semantic_search AS (
          SELECT  
            doi, title, abstract, combined_text, embedding, venue_id,
            ROW_NUMBER() OVER (ORDER BY embedding <=> %s::vector) AS rank_vec
          FROM core.paper
          ORDER BY embedding <=> %s::vector
          LIMIT %s
        ),
        
        keyword_search AS (
          SELECT
            doi, title, abstract, combined_text, embedding, venue_id,
            ROW_NUMBER() OVER (ORDER BY ts_rank(tsv, websearch_to_tsquery('english', %s)) DESC) AS rank_ts
          FROM core.paper
          WHERE tsv @@ websearch_to_tsquery('english', %s)
          ORDER BY ts_rank(tsv, websearch_to_tsquery('english', %s)) DESC
          LIMIT %s
        ),
        
        rrf_ranking AS (
          SELECT 
            COALESCE(s.doi, k.doi) as doi,
            COALESCE(s.title, k.title) as title,
            COALESCE(s.abstract, k.abstract) as abstract,
            COALESCE(s.combined_text, k.combined_text) as combined_text,
            COALESCE(s.embedding, k.embedding) as embedding,
            COALESCE(s.venue_id, k.venue_id) as venue_id,
          
            -- RRF Score Calculation
            (
              COALESCE(1.0 / (%s + s.rank_vec), 0.0) + 
              COALESCE(1.0 / (%s + k.rank_ts), 0.0)
            ) as rrf_score
          FROM semantic_search s
          FULL OUTER JOIN keyword_search k ON s.doi = k.doi
        )
        
        -- Final Selection
        SELECT 
          r.doi, r.title, r.abstract, r.combined_text, 
          v.name as venue_name,
          r.rrf_score
        FROM rrf_ranking r
        LEFT JOIN core.venue v ON r.venue_id = v.venue_id
        ORDER BY r.rrf_score DESC
        LIMIT %s;
        """

        params = (
          embed_query, embed_query, self.filter_top_k,
          keyword_search_query, keyword_search_query, keyword_search_query, self.filter_top_k,
          self.rrf_k, self.rrf_k,
          self.final_top_k
        )
        
        cur.execute(sql, params)
        rows = cur.fetchall()
        
        for row in rows:
          results.append({
            "doi": row[0],
            "title": row[1],
            "abstract": row[2],
            "combined_text": row[3],
            "target_venue": row[4] if row[4] else "Unknown Venue",
            "rrf_score": float(row[5])
          })
            
      return results
    except Exception as e:
      print(f"Recommendation Engine Error: {e}")
      return []