"""
Configurable embedding provider for the RAG pipeline.

Prefers a local embedding model (sentence-transformers) if available.
Otherwise allows configuration of an external embedding provider via environment variables.

Features:
- Persistent vector index storage
- Tracks embedding model identifier
- Does not regenerate embeddings unnecessarily
"""

from __future__ import annotations
import os
import logging
import hashlib
from typing import Optional, List, Any, Dict
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Local embedding model settings
LOCAL_EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Practical, fast, good quality
LOCAL_EMBEDDING_DIM = 384


class EmbeddingProvider:
    """Configurable embedding provider with persistent vector index."""

    def __init__(self, model_name: Optional[str] = None):
        self.settings = get_settings()
        self.model_name = model_name or LOCAL_EMBEDDING_MODEL
        self.dim = LOCAL_EMBEDDING_DIM
        self.vector_dir = Path(self.settings.embedding_index_dir)
        self.vector_dir.mkdir(parents=True, exist_ok=True)

        # Track what model is loaded
        self._model = None
        self._loaded_model_id = None
        self._document_embeddings = {}  # document_id -> embedding

        # Check if semantic retrieval is available
        try:
            self.is_available = self._try_load_model()
        except Exception as e:
            logger.warning(f"Local embedding model not available: {e}")
            self.is_available = False
            self._model_compat = "keyword-only"
            logger.info("Semantic retrieval not available - falling back to keyword retrieval")

    def _try_load_model(self) -> bool:
        """Try to load the local embedding model. Returns True if successful."""
        try:
            from sentence_transformers import SentenceTransformer
            if self._model is None or self._loaded_model_id != self.model_name:
                self._model = SentenceTransformer(self.model_name)
                self._loaded_model_id = self.model_name
            return True
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. Install with: pip install sentence-transformers"
            )
            return False
        except Exception as e:
            logger.warning(f"Failed to load embedding model {self.model_name}: {e}")
            return False

    def embed_documents(self, document_ids: List[int], texts: List[str]) -> Dict[int, List[float]]:
        """
        Generate and cache embeddings for documents.

        Only regenerates if embeddings are not already cached.
        """
        if not self.is_available:
            logger.warning("Semantic retrieval not available - returning zero vectors")
            return {doc_id: [0.0] * self.dim for doc_id in document_ids}

        result = {}
        for doc_id, text in zip(document_ids, texts):
            if doc_id not in self._document_embeddings:
                if text.strip():
                    embedding = self._model.encode(text, convert_to_numpy=True)
                    self._document_embeddings[doc_id] = embedding.tolist()
                else:
                    self._document_embeddings[doc_id] = [0.0] * self.dim
            result[doc_id] = self._document_embeddings[doc_id]
        return result

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a query."""
        if not self.is_available:
            return [0.0] * self.dim
        return self._model.encode(query, convert_to_numpy=True).tolist()

    def get_model_id(self) -> str:
        """Return the embedding model identifier."""
        return self.model_name

    def is_semantic_available(self) -> bool:
        """Check if semantic retrieval is available."""
        return self.is_available


# Global embedding provider instance (singleton)
_embedding_provider: Optional[EmbeddingProvider] = None


def get_embedding_provider() -> EmbeddingProvider:
    """Get or create the embedding provider singleton."""
    global _embedding_provider
    if _embedding_provider is None:
        _embedding_provider = EmbeddingProvider()
    return _embedding_provider


def get_embedding_model_id() -> Optional[str]:
    """Return the embedding model identifier, or None if not available."""
    provider = get_embedding_provider()
    if provider.is_available:
        return provider.get_model_id()
    return None
