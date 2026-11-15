"""
Pydantic schemas for escalation API endpoints.

Phase 3 — Escalation schema definitions.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class EscalationPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class EscalationStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class EscalationCreate(BaseModel):
    user_id: Optional[int] = 1
    question: str = Field(..., min_length=1, max_length=4096)
    context: Optional[str] = None
    evidence_references: Optional[str] = None
    priority: EscalationPriority = EscalationPriority.medium


class EscalationUpdate(BaseModel):
    question: Optional[str] = None
    context: Optional[str] = None
    priority: Optional[EscalationPriority] = None
    status: Optional[EscalationStatus] = None
    assigned_reviewer: Optional[int] = None
    review_notes: Optional[str] = None
    resolution: Optional[str] = None


class EscalationPublic(BaseModel):
    id: int
    user_id: int
    question: str
    context: Optional[str]
    evidence_references: Optional[str]
    status: str
    priority: str
    assigned_reviewer: Optional[int]
    review_notes: Optional[str]
    resolution: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EscalationResponse(EscalationPublic):
    user_id: int
    question: str
    context: Optional[str]
    evidence_references: Optional[str]
    status: str
    priority: str
    assigned_reviewer: Optional[int]
    review_notes: Optional[str]
    resolution: Optional[str]
    created_at: datetime
    updated_at: datetime
    user: Optional[dict] = None
    reviewer: Optional[dict] = None
