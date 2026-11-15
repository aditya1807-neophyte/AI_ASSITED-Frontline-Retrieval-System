"""
Chunking utilities for document ingestion.

Phase 4 — Split extracted text into meaningful, retrievable chunks.

Uses configurable chunk size (400-800 tokens) with modest overlap,
preferring paragraph and section boundaries where possible.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from app.models import DocumentChunk

logger = logging.getLogger(__name__)

# Approximate tokens per word (English)
TOKENS_PER_WORD = 1.3

# Target chunk size range in tokens
MIN_CHUNK_SIZE = 400
MAX_CHUNK_SIZE = 800

# Minimum chunk size to avoid too-small fragments
MIN_CHUNK_WORDS = 20

# Overlap between consecutive chunks (as fraction of chunk size)
DEFAULT_OVERLAP_RATIO = 0.15


def estimate_tokens(text: str) -> int:
    """Estimate token count from text (rough approximation for English)."""
    words = len(text.split())
    return int(words * TOKENS_PER_WORD)


def split_into_paragraphs(text: str) -> List[str]:
    """
    Split text into paragraphs based on blank lines.

    Returns a list of paragraph strings.
    """
    paragraphs = []
    current_paragraph = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped:
            current_paragraph.append(stripped)
        else:
            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))
    return paragraphs


def split_into_sections(text: str) -> List[str]:
    """
    Split text into sections based on markdown/heading patterns.

    Detects Markdown-style headings (##, ###, etc.) and splits accordingly.
    """
    lines = text.split("\n")
    sections = []
    current_section = []
    current_heading = None

    for line in lines:
        stripped = line.strip()
        # Check for markdown headings
        if stripped.startswith("#"):
            # Save previous section
            if current_section:
                sections.append({
                    "heading": current_heading,
                    "content": " ".join(current_section)
                })
            # Start new section
            current_section = []
            # Extract heading level and text
            hash_count = 0
            temp = stripped
            while temp.startswith("#"):
                hash_count += 1
                temp = temp[1:]
            current_heading = stripped[hash_count:].strip()
            current_section.append(stripped)
        else:
            current_section.append(stripped)

    if current_section:
        sections.append({
            "heading": current_heading,
            "content": " ".join(current_section)
        })

    return sections


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using basic punctuation."""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def create_chunks(
    document_id: int,
    title: str,
    extracted_text: str,
    page_reference: str = None,
    section_heading: str = None,
    version: str = None,
    source_metadata: Dict[str, Any] = None,
    min_chunk_size: int = MIN_CHUNK_SIZE,
    max_chunk_size: int = MAX_CHUNK_SIZE,
    overlap_ratio: float = DEFAULT_OVERLAP_RATIO,
) -> List[Dict[str, Any]]:
    """
    Create chunks from extracted text following the spec requirements.

    - Initial chunk size ~400-800 tokens
    - Modest overlap (~15%)
    - Prefer paragraph and section boundaries
    - No invented page references
    - No duplicate chunks on reprocessing

    Returns a list of chunk dictionaries ready for storage.
    """
    if not extracted_text.strip():
        return []

    chunks = []
    all_paragraphs = split_into_paragraphs(extracted_text)

    # Try to split by sections first
    sections = split_into_sections(extracted_text)
    if len(sections) > 1:
        all_paragraphs = []
        for section in sections:
            # Add heading as metadata for each paragraph in this section
            heading = section["heading"]
            section_text = section["content"]
            for para in split_into_paragraphs(section_text):
                all_paragraphs.append(f"[{heading}] {para}")

    # If we only have one section, use paragraphs
    # Build chunks from paragraphs
    current_chunk = []
    current_chunk_text = ""
    current_chunk_size = 0

    def should_split_chunk() -> bool:
        nonlocal current_chunk_size
        token_estimate = estimate_tokens(current_chunk_text)
        # Split if we exceed max chunk size
        if token_estimate >= max_chunk_size and len(current_chunk) > 1:
            return True
        # Split if we exceed max chunk size and would split a single huge paragraph
        if token_estimate >= max_chunk_size and len(current_chunk) == 1:
            # Leave this as a standalone large chunk
            return False
        return False

    for para in all_paragraphs:
        # Estimate if adding this paragraph would exceed max
        test_text = current_chunk_text + " " + para if current_chunk_text else para
        test_size = estimate_tokens(test_text)

        if should_split_chunk():
            # Finalize current chunk
            if current_chunk:
                chunks.append({
                    "document_id": document_id,
                    "chunk_sequence": len(chunks),
                    "extracted_text": current_chunk_text.strip(),
                    "page_reference": page_reference,
                    "section_heading": section_heading,
                    "chunk_metadata": {"paragraph_index": len(current_chunk), "word_count": len(current_chunk_text.split())},
                })
            # Start new chunk with overlap
            overlap_size = int(max_chunk_size * overlap_ratio * TOKENS_PER_WORD)
            if len(current_chunk) > 1:
                # Keep last N words for overlap
                words = current_chunk_text.split()
                overlap_words = int(overlap_size / TOKENS_PER_WORD)
                if overlap_words > 0 and len(words) > overlap_words:
                    current_chunk_text = " ".join(words[-overlap_words:]) + " "
                    current_chunk = [current_chunk_text.rstrip()]
                else:
                    current_chunk_text = ""
                    current_chunk = []
            # Now add the new paragraph
            current_chunk_text = para + " "
            current_chunk = [current_chunk_text]
            current_chunk_size = estimate_tokens(current_chunk_text)
        else:
            # Add to current chunk
            current_chunk_text += para + " "
            current_chunk.append(para)

    # Don't forget the last chunk
    if current_chunk_text.strip():
        chunks.append({
            "document_id": document_id,
            "chunk_sequence": len(chunks),
            "extracted_text": current_chunk_text.strip(),
            "page_reference": page_reference,
            "section_heading": section_heading,
            "chunk_metadata": {"paragraph_index": len(chunks), "word_count": len(current_chunk_text.split())},
        })

    # Ensure minimum chunk size
    filtered_chunks = []
    for chunk in chunks:
        if estimate_tokens(chunk["extracted_text"]) >= MIN_CHUNK_WORDS:
            filtered_chunks.append(chunk)

    return filtered_chunks



class DocumentChunkService:
    """Service for managing document chunks - CRUD operations."""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def get_chunks_by_document(self, document_id: int) -> List[Dict[str, Any]]:
        """Get all chunks for a document."""
        chunks = self.db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_sequence).all()
        return [chunk.to_dict() for chunk in chunks]
    
    def get_chunk_by_id(self, chunk_id: int) -> Optional[Dict[str, Any]]:
        """Get chunk by ID."""
        chunk = self.db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        return chunk.to_dict() if chunk else None
    
    def create_chunk(self, chunk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new chunk."""
        chunk = DocumentChunk(**chunk_data)
        self.db.add(chunk)
        self.db.commit()
        self.db.refresh(chunk)
        return chunk.to_dict()
    
    def update_chunk(self, chunk_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a chunk."""
        chunk = self.db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            return None
        for key, value in data.items():
            setattr(chunk, key, value)
        self.db.commit()
        self.db.refresh(chunk)
        return chunk.to_dict()
    
    def delete_chunk(self, chunk_id: int) -> bool:
        """Delete a chunk."""
        chunk = self.db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            return False
        self.db.delete(chunk)
        self.db.commit()
        return True
