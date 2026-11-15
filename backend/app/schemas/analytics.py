"""
Pydantic schemas for analytics API endpoints.

Phase 3 — Analytics schema definitions.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, List, Any


class AnalyticsOverview(BaseModel):
    total_users: int
    total_documents: int
    total_answers: int
    total_escalations: int
    total_searches_today: int
    total_saved_items: int
    documents_this_week: int
    answers_this_week: int
    escalations_pending: int
    top_topics: List[Dict[str, Any]]


class AnalyticsDocuments(BaseModel):
    metrics: Dict[str, Any]
    documents: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]


class AnalyticsSearch(BaseModel):
    metrics: Dict[str, Any]
    top_queries: List[Dict[str, Any]]


class AnalyticsAnswers(BaseModel):
    metrics: Dict[str, Any]
    recent_answers: List[Dict[str, Any]]


class AnalyticsEscalations(BaseModel):
    metrics: Dict[str, Any]
    escalations: List[Dict[str, Any]]


class AnalyticsReport(BaseModel):
    overview: AnalyticsOverview
    documents: AnalyticsDocuments
    search: AnalyticsSearch
    answers: AnalyticsAnswers
    escalations: AnalyticsEscalations
