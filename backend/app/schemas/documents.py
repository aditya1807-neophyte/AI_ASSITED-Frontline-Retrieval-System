"""
Pydantic schemas for document-related API endpoints.

Phase 4 — Updated with file storage, chunking, and processing support.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.pagination import PageWithMeta
from app.schemas.document import DocumentCreate, DocumentBase

from enum import Enum


class DocumentSearchResult(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    topic: Optional[str] = None
    similarity_score: Optional[float] = None


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
    under_review = "under_review"
    superseded = "superseded"


class DocumentProcessingStatus(str, Enum):
    uploaded = "uploaded"
    extracting = "extracting"
    extracted = "extracted"
    indexing = "indexing"
    indexed = "indexed"
    failed = "failed"
    requires_ocr = "requires_ocr"
    requires_review = "requires_review"


class DocumentLanguage(str, Enum):
    en = "en"
    es = "es"
    fr = "fr"
    de = "de"
    zh = "zh"
    ja = "ja"
    ko = "ko"
    other = "other"


class DocumentUpload(BaseModel):
    """Schema for document upload with file."""
    title: str = Field(..., min_length=1, max_length=512)
    description: Optional[str] = None
    document_type: DocumentType = DocumentType.pdf
    topic: Optional[str] = None
    intended_role: Optional[str] = None
    source_organization: Optional[str] = None
    original_filename: str
    language: Optional[DocumentLanguage] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None
    document_status: DocumentStatus = DocumentStatus.draft
    effective_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    file: Optional[str] = None  # File path after temporary upload


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
    file_size: Optional[int] = None
    num_pages: Optional[int] = None
    word_count: Optional[int] = None

    class Config:
        from_attributes = True


class DocumentInDB(DocumentPublic):
    user_id: Optional[int] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=512)
    description: Optional[str] = None
    document_type: Optional[DocumentType] = None
    topic: Optional[str] = None
    intended_role: Optional[str] = None
    source_organization: Optional[str] = None
    language: Optional[DocumentLanguage] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = None
    document_status: Optional[DocumentStatus] = None
    effective_date: Optional[datetime] = None
    review_date: Optional[datetime] = None
    processing_status: Optional[DocumentProcessingStatus] = None
    file_path: Optional[str] = None


class DocumentDetail(DocumentPublic):
    chunks: Optional[List[Dict[str, Any]]] = None
    user_id: Optional[int] = None


class ChunkCreate(BaseModel):
    document_id: int
    chunk_sequence: int
    extracted_text: str
    page_reference: Optional[str] = None
    section_heading: Optional[str] = None
    chunk_metadata: Optional[Dict[str, Any]] = None


class ChunkPublic(BaseModel):
    id: int
    document_id: int
    chunk_sequence: int
    extracted_text: str
    page_reference: Optional[str] = None
    section_heading: Optional[str] = None
    chunk_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    id: int
    title: str
    original_filename: Optional[str] = None
    storage_reference: Optional[str] = None
    processing_status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class SearchFilters(BaseModel):
    query: Optional[str] = None
    topic: Optional[str] = None
    doc_type: Optional[str] = None
    intended_role: Optional[str] = None
    source_organization: Optional[str] = None
    status: Optional[str] = None
    language: Optional[str] = None
    page: int = 1
    page_size: int = 20


class SearchResults(BaseModel):
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_prev: bool


class ProcessingStatusUpdate(BaseModel):
    processing_status: DocumentProcessingStatus
    note: Optional[str] = None


