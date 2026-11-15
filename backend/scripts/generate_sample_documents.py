"""
Sample document data generator for FieldGuide AI.

Phase 4 — Creates clearly labeled fictional operational documents
for demonstration purposes.

Usage:
    python scripts/generate_sample_documents.py

Creates documents in the database that demonstrate the document
management and search features.

All documents are fictional and attributed to "FieldGuide"
as a demonstration project.
"""

import os
import sys
from datetime import datetime, timezone

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.core.database import Base, engine, SessionLocal
from app.models import Document, DocumentChunk
from app.repositories.documents import DocumentRepository
from app.repositories.chunks import DocumentChunkRepository
from app.repositories.audit_events import AuditEventRepository

# Sample documents
SAMPLE_DOCUMENTS = [
    {
        "title": "FieldGuide Standard Operating Procedures",
        "description": "Standard operating procedures for using the FieldGuide AI system including document management workflows.",
        "document_type": "standard",
        "topic": "operations",
        "intended_role": "analyst",
        "source_organization": "FieldGuide Development Team",
        "original_filename": "fieldguide_sop.pdf",
        "language": "en",
        "tags": ["standard", "operations", "sop", "workflow"],
        "version": "1.0",
        "document_status": "active",
        "effective_date": datetime(2024, 1, 15, tzinfo=timezone.utc),
        "review_date": datetime(2025, 1, 15, tzinfo=timezone.utc),
    },
    {
        "title": "Knowledge Retrieval Policy",
        "description": "Policy governing knowledge retrieval, search, and content management across the FieldGuide platform.",
        "document_type": "policy",
        "topic": "policies",
        "intended_role": "all",
        "source_organization": "FieldGuide Development Team",
        "original_filename": "knowledge_policy.pdf",
        "language": "en",
        "tags": ["policy", "knowledge", "retrieval"],
        "version": "2.0",
        "document_status": "active",
        "effective_date": datetime(2023, 6, 1, tzinfo=timezone.utc),
        "review_date": datetime(2025, 6, 1, tzinfo=timezone.utc),
    },
    {
        "title": "Document Management Guidelines",
        "description": "Guidelines for managing document lifecycle including upload, review, and archival procedures.",
        "document_type": "guideline",
        "topic": "governance",
        "intended_role": "admin",
        "source_organization": "FieldGuide Product Team",
        "original_filename": "doc_management_guidelines.pdf",
        "language": "en",
        "tags": ["guideline", "governance", "document-lifecycle"],
        "version": "1.2",
        "document_status": "active",
        "effective_date": datetime(2024, 3, 1, tzinfo=timezone.utc),
        "review_date": datetime(2025, 3, 1, tzinfo=timezone.utc),
    },
    {
        "title": "Sample Compliance Report Q2 2024",
        "description": "Fictional sample compliance report for demonstration purposes. Not real institutional data.",
        "document_type": "report",
        "topic": "compliance",
        "intended_role": "analyst",
        "source_organization": "FieldGuide Security Team",
        "original_filename": "compliance_report_q2_2024.pdf",
        "language": "en",
        "tags": ["compliance", "sample", "report"],
        "version": "1.0",
        "document_status": "archived",
        "effective_date": datetime(2024, 7, 1, tzinfo=timezone.utc),
        "review_date": datetime(2025, 1, 1, tzinfo=timezone.utc),
    },
    {
        "title": "Document Processing Manual",
        "description": "Manual for processing documents including text extraction, chunking, and indexing workflows.",
        "document_type": "manual",
        "topic": "technical",
        "intended_role": "developer",
        "source_organization": "FieldGuide Engineering Team",
        "original_filename": "processing_manual.pdf",
        "language": "en",
        "tags": ["manual", "technical", "processing"],
        "version": "1.0",
        "document_status": "active",
        "effective_date": datetime(2024, 4, 1, tzinfo=timezone.utc),
        "review_date": datetime(2025, 4, 1, tzinfo=timezone.utc),
    },
    {
        "title": "Security Guidelines for Document Storage",
        "description": "Security guidelines covering file storage, access controls, and data protection for document management.",
        "document_type": "standard",
        "topic": "security",
        "intended_role": "admin",
        "source_organization": "FieldGuide Security Team",
        "original_filename": "security_guidelines.pdf",
        "language": "en",
        "tags": ["security", "storage", "access-control"],
        "version": "2.0",
        "document_status": "active",
        "effective_date": datetime(2024, 2, 1, tzinfo=timezone.utc),
        "review_date": datetime(2025, 2, 1, tzinfo=timezone.utc),
    },
]

