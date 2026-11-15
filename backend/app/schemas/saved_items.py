"""
Pydantic schemas for saved items API endpoints.

Phase 3 — Saved item schema definitions.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class SavedItemCreate(BaseModel):
    item_type: str = Field(..., description="'document' or 'answer'")
    item_reference: str = Field(..., min_length=1, max_length=512)


class SavedItemPublic(BaseModel):
    id: int
    user_id: int
    item_type: str
    item_reference: str
    created_at: datetime

    class Config:
        from_attributes = True


class SavedItemUpdate(BaseModel):
    item_type: Optional[str] = None
    item_reference: Optional[str] = None


class SavedItemResponse(SavedItemPublic):
    user_id: int
    item_type: str
    item_reference: str
    created_at: datetime
    user: Optional[dict] = None
