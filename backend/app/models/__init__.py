import json
"""Database models for the knowledge retrieval workspace.

Phase 4 — Document ingestion and structured knowledge repository.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index, Boolean
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship
from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
class User(Base):
    """Application user account."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    display_name = Column(String(128), nullable=False)
    login_identifier = Column(String(128), unique=True, nullable=False, index=True)
    role = Column(String(64), nullable=False, default="analyst")
    account_status = Column(String(32), nullable=False, default="active")
    password_hash = Column(String(256), nullable=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    email = Column(String(128), nullable=True)
    preferences = Column(Text, nullable=True)

    # Relationships - all use back_populates with explicit foreign keys
    saved_items = relationship("SavedItem", cascade="all, delete-orphan", back_populates="user")
    saved_answers = relationship("SavedAnswer", cascade="all, delete-orphan", back_populates="user")
    search_history = relationship("SearchHistory", cascade="all, delete-orphan", back_populates="user")
    answers = relationship("Answer", cascade="all, delete-orphan", back_populates="user")
    feedback = relationship("Feedback", cascade="all, delete-orphan", back_populates="user")
    escalations = relationship("Escalation", cascade="all, delete-orphan", back_populates="user", foreign_keys="[Escalation.user_id]")
    assigned_escalations = relationship("Escalation", back_populates="assigned_reviewer_user", foreign_keys="[Escalation.assigned_reviewer]")
    audit_events = relationship("AuditEvent", cascade="all, delete-orphan", back_populates="user")

    __table_args__ = ()


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------
class Document(Base):
    """Knowledge document record."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(512), nullable=False, index=True)
    description = Column(Text, nullable=True)
    document_type = Column(String(64), nullable=True)
    topic = Column(String(256), nullable=True)
    intended_role = Column(String(256), nullable=True)
    source_organization = Column(String(256), nullable=True)
    original_filename = Column(String(512), nullable=False)
    storage_reference = Column(String(512), nullable=True, index=True)
    language = Column(String(16), nullable=True, default="en")
    tags = Column(Text, nullable=True)

    @property
    def tags_parsed(self):
        """Return parsed tags list from JSON string."""
        if self.tags and isinstance(self.tags, str):
            try:
                return json.loads(self.tags)
            except (json.JSONDecodeError, TypeError):
                return []
        return self.tags if self.tags else []
    version = Column(String(64), nullable=True, index=True)
    document_status = Column(String(32), nullable=False, default="draft")
    effective_date = Column(DateTime, nullable=True, index=True)
    review_date = Column(DateTime, nullable=True, index=True)
    uploaded_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False, index=True)
    processing_status = Column(String(32), nullable=False, default="pending")
    processed_at = Column(DateTime, nullable=True)

    # File storage fields
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    file_checksum = Column(String(64), nullable=True)
    num_pages = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)

    # Search content
    content = Column(Text, nullable=True)


    # Embedding fields
    embedding_vector = Column(Text, nullable=True, index=True)
    embedding_model = Column(String(128), nullable=True)
    embedding_timestamp = Column(DateTime, nullable=True)
    is_semantic_enabled = Column(Boolean, nullable=False, default=True)

    # Relationships
    chunks = relationship("DocumentChunk", cascade="all, delete-orphan", back_populates="document")
    saved_items = relationship("SavedItem", cascade="all, delete-orphan", back_populates="document")
    saved_answers = relationship("SavedAnswer", cascade="all, delete-orphan", back_populates="document")
    escalations = relationship("Escalation", cascade="all, delete-orphan", back_populates="document", foreign_keys="[Escalation.document_id]")

    __table_args__ = (
        Index("ix_documents_document_status", "document_status"),
        Index("ix_documents_processing_status", "processing_status"),
        Index("ix_documents_topic", "topic"),
        Index("ix_documents_document_type", "document_type"),
        Index("ix_documents_intended_role", "intended_role"),
        Index("ix_documents_source_organization", "source_organization"),
        Index("ix_documents_uploaded_at", "uploaded_at"),
    )

    def to_dict(self):
        """Convert document to dictionary for API responses."""
        # Parse tags from JSON string to list
        tags = self.tags
        if isinstance(tags, str):
            try:
                tags = json.loads(tags) if tags else []
            except (json.JSONDecodeError, TypeError):
                tags = []
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "document_type": self.document_type,
            "topic": self.topic,
            "intended_role": self.intended_role,
            "source_organization": self.source_organization,
            "original_filename": self.original_filename,
            "storage_reference": self.storage_reference,
            "file_path": self.file_path,
            "language": self.language,
            "tags": tags,
            "version": self.version,
            "document_status": self.document_status,
            "effective_date": self.effective_date,
            "review_date": self.review_date,
            "uploaded_at": self.uploaded_at,
            "processing_status": self.processing_status,
            "processed_at": self.processed_at,
            "file_size": self.file_size,
            "file_checksum": self.file_checksum,
            "num_pages": self.num_pages,
            "word_count": self.word_count,
            "content": self.content,
            "chunk_count": len(self.chunks),
        }

# ---\n# Search History
# ---------------------------------------------------------------------------
class DocumentChunk(Base):
    """Text chunk extracted from a document for retrieval."""

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_sequence = Column(Integer, nullable=False, default=0)
    extracted_text = Column(Text, nullable=False)
    page_reference = Column(String(64), nullable=True)
    section_heading = Column(String(256), nullable=True)
    chunk_metadata = Column(Text, nullable=True)

    # Relationships
    document = relationship("Document", back_populates="chunks")


class SavedItem(Base):
    """User-saved document or answer reference."""

    __tablename__ = "saved_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    item_type = Column(String(32), nullable=False, index=True)  # "document" or "answer"
    item_reference = Column(String(512), nullable=False)  # document_id or answer_id
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="saved_items")
    document = relationship("Document", back_populates="saved_items")

    __table_args__ = ()


class SearchHistory(Base):
    """User search query history."""

    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="search_history")

    __table_args__ = ()


# ---------------------------------------------------------------------------
# Answers
# ---------------------------------------------------------------------------
class Answer(Base):
    """Generated AI answer with evidence references."""

    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer_content = Column(Text, nullable=False)
    evidence_references = Column(Text, nullable=True)
    evidence_status = Column(String(32), nullable=False, default="verified")
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="answers")
    saved_answers = relationship("SavedAnswer", cascade="all, delete-orphan", back_populates="answer")

    __table_args__ = (
        Index("ix_answers_created_at", "created_at"),
    )


# ---------------------------------------------------------------------------
# Saved Answers
# ---------------------------------------------------------------------------
class SavedAnswer(Base):
    """Saved answer record with user reference."""

    __tablename__ = "saved_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    answer_id = Column(Integer, ForeignKey("answers.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="saved_answers")
    answer = relationship("Answer", back_populates="saved_answers")
    document = relationship("Document", back_populates="saved_answers")

    __table_args__ = ()


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------
class Feedback(Base):
    """User feedback on an answer or document."""

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    answer_ref = Column(String(512), nullable=True)
    document_ref = Column(String(512), nullable=True)
    feedback_type = Column(String(32), nullable=False, index=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="feedback")

    __table_args__ = ()


# ---------------------------------------------------------------------------
# Escalations
# ---------------------------------------------------------------------------
class Escalation(Base):
    """Escalation record for issues needing review."""

    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    evidence_references = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="open", index=True)
    priority = Column(String(32), nullable=False, default="medium", index=True)
    assigned_reviewer = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    review_notes = Column(Text, nullable=True)
    resolution = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    updated_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"), nullable=False)

    # Document relationship
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True, index=True)
    document = relationship("Document", back_populates="escalations")

    # Relationships
    user = relationship("User", back_populates="escalations", foreign_keys=[user_id])
    assigned_reviewer_user = relationship("User", back_populates="assigned_escalations", foreign_keys=[assigned_reviewer])

    __table_args__ = ()


# ---------------------------------------------------------------------------
# Audit Events
# ---------------------------------------------------------------------------
class AuditEvent(Base):
    """Audit trail for administrative actions and significant state changes."""

    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(128), nullable=False, index=True)
    target_type = Column(String(64), nullable=False, index=True)
    target_id = Column(String(256), nullable=True, index=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(48), nullable=True)
    user_agent = Column(String(256), nullable=True)
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_events")

    __table_args__ = ()


# ---------------------------------------------------------------------------
# Saved Items
# ---------------------------------------------------------------------------
