"""
Data access layer for saved answer-related operations.

Phase 3 — Saved answer repository.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import SavedAnswer


class SavedAnswerRepository:
    """Repository for SavedAnswer model access."""

    @staticmethod
    def get_by_id(db: Session, saved_answer_id: int) -> Optional[SavedAnswer]:
        """Retrieve a saved answer by ID."""
        return db.query(SavedAnswer).filter(SavedAnswer.id == saved_answer_id).first()

    @staticmethod
    def get_user_saved_answers(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[SavedAnswer]:
        """Retrieve saved answers for a user."""
        return (
            db.query(SavedAnswer)
            .filter(SavedAnswer.user_id == user_id)
            .order_by(SavedAnswer.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_answer_id(db: Session, answer_id: int) -> Optional[SavedAnswer]:
        """Retrieve a saved answer by answer ID."""
        return db.query(SavedAnswer).filter(SavedAnswer.answer_id == answer_id).first()

    @staticmethod
    def create(db: Session, saved_answer: SavedAnswer) -> SavedAnswer:
        """Create a new saved answer."""
        db.add(saved_answer)
        db.commit()
        db.refresh(saved_answer)
        return saved_answer

    @staticmethod
    def delete(db: Session, db_saved_answer: SavedAnswer) -> bool:
        """Delete a saved answer."""
        try:
            db.delete(db_saved_answer)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False


    @staticmethod
    def delete_by_document_id(db: Session, document_id: int) -> int:
        """Delete all saved answers for a document."""
        from app.models import SavedAnswer
        result = db.query(SavedAnswer).filter(SavedAnswer.document_id == document_id).delete()
        db.commit()
        return result
