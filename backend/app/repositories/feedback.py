"""Repository for Feedback model operations."""

from sqlalchemy.orm import Session
from app.models import Feedback


def create_feedback(db: Session, feedback_data: dict) -> Feedback:
    """Create a new feedback record."""
    feedback = Feedback(**feedback_data)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def get_feedback_by_id(db: Session, feedback_id: int) -> Feedback:
    """Get a feedback record by ID."""
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()


def get_feedbacks_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all feedback records for a user."""
    return db.query(Feedback).filter(Feedback.user_id == user_id).offset(skip).limit(limit).all()


def delete_feedback(db: Session, feedback_id: int) -> bool:
    """Delete a feedback record."""
    feedback = get_feedback_by_id(db, feedback_id)
    if feedback:
        db.delete(feedback)
        db.commit()
        return True
    return False
