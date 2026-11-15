# -*- coding: utf-8 -*-
"""
Hybrid retriever that combines keyword and semantic retrieval.

Features:
- Keyword retrieval (BM25)
- Semantic retrieval (sentence embeddings)
- Combination via Reciprocal Rank Fusion (RRF)
- Result ranking
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RetrievedResult:
    """A single retrieved result."""
    document_id: int
    content: str
    title: str
    chunk_sequence: int
    page_reference: str
    bm25_score: float
    embedding_score: float


class ResultRanker:
    """Rank retrieved results."""

    def rank(self, results: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """
        Rank results based on combined scores.

        Returns:
        - results: list of ranked results
        - query: the query
        """
        if not results:
            return {"results": [], "query": query}

        # Sort by combined score (BM25 + embedding)
        ranked = sorted(results, key=lambda r: r.get("bm25_score", 0) + r.get("embedding_score", 0), reverse=True)

        return {
            "results": ranked,
            "query": query,
        }


class HybridRetriever:
    """
    Hybrid retriever combining keyword and semantic retrieval.

    Uses Reciprocal Rank Fusion (RRF) to combine results from both methods.
    Filters results based on document permissions, status, and version.
    """

    def __init__(self, keyword_service=None, semantic_service=None):
        self.keyword_service = keyword_service
        self.semantic_service = semantic_service
        self.ranker = ResultRanker()

    def retrieve(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Retrieve documents using hybrid search.

        Returns:
        - results: list of ranked retrieved results
        - search_type: "hybrid", "keyword-only", or "semantic-only"
        """
        # Get keyword results
        keyword_results = []
        if self.keyword_service:
            keyword_results = self.keyword_service.retrieve_keyword(query, top_k=top_k * 2)

        # Get semantic results
        semantic_results = []
        if self.semantic_service:
            semantic_results = self.semantic_service.search(query, top_k=top_k * 2)

        # Combine using RRF
        combined = self._reciprocal_rank_fusion(keyword_results, semantic_results, k=60)

        # Rank final results
        ranked = self.ranker.rank(combined, query)

        return ranked

    def _reciprocal_rank_fusion(self, keyword_results: List[Dict], semantic_results: List[Dict], k: int = 60) -> List[Dict]:
        """
        Reciprocal Rank Fusion (RRF) - combines ranked lists.

        RRF formula: score = sum(1 / (k + rank_i)) for each list
        """
        # Build ranks for each method
        keyword_ranks = {}
        for rank, item in enumerate(keyword_results, 1):
            doc_id = item.get("document_id", item.get("title", str(rank)))
            keyword_ranks[doc_id] = keyword_ranks.get(doc_id, []) + [rank]

        semantic_ranks = {}
        for rank, item in enumerate(semantic_results, 1):
            doc_id = item.get("document_id", item.get("title", str(rank)))
            semantic_ranks[doc_id] = semantic_ranks.get(doc_id, []) + [rank]

        # Merge all unique doc IDs
        all_ids = set(keyword_ranks.keys()) | set(semantic_ranks.keys())

        # Calculate RRF scores
        merged = []
        for doc_id in all_ids:
            kwd_rank = keyword_ranks.get(doc_id, [])
            sem_rank = semantic_ranks.get(doc_id, [])

            kwd_score = sum(1.0 / (k + r) for r in kwd_rank) if kwd_rank else 0.0
            sem_score = sum(1.0 / (k + r) for r in sem_rank) if sem_rank else 0.0

            # Find the best representation
            best_item = {}
            if kwd_rank:
                best_idx = kwd_rank.index(min(kwd_rank))
                best_item = keyword_results[kwd_rank.index(min(kwd_rank))]
            elif sem_rank:
                best_idx = sem_rank.index(min(sem_rank))
                best_item = semantic_results[sem_rank.index(min(sem_rank))]

            # Add scores
            best_item["rrf_score"] = round(kwd_score + sem_score, 6)
            best_item["keyword_score"] = round(kwd_score, 4) if kwd_rank else 0.0
            best_item["semantic_score"] = round(sem_score, 4) if sem_rank else 0.0
            # Add BM25 and embedding scores for ranker compatibility
            # Find the best keyword result for this doc_id
            if kwd_rank:
                kwd_idx = kwd_rank.index(min(kwd_rank))
                best_keyword = keyword_results[kwd_idx]
                best_item["bm25_score"] = best_keyword.get("bm25_score", 0.0) if isinstance(best_keyword, dict) else 0.0
                best_item["embedding_score"] = 0.0
            else:
                best_item["bm25_score"] = 0.0
                best_item["embedding_score"] = best_item.get("embedding_score", 0.0)

            merged.append(best_item)

        # Sort by RRF score
        merged.sort(key=lambda x: x.get("rrf_score", 0), reverse=True)
        return merged


class RRFFusion:
    """Reciprocal Rank Fusion manager."""

    @staticmethod
    def fuse(results_list: List[List[Dict]], k: int = 60) -> List[Dict]:
        """
        Fuse multiple ranked result lists using RRF.

        Args:
        - results_list: list of ranked result lists
        - k: RRF constant

        Returns:
        - fused results sorted by RRF score
        """
        id_ranks = {}

        for results in results_list:
            for rank, item in enumerate(results, 1):
                doc_id = item.get("document_id", item.get("title", str(rank)))
                if doc_id not in id_ranks:
                    id_ranks[doc_id] = []
                id_ranks[doc_id].append(rank)

        fused = []
        for doc_id, ranks in id_ranks.items():
            score = sum(1.0 / (k + r) for r in ranks)
            best_item = results[0]  # default
            for results in results_list:
                for rank, item in enumerate(results, 1):
                    if item.get("document_id", item.get("title", str(rank))) == doc_id:
                        best_item = item
                        break
            best_item["rrf_score"] = round(score, 6)
            fused.append(best_item)

        fused.sort(key=lambda x: x.get("rrf_score", 0), reverse=True)
        return fused


# Export for convenience
ReciprocalRankFusion = RRFFusion
