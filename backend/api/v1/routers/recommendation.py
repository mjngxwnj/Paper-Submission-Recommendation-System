import time
from fastapi import APIRouter, HTTPException, Query
from api.v1.services.recommendation_service import RecommendationService
from api.v1.database import (
    ConferenceRecommendation,
    RecommendationResponse,
    PaperInput
)


router = APIRouter()
recommendation_service = RecommendationService()


@router.post(
    '/recommend',
    response_model = RecommendationResponse,
    summary="Get conference recommendations",
    description="Recommend conferences based on paper title, abstract, and/or keywords"
)
async def recommend_conference(
    paper: PaperInput,
    top_k: int = Query(5, ge=1, le=50, description="Number of top recommendations to return")
) -> RecommendationResponse:
    """
    Recommend conferences based on paper input.

    At least one of title, abstract, or keywords must be provided.
    The system will compute similarity between the input and conferences
    and return the top K most relevant conferences.

    Args:
        paper: Paper information (title, abstract, keywords)
        top_k: Number of recommendations to return (default: 10, max: 50)

    Returns:
        List of recommended conferences.
    """

    start_time = time.time()

    if not paper.title and not paper.abstract and not paper.keywords:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "ValidationError",
                "message": "At least one field (title, abstract, or keywords) must be provided"
            }
        )

    try:
        # Get recommendations from service
        recommendations = await recommendation_service.get_recommendations(
            title=paper.title,
            abstract=paper.abstract,
            keywords=paper.keywords,
            top_k=top_k
        )

        processing_time = (time.time() - start_time) * 1000

        # Prepare query info
        query_info = {
            "has_title": paper.title is not None,
            "has_abstract": paper.abstract is not None,
            "has_keywords": paper.keywords is not None and len(paper.keywords) > 0,
            "top_k": top_k,
            "processing_time_ms": round(processing_time, 2)
        }

        return RecommendationResponse(
            success=True,
            message=f"Successfully found {len(recommendations)} recommendations",
            total_results=len(recommendations),
            recommendations=recommendations,
            query_info=query_info
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "ValueError",
                "message": str(e)
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "InternalServerError",
                "message": f"An error occurred while processing your request: {str(e)}"
            }
        )


