# -*- coding: utf-8 -*-
"""
Keyword retrieval service for the RAG pipeline.

Uses SQLite FTS5 for full-text search, plus BM25 scoring for ranking.
Operates on actual extracted document chunks.
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import func, or_

from app.core.database import get_db
from app.models import Document, DocumentChunk
from app.services.search_service import SearchService

logger = logging.getLogger(__name__)


class KeywordRetrieveService:
    """
    Keyword retrieval service using SQLite FTS and BM25-style scoring.

    Provides query validation, normalization, keyword search over chunks,
    and BM25-style ranking.
    """

    def __init__(self):
        self.search_service = SearchService()
        self.max_results = 20

    def _calculate_bm25_score(self, query: str, content: str) -> float:
        """Calculate BM25-like term frequency score between query and content."""
        if not query or not content:
            return 0.0
        import re
        query_terms = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 2]
        if not query_terms:
            return 0.0
        content_lower = content.lower()
        score = 0.0
        for term in query_terms:
            tf = content_lower.count(term)
            if tf > 0:
                score += (tf * 2.2) / (tf + 1.2)
        return round(score, 4)

    def is_semantic_available(self) -> bool:
        """Check if semantic provider is available."""
        from app.core.embedding_provider import get_embedding_provider
        return get_embedding_provider().is_semantic_available()

    def retrieve_keyword(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve documents using keyword search.

        Returns a list of ranked results with:
        - content: chunk text
        - title: document title
        - chunk_sequence: chunk sequence number
        - page_reference: page reference if available
        - bm25_score: relevance score
        - embedding_score: 0 (not semantic)
        """
        # First, use the search service to find relevant chunks
        search_results = self.search_service.search(
            query=query,
            limit=top_k * 2,  # Get more than needed
        )

        # Build results with BM25-like scoring
        results = []
        for i, chunk in enumerate(search_results[:top_k]):
            score = self._calculate_bm25_score(query, chunk.get("content", ""))
            results.append({
                "content": chunk.get("content", ""),
                "title": chunk.get("title", ""),
                "document_id": chunk.get("document_id"),
                "chunk_sequence": chunk.get("chunk_sequence"),
                "page_reference": chunk.get("page_reference", ""),
                "bm25_score": score,
                "embedding_score": 0.0,
            })

        return results

    def retrieve_hybrid(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve documents using hybrid search (keyword + semantic).

        Returns a list of ranked results with:
        - content: chunk text
        - title: document title
        - chunk_sequence: chunk sequence number
        - page_reference: page reference if available
        - bm25_score: relevance score from keyword search
        - embedding_score: relevance score from semantic search
        """
        # Use keyword-only search when semantic is not available
        results = self.retrieve_keyword(query, top_k=top_k * 2)

        # If semantic provider is available, use hybrid retriever
        if self.is_semantic_available():
            keyword_results = results
            semantic_results = self.retrieve_semantic(query, top_k=top_k * 2)

            # Combine using RRF
            combined = self._rrf_fusion(keyword_results, semantic_results, k=60)

            return combined

        return results

    def _rrf_fusion(self, keyword_results: List[Dict], semantic_results: List[Dict], k: int = 60) -> List[Dict]:
        """Reciprocal Rank Fusion combining keyword and semantic results."""
        # Build ranks for each method
        keyword_ranks = {}
        for rank, item in enumerate(keyword_results, 1):
            doc_id = item.get("content", str(rank))
            keyword_ranks[doc_id] = keyword_ranks.get(doc_id, []) + [rank]

        semantic_ranks = {}
        for rank, item in enumerate(semantic_results, 1):
            doc_id = item.get("content", str(rank))
            semantic_ranks[doc_id] = semantic_ranks.get(doc_id, []) + [rank]

        # Merge all unique content
        all_ids = set(keyword_ranks.keys()) | set(semantic_ranks.keys())

        # Calculate RRF scores
        merged = []
        for doc_id in all_ids:
            kwd_rank = keyword_ranks.get(doc_id, [])
            sem_rank = semantic_ranks.get(doc_id, [])

            kwd_score = sum(1.0 / (k + r) for r in kwd_rank) if kwd_rank else 0.0
            sem_score = sum(1.0 / (k + r) for r in sem_rank) if sem_rank else 0.0

            # Find best keyword item
            best_item = {"content": doc_id, "bm25_score": 0.0, "embedding_score": 0.0}
            if kwd_rank:
                kwd_idx = kwd_rank.index(min(kwd_rank))
                best_item = keyword_results[kwd_idx]
            elif sem_rank:
                sem_idx = sem_rank.index(min(sem_rank))
                best_item = semantic_results[sem_idx]

            # Add scores
            best_item["rrf_score"] = round(kwd_score + sem_score, 6)
            best_item["keyword_score"] = round(kwd_score, 4) if kwd_rank else 0.0
            best_item["semantic_score"] = round(sem_score, 4) if sem_rank else 0.0

            merged.append(best_item)

        # Sort by RRF score
        merged.sort(key=lambda x: x.get("rrf_score", 0), reverse=True)
        return merged
        """
        Calculate a BM25-style relevance score.

        This is a simplified BM25 implementation using term frequency and
        inverse document frequency heuristics.
        """
        # Tokenize
        query_terms = set(query.lower().split())
        text_terms = text.lower().split()

        if not query_terms:
            return 0.0

        # Calculate term frequency for each query term
        term_freq = {}
        for term in text_terms:
            term_freq[term] = term_freq.get(term, 0) + 1

        # Calculate score
        score = 0.0
        for term in query_terms:
            tf = term_freq.get(term, 0)
            if tf == 0:
                continue

            # IDF approximation
            idf = 1.0 + (1.0 / (1.0 + tf))

            # TF component with BM25 k1
            tf_component = tf * (k1 + 1) / (tf + k1)

            # Length normalization with BM25 b
            doc_len = len(text_terms)
            avg_doc_len = max(1, doc_len * 0.01)  # Approximate average
            length_normalization = (1 - b) + b * (doc_len / avg_doc_len)

            score += idf * tf_component / length_normalization

        return round(score, 4)

    def search_chunks(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search chunks using FTS5.

        Returns chunk data suitable for retrieval.
        """
        return self.search_service.search(query=query, limit=limit)

    def get_chunks_by_document(self, document_id: int) -> List[Dict[str, Any]]:
        """Get all chunks for a document."""
        db = next(get_db())
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_sequence).all()
        db.close()

        return [{
            "content": c.extracted_text,
            "title": "",  # Will be filled by document
            "chunk_sequence": c.chunk_sequence,
            "page_reference": c.page_reference,
            "embedding_score": 0.0,
            "bm25_score": 0.0,
        } for c in chunks]

# Alias for compatibility with the RAG pipeline
RetrievalService = KeywordRetrieveService
