"""
Document indexing service with lifecycle state management.

Phase 4 — Full indexing pipeline with state management.

Lifecycle states:
- uploaded: File uploaded, ready for processing
- extracting: Text extraction in progress
- extracted: Text extracted, ready for chunking
- indexing: Chunking and indexing in progress
- indexed: Successfully indexed, ready for search
- failed: Indexing failed, needs review
- requires_ocr: PDF too scanned, requires OCR
- requires_review: Content flagged for human review

Only "indexed" reports successful indexing.
"""

import logging
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models import Document
from app.models import DocumentChunk
from app.repositories.documents import DocumentRepository
from app.repositories.chunks import DocumentChunkRepository
from app.repositories.audit_events import AuditEventRepository
from app.utils.text_extractors import extract_file, ExtractionError
from app.utils.file_storage import get_file_storage_path, delete_file, validate_file_upload
from app.services.chunks_service import create_chunks, MIN_CHUNK_SIZE, MAX_CHUNK_SIZE

logger = logging.getLogger(__name__)

# Valid processing status values
PROCESSING_STATUSES = {
    'uploaded': 'File uploaded, ready for processing',
    'extracting': 'Text extraction in progress',
    'extracted': 'Text extracted, ready for indexing',
    'indexing': 'Chunking and indexing in progress',
    'indexed': 'Successfully indexed and searchable',
    'failed': 'Indexing failed, review required',
    'requires_ocr': 'Requires OCR (scanned PDF)',
    'requires_review': 'Requires human review after extraction',
}


class DocumentIndexingError(Exception):
    """Raised when document indexing fails."""
    pass


class DocumentIndexer:
    """Main service for document ingestion and indexing."""

    @staticmethod
    def get_status_message(status: str) -> str:
        """Get human-readable message for a status."""
        return PROCESSING_STATUSES.get(status, status)

    @staticmethod
    def start_ingestion(db: Session, document_id: int) -> dict:
        """
        Start the ingestion pipeline for a document.

        1. Validate file
        2. Extract text
        3. Chunk text
        4. Index chunks
        5. Update document status
        """
        document = DocumentRepository.get_by_id(db, document_id)
        if not document:
            raise DocumentIndexingError(f"Document {document_id} not found")

        # Set processing status to extracting
        DocumentRepository.update_status(db, document_id, 'extracting')
        AuditEventRepository.log(
            db, document.user_id, 'indexing_start',
            'document', str(document.id),
            details=f"Extracting text: {document.original_filename}",
            ip_address=None, user_agent=None
        )

        try:
            # Step 1: Extract text
            text, source_info = extract_file(document.storage_reference)
            DocumentRepository.update_processing_status(
                db, document_id, 'extracted',
                metadata={"source_info": source_info}
            )

            # Step 2: Chunk text
            chunks = create_chunks(
                document_id=document.id,
                title=document.title,
                extracted_text=text,
                page_reference=None,
                section_heading=None,
                version=document.version,
            )

            # Step 3: Save chunks
            DocumentChunkRepository.bulk_create(db, chunks)

            # Step 4: Update document status
            DocumentRepository.update_status(db, document_id, 'indexed')
            DocumentRepository.update_processed_at(db, document_id)

            # Log audit
            AuditEventRepository.log(
                db, document.user_id, 'indexing_complete',
                'document', str(document.id),
                details=f"Indexed {len(chunks)} chunks from {document.original_filename}",
                ip_address=None, user_agent=None
            )

            return {
                'status': 'indexed',
                'chunk_count': len(chunks),
                'message': f'Successfully indexed {len(chunks)} chunks',
            }

        except ExtractionError as e:
            # Mark as requires_review
            DocumentRepository.update_status(db, document_id, 'failed')
            DocumentRepository.update_processed_at(db, document_id)
            AuditEventRepository.log(
                db, document.user_id, 'indexing_failed',
                'document', str(document.id),
                details=f'Extraction failed: {str(e)}',
                ip_address=None, user_agent=None
            )
            raise

        except Exception as e:
            DocumentRepository.update_status(db, document_id, 'failed')
            DocumentRepository.update_processed_at(db, document_id)
            AuditEventRepository.log(
                db, document.user_id, 'indexing_failed',
                'document', str(document.id),
                details=f'Unexpected error: {str(e)}',
                ip_address=None, user_agent=None
            )
            raise


