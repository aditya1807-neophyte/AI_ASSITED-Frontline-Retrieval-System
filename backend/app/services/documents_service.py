"""
Document service for Phase 4 document ingestion and lifecycle management.

Provides:
- Upload with validation
- Text extraction orchestration
- Chunking and indexing
- Metadata updates
- Status updates
- File deletion with cleanup
"""

import logging
import os
import hashlib
import secrets
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, text

from app.models import Document
from app.repositories.documents import DocumentRepository
from app.repositories.chunks import DocumentChunkRepository
from app.repositories.audit_events import AuditEventRepository
from app.utils.file_storage import (
    get_file_storage_path, get_file_url, delete_file,
    validate_file_upload, save_uploaded_file
)
from app.utils.text_extractors import extract_file as extract_text, ExtractionError
from app.services.chunks_service import create_chunks
from app.services.indexing_service import DocumentIndexer, DocumentIndexingError

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document management operations."""

    @staticmethod
    def document_exists(db: Session, doc_id: int) -> bool:
        """Check if document exists."""
        return DocumentRepository.get_by_id(db, doc_id) is not None

    @staticmethod
    def upload_document(db: Session, doc_data: dict, file_path: Optional[str] = None) -> dict:
        """
        Create a new document and start ingestion.

        1. Create document record
        2. Store file
        3. Start extraction/indexing pipeline
        4. Log audit event
        """
        # Generate unique storage reference
        storage_ref = f"doc_{secrets.token_hex(12)}"
        file_info = None

        if file_path and os.path.exists(file_path):
            # Validate file
            is_valid, error = validate_file_upload(file_path, expected_type=doc_data.get('document_type', 'pdf'))
            if not is_valid:
                raise ValueError(f"File validation error: {error}")

            # Compute checksum
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            checksum = sha256.hexdigest()

            # Save to storage
            storage_ref, file_info = save_uploaded_file(file_path, storage_ref)

        # Create document record
        doc = DocumentRepository.create(
            db,
            title=doc_data['title'],
            description=doc_data.get('description'),
            document_type=doc_data.get('document_type', 'pdf'),
            topic=doc_data.get('topic'),
            intended_role=doc_data.get('intended_role'),
            source_organization=doc_data.get('source_organization'),
            original_filename=doc_data.get('original_filename'),
            storage_reference=storage_ref,
            language=doc_data.get('language'),
            tags=doc_data.get('tags'),
            version=doc_data.get('version'),
            document_status=doc_data.get('document_status', 'uploaded'),
            effective_date=doc_data.get('effective_date'),
            review_date=doc_data.get('review_date'),
            file_path=file_info.get('file_path') if file_info else None,
            file_size=file_info.get('file_size') if file_info else None,
            file_checksum=checksum if file_info else None,
            num_pages=None,
            word_count=None,
            content=None,
        )

        # Set processing status
        document = DocumentRepository.get_by_id(db, doc.id)
        if document:
            document.document_status = 'extracting'
            document.processing_status = 'extracting'
            db.commit()
            db.refresh(document)

        # Log audit
        AuditEventRepository.log(
            db, doc.user_id, 'document_uploaded',
            'document', str(doc.id),
            details=f"Uploaded {doc.original_filename}",
            ip_address=None, user_agent=None
        )

        return doc.to_dict()

    @staticmethod
    def start_indexing(db: Session, document_id: int) -> dict:
        """
        Start the extraction and indexing pipeline.

        1. Validate file
        2. Extract text
        3. Create chunks
        4. Save chunks
        5. Update status to indexed
        """
        document = DocumentRepository.get_by_id(db, document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        if document.processing_status == 'indexed':
            return {"status": "already_indexed", "message": "Document is already indexed"}

        # Use the indexer service
        result = DocumentIndexer.start_ingestion(db, document_id)
        return result

    @staticmethod
    def reprocess_document(db: Session, document_id: int) -> dict:
        """
        Reprocess a document, clearing existing chunks first.

        Prevents duplicate chunks by deleting old chunks before re-indexing.
        """
        document = DocumentRepository.get_by_id(db, document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Delete existing chunks
        DocumentChunkRepository.delete_by_document_id(db, document_id)

        # Reset status
        document = DocumentRepository.get_by_id(db, document_id)
        if document:
            document.document_status = 'uploaded'
            document.processing_status = 'uploaded'
            db.commit()
            db.refresh(document)

        # Re-index
        return DocumentIndexer.start_ingestion(db, document_id)

    @staticmethod
    def update_metadata(db: Session, document_id: int, update_data: dict) -> dict:
        """
        Update document metadata (title, description, tags, etc.).

        Only updates metadata fields, not the stored file.
        """
        if not DocumentService.document_exists(db, document_id):
            raise ValueError(f"Document {document_id} not found")

        # Get existing document
        doc = DocumentRepository.get_by_id(db, document_id)

        # Build update fields
        update_fields = {}
        status_field_updates = {
            'title', 'description', 'document_type', 'topic',
            'intended_role', 'source_organization', 'language',
            'tags', 'version', 'document_status', 'effective_date',
            'review_date'
        }

        for key, value in update_data.items():
            if key in status_field_updates and hasattr(doc, key):
                if key == 'tags' and value is not None:
                    value = ', '.join(value) if isinstance(value, list) else value
                setattr(doc, key, value)

        # Update in DB
        DocumentRepository.update(db, document_id, update_fields)

        # Log audit
        AuditEventRepository.log(
            db, doc.user_id, 'metadata_updated',
            'document', str(doc.id),
            details=f"Updated metadata: {list(update_data.keys())}",
            ip_address=None, user_agent=None
        )

        return DocumentRepository.get_by_id(db, document_id).to_dict()

    @staticmethod
    def update_processing_status(db: Session, document_id: int,
                                  processing_status: str,
                                  note: Optional[str] = None) -> dict:
        """
        Update processing status of a document.

        Valid statuses: uploaded, extracting, extracted, indexing, indexed,
        failed, requires_ocr, requires_review
        """
        if not DocumentService.document_exists(db, document_id):
            raise ValueError(f"Document {document_id} not found")

        document = DocumentRepository.get_by_id(db, document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Update status directly
        document.processing_status = processing_status
        if note:
            # metadata could be extended but keeping simple
            pass
        db.commit()
        db.refresh(document)

        # Log status change
        AuditEventRepository.log(
            db, document.user_id, 'processing_status_changed',
            'document', str(document.id),
            details=f"Status changed from {processing_status} to {processing_status}",
            ip_address=None, user_agent=None
        )

        return {
            'document_id': document_id,
            'processing_status': processing_status,
            'changed_from': 'previous',
        }

    @staticmethod
    def delete_document(db: Session, document_id: int, user_id: int) -> dict:
        """
        Delete a document and all associated data.

        - Deletes stored file
        - Deletes chunks
        - Deletes saved items
        - Deletes audit events
        - Removes record
        """
        if not DocumentService.document_exists(db, document_id):
            raise ValueError(f"Document {document_id} not found")

        document = DocumentRepository.get_by_id(db, document_id)

        # Delete stored file if exists
        if document.storage_reference:
            delete_file(document.storage_reference)

        # Delete chunks (CASCADE will handle this, but do explicitly for cleanup)
        DocumentChunkRepository.delete_by_document_id(db, document_id)

        # Delete saved answers
        from app.repositories.saved_answers import SavedAnswerRepository
        from app.repositories.saved_items import SavedItemRepository
        SavedAnswerRepository.delete_by_document_id(db, document_id)
        SavedItemRepository.delete_by_document_id(db, document_id)

        # Delete audit events (CASCADE)
        # Document deletion will cascade

        # Delete document
        DocumentRepository.delete(db, document_id)

        # Log audit
        AuditEventRepository.log(
            db, user_id, 'document_deleted',
            'document', str(document_id),
            details=f"Deleted {document.original_filename}",
            ip_address=None, user_agent=None
        )

        return {"message": "Document deleted successfully", "id": document_id}

    @staticmethod
    def get_document_content(db: Session, document_id: int) -> dict:
        """
        Get document content with chunks for display.

        Used by frontend for document preview.
        """
        document = DocumentRepository.get_by_id(db, document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        if document.processing_status not in ['indexed', 'completed', 'active'] and not document.content:
            chunks = DocumentChunkRepository.get_by_document_id(db, document_id)
            if not chunks:
                raise ValueError(f"Document {document_id} is still processing")

        chunks = DocumentChunkRepository.get_by_document_id(db, document_id)

        return {
            "id": document.id,
            "title": document.title,
            "description": document.description,
            "document_status": document.document_status,
            "processing_status": document.processing_status,
            "word_count": document.word_count,
            "num_pages": document.num_pages,
            "uploaded_at": document.uploaded_at,
            "content": getattr(document, "content", "") or "",
            "chunks": [
                {
                    "id": chunk.id,
                    "chunk_sequence": chunk.chunk_sequence,
                    "extracted_text": chunk.extracted_text,
                    "page_reference": chunk.page_reference,
                    "section_heading": chunk.section_heading,
                }
                for chunk in chunks
            ],
        }

    @staticmethod
    def get_document_for_upload(db: Session, document_id: int) -> dict:
        """
        Get minimal document info for frontend upload confirmation.
        """
        document = DocumentRepository.get_by_id(db, document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        return {
            "id": document.id,
            "title": document.title,
            "original_filename": document.original_filename,
            "processing_status": document.processing_status,
            "uploaded_at": document.uploaded_at,
        }


