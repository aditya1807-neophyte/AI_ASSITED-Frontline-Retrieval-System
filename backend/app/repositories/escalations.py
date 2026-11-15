"""
Data access layer for escalation-related operations.

Phase 3 — Escalation repository.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import Escalation


class EscalationRepository:
    """Repository for Escalation model access."""

    @staticmethod
    def get_by_id(db: Session, escalation_id: int) -> Optional[Escalation]:
        """Retrieve an escalation by ID."""
        return db.query(Escalation).filter(Escalation.id == escalation_id).first()

    @staticmethod
    def get_all_by_filters(
        db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None,
        priority: Optional[str] = None, user_id: Optional[int] = None
    ) -> List[Escalation]:
        """Retrieve escalations with filters."""
        query = db.query(Escalation)
        if status:
            query = query.filter(Escalation.status == status)
        if priority:
            query = query.filter(Escalation.priority == priority)
        if user_id:
            query = query.filter(Escalation.user_id == user_id)
        return query.order_by(Escalation.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def count_all_by_filters(
        db: Session, status: Optional[str] = None,
        priority: Optional[str] = None, user_id: Optional[int] = None
    ) -> int:
        """Count escalations with filters."""
        query = db.query(Escalation)
        if status:
            query = query.filter(Escalation.status == status)
        if priority:
            query = query.filter(Escalation.priority == priority)
        if user_id:
            query = query.filter(Escalation.user_id == user_id)
        return query.count()

    @staticmethod
    def count_pending(db: Session) -> int:
        """Count pending escalations."""
        return db.query(Escalation).filter(Escalation.status.in_(["open", "in_progress"])).count()

    @staticmethod
    def count_user_escalations(db: Session, user_id: int) -> int:
        """Count user escalations."""
        return db.query(Escalation).filter(Escalation.user_id == user_id).count()

    @staticmethod
    def get_open_escalations(db: Session, skip: int = 0, limit: int = 100) -> List[Escalation]:
        """Retrieve all open escalations."""
        return (
            db.query(Escalation)
            .filter(Escalation.status.in_(["open", "in_progress"]))
            .order_by(Escalation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_pending_escalations(db: Session, skip: int = 0, limit: int = 100) -> List[Escalation]:
        """Retrieve escalations with pending or open status."""
        return (
            db.query(Escalation)
            .filter(Escalation.status.in_(["open", "in_progress"]))
            .order_by(Escalation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_user_escalations(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Escalation]:
        """Retrieve escalations for a user."""
        return (
            db.query(Escalation)
            .filter(Escalation.user_id == user_id)
            .order_by(Escalation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_escalations_by_reviewer(db: Session, reviewer_id: int, skip: int = 0, limit: int = 100) -> List[Escalation]:
        """Retrieve escalations assigned to a reviewer."""
        return (
            db.query(Escalation)
            .filter(Escalation.assigned_reviewer == reviewer_id)
            .order_by(Escalation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create(db: Session, escalation: Escalation) -> Escalation:
        """Create a new escalation."""
        db.add(escalation)
        db.commit()
        db.refresh(escalation)
        return escalation

    @staticmethod
    def update(db: Session, db_escalation: Escalation, update_data: dict) -> Escalation:
        """Update an escalation with provided data."""
        for key, value in update_data.items():
            if hasattr(db_escalation, key):
                setattr(db_escalation, key, value)
        db.commit()
        db.refresh(db_escalation)
        return db_escalation

    @staticmethod
    def delete(db: Session, db_escalation: Escalation) -> bool:
        """Delete an escalation."""
        try:
            db.delete(db_escalation)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False

    @staticmethod
    def count_open(db: Session) -> int:
        """Count open escalations."""
        return db.query(Escalation).filter(Escalation.status.in_(["open", "in_progress"])).count()

    @staticmethod
    def get_stats(db: Session) -> dict:
        """Get escalation statistics."""
        total = db.query(Escalation).count()
        open = db.query(Escalation).filter(Escalation.status == "open").count()
        in_progress = db.query(Escalation).filter(Escalation.status == "in_progress").count()
        resolved = db.query(Escalation).filter(Escalation.status == "resolved").count()
        closed = db.query(Escalation).filter(Escalation.status == "closed").count()

        return {
            "total": total,
            "open": open,
            "in_progress": in_progress,
            "resolved": resolved,
            "closed": closed,
        }
