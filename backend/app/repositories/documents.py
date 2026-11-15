"""
Data access layer for document-related operations.

Phase 3 — Full document repository with pagination and filtering.
"""

from typing import Optional, List, Any
from sqlalchemy import desc, asc, and_
from sqlalchemy.orm import Session
from app.models import Document
from app.schemas.documents import DocumentStatus, DocumentType, DocumentLanguage


class DocumentRepository:
    """Repository for Document model access."""

    @staticmethod
    def get_by_id(db: Session, document_id: int) -> Optional[Document]:
        """Retrieve a document by ID."""
        return db.query(Document).filter(Document.id == document_id).first()

    @staticmethod
    def get_by_storage_reference(db: Session, storage_reference: str) -> Optional[Document]:
        """Retrieve a document by its storage reference."""
        return db.query(Document).filter(Document.storage_reference == storage_reference).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        doc_type: Optional[str] = None,
        topic: Optional[str] = None,
        user_id: Optional[int] = None,
        intended_role: Optional[str] = None,
        source_organization: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Document]:
        """Retrieve all documents with pagination and filtering."""
        query = db.query(Document)

        if status:
            query = query.filter(Document.document_status == status)
        if doc_type:
            query = query.filter(Document.document_type == doc_type)
        if topic:
            query = query.filter(Document.topic.ilike(f"%{topic}%"))
        if intended_role:
            query = query.filter(Document.intended_role.ilike(f"%{intended_role}%"))
        if source_organization:
            query = query.filter(Document.source_organization.ilike(f"%{source_organization}%"))
        if language:
            query = query.filter(Document.language == language)
        if user_id is not None:
            query = query.filter(Document.user_id == user_id)

        return query.order_by(desc(Document.uploaded_at)).offset(skip).limit(limit).all()

    @staticmethod
    def search(
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        doc_type: Optional[str] = None,
    ) -> List[Document]:
        """Search documents by title, description, or topic."""
        search_query = f"%{query}%"
        search_condition = or_(
            Document.title.ilike(search_query),
            Document.description.ilike(search_query),
            Document.topic.ilike(search_query),
        )
        full_query = db.query(Document).filter(search_condition)

        if status:
            full_query = full_query.filter(Document.document_status == status)
        if doc_type:
            full_query = full_query.filter(Document.document_type == doc_type)

        return full_query.order_by(desc(Document.uploaded_at)).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, document: Document) -> Document:
        """Create a new document."""
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def update(
        db: Session, db_document: Document, update_data: dict
    ) -> Document:
        """Update a document with provided data."""
        for key, value in update_data.items():
            if hasattr(db_document, key):
                setattr(db_document, key, value)
        db.commit()
        db.refresh(db_document)
        return db_document

    @staticmethod
    def delete(db: Session, db_document: Any) -> bool:
        """Delete a document and its associated chunks."""
        try:
            from app.models import Document, DocumentChunk
            if isinstance(db_document, int):
                doc = db.query(Document).filter(Document.id == db_document).first()
            else:
                doc = db_document
            if not doc:
                return False
            db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
            db.delete(doc)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False

    @staticmethod
    def count_all(db: Session) -> int:
        """Count total documents."""
        return db.query(Document).count()

    @staticmethod
    def get_stats(db: Session) -> dict:
        """Get document statistics."""
        total = db.query(Document).count()
        active = db.query(Document).filter(Document.document_status == "active").count()
        draft = db.query(Document).filter(Document.document_status == "draft").count()
        review = db.query(Document).filter(Document.document_status == "review").count()
        archived = db.query(Document).filter(Document.document_status == "archived").count()
        processing = db.query(Document).filter(Document.processing_status == "processing").count()

        return {
            "total": total,
            "active": active,
            "draft": draft,
            "review": review,
            "archived": archived,
            "processing": processing,
        }
