from typing import Optional, List
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.orm import Session
from api.v1.services.db_service import get_db_session


class SearchService:
    """ Service for handling search operations. """

    def __init__(self):
        pass

    async def search(self, keyword: str, limit: int = 5) -> List[dict]:
        query = text("SELECT doi FROM core.paper LIMIT 10")
        with get_db_session() as session:
            result = session.execute(query)
            return [dict(row._mapping) for row in result]
