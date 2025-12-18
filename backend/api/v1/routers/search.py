import time
from typing import List
from fastapi import APIRouter, HTTPException, Query
from api.v1.services.search_service import SearchService
from api.v1.models import (
    ConferenceRecommendation,
    RecommendationResponse,
    PaperInput
)


router = APIRouter()
recommendation_service = SearchService()

@router.get("/", response_model=List[dict])
async def search_papers_api(keyword: str = Query(..., min_length=1, description="Keyword to search")):
    """
    Search papers by keyword.
    """
    service = SearchService()
    results = await service.search(keyword)
    return results
