"""
Business logic and orchestration layer for escalation operations.

Phase 3 — Escalation service with filter support.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.escalations import EscalationRepository
from app.schemas.escalations import EscalationCreate, EscalationUpdate
from app.models import Escalation


class EscalationService:
    """Service layer for escalation operations."""

    @staticmethod
    def get_by_id(db: Session, escalation_id: int) -> Optional[Escalation]:
        """Retrieve an escalation by ID."""
        return EscalationRepository.get_by_id(db, escalation_id)

    @staticmethod
    def get_all_by_filters(
        db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None,
        priority: Optional[str] = None, user_id: Optional[int] = None
    ) -> tuple:
        """Retrieve escalations with filter support."""
        items = EscalationRepository.get_all_by_filters(db, skip, limit, status, priority, user_id)
        total = EscalationRepository.count_all_by_filters(db, status, priority, user_id)
        return items, total

    @staticmethod
    def get_open_escalations(db: Session, skip: int = 0, limit: int = 100) -> tuple:
        """Retrieve all open escalations."""
        items = EscalationRepository.get_open_escalations(db, skip, limit)
        total = EscalationRepository.count_open(db)
        return items, total

    @staticmethod
    def get_pending(db: Session, skip: int = 0, limit: int = 100) -> tuple:
        """Retrieve all pending escalations."""
        items = EscalationRepository.get_pending_escalations(db, skip, limit)
        total = EscalationRepository.count_pending(db)
        return items, total

    @staticmethod
    def get_user_escalations(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> tuple:
        """Retrieve escalations for a user."""
        items = EscalationRepository.get_user_escalations(db, user_id, skip, limit)
        total = EscalationRepository.count_user_escalations(db, user_id)
        return items, total

    @staticmethod
    def get_escalations_by_reviewer(db: Session, reviewer_id: int, skip: int = 0, limit: int = 100) -> tuple:
        """Retrieve escalations assigned to a reviewer."""
        items = EscalationRepository.get_escalations_by_reviewer(db, reviewer_id, skip, limit)
        total = EscalationRepository.count_by_reviewer(db, reviewer_id)
        return items, total

    @staticmethod
    def create(db: Session, data: EscalationCreate) -> Escalation:
        """Create a new escalation."""
        escalation = Escalation(**data.dict(exclude_unset=True))
        return EscalationRepository.create(db, escalation)

    @staticmethod
    def update(db: Session, escalation_id: int, data: EscalationUpdate) -> Optional[Escalation]:
        """Update an escalation."""
        db_escalation = EscalationRepository.get_by_id(db, escalation_id)
        if not db_escalation:
            return None
        update_dict = data.dict(exclude_unset=True)
        return EscalationRepository.update(db, db_escalation, update_dict)

    @staticmethod
    def delete(db: Session, escalation_id: int) -> bool:
        """Delete an escalation."""
        db_escalation = EscalationRepository.get_by_id(db, escalation_id)
        if not db_escalation:
            return False
        return EscalationRepository.delete(db, db_escalation)

    @staticmethod
    def get_stats(db: Session) -> dict:
        """Get escalation statistics."""
        return EscalationRepository.get_stats(db)

    @staticmethod
    def record_audit(
        action: str, target_type: str, target_id: str,
        details: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None,
        user_agent: Optional[str] = None, db_session: Optional[Session] = None
    ) -> None:
        """Record an audit event for escalation operations."""
        from app.services.document_service import DocumentService
        DocumentService.record_audit(
            action=action, target_type=target_type, target_id=target_id,
            details=details, ip_address=ip_address, user_agent=user_agent,
            db_session=db_session
        )
