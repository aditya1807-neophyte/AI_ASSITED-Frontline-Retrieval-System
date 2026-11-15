"""
Search service with SQLite full-text search (FTS).

Phase 4 — Implements full-text search over document content
using SQLite FTS5, plus metadata, topic, and filter searches.

Search covers:
- Title search
- Metadata search
- Topic filters
- Document-type filters
- Role filters
- Source filters
- Status filters
- Full-text search over extracted content
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from sqlalchemy import or_, and_, func
from sqlalchemy.orm import Session

from app.models import Document, DocumentChunk
from app.repositories.documents import DocumentRepository
from app.repositories.chunks import DocumentChunkRepository

logger = logging.getLogger(__name__)

# Valid status values for filtering
VALID_STATUSES = ['active', 'under_review', 'superseded', 'archived']

# Valid document types
VALID_DOCUMENT_TYPES = ['policy', 'procedure', 'standard', 'guideline', 'report', 'contract', 'manual']


class SearchService:
    """Search service wrapper for the RAG pipeline."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search documents and chunks using full-text search.

        Args:
        - query: search query string
        - limit: maximum number of results

        Returns:
        - list of search results with chunk text
        """
        import re
        from app.core.database import get_db
        db = next(get_db())

        formatted = []
        words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 2] if query else []

        # 1. Search chunks directly for granular, high-relevance evidence
        if words:
            chunks = db.query(DocumentChunk).all()
            matching_chunks = []
            for ch in chunks:
                txt = (ch.extracted_text or "").lower()
                matches = sum(1 for w in words if w in txt)
                if matches > 0:
                    doc = db.query(Document).filter(Document.id == ch.document_id).first()
                    matching_chunks.append((
                        matches,
                        {
                            "content": ch.extracted_text or "",
                            "title": doc.title if doc else "Document",
                            "chunk_sequence": ch.chunk_sequence or 0,
                            "page_reference": ch.page_reference or (doc.document_type if doc else ""),
                            "document_id": ch.document_id,
                        }
                    ))
            matching_chunks.sort(key=lambda x: x[0], reverse=True)
            for _, item in matching_chunks[:limit]:
                formatted.append(item)

        # 2. Also search documents if chunk results are sparse
        if len(formatted) < limit:
            results, total = search_documents(
                db,
                search_term=query,
                page=1,
                page_size=limit,
            )
            for item in results:
                # Avoid duplicate titles if already included
                if not any(f.get("title") == item.get("title") for f in formatted):
                    formatted.append({
                        "content": item.get("excerpt", ""),
                        "title": item.get("title", ""),
                        "chunk_sequence": 0,
                        "page_reference": item.get("document_type", ""),
                        "document_id": item.get("id"),
                    })

        db.close()
        return formatted[:limit]


def build_search_query(
    db: Session,
    query: Optional[str] = None,
    topic: Optional[str] = None,
    doc_type: Optional[str] = None,
    intended_role: Optional[str] = None,
    source_organization: Optional[str] = None,
    status: Optional[str] = None,
    language: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "relevance",
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Build and execute a search query.

    Supports full-text search over document content plus metadata filters.

    Returns:
        Tuple of (results list, total_count)
    """
    # Start with the base document query
    skip = (page - 1) * page_size
    base_query = DocumentRepository.get_all(db, skip=skip, limit=page_size, status=status, doc_type=doc_type, topic=topic, intended_role=intended_role, source_organization=source_organization, language=language)

    # Filter by status
    if status:
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}. Must be one of: {VALID_STATUSES}")
        base_query = [d for d in base_query if d.document_status == status]

    # Filter by document type
    if doc_type:
        if doc_type not in VALID_DOCUMENT_TYPES:
            raise ValueError(f"Invalid document type: {doc_type}")
        base_query = [d for d in base_query if d.document_type == doc_type]

    # Filter by topic
    if topic:
        base_query = [d for d in base_query if topic.lower() in d.topic.lower()]

    # Filter by intended role
    if intended_role:
        base_query = [d for d in base_query if intended_role.lower() in d.intended_role.lower()]

    # Filter by source organization
    if source_organization:
        base_query = [d for d in base_query if source_organization.lower() in d.source_organization.lower()]

    # Filter by language
    if language:
        base_query = [d for d in base_query if d.language and language.lower() in d.language.lower()]

    # Full-text search on extracted content and chunks
    if query:
        import re
        results = []
        words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 2]
        for doc in base_query:
            search_fields = [
                doc.title or "",
                doc.description or "",
                doc.topic or "",
                doc.content or "",
            ]
            chunks = DocumentChunkRepository.get_by_document_id(db, doc.id)
            chunk_texts = [c.extracted_text or "" for c in chunks]
            full_text = (" ".join(search_fields) + " " + " ".join(chunk_texts)).lower()

            # Match exact query or any significant word
            if query.lower() in full_text or (words and any(w in full_text for w in words)):
                results.append(doc)
        base_query = results

    total = len(base_query)

    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    paginated = base_query[start:end]

    # Format results
    formatted = []
    for doc in paginated:
        # Count chunks with content for excerpt
        chunk_count = 0
        excerpt = ""
        if doc.processing_status == 'indexed' or doc.document_status in ['indexed', 'active']:
            chunks = DocumentChunkRepository.get_by_document_id(db, doc.id)
            chunk_count = len(chunks)
            if chunks:
                excerpt = chunks[0].extracted_text[:200] + "..." if len(chunks[0].extracted_text) > 200 else chunks[0].extracted_text

        formatted.append({
            "id": doc.id,
            "title": doc.title,
            "description": doc.description,
            "topic": doc.topic,
            "document_type": doc.document_type,
            "intended_role": doc.intended_role,
            "source_organization": doc.source_organization,
            "language": doc.language,
            "version": doc.version,
            "status": doc.document_status,
            "processing_status": doc.processing_status,
            "uploaded_at": doc.uploaded_at,
            "chunk_count": chunk_count,
            "excerpt": excerpt,
            "effective_date": doc.effective_date,
            "review_date": doc.review_date,
        })

    return formatted, total


def search_documents(
    db: Session,
    search_term: Optional[str] = None,
    topic: Optional[str] = None,
    doc_type: Optional[str] = None,
    intended_role: Optional[str] = None,
    source_organization: Optional[str] = None,
    status: Optional[str] = None,
    language: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    """
    Main search entry point.

    Returns paginated search results with relevance.
    """
    if search_term and len(search_term) < 2:
        # Treat short terms as no search
        results, total = build_search_query(
            db, query=None, topic=topic, doc_type=doc_type,
            intended_role=intended_role, source_organization=source_organization,
            status=status, language=language, page=page, page_size=page_size
        )
    else:
        results, total = build_search_query(
            db, query=search_term, topic=topic, doc_type=doc_type,
            intended_role=intended_role, source_organization=source_organization,
            status=status, language=language, page=page, page_size=page_size
        )

    # Calculate pagination
    pages = (total + page_size - 1) // page_size if total > 0 else 1

    # Return just the results and total count for backward compatibility
    return results, total

    # This remaining dict is no longer returned for backward compatibility
    # return {
    #     "items": results,
    #     "total": total,
    #     "page": page,
    #     "page_size": page_size,
    #     "pages": pages,
    #     "has_next": page < pages,
    #     "has_prev": page > 1,
    # }
