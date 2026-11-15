"""
Data access layer for search history-related operations.

Phase 3 — Search history repository.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import SearchHistory


class SearchHistoryRepository:
    """Repository for SearchHistory model access."""

    @staticmethod
    def get_by_id(db: Session, search_id: int) -> Optional[SearchHistory]:
        """Retrieve a search history entry by ID."""
        return db.query(SearchHistory).filter(SearchHistory.id == search_id).first()

    @staticmethod
    def get_user_search_history(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[SearchHistory]:
        """Retrieve search history for a user."""
        return (
            db.query(SearchHistory)
            .filter(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_last_n_queries(db: Session, user_id: int, n: int = 10) -> List[SearchHistory]:
        """Retrieve the last n queries for a user."""
        return (
            db.query(SearchHistory)
            .filter(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.timestamp.desc())
            .limit(n)
            .all()
        )

    @staticmethod
    def create(db: Session, search_history: SearchHistory) -> SearchHistory:
        """Create a new search history entry."""
        db.add(search_history)
        db.commit()
        db.refresh(search_history)
        return search_history

    @staticmethod
    def delete_by_user(db: Session, user_id: int) -> bool:
        """Delete all search history for a user."""
        try:
            db.query(SearchHistory).filter(SearchHistory.user_id == user_id).delete()
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False

    @staticmethod
    def get_top_queries(db: Session, n: int = 20) -> List[tuple]:
        """Get the top N most searched queries across all users."""
        return (
            db.query(SearchHistory.query, db.func.count(SearchHistory.id))
            .group_by(SearchHistory.query)
            .order_by(db.desc(db.func.count(SearchHistory.id)))
            .limit(n)
            .all()
        )
