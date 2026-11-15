"""
Business logic and orchestration layer for audit event operations.

Phase 3 — Audit event service.
"""

from __future__ import annotations
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import AuditEvent
from app.repositories.audit_events import AuditEventRepository
from app.schemas.audit_events import AuditEventCreate, AuditEventPublic


class AuditEventService:
    """Service layer for audit event operations."""

    @staticmethod
    def get_by_id(db: Session, audit_id: int) -> Optional[AuditEvent]:
        """Retrieve an audit event by ID."""
        return AuditEventRepository.get_by_id(db, audit_id)

    @staticmethod
    def get_user_events(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> tuple:
        """Retrieve audit events for a user."""
        items = AuditEventRepository.get_user_events(db, user_id, skip, limit)
        total = AuditEventRepository.count_user_events(db, user_id)
        return items, total

    @staticmethod
    def get_events_by_target(
        db: Session, target_type: str, target_id: str, skip: int = 0, limit: int = 100
    ) -> List[AuditEvent]:
        """Retrieve audit events for a specific target."""
        return AuditEventRepository.get_events_by_target(db, target_type, target_id, skip, limit)

    @staticmethod
    def get_all_events(db: Session, skip: int = 0, limit: int = 100) -> tuple:
        """Retrieve all audit events."""
        items = AuditEventRepository.get_all_events(db, skip, limit)
        total = AuditEventRepository.count_all(db)
        return items, total

    @staticmethod
    def create(db: Session, data: AuditEventCreate) -> AuditEvent:
        """Create a new audit event."""
        return AuditEventRepository.create(db, data)

    @staticmethod
    def get_event_count_today(db: Session) -> int:
        """Count audit events created today."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        return AuditEventRepository.count_by_date(db, today)
