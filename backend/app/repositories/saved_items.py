"""
Data access layer for saved-item-related operations.

Phase 3 — Saved item repository.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import SavedItem


class SavedItemRepository:
    """Repository for SavedItem model access."""

    @staticmethod
    def get_by_id(db: Session, saved_item_id: int) -> Optional[SavedItem]:
        """Retrieve a saved item by ID."""
        return db.query(SavedItem).filter(SavedItem.id == saved_item_id).first()

    @staticmethod
    def get_by_user_and_reference(
        db: Session, user_id: int, item_type: str, item_reference: str
    ) -> Optional[SavedItem]:
        """Retrieve a saved item by user and reference."""
        return (
            db.query(SavedItem)
            .filter(
                SavedItem.user_id == user_id,
                SavedItem.item_type == item_type,
                SavedItem.item_reference == item_reference,
            )
            .first()
        )

    @staticmethod
    def get_user_saved_items(
        db: Session, user_id: int, item_type: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> List[SavedItem]:
        """Retrieve saved items for a user."""
        query = db.query(SavedItem).filter(SavedItem.user_id == user_id)
        if item_type:
            query = query.filter(SavedItem.item_type == item_type)
        return query.order_by(SavedItem.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_saved_count(db: Session, user_id: int, item_type: Optional[str] = None) -> int:
        """Count saved items for a user."""
        query = db.query(SavedItem).filter(SavedItem.user_id == user_id)
        if item_type:
            query = query.filter(SavedItem.item_type == item_type)
        return query.count()

    @staticmethod
    def create(db: Session, saved_item: SavedItem) -> SavedItem:
        """Create a new saved item."""
        db.add(saved_item)
        db.commit()
        db.refresh(saved_item)
        return saved_item

    @staticmethod
    def delete(db: Session, db_saved_item: SavedItem) -> bool:
        """Delete a saved item."""
        try:
            db.delete(db_saved_item)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False


    @staticmethod
    def delete_by_document_id(db: Session, document_id: int) -> int:
        """Delete all saved items for a document."""
        from app.models import SavedItem
        result = db.query(SavedItem).filter(SavedItem.document_id == document_id).delete()
        db.commit()
        return result
