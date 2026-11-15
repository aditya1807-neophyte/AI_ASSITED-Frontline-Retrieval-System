"""
API routes for document management.

Phase 4 — Document ingestion, processing lifecycle, and content access.

Route prefix: /documents
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query, Request
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, get_current_active_user
from app.services.documents_service import DocumentService
from app.services.search_service import search_documents as search_service
from app.schemas.documents import (
    DocumentPublic, DocumentDetail, DocumentUpload, DocumentUpdate,
    DocumentStatus, DocumentType, DocumentProcessingStatus, DocumentLanguage,
    UploadResponse
)
from app.schemas.pagination import PageWithMeta

router = APIRouter(prefix="/documents", tags=["documents"])


class User:
    """Minimal user model for dependency injection in this router."""
    def __init__(self, id: int, display_name: str, role: str, account_status: str):
        self.id = id
        self.display_name = display_name
        self.role = role
        self.account_status = account_status


# Placeholder for testing; real integration will use auth.get_current_user
async def dummy_current_user():
    return User(id=1, display_name="admin", role="admin", account_status="active")


@router.get("/", response_model=PageWithMeta)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
    doc_type: Optional[str] = Query(None, description="Filter by document type"),
    status: Optional[str] = Query(None, description="Filter by document status"),
    language: Optional[str] = Query(None, description="Filter by language"),
    search: Optional[str] = Query(None, description="Full-text search"),
    current_user: User = Depends(dummy_current_user),
):
    """
    List documents with filtering and pagination.

    Supports: topic filters, document-type filters, status filters, full-text search.
    """
    from app.repositories.documents import DocumentRepository
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        # Build filtered query
        items = DocumentRepository.get_all(db, skip=0, limit=10000)

        # Apply filters
        if topic:
            items = [d for d in items if d.topic and topic.lower() in d.topic.lower()]
        if doc_type:
            items = [d for d in items if d.document_type == doc_type]
        if status:
            items = [d for d in items if d.document_status == status]
        if language:
            items = [d for d in items if d.language and language.lower() in d.language.lower()]
        if search:
            search_lower = search.lower()
            items = [d for d in items if (
                search_lower in (d.title or '').lower() or
                search_lower in (d.description or '').lower() or
                search_lower in (d.topic or '').lower()
            )]

        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = items[start:end]

        # Format for response
        items_formatted = []
        for doc in paginated:
            items_formatted.append({
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
                "tags": doc.tags_parsed,
                "version": doc.version,
                "document_status": doc.document_status,
                "effective_date": doc.effective_date,
                "review_date": doc.review_date,
                "uploaded_at": doc.uploaded_at,
                "processing_status": doc.processing_status,
                "file_size": doc.file_size,
                "num_pages": doc.num_pages,
                "word_count": doc.word_count,
            })

        return {
            "items": items_formatted,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size if total > 0 else 1,
            "has_next": page < (total + page_size - 1) // page_size if total > 0 else False,
            "has_prev": page > 1,
        }
    finally:
        db.close()


@router.get("/stats")
async def get_document_stats(
    current_user: User = Depends(dummy_current_user),
):
    """Get aggregate document database statistics."""
    from app.core.database import SessionLocal
    from app.repositories.documents import DocumentRepository

    db = SessionLocal()
    try:
        return DocumentRepository.get_stats(db)
    finally:
        db.close()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_document(
    request: Request,
    current_user: User = Depends(dummy_current_user),
):
    """
    Create a new document, upload to database & storage, and generate indexed chunks.
    Supports both multipart/form-data and application/json.
    """
    from app.models import Document, DocumentChunk
    from app.core.database import SessionLocal
    import json
    import uuid
    import os

    content_type = request.headers.get("content-type", "")
    title = None
    description = None
    document_type = "SOP"
    topic = "operations"
    intended_role = "field_technician"
    source_organization = "Frontline Operations"
    original_filename = None
    content = ""
    language = "en"
    tags_list = []
    version = "1.0"
    document_status = "active"
    file_bytes = None
    filename = None

    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                title = body.get("title")
                description = body.get("description")
                document_type = body.get("document_type", "SOP")
                topic = body.get("topic", "operations")
                intended_role = body.get("intended_role", "field_technician")
                source_organization = body.get("source_organization", "Frontline Operations")
                original_filename = body.get("original_filename")
                content = body.get("content", "")
                language = body.get("language", "en")
                tags = body.get("tags")
                if isinstance(tags, list):
                    tags_list = tags
                elif isinstance(tags, str):
                    try:
                        tags_list = json.loads(tags)
                    except Exception:
                        tags_list = [t.strip() for t in tags.split(",") if t.strip()]
                version = body.get("version", "1.0")
                document_status = body.get("document_status", "active")
        except Exception:
            pass

    # If title not found via JSON, attempt form parsing (handles multipart/form-data or form bodies)
    if not title:
        try:
            form = await request.form()
            title = form.get("title")
            description = form.get("description")
            document_type = form.get("document_type") or "SOP"
            topic = form.get("topic") or "operations"
            intended_role = form.get("intended_role") or "field_technician"
            source_organization = form.get("source_organization") or "Frontline Operations"
            original_filename = form.get("original_filename")
            content = form.get("content") or ""
            language = form.get("language") or "en"
            tags = form.get("tags")
            if tags:
                try:
                    tags_list = json.loads(tags)
                except Exception:
                    tags_list = [t.strip() for t in tags.split(",") if t.strip()]
            version = form.get("version") or "1.0"
            document_status = form.get("document_status") or "active"

            upload_file = form.get("file")
            if upload_file and hasattr(upload_file, "filename") and upload_file.filename:
                raw_bytes = await upload_file.read()
                if raw_bytes and len(raw_bytes) > 0:
                    filename = upload_file.filename
                    file_bytes = raw_bytes
        except Exception as e:
            if not title:
                raise HTTPException(status_code=400, detail=f"Invalid upload data: {str(e)}")

    if not title or not str(title).strip():
        raise HTTPException(status_code=422, detail="Document title is required")

    db = SessionLocal()
    try:
        # Prepare upload directory
        upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "uploads"))
        os.makedirs(upload_dir, exist_ok=True)

        file_path = None
        storage_reference = None
        file_size = None
        extracted_text = content or ""
        num_pages = 1

        if file_bytes and filename:
            original_filename = original_filename or filename
            file_size = len(file_bytes)

            file_ext = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4().hex[:12]}_{filename}"
            saved_path = os.path.join(upload_dir, unique_filename)
            with open(saved_path, "wb") as f:
                f.write(file_bytes)

            file_path = saved_path
            storage_reference = f"uploads/{unique_filename}"

            # Extract text if plain text / markdown / csv / json
            if file_ext.lower() in [".txt", ".md", ".csv", ".json", ".log"]:
                try:
                    extracted_text = file_bytes.decode("utf-8", errors="ignore")
                except Exception:
                    pass
            elif file_ext.lower() == ".pdf":
                try:
                    import pypdf
                    import io
                    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                    pdf_texts = [p.extract_text() or "" for p in reader.pages]
                    extracted_text = "\n\n".join(pdf_texts).strip()
                    num_pages = len(reader.pages)
                except Exception:
                    pass
            elif file_ext.lower() in [".docx", ".doc"]:
                try:
                    import docx
                    import io
                    doc_obj = docx.Document(io.BytesIO(file_bytes))
                    paragraphs = [p.text.strip() for p in doc_obj.paragraphs if p.text.strip()]
                    extracted_text = "\n\n".join(paragraphs).strip()
                    num_pages = max(1, len(paragraphs) // 5)
                except Exception:
                    pass

        # Finalize text content
        final_content = (extracted_text or content or description or title).strip()
        word_count = len(final_content.split()) if final_content else 0
        if not num_pages or num_pages <= 1:
            num_pages = max(1, len(final_content) // 1800) if final_content else 1

        # Instantiate Document in DB
        doc = Document(
            user_id=getattr(current_user, "id", 1),
            title=str(title).strip(),
            description=str(description).strip() if description else None,
            document_type=str(document_type).strip(),
            topic=str(topic).strip() if topic else "operations",
            intended_role=str(intended_role).strip() if intended_role else "field_technician",
            source_organization=str(source_organization).strip() if source_organization else "Frontline Operations",
            original_filename=original_filename or f"{str(title).lower().replace(' ', '_')}.pdf",
            storage_reference=storage_reference,
            file_path=file_path,
            file_size=file_size,
            language=language or "en",
            tags=json.dumps(tags_list) if tags_list else None,
            version=str(version) or "1.0",
            document_status=str(document_status) or "active",
            processing_status="completed",
            num_pages=num_pages,
            word_count=word_count,
            content=final_content,
        )

        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Automatically create DocumentChunk records for RAG / search retrieval
        raw_chunks = [p.strip() for p in final_content.split("\n\n") if len(p.strip()) > 25]
        if not raw_chunks:
            raw_chunks = [final_content]

        for idx, chunk_text in enumerate(raw_chunks[:40]):
            chunk = DocumentChunk(
                document_id=doc.id,
                chunk_sequence=idx + 1,
                extracted_text=chunk_text,
                page_reference=str(max(1, (idx // 3) + 1)),
                section_heading=f"Section {idx + 1}",
                chunk_metadata=json.dumps({
                    "word_count": len(chunk_text.split()),
                    "role": doc.intended_role,
                    "topic": doc.topic,
                }),
            )
            db.add(chunk)

        db.commit()

        return {
            "id": doc.id,
            "title": doc.title,
            "original_filename": doc.original_filename,
            "storage_reference": doc.storage_reference,
            "processing_status": doc.processing_status,
            "document_status": doc.document_status,
            "topic": doc.topic,
            "intended_role": doc.intended_role,
            "num_pages": doc.num_pages,
            "word_count": doc.word_count,
            "uploaded_at": doc.uploaded_at,
        }
    finally:
        db.close()


@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: int,
    current_user: User = Depends(dummy_current_user),
):
    """
    Get document details with metadata and chunk count.
    """
    from app.repositories.documents import DocumentRepository
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        doc = DocumentRepository.get_by_id(db, document_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        return doc.to_dict()
    finally:
        db.close()


@router.put("/{document_id}", response_model=DocumentPublic)
async def update_document(
    document_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    topic: Optional[str] = Form(None),
    intended_role: Optional[str] = Form(None),
    source_organization: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    version: Optional[str] = Form(None),
    document_status: Optional[str] = Form(None),
    effective_date: Optional[str] = Form(None),
    review_date: Optional[str] = Form(None),
    current_user: User = Depends(dummy_current_user),
):
    """
    Update document metadata (title, description, status, etc.).

    Does not change the stored file or processing status.
    """
    from app.schemas.documents import DocumentLanguage
    from app.repositories.documents import DocumentRepository
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        update_data = {}
        if title is not None:
            update_data['title'] = title
        if description is not None:
            update_data['description'] = description
        if document_type is not None:
            update_data['document_type'] = document_type
        if topic is not None:
            update_data['topic'] = topic
        if intended_role is not None:
            update_data['intended_role'] = intended_role
        if source_organization is not None:
            update_data['source_organization'] = source_organization
        if language is not None:
            update_data['language'] = DocumentLanguage(language)
        if version is not None:
            update_data['version'] = version
        if document_status is not None:
            update_data['document_status'] = document_status
        if effective_date is not None:
            update_data['effective_date'] = datetime.fromisoformat(effective_date)
        if review_date is not None:
            update_data['review_date'] = datetime.fromisoformat(review_date)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )

        DocumentRepository.update(db, document_id, update_data)

        doc = DocumentRepository.get_by_id(db, document_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )

        return doc.to_dict()
    finally:
        db.close()


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(dummy_current_user),
):
    """
    Delete a document and all associated chunks from database.
    """
    from app.repositories.documents import DocumentRepository
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        success = DocumentRepository.delete(db, document_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        return {"success": True, "message": "Document deleted successfully"}
    finally:
        db.close()


@router.post("/{document_id}/process", response_model=dict)
async def process_document(
    document_id: int,
    current_user: User = Depends(dummy_current_user),
):
    """
    Start or resume document processing/indexing.

    Triggers text extraction and chunking.
    """
    from app.repositories.documents import DocumentRepository
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        return DocumentService.start_indexing(db, document_id)
    finally:
        db.close()


@router.post("/{document_id}/reprocess", response_model=dict)
async def reprocess_document(
    document_id: int,
    current_user: User = Depends(dummy_current_user),
):
    """
    Reprocess a document, clearing existing chunks first.

    Prevents duplicate chunks during re-indexing.
    """
    from app.repositories.documents import DocumentRepository
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        return DocumentService.reprocess_document(db, document_id)
    finally:
        db.close()


@router.get("/{document_id}/content", response_model=dict)
async def get_document_content(
    document_id: int,
    current_user: User = Depends(dummy_current_user),
):
    """
    Get document content with extracted chunks.

    Used by frontend for document preview.
    """
    from app.repositories.documents import DocumentRepository
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        return DocumentService.get_document_content(db, document_id)
    finally:
        db.close()


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    current_user: User = Depends(dummy_current_user),
):
    """
    Download the original file for a document.

    Returns the stored file (no internal path exposed).
    """
    from app.repositories.documents import DocumentRepository
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        doc = DocumentRepository.get_by_id(db, document_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )

        if not doc.storage_reference:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No stored file for this document"
            )

        from app.utils.file_storage import get_file_storage_path
        file_path = get_file_storage_path(doc.storage_reference)
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk"
            )

        return FileResponse(
            path=file_path,
            filename=doc.original_filename,
            media_type="application/octet-stream",
        )
    finally:
        db.close()


