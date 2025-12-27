import os
import logging
from typing import Optional, List, Dict

from .utils import UserInputProcessor
from .embedding_service import EmbeddingService
from api.v1.models import ConferenceRecommendation

class RecommendationService:
  def __init__(self):
    self.processor = UserInputProcessor()
    self.embedding_service = EmbeddingService(api_key=os.getenv("GOOGLE_API_KEY"))
  
  # ----------------------------------------------------------------------------
  def handle_user_query(
    self,
    user_title: Optional[str] = None,
    user_abstract: Optional[str] = None,
    user_keyword: Optional[str] = None
  ) -> Dict[str, str]:
    processed_query = self.processor.process_user_input(
      title=user_title,
      abstract=user_abstract,
      keyword=user_keyword
    )
    
    vector_search = self.processor.combine_user_query(
      title=processed_query["title"],
      abstract=processed_query["abstract"],
      keyword=processed_query["keyword"],
      task_type="VECTOR_SEARCH"
    )
    
    keyword_search = self.processor.combine_user_query(
      title=processed_query["title"],
      abstract=processed_query["abstract"],
      keyword=processed_query["keyword"],
      task_type="KEYWORD_SEARCH"
    )
    
    return {
      "vector_search_query": vector_search,
      "keyword_search_query": keyword_search
    }
    
  async def get_recommendations(
    self,
    title: Optional[str] = None,
    abstract: Optional[str] = None,
    keyword: Optional[str] = None,
  ) -> List[ConferenceRecommendation]:
    """
    Orchestrates the recommendation flow:
    Input -> Preprocess -> Hybrid Search (via EmbeddingService) -> Format Output
    
    Args:
      title (Optional[str]): The user-provided title query.
      abstract (Optional[str]): The user-provided abstract query.
      keyword (Optional[str]): The user-provided keywords.
      
    Returns:
      List of conference recommendations
    """
    try:
      processed_user_input = self.handle_user_query(
        user_title=title,
        user_abstract=abstract,
        user_keyword=keyword
      )
      
      results = self.embedding_service.hybrid_search_rrf(
        vector_search_query=processed_user_input["vector_search_query"],
        keyword_search_query=processed_user_input["keyword_search_query"]
      )
      
      recommendations = []
      seen_venues = set()
      
      for item in results:
        venue_name = item["target_venue"]
        
        if venue_name not in seen_venues:
          recommendations.append(
            ConferenceRecommendation(conference_name=venue_name)
          )
          seen_venues.add(venue_name)

      return recommendations

    except Exception as e:
      logging.error(f"Error in get recommendations: {e}")
      return []


