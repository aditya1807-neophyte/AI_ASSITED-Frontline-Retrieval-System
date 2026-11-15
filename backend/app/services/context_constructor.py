# -*- coding: utf-8 -*-
"""
Context constructor for the RAG pipeline.

Constructs the context window passed to the LLM.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ContextConstructor:
    """
    Constructs the context window from selected evidence.

    Features:
    - Formats evidence into a coherent context
    - Prioritizes the most relevant passages
    - Adds section headers and structure
    - Preserves source references
    """

    def __init__(self):
        self.max_context_length = 3000  # characters

    def construct(
        self,
        evidence: List[Dict[str, Any]],
        query: str,
    ) -> str:
        """
        Construct the context string from evidence.

        Args:
        - evidence: list of evidence items
        - query: original query (for context introduction)

        Returns:
        - formatted context string
        """
        if not evidence:
            return "No evidence was retrieved for this query."

        # Limit evidence to top passages
        top_evidence = evidence[:5]

        # Format the context
        context_parts = []
        context_parts.append(f"Query: {query}")
        context_parts.append("")

        for i, item in enumerate(top_evidence, 1):
            content = item.get("content", "")
            title = item.get("title", "")
            page = item.get("page_reference", "")
            chunk_seq = item.get("chunk_sequence", "")

            # Add source header
            source_ref = self._get_source_ref(item)
            if title:
                context_parts.append(f"--- Source: {title} ---")
            elif source_ref:
                context_parts.append(f"--- {source_ref} ---")

            # Add chunk info
            if chunk_seq:
                context_parts.append(f"(Chunk {chunk_seq})")
            if page:
                context_parts.append(f"(Page: {page})")

            # Add content
            if content:
                # Clean and truncate
                content = content.strip()
                if len(content) > 500:
                    content = content[:500] + "..."
                context_parts.append(content)
            else:
                context_parts.append("(Empty content)")

            context_parts.append("")

        # Truncate if too long
        full_context = "\n".join(context_parts)
        if len(full_context) > self.max_context_length:
            full_context = full_context[:self.max_context_length] + "\n... (context truncated)"

        return full_context

    def _get_source_ref(self, item: Dict[str, Any]) -> str:
        """Get a reusable source reference string."""
        title = item.get("title", "")
        doc_id = item.get("document_id", "")
        page = item.get("page_reference", "")

        parts = []
        if title:
            parts.append(title)
        if doc_id:
            parts.append(f"doc_{doc_id}")
        if page:
            parts.append(f"p.{page}")

        return " | ".join(parts) if parts else f"source_{doc_id}"

    def construct_for_multiple_queries(
        self,
        evidence: List[Dict[str, Any]],
        queries: List[str],
    ) -> str:
        """
        Construct context for multiple queries.

        Useful for batch processing.
        """
        context_parts = []

        for i, query in enumerate(queries):
            context_parts.append(f"Query {i+1}: {query}")
            context_parts.append("")

            # Add top evidence for this query
            top_evidence = evidence[:3]
            for item in top_evidence:
                content = item.get("content", "").strip()
                if content:
                    context_parts.append(f"  {content[:200]}...")

            context_parts.append("")

        return "\n".join(context_parts)
