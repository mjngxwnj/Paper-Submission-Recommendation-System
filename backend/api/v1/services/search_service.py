from typing import Literal
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from api.v1.models.paper import Paper
from api.v1.models.author import Author
from api.v1.services.db_service import get_db_session
from api.v1.schemas.paper import PaperSearchInput, PaperResult, SearchPapersResponse


class SearchService:

    async def search_papers(self, input: PaperSearchInput) -> SearchPapersResponse:
        """Search papers by title keyword"""
        with get_db_session() as session:
            stmt = select(Paper).where(Paper.title.ilike(f"%{input.keyword}%"))

            if input.sort == "newest":
                stmt = stmt.order_by(Paper.publication_year.desc())
            else:
                stmt = stmt.order_by(Paper.publication_year.asc())

            stmt = stmt.limit(input.limit)
            stmt = stmt.options(joinedload(Paper.venue))
            results = session.execute(stmt).scalars().all()

            papers_list = [
                PaperResult(
                    doi=p.doi,
                    title=p.title,
                    year=p.publication_year,
                    month=p.publication_month,
                    day=p.publication_day,
                    venue=p.venue.name if p.venue else None,
                    abstract_link=p.abstract_link
                )
                for p in results
            ]

            return SearchPapersResponse(
                success=True,
                message="Papers found" if papers_list else "No papers found",
                total_results=len(papers_list),
                papers=papers_list,
                query_info={
                    "keyword": input.keyword,
                    "limit": input.limit,
                    "sort": input.sort
                }
            )
