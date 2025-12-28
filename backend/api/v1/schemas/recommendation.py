from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any

class ConferenceRecommendation(BaseModel):
    """Model for a single conference recommendation"""
    conference_name: str = Field(..., description="Conference name")
#    acronym: Optional[str] = Field(None, description="Conference acronym")
#    similarity_score: float = Field(..., ge=0, le=1, description="Similarity score (0-1)")
#    description: Optional[str] = Field(None, description="Conference description")
#    topics: Optional[List[str]] = Field(None, description="Conference topics")
#    deadline: Optional[str] = Field(None, description="Submission deadline")
#    location: Optional[str] = Field(None, description="Conference location")
#    date: Optional[str] = Field(None, description="Conference date")
#    website: Optional[str] = Field(None, description="Conference website")
#    rank: Optional[str] = Field(None, description="Conference ranking (A*, A, B, C)")

    class Config:
        json_schema_extra = {
            "example": {
                "conference_name": "International Conference on Machine Learning"
            }
        }


class RecommendationResponse(BaseModel):
    """Response model for conference recommendations"""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    total_results: int = Field(..., description="Total number of recommendations")
    recommendations: List[ConferenceRecommendation] = Field(..., description="List of recommended conferences")
    query_info: Dict[str, Any] = Field(..., description="Information about the query")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully found recommendations",
                "total_results": 10,
                "recommendations": [],
                "query_info": {
                    "has_title": True,
                    "has_abstract": True,
                    "has_keywords": True,
                    "processing_time_ms": 245
                }
            }
        }
