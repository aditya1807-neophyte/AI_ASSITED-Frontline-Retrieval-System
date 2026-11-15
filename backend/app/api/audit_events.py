"""
FastAPI routers for audit events API endpoints.

Phase 3 — Audit event API routes.
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.audit_events import AuditEventCreate, AuditEventPublic
from app.services.audit_events_service import AuditEventService
from app.core.auth import get_current_admin_user
from app.models import User
from app.schemas.pagination import Page, PageWithMeta

router = APIRouter(prefix="/audit-events", tags=["Audit Events"])


@router.get("/", response_model=PageWithMeta[AuditEventPublic])
def list_audit_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    action: Optional[str] = Query(None),
    target_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """List audit events (admin only)."""
    filters = {}
    if action:
        filters["action"] = action
    if target_type:
        filters["target_type"] = target_type

    items, total = AuditEventService.get_all_by_filters(db, skip, limit, **filters)
    return {
        "items": [AuditEventPublic.from_orm(item) for item in items],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "pages": (total + limit - 1) // limit,
        "has_next": skip + limit < total,
        "has_prev": skip > 0,
    }


@router.post("/", response_model=AuditEventPublic, status_code=status.HTTP_201_CREATED)
def create_audit_event(
    audit_event_data: AuditEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Create a new audit event (admin only)."""
    from app.core.database import SessionLocal
    # Audit events are recorded by services; this is for direct administration
    audit_event = AuditEventService.create(db, audit_event_data)
    return AuditEventPublic.from_orm(audit_event)


@router.get("/stats", response_model=dict)
def get_audit_event_stats(db: Session = Depends(get_db)):
    """Get audit event statistics."""
    return {
        "total": AuditEventService.get_total(db),
        "today": AuditEventService.get_event_count_today(db),
        "by_action": AuditEventService.get_events_by_action(db),
    }
