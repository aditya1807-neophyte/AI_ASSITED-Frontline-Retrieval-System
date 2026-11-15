# -*- coding: utf-8 -*-
"""
Query processor for the RAG pipeline.

Implements:
- Query validation (empty, too long, inappropriate content)
- Query normalization (lowercasing, stemming, stopword removal)
- Query classification (fact-based vs procedural)
"""

import re
import logging
from typing import Tuple, List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QueryValidationResult:
    """Result of query validation."""
    is_valid: bool
    normalized_query: str
    errors: List[str]
    warnings: List[str]
    query_type: str  # "factual", "procedural", "comparative", "other"


class QueryProcessor:
    """Process and validate user queries."""

    # Common stop words to remove during normalization
    STOP_WORDS = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "this",
        "that", "these", "those", "i", "you", "he", "she", "it", "we", "they",
        "what", "which", "who", "whom", "whose", "when", "where", "why", "how",
        "all", "each", "every", "both", "few", "many", "much", "some", "any",
        "no", "not", "if", "then", "than", "so", "as", "until", "while", "during",
    }

    def __init__(self):
        self.max_query_length = 500
        self.min_query_length = 3

    def validate(self, query: str) -> QueryValidationResult:
        """
        Validate and normalize a user query.

        Returns QueryValidationResult with:
        - is_valid: whether the query is acceptable
        - normalized_query: cleaned query
        - errors: list of validation errors
        - warnings: list of warnings
        - query_type: classification of query type
        """
        errors = []
        warnings = []

        # Check for empty or whitespace-only
        if not query or not query.strip():
            errors.append("Query cannot be empty.")
            return QueryValidationResult(
                is_valid=False,
                normalized_query="",
                errors=errors,
                warnings=warnings,
                query_type="other",
            )

        # Check length
        if len(query) > self.max_query_length:
            errors.append(f"Query is too long (max {self.max_query_length} characters).")
            # Truncate
            normalized_query = query[:self.max_query_length]
        else:
            normalized_query = query

        # Check for unacceptable content (basic patterns)
        if re.search(r'\b(password|secret|api[_-]?key|token|credential)\b', normalized_query, re.IGNORECASE):
            warnings.append("Query contains potentially sensitive terms. Results may be limited.")

        # Normalize the query
        normalized_query = self._normalize(normalized_query)
        if not normalized_query:
            errors.append("Could not normalize query.")

        # Classify query type
        query_type = self._classify_query(normalized_query)

        return QueryValidationResult(
            is_valid=len(errors) == 0,
            normalized_query=normalized_query,
            errors=errors,
            warnings=warnings,
            query_type=query_type,
        )

    def _normalize(self, query: str) -> str:
        """
        Normalize query: lowercase, remove extra whitespace, remove stop words.
        """
        # Convert to lowercase
        text = query.lower().strip()

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Split into words and filter stop words
        words = text.split()
        words = [w for w in words if w not in self.STOP_WORDS]

        # Rejoin
        normalized = " ".join(words)
        return normalized.strip()

    def _classify_query(self, query: str) -> str:
        """
        Classify query type based on keywords.
        """
        query_lower = query.lower()

        # Procedural queries
        if any(phrase in query_lower for phrase in [
            "how to", "procedure", "process", "steps", "method", "way to", "best way",
            "guide", "manual", "implement", "execute", "apply"
        ]):
            return "procedural"

        # Comparative queries
        if any(phrase in query_lower for phrase in [
            "compare", "difference", "similar", "vs", "versus", "better than", "more"
        ]):
            return "comparative"

        # Factual queries (most common)
        if any(phrase in query_lower for phrase in [
            "what", "when", "where", "who", "why", "which"
        ]):
            return "factual"

        # Default
        return "other"

    def normalize(self, query: str) -> Tuple[str, List[str]]:
        """
        Normalize a query and return the cleaned version.

        Returns:
        - normalized_query: cleaned query string
        - errors: list of validation errors (empty if no errors)
        """
        result = self.validate(query)
        return result.normalized_query, result.errors

    def extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from a query."""
        normalized = self._normalize(query)
        return normalized.split()
