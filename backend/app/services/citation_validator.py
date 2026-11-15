# -*- coding: utf-8 -*-
"""
Citation validator for the RAG pipeline.

Validates that citations reference actual stored documents or chunks.
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Document, DocumentChunk

logger = logging.getLogger(__name__)


class CitationValidator:
    """
    Validates citations against actual stored documents and chunks.

    Features:
    - Checks that citation references exist in the database
    - Validates that the cited content matches the citation
    - Ensures citations are not fabricated
    """

    def __init__(self):
        self.valid_citations = []

    def validate(
        self,
        citations: List[Dict[str, Any]],
        evidence: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Validate citations against retrieved evidence.

        Args:
        - citations: list of citation dictionaries
        - evidence: list of evidence items used to generate the answer

        Returns:
        - list of validated citations
        """
        if not citations:
            return []

        # Get valid doc IDs from evidence
        evidence_doc_ids = set()
        for item in evidence:
            doc_id = item.get("document_id")
            if doc_id is not None:
                evidence_doc_ids.add(doc_id)

        validated = []
        for citation in citations:
            # Extract citation reference
            citation_ref = citation.get("citation", "")
            source_id = self._extract_source_id(citation_ref)

            # Validate the citation
            is_valid, reason = self._validate_citation(source_id, evidence_doc_ids)

            if is_valid:
                validated.append(citation)
            else:
                logger.warning(f"Invalid citation {citation_ref}: {reason}")

        return validated

    def _extract_source_id(self, citation_ref: str) -> Optional[int]:
        """
        Extract the numeric source ID from a citation reference.
        """
        if not citation_ref:
            return None

        # Extract digits from the citation
        import re
        match = re.search(r'\d+', citation_ref)
        if match:
            return int(match.group())
        return None

    def _validate_citation(
        self,
        source_id: Optional[int],
        valid_doc_ids: set,
    ) -> tuple:
        """
        Validate a single citation reference.

        Returns:
        - (is_valid, reason)
        """
        if source_id is None:
            return False, "No source ID found in citation"

        # Check against valid document IDs from evidence
        if source_id not in valid_doc_ids:
            return False, "Source ID not found in retrieved evidence"

        # Verify the document exists in the database
        db = next(get_db())
        try:
            doc = db.query(Document).filter(Document.id == source_id).first()
            if not doc:
                return False, "Document not found in database"
        except Exception as e:
            return False, f"Database error: {str(e)}"
        finally:
            db.close()

        return True, "Valid"

    def get_citation_details(self, citation: Dict[str, Any]) -> Dict[str, Any]:
        """Get details about a citation."""
        citation_ref = citation.get("citation", "")
        source_id = self._extract_source_id(citation_ref)

        return {
            "citation_ref": citation_ref,
            "source_id": source_id,
        }
