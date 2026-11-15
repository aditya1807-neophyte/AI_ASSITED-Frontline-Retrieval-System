"""FastAPI router for Feedback endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackPublic
from app.services.feedback_service import FeedbackService
from app.core.auth import get_current_active_user
from app.models import User

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/", response_model=FeedbackPublic, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new feedback."""
    feedback = FeedbackService.create(
        db,
        user_id=current_user.id,
        answer_ref=feedback_data.answer_ref,
        document_ref=feedback_data.document_ref,
        feedback_type=feedback_data.feedback_type,
        explanation=feedback_data.explanation,
    )
    return feedback


@router.get("/user", response_model=List[FeedbackPublic])
def get_user_feedback(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all feedback records for the current user."""
    feedbacks = FeedbackService.get_by_user(db, current_user.id, skip, limit)
    return feedbacks


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a feedback record."""
    feedback = FeedbackService.get_by_id(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    if feedback.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    FeedbackService.delete(db, feedback_id)
