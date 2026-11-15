"""
FastAPI routers for answers API endpoints.

Phase 3 — Answer API routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.answers import AnswerCreate, AnswerPublic, AnswerUpdate
from app.services.answers_service import AnswerService
from app.core.auth import get_current_active_user
from app.models import User
from app.schemas.pagination import Page, PageWithMeta

router = APIRouter(prefix="/answers", tags=["Answers"])


@router.get("/", response_model=PageWithMeta[AnswerPublic])
def list_answers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List answers for the current user."""
    items, total = AnswerService.get_user_answers(db, current_user.id, skip, limit)
    return {
        "items": [AnswerPublic.from_orm(item) for item in items],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "pages": (total + limit - 1) // limit,
        "has_next": skip + limit < total,
        "has_prev": skip > 0,
    }


@router.get("/{answer_id}", response_model=AnswerPublic)
def get_answer(answer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get an answer by ID."""
    answer = AnswerService.get_by_id(db, answer_id)
    if not answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found")
    if answer.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your answer")
    return AnswerPublic.from_orm(answer)


@router.post("/", response_model=AnswerPublic, status_code=status.HTTP_201_CREATED)
def create_answer(
    answer_data: AnswerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Create a new answer."""
    answer = AnswerService.create(db, answer_data)
    return AnswerPublic.from_orm(answer)


@router.put("/{answer_id}", response_model=AnswerPublic)
def update_answer(
    answer_id: int, answer_data: AnswerUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Update an answer."""
    answer = AnswerService.update(db, answer_id, answer_data)
    if not answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found")
    if answer.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your answer")
    return AnswerPublic.from_orm(answer)


@router.delete("/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_answer(answer_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Delete an answer."""
    answer = AnswerService.get_by_id(db, answer_id)
    if not answer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Answer not found")
    if answer.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your answer")
    AnswerService.delete(db, answer_id)
    return None
