"""
FastAPI routers for search history API endpoints.

Phase 3 — Search history API routes.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.search_history_service import SearchHistoryService
from app.core.auth import get_current_active_user
from app.models import User
from app.schemas.search_history import SearchHistoryPublic
from app.schemas.pagination import Page, PageWithMeta

router = APIRouter(prefix="/search-history", tags=["Search History"])


@router.get("/", response_model=PageWithMeta[SearchHistoryPublic])
def list_search_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List search history for the current user."""
    items, total = SearchHistoryService.get_user_search_history(db, current_user.id, skip, limit)
    return {
        "items": [SearchHistoryPublic.from_orm(item) for item in items],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "pages": (total + limit - 1) // limit,
        "has_next": skip + limit < total,
        "has_prev": skip > 0,
    }


@router.get("/top", response_model=List[dict])
def get_top_queries(
    n: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)
):
    """Get top N most searched queries across all users."""
    return SearchHistoryService.get_top_queries(db, n)


@router.post("/", status_code=status.HTTP_201_CREATED)
def record_search(
    query: str = Query(..., min_length=1, max_length=1024),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Record a search query."""
    return SearchHistoryService.record(db, current_user.id, query)


@router.delete("/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_search_history(
    search_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Delete a specific search history entry."""
    entry = SearchHistoryService.get_by_id(db, search_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search history entry not found")
    if entry.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your search history")
    SearchHistoryService.delete(db, entry)
    return None
