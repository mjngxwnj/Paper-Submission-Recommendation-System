from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any

class PaperSearchInput(BaseModel):
    """Input model for searching papers by title"""
    keyword: Optional[str] = Field(None, description="Keyword to search in paper titles")
    author: Optional[str] = Field(None, description="Author names to filter by")
    limit: Optional[int] = Field(10, description="Maximum number of results")
    sort: Optional[str] = Field("newest", description="Sort order: newest or oldest")

    class Config:
        schema_extra = {
            "example": {
                "keyword": "NLP",
                "author": "Huynh Minh Thuan",
                "limit": 10,
                "sort": "newest"
            }
        }


class PaperRecommendInput(BaseModel):
    """ Input model for paper submissions """
    title: Optional[str] = Field(None, description="Paper title", max_length=500)
    abstract: Optional[str] = Field(None, description="Paper abstract", max_length=5000)
    keywords: Optional[List[str]] = Field(None, description="Paper keywords")

    @validator('keywords')
    def validate_keywords(cls, v):
        if v is not None and len(v) == 0:
            return None
        return v

    @validator('title', 'abstract')
    def validate_not_empty(cls, v):
        if v is not None and v.strip() == "":
            return None
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Deep Learning for Natural Language Processing",
                "abstract": "This paper presents a novel approach to NLP using transformer models...",
                "keywords": ["deep learning", "NLP", "transformers", "BERT"]
            }
        }


class PaperResult(BaseModel):
    doi: str
    title: str
    year: int
    month: int
    day: int
    venue: Optional[str] = None
    abstract_link: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "doi": "10.1234/abcd",
                "title": "Deep Learning for NLP",
                "year": 2023,
                "month": 1,
                "day":1,
                "venue": "ICML",
                "abstract_link": "http://example.com/abstract"
            }
        }


class SearchPapersResponse(BaseModel):
    success: bool
    message: str
    total_results: int
    papers: List[PaperResult]
    query_info: Dict[str, Any]

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Papers found",
                "total_results": 2,
                "papers": [
                    {
                        "doi": "10.1234/abcd",
                        "title": "Deep Learning for NLP",
                        "year": 2023,
                        "venue": "ICML",
                        "abstract_link": "http://example.com/abstract"
                    }
                ],
                "query_info": {
                    "keyword": "NLP",
                    "author": "Huynh Minh Thuan",
                    "limit": 10,
                    "sort": "newest"
                }
            }
        }
