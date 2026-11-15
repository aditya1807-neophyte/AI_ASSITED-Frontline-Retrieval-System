"""
FastAPI routers for saved items API endpoints.

Phase 3 — Saved item API routes.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.saved_items import SavedItemCreate, SavedItemPublic, SavedItemUpdate
from app.services.saved_items_service import SavedItemService
from app.core.auth import get_current_active_user
from app.models import User
from app.schemas.pagination import Page, PageWithMeta

router = APIRouter(prefix="/saved-items", tags=["Saved Items"])


@router.get("/", response_model=PageWithMeta[SavedItemPublic])
def list_saved_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    item_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List saved items for the current user."""
    items, total = SavedItemService.get_user_saved_items(
        db, current_user.id, item_type, skip, limit
    )
    return {
        "items": [SavedItemPublic.from_orm(item) for item in items],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "pages": (total + limit - 1) // limit,
        "has_next": skip + limit < total,
        "has_prev": skip > 0,
    }


@router.get("/count", response_model=int)
def get_saved_items_count(
    item_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get saved items count for the current user."""
    return SavedItemService.get_user_saved_count(db, current_user.id, item_type)


@router.post("/", response_model=SavedItemPublic, status_code=status.HTTP_201_CREATED)
def save_item(
    item_data: SavedItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Save a document or answer."""
    # Verify the item exists
    from app.services.document_service import DocumentService
    from app.services.answers_service import AnswerService
    if item_data.item_type == "document":
        if not DocumentService.get_by_id(db, int(item_data.item_reference)):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    elif item_data.item_type == "answer":
        if not AnswerService.get_by_id(db, int(item_data.item_reference)):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item type")

    # Check for duplicate
    existing = SavedItemService.get_by_user_and_reference(db, current_user.id, item_data.item_type, item_data.item_reference)
    if existing:
        return SavedItemPublic.from_orm(existing)

    item_data.user_id = current_user.id
    saved_item = SavedItemService.create(db, item_data)
    return SavedItemPublic.from_orm(saved_item)


@router.delete("/{saved_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_item(
    saved_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a saved item."""
    db_item = SavedItemService.get_by_id(db, saved_item_id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved item not found")
    if db_item.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your item")
    SavedItemService.delete(db, saved_item_id)
    return None