# Sample chunk content for each document
SAMPLE_CHUNKS = {
    "fieldguide_sop.pdf": [
        "FieldGuide Operations Standard Operating Procedure v1.0",
        "This document establishes standard operating procedures for all FieldGuide AI users.",
        "Section 1: Document Upload - Users authenticate to the system before uploading documents.",
        "Each document must include title, description, document type, and topic metadata.",
        "Section 2: Document Processing - After upload, documents are extracted, chunked, and indexed.",
        "The ingestion pipeline supports PDF, DOCX, TXT, Markdown, and CSV file formats.",
        "Section 3: Search - Full-text search is available across all indexed document content.",
        "Section 4: Retrieval - Users can search by title, topic, document type, and status filters.",
        "Section 5: Document Lifecycle - Documents transition through draft, active, under_review, archived, and superseded states.",
    ],
    "knowledge_policy.pdf": [
        "Knowledge Retrieval Policy v2.0",
        "This policy defines how knowledge is retrieved, indexed, and maintained within the FieldGuide platform.",
        "Section 1: Content Ingestion - All documents must pass through validation before indexing.",
        "File type validation ensures only supported document types are accepted.",
        "Text extraction preserves page references for PDFs and heading structure for Markdown.",
        "Section 2: Quality Assurance - Index status must be confirmed before content appears in search results.",
        "Failed extractions must be flagged with requires_review or requires_ocr status.",
        "Section 3: Access Control - Document access is governed by user roles and document permissions.",
        "Section 4: Audit Trails - All administrative actions are recorded in the audit event log.",
        "Section 5: Periodic Review - Documents must be reviewed at their review_date.",
    ],
    "doc_management_guidelines.pdf": [
        "Document Management Guidelines v1.2",
        "This guideline covers the complete document lifecycle from ingestion to archival.",
        "Section 1: Upload - Files are validated for type, size, and content before storage.",
        "Section 2: Metadata - All documents require title, description, and relevant metadata tags.",
        "Section 3: Review - Documents in review status are not searchable until indexed.",
        "Section 4: Archival - Archived documents are retained but marked as inactive in search.",
        "Section 5: Deletion - Deleting a document also removes associated chunks, saved items, and audit records.",
    ],
    "compliance_report_q2_2024.pdf": [
        "Sample Compliance Report Q2 2024",
        "This is a fictional demonstration report. It does not represent actual compliance data.",
        "The report demonstrates document upload, metadata entry, and search functionality.",
        "Section 1: Overview - This sample demonstrates the document management system.",
        "Section 2: Procedures - The procedures are fictional and for illustration only.",
        "Section 3: Compliance - This document is marked as archived for demonstration.",
        "Section 4: Status - Archived documents do not appear in active search results.",
        "Section 5: Limitations - This document contains no real institutional data.",
    ],
    "processing_manual.pdf": [
        "Document Processing Manual v1.0",
        "This manual describes the technical pipeline for processing documents.",
        "Section 1: File Validation - File extensions and content are validated before processing.",
        "Section 2: Text Extraction - PDF extraction via pypdf, DOCX via python-docx, TXT via UTF-8.",
        "Section 3: Chunking - Text is split into chunks of 400-800 tokens with 15% overlap.",
        "Section 4: Indexing - Chunks are stored in the database with document references.",
        "Section 5: Search - SQLite full-text search is used for content retrieval.",
        "Section 6: Status Tracking - Processing status is tracked in the database.",
    ],
    "security_guidelines.pdf": [
        "Security Guidelines for Document Storage v2.0",
        "This document defines security requirements for the document management system.",
        "Section 1: Access Control - Users are authenticated via JWT tokens and authorized by role.",
        "Section 2: File Storage - Files are stored with generated internal identifiers.",
        "Section 3: Path Traversal Prevention - File paths are validated to prevent traversal attacks.",
        "Section 4: Data Protection - Passwords are hashed with bcrypt; data is encrypted at rest.",
        "Section 5: Audit Logging - All administrative actions are logged in the audit event system.",
    ],
}


def generate_sample_documents():
    """Create sample documents in the database."""
    print("Creating sample documents for FieldGuide AI demonstration...")

    # Create tables if they don't exist
    from app.core.database import Base, engine
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Check if documents already exist
    existing_count = db.query(Document).count()
    if existing_count > 0:
        print(f"Database already contains {existing_count} documents. Skipping sample data creation.")
        print("Use this command to re-create sample data: rm -rf data && python scripts/generate_sample_documents.py")
        db.close()
        return

    # Create each sample document
    created = 0
    for i, doc_data in enumerate(SAMPLE_DOCUMENTS):
        print(f"  [{i+1}/{len(SAMPLE_DOCUMENTS)}] Creating {doc_data['title']}...")

        # Create document
        doc = Document(
            title=doc_data["title"],
            description=doc_data["description"],
            document_type=doc_data["document_type"],
            topic=doc_data["topic"],
            intended_role=doc_data["intended_role"],
            source_organization=doc_data["source_organization"],
            original_filename=doc_data["original_filename"],
            storage_reference=f"sample_doc_{i+1}",
            language=doc_data.get("language"),
            tags=doc_data.get("tags"),
            version=doc_data.get("version"),
            document_status=doc_data.get("document_status"),
            effective_date=doc_data.get("effective_date"),
            review_date=doc_data.get("review_date"),
            uploaded_at=datetime.now(timezone.utc),
            processing_status="indexed",
            content="Sample document content. This document has been marked for demonstration purposes.",
            file_path=None,
            file_size=None,
            file_checksum=None,
            num_pages=None,
            word_count=None,
        )
        db.add(doc)
        db.flush()

        # Create chunks for this document
        doc_chunks = [
            DocumentChunk(
                document_id=doc.id,
                chunk_sequence=j,
                extracted_text=chunk_text,
                page_reference=None,
                section_heading=None,
                chunk_metadata={},
            )
            for j, chunk_text in enumerate(SAMPLE_CHUNKS.get(doc_data["original_filename"], []))
        ]
        db.add_all(doc_chunks)
        created += 1

    db.commit()
    print(f"\nSuccessfully created {created} sample documents.")
    print("Sample documents are now available for search and demonstration.")
    db.close()


if __name__ == "__main__":
    generate_sample_documents()
