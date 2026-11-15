"""
FastAPI routers for document chunk endpoints.

Phase 3 — Document chunk API routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.chunks import DocumentChunkCreate, DocumentChunkPublic
from app.services.chunks_service import DocumentChunkService
from app.core.auth import get_current_active_user
from app.models import User

router = APIRouter(prefix="/documents/{document_id}/chunks", tags=["Document Chunks"])


@router.get("/", response_model=List[DocumentChunkPublic])
def get_document_chunks(
    document_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve all chunks for a document."""
    chunks = DocumentChunkService.get_by_document_id(db, document_id, skip, limit)
    if not chunks:
        return []
    return chunks


@router.post("/", response_model=DocumentChunkPublic, status_code=status.HTTP_201_CREATED)
def create_document_chunk(
    document_id: int,
    chunk_data: DocumentChunkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new document chunk."""
    # Verify document exists
    from app.services.document_service import DocumentService
    if not DocumentService.get_by_id(db, document_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    chunk_data.document_id = document_id
    chunk = DocumentChunkService.create(db, chunk_data)
    return chunk
