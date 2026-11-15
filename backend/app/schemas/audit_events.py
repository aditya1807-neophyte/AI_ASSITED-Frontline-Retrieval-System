"""
Pydantic schemas for audit events API endpoints.

Phase 3 — Audit event schema definitions.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class AuditAction(str, Enum):
    user_created = "user_created"
    user_updated = "user_updated"
    user_deleted = "user_deleted"
    document_created = "document_created"
    document_updated = "document_updated"
    document_deleted = "document_deleted"
    document_accessed = "document_accessed"
    document_migrated = "document_migrated"
    escalation_created = "escalation_created"
    escalation_resolved = "escalation_resolved"
    escalation_assigned = "escalation_assigned"
    admin_action = "admin_action"


class AuditEventCreate(BaseModel):
    user_id: Optional[int] = None
    action: AuditAction
    target_type: str
    target_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditEventPublic(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    target_type: str
    target_id: Optional[str]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditEventResponse(AuditEventPublic):
    user_id: Optional[int]
    action: str
    target_type: str
    target_id: Optional[str]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    user: Optional[dict] = None
