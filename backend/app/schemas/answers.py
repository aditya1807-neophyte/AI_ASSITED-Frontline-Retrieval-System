"""
Pydantic schemas for answers API endpoints.

Phase 3 — Answer schema definitions.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class AnswerCreate(BaseModel):
    user_id: int
    question: str = Field(..., min_length=1, max_length=4096)
    answer_content: str = Field(..., min_length=1, max_length=16384)
    evidence_references: Optional[str] = None
    evidence_status: str = "verified"


class AnswerPublic(BaseModel):
    id: int
    user_id: int
    question: str
    answer_content: str
    evidence_references: Optional[str]
    evidence_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AnswerUpdate(BaseModel):
    question: Optional[str] = None
    answer_content: Optional[str] = None
    evidence_references: Optional[str] = None
    evidence_status: Optional[str] = None


class AnswerResponse(AnswerPublic):
    user_id: int
    question: str
    answer_content: str
    evidence_references: Optional[str]
    evidence_status: str
    created_at: datetime
    user: Optional[dict] = None
