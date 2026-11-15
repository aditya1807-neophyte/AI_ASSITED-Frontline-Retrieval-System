"""Service layer for Feedback operations."""

from sqlalchemy.orm import Session
from app.models import Feedback
from app.repositories.feedback import create_feedback, get_feedback_by_id, get_feedbacks_by_user, delete_feedback


class FeedbackService:
    """Service for managing feedback operations."""
    
    @staticmethod
    def create(db: Session, user_id: int, answer_ref: str = None, document_ref: str = None, 
               feedback_type: str = "like", explanation: str = None) -> Feedback:
        """Create a new feedback record."""
        feedback_data = {
            "user_id": user_id,
            "answer_ref": answer_ref,
            "document_ref": document_ref,
            "feedback_type": feedback_type,
            "explanation": explanation,
        }
        return create_feedback(db, feedback_data)
    
    @staticmethod
    def get_by_id(db: Session, feedback_id: int) -> Feedback:
        """Get a feedback record by ID."""
        return get_feedback_by_id(db, feedback_id)
    
    @staticmethod
    def get_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
        """Get all feedback records for a user."""
        return get_feedbacks_by_user(db, user_id, skip, limit)
    
    @staticmethod
    def delete(db: Session, feedback_id: int) -> bool:
        """Delete a feedback record."""
        return delete_feedback(db, feedback_id)
