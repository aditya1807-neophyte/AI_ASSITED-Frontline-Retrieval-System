# -*- coding: utf-8 -*-
"""
Evidence status calculator.

Maps evidence sufficiency results to human-readable status strings.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class EvidenceStatusCalculator:
    """
    Calculates the evidence status and provides human-readable explanations.

    Statuses:
    - supported_by_available_evidence
    - partially_supported
    - insufficient_evidence
    - conflicting_sources
    - ai_unavailable
    """

    def __init__(self):
        self.status_descriptions = {
            "supported_by_available_evidence": "The available evidence supports this answer.",
            "partially_supported": "Some evidence supports this answer, but more information is needed for full certainty.",
            "insufficient_evidence": "The repository does not contain sufficient evidence to adequately answer this question.",
            "conflicting_sources": "The retrieved sources contain conflicting information that requires human review.",
            "ai_unavailable": "AI generation is not available. Evidence is provided for review.",
        }

    def calculate(self, sufficiency: Dict[str, Any], evidence: list) -> Dict[str, Any]:
        """
        Calculate the evidence status with explanation.

        Returns:
        - status: the evidence status string
        - description: human-readable explanation
        - is_sufficient: whether evidence is sufficient
        - missing_aspects: what is missing (if any)
        """
        # Determine base status from sufficiency
        is_sufficient = sufficiency.get("is_sufficient", False)
        confidence = sufficiency.get("confidence_score", 0)

        if not is_sufficient:
            status = "insufficient_evidence"
        elif confidence >= 0.7:
            status = "supported_by_available_evidence"
        elif confidence >= 0.4:
            status = "partially_supported"
        else:
            status = "insufficient_evidence"

        # Override with conflict detection
        missing_aspects = sufficiency.get("missing_aspects", [])
        if any("conflict" in aspect.lower() for aspect in missing_aspects):
            status = "conflicting_sources"

        # Check for conflicts in evidence
        if self._has_conflict_indicators(evidence):
            status = "conflicting_sources"

        return {
            "status": status,
            "description": self.status_descriptions.get(status, "Evidence status determined."),
            "is_sufficient": is_sufficient,
            "missing_aspects": missing_aspects,
        }

    def _has_conflict_indicators(self, evidence: list) -> bool:
        """Check if evidence contains conflict indicators."""
        if not evidence:
            return False

        conflict_keywords = [
            "however", "but", "contrary", "opposing", "incompatible", "dispute",
            "conflict", "disagreement", "differ", "differs", "unlike", "contrast"
        ]

        content_lower = " ".join([e.get("content", "").lower() for e in evidence])
        return any(word in content_lower for word in conflict_keywords)
