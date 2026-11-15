"""
Pydantic schemas for search history API endpoints.

Phase 3 — Search history schema definitions.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class SearchHistoryCreate(BaseModel):
    user_id: int
    query: str = Field(..., min_length=1, max_length=1024)


class SearchHistoryPublic(BaseModel):
    id: int
    user_id: int
    query: str
    timestamp: datetime

    class Config:
        from_attributes = True


class SearchHistoryResponse(SearchHistoryPublic):
    user_id: int
    query: str
    timestamp: datetime
    user: Optional[dict] = None
