
import sys
sys.path.insert(0, ".")

from app.core.database import SessionLocal
from app.models import Document, DocumentChunk
from datetime import datetime, timezone
import json

# Sample documents
SAMPLE_DOCUMENTS = [
    ["FieldGuide Standard Operating Procedures", "Standard operating procedures for using the FieldGuide AI system including document management workflows.", "standard", "operations", "analyst", "FieldGuide Development Team", "fieldguide_sop.pdf", "en", ["standard", "operations", "sop", "workflow"], "1.0", "active"],
    ["Knowledge Retrieval Policy", "Policy governing knowledge retrieval, search, and content management across the FieldGuide platform.", "policy", "policies", "all", "FieldGuide Development Team", "knowledge_policy.pdf", "en", ["policy", "knowledge", "retrieval"], "2.0", "active"],
    ["Document Management Guidelines", "Guidelines for managing document lifecycle including upload, review, and archival procedures.", "guideline", "governance", "admin", "FieldGuide Product Team", "doc_management_guidelines.pdf", "en", ["guideline", "governance", "document-lifecycle"], "1.2", "active"],
    ["Sample Compliance Report Q2 2024", "Fictional sample compliance report for demonstration purposes. Not real institutional data.", "report", "compliance", "analyst", "FieldGuide Security Team", "compliance_report_q2_2024.pdf", "en", ["compliance", "sample", "report"], "1.0", "archived"],
    ["Document Processing Manual", "Manual for processing documents including text extraction, chunking, and indexing workflows.", "manual", "technical", "developer", "FieldGuide Engineering Team", "processing_manual.pdf", "en", ["manual", "technical", "processing"], "1.0", "active"],
    ["Security Guidelines for Document Storage", "Security guidelines covering file storage, access controls, and data protection for document management.", "standard", "security", "admin", "FieldGuide Security Team", "security_guidelines.pdf", "en", ["security", "storage", "access-control"], "2.0", "active"],
]

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

# Create tables if they don't exist
from app.core.database import Base, engine
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Check if documents already exist
    existing_count = db.query(Document).count()
    if existing_count > 0:
        print("Database already contains " + str(existing_count) + " documents. Skipping sample data creation.")
        sys.exit(0)

    # Create documents
    created = 0
    for i, doc_data in enumerate(SAMPLE_DOCUMENTS):
        print("  [" + str(i+1) + "/" + str(len(SAMPLE_DOCUMENTS)) + "] Creating " + doc_data[0] + "...")
        tags_str = json.dumps(doc_data[8])
        doc = Document(
            title=doc_data[0],
            description=doc_data[1],
            document_type=doc_data[2],
            topic=doc_data[3],
            intended_role=doc_data[4],
            source_organization=doc_data[5],
            original_filename=doc_data[6],
            storage_reference="sample_doc_" + str(i+1),
            language=doc_data[7],
            tags=tags_str,
            version=doc_data[9],
            document_status=doc_data[10],
            effective_date=datetime(2024, 1, 15, tzinfo=timezone.utc),
            review_date=datetime(2025, 1, 15, tzinfo=timezone.utc),
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
        doc_chunks = []
        chunk_list = SAMPLE_CHUNKS.get(doc_data[6], [])
        for j, chunk_text in enumerate(chunk_list):
            doc_chunk = DocumentChunk(
                document_id=doc.id,
                chunk_sequence=j,
                extracted_text=chunk_text,
                page_reference=None,
                section_heading=None,
                chunk_metadata=json.dumps({}),
            )
            doc_chunks.append(doc_chunk)
        db.add_all(doc_chunks)
        created += 1

    db.commit()
    print("")
    print("Successfully created " + str(created) + " sample documents.")
    print("Sample documents are now available for search and demonstration.")
except Exception as e:
    db.rollback()
    print("Error:", str(e))
    import traceback
    traceback.print_exc()
finally:
    db.close()
