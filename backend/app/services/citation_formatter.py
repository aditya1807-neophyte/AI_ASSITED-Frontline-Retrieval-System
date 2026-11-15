# -*- coding: utf-8 -*-
"""
Citation formatter for the RAG pipeline.

Formats citations for display in the interface.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class CitationFormatter:
    """
    Formats evidence items into citation objects for the frontend.

    Creates citations that reference actual stored documents and chunks
    with page/section information.
    """

    def __init__(self):
        pass

    def format(
        self,
        evidence: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Format evidence into citation objects.

        Args:
        - evidence: list of evidence items

        Returns:
        - list of citation objects with:
          - citation: citation reference string
          - title: document title
          - document_id: document ID
          - chunk_sequence: chunk sequence number
          - page_reference: page reference if available
          - content_snippet: preview of the content
          - is_valid: whether the citation is valid
        """
        citations = []

        for item in evidence:
            citation_ref = self._format_citation_ref(item)
            doc_id = item.get("document_id")

            citations.append({
                "citation": citation_ref,
                "title": item.get("title", ""),
                "document_id": doc_id,
                "chunk_sequence": item.get("chunk_sequence"),
                "page_reference": item.get("page_reference", ""),
                "content_snippet": self._get_content_snippet(item),
                "is_valid": True,
            })

        return citations

    def _format_citation_ref(self, item: Dict[str, Any]) -> str:
        """
        Create a citation reference string.
        """
        doc_id = item.get("document_id", "unknown")
        page = item.get("page_reference", "")
        chunk_seq = item.get("chunk_sequence", "")

        parts = [f"doc_{doc_id}"]

        if page:
            parts.append(f"p.{page}")

        if chunk_seq:
            parts.append(f"chunk_{chunk_seq}")

        return " ".join(parts)

    def _get_content_snippet(self, item: Dict[str, Any]) -> str:
        """Get a short content snippet."""
        content = item.get("content", "")
        if not content:
            return ""

        if len(content) > 200:
            return content[:200] + "..."
        return content

    def format_with_citation_ids(self, evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format evidence with citation IDs for use in LLM prompts.
        """
        formatted = []

        for idx, item in enumerate(evidence, 1):
            formatted.append({
                "citation_id": f"source_{idx}",
                "citation_ref": f"[source_{idx}]",
                "content": item.get("content", ""),
                "title": item.get("title", ""),
                "document_id": item.get("document_id"),
                "page_reference": item.get("page_reference", ""),
            })

        return formatted
