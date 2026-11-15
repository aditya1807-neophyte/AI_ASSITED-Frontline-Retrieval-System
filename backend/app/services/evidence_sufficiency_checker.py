# -*- coding: utf-8 -*-
"""
Evidence sufficiency checker for the RAG pipeline.

Determines if the retrieved evidence is sufficient to answer the query.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class EvidenceSufficiencyChecker:
    """
    Checks whether evidence is sufficient to answer a question.

    Criteria:
    - Minimum number of relevant passages
    - Relevance of passages to the query
    - Coverage of key aspects
    - Caption of relevance (above threshold)

    Returns:
    - is_sufficient: whether evidence is sufficient
    - confidence_score: 0-1 (not a factual confidence, but relevance score)
    - missing_aspects: what information is missing
    """

    def __init__(self):
        self.min_passages = 1  # At least 1 relevant passage
        self.min_relevance_score = 0.1  # Minimum relevance threshold
        self.max_passages = 10  # Cap on passages to consider

    def check(self, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check evidence sufficiency.

        Returns:
        - is_sufficient: bool
        - confidence_score: float (0-1, relevance-based)
        - missing_aspects: list of missing information
        - total_passages: number of passages
        - avg_relevance: average relevance score
        """
        if not evidence:
            return {
                "is_sufficient": False,
                "confidence_score": 0.0,
                "missing_aspects": ["No evidence retrieved"],
                "total_passages": 0,
                "avg_relevance": 0.0,
            }

        # Limit passages
        limited = evidence[:self.max_passages]

        # Calculate average relevance
        relevance_scores = [r.get("bm25_score", 0) + r.get("embedding_score", 0) for r in limited]
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0

        # Check minimum passages
        has_enough_passages = len(limited) >= self.min_passages

        # Check average relevance
        has_relevance = avg_relevance >= self.min_relevance_score

        is_sufficient = has_enough_passages and has_relevance

        # Determine missing aspects
        missing_aspects = self._identify_missing_aspects(evidence, limited)

        return {
            "is_sufficient": is_sufficient,
            "confidence_score": round(avg_relevance, 4),
            "missing_aspects": missing_aspects,
            "total_passages": len(limited),
            "avg_relevance": round(avg_relevance, 4),
        }

    def _identify_missing_aspects(
        self,
        all_evidence: List[Dict[str, Any]],
        selected: List[Dict[str, Any]],
    ) -> List[str]:
        """Identify what information might be missing."""
        missing = []

        if not all_evidence:
            missing.append("No relevant evidence retrieved")
            return missing

        if len(selected) < len(all_evidence):
            missing.append("Limited evidence coverage")

        if len(selected) < self.min_passages:
            missing.append("Insufficient evidence passages")

        # Check content diversity
        contents = [e.get("content", "") for e in selected]
        if contents:
            # Simple check: is the evidence too similar?
            first_content = contents[0].lower()
            similar_count = sum(1 for c in contents if c and first_content[:50] in c.lower())
            if similar_count >= len(contents) * 0.8:
                missing.append("Evidence is too similar - limited perspective")

        return missing


class EvidenceStatusCalculator:
    """
    Calculates the evidence status for a query.

    Statuses:
    - "supported_by_available_evidence"
    - "partially_supported"
    - "insufficient_evidence"
    - "conflicting_sources"
    - "ai_unavailable"
    """

    def calculate(
        self,
        sufficiency: Dict[str, Any],
        evidence: List[Dict[str, Any]],
    ) -> str:
        """
        Calculate the evidence status.

        Returns:
        - status string
        """
        # Check if evidence has conflict indicators
        has_conflicts = self._detect_conflicts(evidence)

        if has_conflicts:
            return "conflicting_sources"

        if not sufficiency.get("is_sufficient"):
            return "insufficient_evidence"

        if sufficiency.get("confidence_score", 0) >= 0.7:
            return "supported_by_available_evidence"

        return "partially_supported"

    def _detect_conflicts(self, evidence: List[Dict[str, Any]]) -> bool:
        """
        Detect potential conflicts between evidence sources.
        """
        if len(evidence) < 2:
            return False

        content_list = [e.get("content", "").lower() for e in evidence]

        # Check for contradiction indicators
        conflict_words = ["however", "but", "contrary", "opposing", "incompatible", "dispute"]

        for i, content in enumerate(content_list):
            for j, other in enumerate(content_list):
                if i >= j:
                    continue
                # Simple heuristic: check if both contain different claims
                if any(w in content for w in conflict_words) and any(w in other for w in conflict_words):
                    # Check if they seem to contradict each other
                    # (simplified: just return True if there are conflict indicators)
                    return True

        return False
