# -*- coding: utf-8 -*-
"""
Evidence selector for the RAG pipeline.

Selects and ranks evidence pieces from retrieved chunks.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class EvidenceSelector:
    """
    Selects the most relevant evidence from retrieved chunks.

    Features:
    - Ranks evidence by relevance score
    - Filters out low-quality or redundant content
    - Returns top evidence for context construction
    """

    def __init__(self):
        self.min_score = 0.0
        self.max_score = 1.0

    def select(
        self,
        results: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Select and rank evidence from results.

        Args:
        - results: list of retrieved results
        - top_k: maximum number of evidence pieces to return

        Returns:
        - list of selected evidence, sorted by relevance
        """
        if isinstance(results, dict):
            results = results.get("results", [])

        if not results:
            return []

        # Sort by combined score (BM25 + embedding)
        sorted_results = sorted(
            results,
            key=lambda r: r.get("bm25_score", 0) + r.get("embedding_score", 0),
            reverse=True,
        )

        # Apply scoring threshold
        threshold = self.max_score * 0.3  # Keep top 30% of best scores
        filtered = [r for r in sorted_results if r.get("bm25_score", 0) >= threshold]

        # Limit to top_k
        selected = filtered[:top_k]

        # Add quality markers
        for item in selected:
            self._assess_quality(item)

        return selected

    def _assess_quality(self, item: Dict[str, Any]):
        """Add quality assessments to an evidence item."""
        score = item.get("bm25_score", 0) + item.get("embedding_score", 0)
        item["quality_score"] = round(min(score / 2.0, 1.0), 4)

        # Check for source type
        title = item.get("title", "").lower()
        if "policy" in title or "procedure" in title:
            item["is_procedural"] = True
        else:
            item["is_procedural"] = False

        # Check for conflict indicators
        content = item.get("content", "").lower()
        if any(word in content for word in ["however", "but", "although", "despite", "on the other hand", "conflicting"]):
            item["has_conflict_indicator"] = True
        else:
            item["has_conflict_indicator"] = False

    def rank_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank results by relevance."""
        return sorted(results, key=lambda r: r.get("bm25_score", 0) + r.get("embedding_score", 0), reverse=True)

    def deduplicate(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate evidence (same document, same page, different chunks).
        """
        seen = set()
        deduplicated = []

        for item in results:
            doc_id = item.get("document_id", "")
            page = item.get("page_reference", "")
            key = (doc_id, page)
            if key not in seen:
                seen.add(key)
                deduplicated.append(item)

        return deduplicated
