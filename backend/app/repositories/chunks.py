"""
Data access layer for document chunk-related operations.

Phase 3 — Document chunk repository.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import DocumentChunk


class DocumentChunkRepository:
    """Repository for DocumentChunk model access."""

    @staticmethod
    def get_by_id(db: Session, chunk_id: int) -> Optional[DocumentChunk]:
        """Retrieve a chunk by ID."""
        return db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()

    @staticmethod
    def get_by_document_id(db: Session, document_id: int, skip: int = 0, limit: int = 100) -> List[DocumentChunk]:
        """Retrieve all chunks for a document."""
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_sequence)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_document_id_ordered(db: Session, document_id: int) -> List[DocumentChunk]:
        """Retrieve all chunks for a document, ordered by sequence."""
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_sequence)
            .all()
        )

    @staticmethod
    def create(db: Session, chunk: DocumentChunk) -> DocumentChunk:
        """Create a new document chunk."""
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        return chunk

    @staticmethod
    def delete_by_document_id(db: Session, document_id: int) -> bool:
        """Delete all chunks for a document."""
        try:
            db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
