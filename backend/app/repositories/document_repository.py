"""Data access layer for document-related operations.

Phase 1 placeholder. Added in Phase 2 with full repository implementations.
"""

from typing import Any, List, Optional


class DocumentRepository:
    """Repository for Document model access."""

    def get_all(self, db: Any, skip: int = 0, limit: int = 100) -> List[Any]:
        """Retrieve all documents.

        Not implemented in Phase 1 — placeholder.
        """
        raise NotImplementedError('DocumentRepository not implemented in Phase 1.')

    def get_by_id(self, db: Any, document_id: int) -> Optional[Any]:
        """Retrieve a document by ID.

        Not implemented in Phase 1 — placeholder.
        """
        raise NotImplementedError('DocumentRepository not implemented in Phase 1.')
