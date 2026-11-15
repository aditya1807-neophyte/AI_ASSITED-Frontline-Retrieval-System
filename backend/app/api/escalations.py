"""
FastAPI routers for escalation API endpoints.

Phase 3 — Escalation API routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.escalations import EscalationCreate, EscalationUpdate, EscalationPublic
from app.services.escalations_service import EscalationService
from app.core.auth import get_current_active_user, get_current_admin_user
from app.models import User
from app.schemas.pagination import Page, PageWithMeta

router = APIRouter(prefix="/escalations", tags=["Escalations"])


@router.get("/", response_model=PageWithMeta[EscalationPublic])
def list_escalations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List escalations with filtering."""
    filters = {}
    if status:
        filters["status"] = status
    if priority:
        filters["priority"] = priority

    items, total = EscalationService.get_all_by_filters(db, skip, limit, **filters)
    return {
        "items": [EscalationPublic.from_orm(item) for item in items],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "pages": (total + limit - 1) // limit,
        "has_next": skip + limit < total,
        "has_prev": skip > 0,
    }


@router.get("/open", response_model=PageWithMeta[EscalationPublic])
def list_open_escalations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List open escalations."""
    items, total = EscalationService.get_open_escalations(db, skip, limit)
    return {
        "items": [EscalationPublic.from_orm(item) for item in items],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "pages": (total + limit - 1) // limit,
        "has_next": skip + limit < total,
        "has_prev": skip > 0,
    }


@router.get("/pending", response_model=PageWithMeta[EscalationPublic])
def list_pending_escalations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List pending escalations."""
    items, total = EscalationService.get_pending_escalations(db, skip, limit)
    return {
        "items": [EscalationPublic.from_orm(item) for item in items],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "pages": (total + limit - 1) // limit,
        "has_next": skip + limit < total,
        "has_prev": skip > 0,
    }


@router.get("/{escalation_id}", response_model=EscalationPublic)
def get_escalation(escalation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get an escalation by ID."""
    escalation = EscalationService.get_by_id(db, escalation_id)
    if not escalation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escalation not found")
    return EscalationPublic.from_orm(escalation)


@router.post("/", response_model=EscalationPublic, status_code=status.HTTP_201_CREATED)
def create_escalation(
    escalation_data: EscalationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Create a new escalation."""
    escalation = EscalationService.create(db, escalation_data)
    return EscalationPublic.from_orm(escalation)


@router.put("/{escalation_id}", response_model=EscalationPublic)
def update_escalation(
    escalation_id: int,
    escalation_data: EscalationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Update an escalation."""
    escalation = EscalationService.update(db, escalation_id, escalation_data)
    if not escalation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escalation not found")
    return EscalationPublic.from_orm(escalation)


@router.delete("/{escalation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_escalation(
    escalation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)
):
    """Delete an escalation."""
    escalation = EscalationService.get_by_id(db, escalation_id)
    if not escalation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escalation not found")
    EscalationService.delete(db, escalation_id)
    return None
