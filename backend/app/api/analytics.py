"""
FastAPI routers for analytics API endpoints.

Phase 3 — Analytics API routes.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.analytics_service import AnalyticsService
from app.core.auth import get_current_active_user
from app.models import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=Dict[str, Any])
def get_analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get analytics overview."""
    return AnalyticsService.get_overview(db)


@router.get("/documents", response_model=Dict[str, Any])
def get_analytics_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get document analytics."""
    return AnalyticsService.get_documents_analytics(db)


@router.get("/search", response_model=Dict[str, Any])
def get_analytics_search(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get search analytics."""
    return AnalyticsService.get_search_analytics(db)


@router.get("/answers", response_model=Dict[str, Any])
def get_analytics_answers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get answer analytics."""
    return AnalyticsService.get_answers_analytics(db)


@router.get("/escalations", response_model=Dict[str, Any])
def get_analytics_escalations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get escalation analytics."""
    return AnalyticsService.get_escalations_analytics(db)
