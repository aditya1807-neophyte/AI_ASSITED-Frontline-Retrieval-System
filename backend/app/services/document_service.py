"""
Business logic and orchestration layer for document operations.

Phase 3 — Document service layer with database operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Document
from app.models import DocumentChunk
from app.repositories.documents import DocumentRepository
from app.repositories.chunks import DocumentChunkRepository
from app.repositories.saved_items import SavedItemRepository
from app.repositories.audit_events import AuditEventRepository
from app.schemas.documents import DocumentCreate, DocumentUpdate
from app.schemas.chunks import DocumentChunkCreate
from app.schemas.audit_events import AuditAction
from app.core.database import SessionLocal


class DocumentService:
    """Service layer for document operations."""

    @staticmethod
    def get_all(
        db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None,
        doc_type: Optional[str] = None, topic: Optional[str] = None
    ) -> tuple:
        """Retrieve all documents with pagination and filtering."""
        documents = DocumentRepository.get_all(db, skip, limit, status, doc_type, topic)
        total = DocumentRepository.count_all(db)
        return documents, total

    @staticmethod
    def get_by_id(db: Session, document_id: int) -> Optional[Document]:
        """Retrieve a document by ID."""
        return DocumentRepository.get_by_id(db, document_id)

    @staticmethod
    def get_public_by_id(db: Session, document_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a document as a public dictionary."""
        doc = DocumentRepository.get_by_id(db, document_id)
        if not doc:
            return None
        # Parse tags from JSON string to list
        tags = doc.tags
        if isinstance(tags, str):
            try:
                tags = json.loads(tags) if tags else []
            except (json.JSONDecodeError, TypeError):
                tags = []
        return {
            "id": doc.id,
            "title": doc.title,
            "description": doc.description,
            "document_type": doc.document_type,
            "topic": doc.topic,
            "intended_role": doc.intended_role,
            "source_organization": doc.source_organization,
            "original_filename": doc.original_filename,
            "storage_reference": doc.storage_reference,
            "language": doc.language,
            "tags": tags,
            "version": doc.version,
            "document_status": doc.document_status,
            "effective_date": doc.effective_date,
            "review_date": doc.review_date,
            "uploaded_at": doc.uploaded_at,
            "processing_status": doc.processing_status,
            "chunk_count": len(DocumentChunkRepository.get_by_document_id(db, document_id)),
        }

    @staticmethod
    def create(db: Session, data: DocumentCreate, user_id: Optional[int] = None) -> Document:
        """Create a new document."""
        doc = Document(**data.dict(exclude_unset=True))
        if user_id is not None:
            doc.user_id = user_id
        return DocumentRepository.create(db, doc)

    @staticmethod
    def update(db: Session, document_id: int, data: DocumentUpdate) -> Optional[Document]:
        """Update a document."""
        db_doc = DocumentRepository.get_by_id(db, document_id)
        if not db_doc:
            return None
        update_dict = data.dict(exclude_unset=True)
        return DocumentRepository.update(db, db_doc, update_dict)

    @staticmethod
    def delete(db: Session, document_id: int) -> bool:
        """Delete a document and its associated chunks."""
        db_doc = DocumentRepository.get_by_id(db, document_id)
        if not db_doc:
            return False
        # Delete related chunks first (CASCADE on document_id
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
        return DocumentRepository.delete(db, db_doc)

    @staticmethod
    def search(
        db: Session, query: str, skip: int = 0, limit: int = 100,
        status: Optional[str] = None, doc_type: Optional[str] = None
    ) -> tuple:
        """Search documents by query string."""
        documents = DocumentRepository.search(db, query, skip, limit, status, doc_type)
        total = DocumentRepository.count_all(db)
        return documents, total

    @staticmethod
    def get_stats(db: Session) -> dict:
        """Get document statistics."""
        return DocumentRepository.get_stats(db)

    @staticmethod
    def get_recent(db: Session, limit: int = 10) -> List[Document]:
        """Get recently uploaded documents."""
        return db.query(Document).order_by(Document.uploaded_at.desc()).limit(limit).all()

    @staticmethod
    def record_audit(
        action: AuditAction, target_type: str, target_id: str,
        details: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None,
        user_agent: Optional[str] = None, db_session: Optional[Session] = None
    ) -> None:
        """Record an audit event."""
        session = db_session or SessionLocal()
        audit = AuditEvent(
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        session.add(audit)
        session.commit()

    @staticmethod
    def ingest_documents(
        documents: List[Dict[str, Any]], db_session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Create document records from uploaded files.

        NOTE: This is a simplified version. Full document ingestion with
        PDF/DOCX parsing and embedding generation is deferred to Phase 4+.
        """
        session = db_session or SessionLocal()
        created = []
        for doc_data in documents:
            doc = Document(
                title=doc_data.get("title"),
                description=doc_data.get("description"),
                document_type=doc_data.get("document_type"),
                topic=doc_data.get("topic"),
                source_organization=doc_data.get("source_organization"),
                original_filename=doc_data.get("original_filename"),
                storage_reference=doc_data.get("storage_reference"),
                language=doc_data.get("language"),
                tags=doc_data.get("tags"),
                version=doc_data.get("version"),
                document_status=doc_data.get("document_status", "draft"),
                effective_date=doc_data.get("effective_date"),
                review_date=doc_data.get("review_date"),
                processing_status="processing",
                uploaded_at=datetime.utcnow(),
            )
            session.add(doc)
            created.append(doc)

        session.commit()
        for doc in created:
            session.refresh(doc)
        session.close()

        return {
            "created": len(created),
            "documents": [{"id": d.id, "title": d.title} for d in created],
        }

@staticmethod
def start_indexing(db: Session, document_id: int) -> dict:
    """Start document processing and indexing pipeline."""
    from app.repositories.documents import DocumentRepository
    from app.repositories.chunks import DocumentChunkRepository
    from app.models import Document
    
    # Get the document
    doc = DocumentRepository.get_by_id(db, document_id)
    if not doc:
        raise ValueError(f"Document {document_id} not found")
    
    # Update processing status
    doc.processing_status = "indexing"
    doc.processed_at = None
    db.commit()
    db.refresh(doc)
    
    # In a real implementation, this would:
    # 1. Extract text from the source file
    # 2. Chunk the extracted text
    # 3. Store chunks
    # 4. Update processing status to "indexed"
    
    doc.processing_status = "indexed"
    doc.processed_at = datetime.utcnow()
    db.commit()
    db.refresh(doc)
    
    return {
        "document_id": doc.id,
        "status": "indexed",
        "title": doc.title,
        "processing_status": doc.processing_status
    }


@staticmethod
def reprocess_document(db: Session, document_id: int) -> dict:
    """Reprocess a document, clearing existing chunks first."""
    from app.repositories.chunks import DocumentChunkRepository
    from app.models import DocumentChunk
    
    # Get the document
    doc = DocumentRepository.get_by_id(db, document_id)
    if not doc:
        raise ValueError(f"Document {document_id} not found")
    
    # Clear existing chunks
    DocumentChunkRepository.delete_by_document_id(db, document_id)
    
    # Update processing status
    doc.processing_status = "indexing"
    db.commit()
    db.refresh(doc)
    
    # In a real implementation, this would:
    # 1. Extract text from the source file
    # 2. Chunk the extracted text (avoiding duplicates)
    # 3. Store chunks
    # 4. Update processing status to "indexed"
    
    doc.processing_status = "indexed"
    doc.processed_at = datetime.utcnow()
    db.commit()
    db.refresh(doc)
    
    return {
        "document_id": doc.id,
        "status": "indexed",
        "title": doc.title,
        "processing_status": doc.processing_status
    }


@staticmethod
def get_document_content(db: Session, document_id: int) -> dict:
    """Get document content with all extracted chunks."""
    from app.repositories.chunks import DocumentChunkRepository
    
    # Get document
    doc = DocumentRepository.get_by_id(db, document_id)
    if not doc:
        raise ValueError(f"Document {document_id} not found")
    
    # Get all chunks
    chunks = DocumentChunkRepository.get_by_document_id(db, document_id)
    
    return {
        "id": doc.id,
        "title": doc.title,
        "description": doc.description,
        "document_status": doc.document_status,
        "processing_status": doc.processing_status,
        "word_count": doc.word_count,
        "num_pages": doc.num_pages,
        "chunks": [
            {
                "chunk_id": c.id,
                "sequence": c.chunk_sequence,
                "text": c.extracted_text,
                "page_reference": c.page_reference,
                "section_heading": c.section_heading,
            }
            for c in chunks
        ],
        "uploaded_at": doc.uploaded_at,
    }


@staticmethod
def delete_document(db: Session, document_id: int) -> bool:
    """Delete a document and all associated data."""
    from app.repositories.chunks import DocumentChunkRepository
    from app.repositories.saved_items import SavedItemRepository
    from app.repositories.saved_answers import SavedAnswerRepository
    from app.repositories.audit_events import AuditEventRepository
    from app.models import Document
    
    # Get the document
    document = DocumentRepository.get_by_id(db, document_id)
    if not document:
        return False
    
    # Delete stored file if exists
    if document.storage_reference:
        delete_file(document.storage_reference)
    
    # Delete chunks
    DocumentChunkRepository.delete_by_document_id(db, document_id)
    
    # Delete saved answers
    SavedAnswerRepository.delete_by_document_id(db, document_id)
    
    # Delete saved items
    SavedItemRepository.delete_by_document_id(db, document_id)
    
    # Delete document
    DocumentRepository.delete(db, document_id)
    
    # Log audit event
    AuditEventRepository.log(
        db, user_id=None, action='document_deleted',
        target_type='document', target_id=str(document_id),
        details=f"Deleted {document.original_filename}"
    )
    
    return True
