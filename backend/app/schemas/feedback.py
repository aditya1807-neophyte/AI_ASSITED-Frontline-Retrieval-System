"""Pydantic schemas for Feedback."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FeedbackCreate(BaseModel):
    """Schema for creating feedback."""
    answer_ref: Optional[str] = Field(None, max_length=512, description="Answer reference ID")
    document_ref: Optional[str] = Field(None, max_length=512, description="Document reference ID")
    feedback_type: str = Field(..., description="Like, dislike, or comment")
    explanation: Optional[str] = Field(None, description="Optional explanation")


class FeedbackPublic(BaseModel):
    """Schema for feedback responses."""
    id: int
    user_id: int
    answer_ref: Optional[str] = None
    document_ref: Optional[str] = None
    feedback_type: str
    explanation: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
