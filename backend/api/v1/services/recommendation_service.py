import sys
import os
from typing import Optional, List, Dict, Any

from api.v1.models import ConferenceRecommendation

class RecommendationService:
  """
  Core engine for retrieving and ranking research papers based on user queries.
  
  This class implements a Hybrid Search strategy combining:
  1. Semantic Search (Vector Similarity via HNSW)
  2. Keyword Search (BM25/TF-IDF via Postgres Full Text Search)
  
  The results are merged and re-ranked using Reciprocal Rank Fusion (RRF) algorithm.
  Final results are enriched with metadata (Venue Name) via SQL Joins.
  """
  def __init__(
    self, 
    filter_top_k: int = 100, 
    rrf_k: int = 60, 
    final_top_k: int = 10
  ):
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
    self.rrk_k = rrf_k
    self.final_top_k = final_top_k
    self.processor = DataPreprocessor()
    self.combiner = DocumentCombiner()
    self.embedding = EmbeddingService(api_key=get_api_key("GOOGLE_API_KEY"))

  async def handle_user_input(
    self, 
    user_title: Optional[str],
    user_abtract: Optional[str],
    user_keyword: Optional[str]
  ) -> Dict[str, Any]:
    processed_query = self.processor.process_user_input(
      title=user_title,
      abstract=user_abtract,
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
    
    return {
      "vector_search_query": vector_search_query,
      "keyword_search_query": keyword_search_query
    }
    
  async def get_recommendations(
    self,
    title: Optional[str] = None,
    abstract: Optional[str] = None,
    keywords: Optional[str] = None,
  ) -> List[ConferenceRecommendation]:
    """
    Get conference recommendations based on paper input.

    Args:
      title: Paper title
      abstract: Paper abstract
      keywords: Paper keywords
      
    Returns:
        List of conference recommendations
    """
    try:
      queries = await self.handle_user_input(
        user_title=title,
        user_abtract=abstract,
        user_keyword=keywords
      )
      
      vector_query = queries["vector_search_query"]
      keyword_query = queries["keyword_search_query"]
      
      query_embedding = self.embedding.embed_query(vector_query).tolist()
      
      # TODO
      # write config ORM for vector & keyword search + reranking with RRF

      # Sample return
      return [
        ConferenceRecommendation(
            conference_name="International Conference on Machine Learning"
        ),
        ConferenceRecommendation(
            conference_name="Neural Information Processing Systems"
        ),
        ConferenceRecommendation(
            conference_name="ACL – Annual Meeting of the Association for Computational Linguistics"
        ),
      ][:self.final_top_k]

    except Exception as e:
      print(f"Error in get_recommendations: {e}")


