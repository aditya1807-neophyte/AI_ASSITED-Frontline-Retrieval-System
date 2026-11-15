# -*- coding: utf-8 -*-
"""
Vector store for persistent vector index.

Features:
- Persistent vector index storage on disk
- Embedding model identifier tracking
- Does not regenerate embeddings unnecessarily
- Supports semantic vectorization and similarity search
"""

import os
import json
import logging
import pickle
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone

from app.core.config import get_settings
from app.core.embedding_provider import get_embedding_provider

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Persistent vector index for document embeddings.

    Stores embeddings on disk and supports retrieval by vector similarity.
    Embedding model identifier is tracked in the index metadata.
    """

    def __init__(self):
        self.settings = get_settings()
        self.vector_dir = Path(self.settings.embedding_index_dir)
        self.vector_dir.mkdir(parents=True, exist_ok=True)

        # Index files
        self.index_file = self.vector_dir / "index.json"
        self.embeddings_file = self.vector_dir / "embeddings.pkl"
        self.model_file = self.vector_dir / "model.json"

        # Loaded data
        self.documents: Dict[int, Dict[str, Any]] = {}  # doc_id -> doc_info
        self.embeddings: Dict[int, List[float]] = {}  # doc_id -> embedding
        self.model_id: Optional[str] = None
        self.embedding_dim: Optional[int] = None
        self.last_updated: Optional[datetime] = None

        # Load if exists
        self._load()

    def _load(self):
        """Load the vector index from disk."""
        if self.index_file.exists() and self.embeddings_file.exists():
            try:
                with open(self.index_file, "r") as f:
                    index_data = json.load(f)
                    self.documents = {int(k): v for k, v in index_data.get("documents", {}).items()}
                    self.model_id = index_data.get("model_id")
                    self.embedding_dim = index_data.get("embedding_dim")
                    self.last_updated = datetime.fromisoformat(index_data.get("last_updated", "")) if index_data.get("last_updated") else None

                with open(self.embeddings_file, "rb") as f:
                    self.embeddings = pickle.load(f)

                logger.info(f"Vector index loaded: {len(self.embeddings)} embeddings, model={self.model_id}")
            except Exception as e:
                logger.warning(f"Failed to load vector index: {e}")
                self.documents = {}
                self.embeddings = {}
                self.model_id = None
                self.embedding_dim = None
                self.last_updated = None

    def _save(self):
        """Save the vector index to disk."""
        try:
            # Save index metadata
            index_data = {
                "documents": {str(k): v for k, v in self.documents.items()},
                "model_id": self.model_id,
                "embedding_dim": self.embedding_dim,
                "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            }
            with open(self.index_file, "w") as f:
                json.dump(index_data, f, indent=2)

            # Save embeddings
            with open(self.embeddings_file, "wb") as f:
                pickle.dump(self.embeddings, f)

            logger.info(f"Vector index saved: {len(self.embeddings)} embeddings")
        except Exception as e:
            logger.error(f"Failed to save vector index: {e}")

    def add_document(self, document_id: int, text: str, embedding: Optional[List[float]] = None) -> bool:
        """
        Add a document embedding to the vector index.

        Only adds if embedding is not already cached (avoids unnecessary regeneration).
        """
        provider = get_embedding_provider()

        if document_id in self.embeddings:
            logger.info(f"Embedding for doc {document_id} already cached, skipping")
            return False

        if embedding is None:
            # Generate embedding if not provided
            if not provider.is_available:
                logger.warning(f"Semantic provider not available, cannot embed doc {document_id}")
                return False
            if not text or not text.strip():
                logger.warning(f"Empty text for doc {document_id}")
                return False
            embedding = provider.embed_query(text)

        self.embeddings[document_id] = embedding
        self.documents[document_id] = {
            "added_at": datetime.now(timezone.utc).isoformat(),
            "text_preview": text[:200] if text else "",
        }

        self._save()
        return True

    def add_documents(self, documents: List[Tuple[int, str]]) -> Dict[int, bool]:
        """Add multiple document embeddings."""
        results = {}
        for doc_id, text in documents:
            results[doc_id] = self.add_document(doc_id, text)
        return results

    def get_embedding(self, document_id: int) -> Optional[List[float]]:
        """Get the embedding for a document."""
        return self.embeddings.get(document_id)

    def delete_document(self, document_id: int) -> bool:
        """Remove a document from the index."""
        if document_id in self.embeddings:
            del self.embeddings[document_id]
            self.documents.pop(document_id, None)
            self._save()
            return True
        return False

    def vector_similarity(self, query_embedding: List[float], doc_embedding: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(query_embedding) != len(doc_embedding):
            return 0.0

        dot_product = sum(a * b for a, b in zip(query_embedding, doc_embedding))
        norm_a = sum(a * a for a in query_embedding) ** 0.5
        norm_b = sum(b * b for b in doc_embedding) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for documents by vector similarity."""
        if not self.embeddings:
            return []

        results = []
        for doc_id, emb in self.embeddings.items():
            score = self.vector_similarity(query_embedding, emb)
            if doc_id in self.documents:
                doc_info = self.documents[doc_id]
                results.append({
                    "document_id": doc_id,
                    "embedding_score": score,
                    "metadata": doc_info,
                })

        # Sort by similarity (descending)
        results.sort(key=lambda x: x["embedding_score"], reverse=True)
        return results[:top_k]

    def clear(self):
        """Clear the vector index."""
        self.documents = {}
        self.embeddings = {}
        self.model_id = None
        self.embedding_dim = None
        self._save()

    def get_model_id(self) -> Optional[str]:
        """Return the embedding model identifier."""
        return self.model_id

    def set_model_id(self, model_id: str):
        """Set and save the embedding model identifier."""
        self.model_id = model_id
        self._save()

    def is_semantic_available(self) -> bool:
        """Check if semantic retrieval is available."""
        return len(self.embeddings) > 0 and self.model_id is not None


# Singleton instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get the singleton vector store."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
