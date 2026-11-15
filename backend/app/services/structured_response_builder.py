# -*- coding: utf-8 -*-
"""
Structured response builder for the RAG pipeline.

Builds structured, consistent responses that map to the frontend component.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class StructuredResponseBuilder:
    """
    Builds structured responses with required fields:
    - direct_answer
    - supporting_citations
    - important_conditions
    - limitations
    - conflicts
    - evidence_status
    - recommended_next_action
    """

    def __init__(self):
        pass

    def build(
        self,
        answer: str,
        citations: List[Dict[str, Any]],
        conditions: List[str],
        limitations: List[str],
        conflicts: List[str],
        evidence_status: str,
        next_action: str,
        query: str,
        is_semantic_available: bool,
    ) -> Dict[str, Any]:
        """
        Build a structured response.

        Returns a dictionary with all required fields.
        """
        return {
            "direct_answer": str(answer or ""),
            "supporting_citations": citations if isinstance(citations, list) else [],
            "important_conditions": conditions if isinstance(conditions, list) else [],
            "limitations": limitations if isinstance(limitations, list) else [],
            "conflicts": conflicts if isinstance(conflicts, list) else [],
            "evidence_status": str(evidence_status or "insufficient_evidence"),
            "recommended_next_action": str(next_action or "Review documents."),
            "query": str(query or ""),
            "is_semantic_available": bool(is_semantic_available),
        }

    def build_from_llm_output(
        self,
        llm_response: str,
        evidence: List[Dict[str, Any]],
        query: str,
    ) -> Dict[str, Any]:
        """
        Parse and build a response from raw LLM output.

        The LLM response should be a valid JSON string.
        """
        import json
        import re

        try:
            # Clean markdown code fences if present (e.g., ```json ... ```)
            cleaned = llm_response.strip()
            if "```" in cleaned:
                fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
                if fence_match:
                    cleaned = fence_match.group(1).strip()
            
            # If not pure JSON yet, try finding the outer {...}
            if not (cleaned.startswith("{") and cleaned.endswith("}")):
                brace_match = re.search(r"\{[\s\S]*\}", cleaned)
                if brace_match:
                    cleaned = brace_match.group(0).strip()

            # Parse JSON
            data = json.loads(cleaned)

            # Extract fields with defaults
            citations = data.get("citations", [])
            if isinstance(citations, list):
                citations = self._format_citations_for_display(citations, evidence)
            else:
                citations = []

            conditions = data.get("conditions") if isinstance(data.get("conditions"), list) else []
            limitations = data.get("limitations") if isinstance(data.get("limitations"), list) else []
            conflicts = data.get("conflicts") if isinstance(data.get("conflicts"), list) else []
            evidence_status = str(data.get("evidence_status") or "supported_by_available_evidence")
            next_action = str(data.get("next_action") or "Ask a follow-up question.")

            # Build final response
            return {
                "direct_answer": data.get("direct_answer", ""),
                "supporting_citations": citations,
                "important_conditions": conditions,
                "limitations": limitations,
                "conflicts": conflicts,
                "evidence_status": evidence_status,
                "recommended_next_action": next_action,
                "query": query,
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Fallback to a simple response
            return {
                "direct_answer": llm_response[:500] + "..." if len(llm_response) > 500 else llm_response,
                "supporting_citations": [],
                "important_conditions": [],
                "limitations": ["Failed to parse LLM response as structured JSON."],
                "conflicts": [],
                "evidence_status": "insufficient_evidence",
                "recommended_next_action": "Ask a follow-up question.",
                "query": query,
            }

    def parse(
        self,
        llm_response: str,
        evidence: Optional[List[Dict[str, Any]]] = None,
        query: str = "",
    ) -> Dict[str, Any]:
        """Alias for build_from_llm_output for pipeline compatibility."""
        return self.build_from_llm_output(llm_response, evidence or [], query)

    def _format_citations_for_display(self, citations: List, evidence: List[Dict]) -> List[Dict]:
        """
        Format citation references for display.
        """
        # Check if citations are already in the right format
        if citations and isinstance(citations[0], dict) and "citation" in citations[0]:
            return citations

        # Convert simple citation strings to display format
        formatted = []
        for i, cite in enumerate(citations, 1):
            formatted.append({
                "citation": cite,
                "title": f"Evidence {i}",
                "document_id": None,
                "chunk_sequence": None,
                "page_reference": "",
                "content_snippet": "",
                "is_valid": True,
            })

        return formatted
