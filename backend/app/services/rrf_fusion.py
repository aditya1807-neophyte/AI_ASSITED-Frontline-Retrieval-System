# -*- coding: utf-8 -*-
"""
Reciprocal Rank Fusion (RRF) fusion manager.

Implements the RRF algorithm to combine ranked result lists from
multiple retrieval methods (keyword, semantic, etc.).

RRF formula: score = sum(1 / (k + rank_i)) for each retrieved list
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class RRFFusion:
    """
    Reciprocal Rank Fusion implementation.

    Combines ranked results from multiple retrieval methods into a single
    ranked list, without requiring normalized scores.
    """

    def __init__(self, k: int = 60):
        """
        Initialize the fusion manager.

        Args:
        - k: RRF constant (default 60). Higher values reduce the impact
          of rank differences.
        """
        self.k = k

    def fuse(
        self,
        result_lists: List[List[Dict[str, Any]]],
        k: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Fuse multiple ranked result lists.

        Args:
        - result_lists: List of ranked result lists. Each list should contain
          dictionaries with "document_id" or "title" as the identifier key.
        - k: RRF constant (overrides constructor value if provided).

        Returns:
        - fused results sorted by RRF score (descending)
        """
        if k is None:
            k = self.k

        # Build ranks for each method
        id_ranks = {}
        item_by_id = {}

        for results in result_lists:
            for rank, item in enumerate(results, 1):
                # Extract document ID
                doc_id = item.get("document_id") or item.get("title") or str(rank)

                if doc_id not in id_ranks:
                    id_ranks[doc_id] = []
                id_ranks[doc_id].append(rank)

                # Store the best item representation
                if doc_id not in item_by_id:
                    item_by_id[doc_id] = item

        # Calculate RRF scores
        fused = []
        for doc_id, ranks in id_ranks.items():
            # RRF score: sum of 1/(k + rank) for each list
            score = sum(1.0 / (k + r) for r in ranks)

            best_item = item_by_id[doc_id]
            best_item["rrf_score"] = round(score, 6)
            fused.append(best_item)

        # Sort by RRF score descending
        fused.sort(key=lambda x: x.get("rrf_score", 0), reverse=True)
        return fused

    def fuse_with_scores(
        self,
        result_lists: List[List[Dict[str, Any]]],
        k: int = None,
    ) -> Dict[str, Any]:
        """
        Fuse with additional metadata about which method contributed what.

        Returns:
        - dict with "results" (fused list) and "metadata" (score breakdown)
        """
        if k is None:
            k = self.k

        id_ranks = {}
        item_by_id = {}
        score_breakdown = {}

        for results in result_lists:
            for rank, item in enumerate(results, 1):
                doc_id = item.get("document_id") or item.get("title") or str(rank)
                method_name = item.get("search_type", "unknown")

                if doc_id not in id_ranks:
                    id_ranks[doc_id] = {}
                    score_breakdown[doc_id] = {}
                    item_by_id[doc_id] = item

                if method_name not in id_ranks[doc_id]:
                    id_ranks[doc_id][method_name] = []
                    score_breakdown[doc_id][method_name] = 0.0

                id_ranks[doc_id][method_name].append(rank)
                score_breakdown[doc_id][method_name] += 1.0 / (k + rank)

        fused = []
        metadata = {}

        for doc_id, ranks in id_ranks.items():
            total_score = 0.0
            for method, method_ranks in ranks.items():
                method_score = sum(1.0 / (k + r) for r in method_ranks)
                total_score += method_score
                score_breakdown[doc_id][method] = round(method_score, 6)

            best_item = item_by_id[doc_id]
            best_item["rrf_score"] = round(total_score, 6)
            fused.append(best_item)

        fused.sort(key=lambda x: x.get("rrf_score", 0), reverse=True)
        metadata["results"] = fused
        metadata["scores"] = score_breakdown
        metadata["k"] = k

        return metadata


# Convenience function
def reciprocal_rank_fusion(
    result_lists: List[List[Dict[str, Any]]],
    k: int = 60,
) -> List[Dict[str, Any]]:
    """
    Convenience function for RRF fusion.

    Args:
    - result_lists: list of ranked result lists
    - k: RRF constant

    Returns:
    - fused results sorted by RRF score
    """
    fusion = RRFFusion(k=k)
    return fusion.fuse(result_lists, k=k)
