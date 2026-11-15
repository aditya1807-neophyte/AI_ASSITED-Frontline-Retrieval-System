"""
Pydantic schemas for document chunk API endpoints.

Phase 3 — Document chunk schema definitions.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


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
    page_reference: Optional[str] = None
    section_heading: Optional[str] = None
    chunk_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
