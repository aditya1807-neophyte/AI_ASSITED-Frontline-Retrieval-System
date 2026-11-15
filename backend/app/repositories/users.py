"""
Data access layer for user-related operations.

Phase 3 — User repository implementing all CRUD operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import User
from app.core.database import SessionLocal


class UserRepository:
    """Repository for User model access."""

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Retrieve a user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_login_identifier(db: Session, login_identifier: str) -> Optional[User]:
        """Retrieve a user by login identifier."""
        return db.query(User).filter(User.login_identifier == login_identifier).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Retrieve all users with pagination."""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, user: User) -> User:
        """Create a new user."""
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, db_user: User, update_data: dict) -> User:
        """Update a user with provided data."""
        for key, value in update_data.items():
            if hasattr(db_user, key) and key != 'password_hash':
                setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete(db: Session, db_user: User) -> bool:
        """Delete a user."""
        try:
            db.delete(db_user)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
