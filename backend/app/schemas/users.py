"""
Pydantic schemas for API request/response validation.

Phase 3 — Complete schema definitions for all entities.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
class UserRole(str, Enum):
    admin = "admin"
    analyst = "analyst"
    manager = "manager"
    field_technician = "field_technician"


class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class UserCreate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=128)
    login_identifier: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = Field(default="analyst")
    account_status: UserStatus = Field(default="active")


class UserPublic(BaseModel):
    id: int
    display_name: str
    login_identifier: str
    role: str
    account_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserPublic):
    password_hash: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------
class DocumentType(str, Enum):
    pdf = "pdf"
    docx = "docx"
    txt = "txt"
    md = "md"
    json = "json"
    csv = "csv"
    other = "other"


class DocumentStatus(str, Enum):
    draft = "draft"
    active = "active"
    archived = "archived"
    review = "review"
    processing = "processing"


class DocumentLanguage(str, Enum):
    en = "en"
    es = "es"
    fr = "fr"
    de = "de"
    zh = "zh"
    ja = "ja"
    ko = "ko"


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=512)
    description: Optional[str] = None
    document_type: Optional[DocumentType] = None
    topic: Optional[str] = None
    intended_role: Optional[str] = None
    source_organization: Optional[str] = None
    original_filename: Optional[str] = None
    storage_reference: Optional[str] = None
    language: Optional[DocumentLanguage] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None
    document_status: Optional[DocumentStatus] = None
    effective_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    processing_status: Optional[DocumentStatus] = None


class DocumentPublic(BaseModel):
    id: int
    title: str
    description: Optional[str]
    document_type: Optional[str]
    topic: Optional[str]
    intended_role: Optional[str]
    source_organization: Optional[str]
    original_filename: Optional[str]
    storage_reference: Optional[str]
    language: Optional[str]
    tags: Optional[List[str]]
    version: Optional[str]
    document_status: str
    effective_date: Optional[datetime]
    review_date: Optional[datetime]
    uploaded_at: datetime
    processing_status: str

    class Config:
        from_attributes = True


class DocumentInDB(DocumentPublic):
    id: int
    title: str
    description: Optional[str]
    document_type: Optional[str]
    topic: Optional[str]
    intended_role: Optional[str]
    source_organization: Optional[str]
    original_filename: Optional[str]
    storage_reference: Optional[str]
    language: Optional[str]
    tags: Optional[List[str]]
    version: Optional[str]
    document_status: str
    effective_date: Optional[datetime]
    review_date: Optional[datetime]
    uploaded_at: datetime
    processing_status: str
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Document Chunks
# ---------------------------------------------------------------------------
class DocumentChunkCreate(BaseModel):
    document_id: int
    chunk_sequence: int = 0
    extracted_text: str = Field(..., min_length=1)
    page_reference: Optional[str] = None
    section_heading: Optional[str] = None
    chunk_metadata: Optional[Dict[str, Any]] = None


class DocumentChunkPublic(BaseModel):
    id: int
    document_id: int
    chunk_sequence: int
    extracted_text: str
    page_reference: Optional[str]
    section_heading: Optional[str]
    chunk_metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Saved Items
# ---------------------------------------------------------------------------
class SavedItemCreate(BaseModel):
    user_id: int
    item_type: str  # "document" or "answer"
    item_reference: str


class SavedItemPublic(BaseModel):
    id: int
    user_id: int
    item_type: str
    item_reference: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Search History
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Answers
# ---------------------------------------------------------------------------
class AnswerCreate(BaseModel):
    user_id: int
    question: str = Field(..., min_length=1, max_length=4096)
    answer_content: str = Field(..., min_length=1)
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


# ---------------------------------------------------------------------------
# Saved Answer
# ---------------------------------------------------------------------------
class SavedAnswerCreate(BaseModel):
    user_id: int
    answer_id: int
    document_id: Optional[int] = None


class SavedAnswerPublic(BaseModel):
    id: int
    user_id: int
    answer_id: int
    document_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------
class FeedbackType(str, Enum):
    like = "like"
    dislike = "dislike"
    comment = "comment"


class FeedbackCreate(BaseModel):
    user_id: int
    answer_ref: Optional[str] = None
    document_ref: Optional[str] = None
    feedback_type: FeedbackType
    explanation: Optional[str] = None


class FeedbackPublic(BaseModel):
    id: int
    user_id: int
    answer_ref: Optional[str]
    document_ref: Optional[str]
    feedback_type: str
    explanation: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Escalations
# ---------------------------------------------------------------------------
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
    user_id: int
    question: str = Field(..., min_length=1, max_length=4096)
    context: Optional[str] = None
    evidence_references: Optional[str] = None
    priority: EscalationPriority = "medium"
    assigned_reviewer: Optional[int] = None


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


# ---------------------------------------------------------------------------
# Audit Events
# ---------------------------------------------------------------------------
class AuditAction(str, Enum):
    user_created = "user_created"
    user_updated = "user_updated"
    user_deleted = "user_deleted"
    document_created = "document_created"
    document_updated = "document_updated"
    document_deleted = "document_deleted"
    document_accessed = "document_accessed"
    document_migrated = "document_migrated"
    escalation_created = "escalation_created"
    escalation_resolved = "escalation_resolved"
    escalation_assigned = "escalation_assigned"
    admin_action = "admin_action"


class AuditEventCreate(BaseModel):
    user_id: Optional[int] = None
    action: AuditAction
    target_type: str
    target_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditEventPublic(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    target_type: str
    target_id: Optional[str]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str
    message: str
    database: str
    timestamp: datetime
