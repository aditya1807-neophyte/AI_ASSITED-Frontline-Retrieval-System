"""
Data access layer for audit event-related operations.

Phase 3 — Audit event repository.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import AuditEvent


class AuditEventRepository:
    """Repository for AuditEvent model access."""

    @staticmethod
    def get_by_id(db: Session, audit_id: int) -> Optional[AuditEvent]:
        """Retrieve an audit event by ID."""
        return db.query(AuditEvent).filter(AuditEvent.id == audit_id).first()

    @staticmethod
    def get_user_events(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[AuditEvent]:
        """Retrieve audit events for a user."""
        return (
            db.query(AuditEvent)
            .filter(AuditEvent.user_id == user_id)
            .order_by(AuditEvent.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_events_by_target(
        db: Session, target_type: str, target_id: str, skip: int = 0, limit: int = 100
    ) -> List[AuditEvent]:
        """Retrieve audit events for a specific target."""
        return (
            db.query(AuditEvent)
            .filter(AuditEvent.target_type == target_type, AuditEvent.target_id == target_id)
            .order_by(AuditEvent.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create(db: Session, audit_event: AuditEvent) -> AuditEvent:
        """Create a new audit event."""
        db.add(audit_event)
        db.commit()
        db.refresh(audit_event)
        return audit_event

    @staticmethod
    def get_all_events(db: Session, skip: int = 0, limit: int = 100) -> List[AuditEvent]:
        """Retrieve all audit events."""
        return (
            db.query(AuditEvent)
            .order_by(AuditEvent.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


    @staticmethod
    def log(
        db: Session,
        user_id: Optional[int],
        action: str,
        target_type: str,
        target_id: str,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditEvent:
        """Create a new audit event."""
        from app.models import AuditEvent
        audit = AuditEvent(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit
