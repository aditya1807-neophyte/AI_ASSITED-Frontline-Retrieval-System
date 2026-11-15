"""
Business logic and orchestration layer for search history operations.

Phase 3 — Search history service.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.search_history import SearchHistoryRepository
from app.schemas.search_history import SearchHistoryCreate
from app.schemas.search_history import SearchHistoryPublic
from app.models import SearchHistory


class SearchHistoryService:
    """Service layer for search history operations."""

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> tuple:
        """Retrieve all search history entries with pagination."""
        items = SearchHistoryRepository.get_all(db, skip, limit)
        total = SearchHistoryRepository.count_all(db)
        return items, total

    @staticmethod
    def get_by_id(db: Session, search_id: int) -> Optional[SearchHistory]:
        """Retrieve a search history entry by ID."""
        return SearchHistoryRepository.get_by_id(db, search_id)

    @staticmethod
    def get_user_search_history(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> tuple:
        """Retrieve search history for a user."""
        items = SearchHistoryRepository.get_user_search_history(db, user_id, skip, limit)
        total = SearchHistoryRepository.get_user_count(db, user_id)
        return items, total

    @staticmethod
    def get_last_n_queries(db: Session, user_id: int, n: int = 10) -> List[SearchHistory]:
        """Retrieve the last n queries for a user."""
        return SearchHistoryRepository.get_last_n_queries(db, user_id, n)

    @staticmethod
    def create(db: Session, data: SearchHistoryCreate) -> SearchHistory:
        """Create a new search history entry."""
        return SearchHistoryRepository.create(db, data)

    @staticmethod
    def record(
        db: Session, user_id: int, query: str, ip_address: Optional[str] = None
    ) -> SearchHistory:
        """Record a search query in history."""
        entry = SearchHistory(
            user_id=user_id,
            query=query,
            ip_address=ip_address,
            timestamp=datetime.utcnow(),
        )
        return SearchHistoryRepository.create(db, entry)

    @staticmethod
    def delete_user_history(db: Session, user_id: int) -> bool:
        """Delete all search history for a user."""
        return SearchHistoryRepository.delete_by_user(db, user_id)

    @staticmethod
    def get_top_queries(db: Session, n: int = 20) -> List[tuple]:
        """Get top N most searched queries across all users."""
        return SearchHistoryRepository.get_top_queries(db, n)

    @staticmethod
    def count_all(db: Session) -> int:
        """Count all search history entries."""
        return SearchHistoryRepository.count_all(db)
