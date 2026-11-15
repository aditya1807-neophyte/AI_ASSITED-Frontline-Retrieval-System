"""
Business logic and orchestration layer for saved item operations.

Phase 3 — Saved item service.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.saved_items import SavedItemRepository
from app.schemas.saved_items import SavedItemCreate
from app.schemas.saved_items import SavedItemPublic
from app.models import SavedItem


class SavedItemService:
    """Service layer for saved item operations."""

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> tuple:
        """Retrieve all saved items with pagination."""
        items = SavedItemRepository.get_all(db, skip, limit)
        total = SavedItemRepository.count_all(db)
        return items, total

    @staticmethod
    def get_by_id(db: Session, saved_item_id: int) -> Optional[SavedItem]:
        """Retrieve a saved item by ID."""
        return SavedItemRepository.get_by_id(db, saved_item_id)

    @staticmethod
    def get_user_saved_items(
        db: Session, user_id: int, item_type: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> tuple:
        """Retrieve saved items for a user."""
        items = SavedItemRepository.get_user_saved_items(db, user_id, item_type, skip, limit)
        total = SavedItemRepository.get_user_saved_count(db, user_id, item_type)
        return items, total

    @staticmethod
    def get_user_saved_count(db: Session, user_id: int, item_type: Optional[str] = None) -> int:
        """Get saved items count for a user."""
        return SavedItemRepository.get_user_saved_count(db, user_id, item_type)

    @staticmethod
    def create(db: Session, data: SavedItemCreate) -> SavedItem:
        """Create a new saved item."""
        return SavedItemRepository.create(db, data)

    @staticmethod
    def delete(db: Session, saved_item_id: int) -> bool:
        """Delete a saved item."""
        db_item = SavedItemRepository.get_by_id(db, saved_item_id)
        if not db_item:
            return False
        return SavedItemRepository.delete(db, db_item)
