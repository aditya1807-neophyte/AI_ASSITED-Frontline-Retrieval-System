"""
Data access layer for answer-related operations.

Phase 3 — Answer repository.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import Answer


class AnswerRepository:
    """Repository for Answer model access."""

    @staticmethod
    def get_by_id(db: Session, answer_id: int) -> Optional[Answer]:
        """Retrieve an answer by ID."""
        return db.query(Answer).filter(Answer.id == answer_id).first()

    @staticmethod
    def get_user_answers(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Answer]:
        """Retrieve answers for a user."""
        return (
            db.query(Answer)
            .filter(Answer.user_id == user_id)
            .order_by(Answer.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create(db: Session, answer: Answer) -> Answer:
        """Create a new answer."""
        db.add(answer)
        db.commit()
        db.refresh(answer)
        return answer

    @staticmethod
    def delete(db: Session, db_answer: Answer) -> bool:
        """Delete an answer."""
        try:
            db.delete(db_answer)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
