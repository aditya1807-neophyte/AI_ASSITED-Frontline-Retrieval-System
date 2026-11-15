"""
FastAPI routers for health and document endpoints.

Phase 3 — Health check and document listing API routes.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.documents import DocumentPublic
from app.schemas.pagination import PageWithMeta

router = APIRouter()


@router.get('/health')
def health_check():
    """Health check endpoint."""
    return {
        'status': 'healthy',
        'message': 'Frontline Knowledge Workspace API is up',
        'timestamp': datetime.utcnow().isoformat(),
    }


@router.get('/docs', response_model=PageWithMeta[DocumentPublic])
def list_documents(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    doc_type: str = None,
    topic: str = None,
    db: Session = Depends(get_db),
):
    """List all documents with pagination and filtering."""
    from app.services.document_service import DocumentService
    documents, total = DocumentService.get_all(db, skip, limit, status, doc_type, topic)
    return {
        "items": [DocumentPublic.from_orm(d) for d in documents],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "pages": (total + limit - 1) // limit,
        "has_next": skip + limit < total,
        "has_prev": skip > 0,
    }
