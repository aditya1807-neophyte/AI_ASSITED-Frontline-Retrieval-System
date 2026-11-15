# -*- coding: utf-8 -*-
"""
Result ranker for the RAG pipeline.

Ranks retrieved results based on relevance scores.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ResultRanker:
    """Rank retrieved results."""

    def rank(self, results: Any, query: str) -> Dict[str, Any]:
        """
        Rank results based on combined scores.

        Returns:
        - results: list of ranked results
        - query: the query
        """
        if isinstance(results, dict):
            results_list = results.get("results", [])
        elif isinstance(results, list):
            results_list = results
        else:
            results_list = []

        if not results_list:
            return {"results": [], "query": query}

        # Sort by combined score (BM25 + embedding)
        ranked = sorted(
            results_list,
            key=lambda r: (r.get("bm25_score", 0) if isinstance(r, dict) else 0) + (r.get("embedding_score", 0) if isinstance(r, dict) else 0),
            reverse=True,
        )

        return {
            "results": ranked,
            "query": query,
        }
