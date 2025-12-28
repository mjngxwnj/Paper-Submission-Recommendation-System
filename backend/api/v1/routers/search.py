import time
from fastapi import APIRouter, Query, HTTPException
from api.v1.schemas.paper import PaperSearchInput, SearchPapersResponse
from api.v1.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])
search_service = SearchService()


@router.get(
    "/papers",
    response_model=SearchPapersResponse,
    summary="Search papers by title keyword",
    description="Search papers using a keyword in the title with optional limit and sort"
)
async def search_papers_api(
    keyword: str = Query(..., min_length=1, description="Keyword to search in paper titles"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results to return"),
    sort: str = Query("newest", regex="^(newest|oldest)$", description="Sort order: newest or oldest")
) -> SearchPapersResponse:
    """
    Search papers by title keyword.

    Args:
        keyword: Keyword to search
        limit: Maximum number of results
        sort: Sort order, "newest" or "oldest"

    Returns:
        List of papers matching the keyword with metadata.
    """

    if not keyword.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "ValidationError",
                "message": "Keyword must not be empty"
            }
        )

    try:
        input_data = PaperSearchInput(keyword=keyword, limit=limit, sort=sort)
        results = await search_service.search_papers(input_data)

        return results

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
                "message": f"An unexpected error occurred: {str(e)}"
            }
        )
