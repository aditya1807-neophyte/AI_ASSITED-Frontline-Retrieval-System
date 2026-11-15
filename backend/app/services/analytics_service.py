"""
Business logic and orchestration layer for analytics operations.

Phase 3 — Analytics service.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import User
from app.models import Document
from app.models import Answer
from app.models import Escalation
from app.models import SearchHistory
from app.models import SavedItem
from app.models import Feedback
from app.models import Document  # for stats


class AnalyticsService:
    """Service layer for analytics operations."""

    @staticmethod
    def get_overview(db: Session) -> Dict[str, Any]:
        """Get analytics overview."""
        total_users = db.query(User).count()
        total_documents = db.query(Document).count()
        total_answers = db.query(Answer).count()
        total_escalations = db.query(Escalation).count()
        total_searches_today = db.query(SearchHistory).filter(
            SearchHistory.timestamp >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        total_saved_items = db.query(SavedItem).count()
        documents_this_week = db.query(Document).filter(
            Document.uploaded_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(weeks=1)
        ).count()
        answers_this_week = db.query(Answer).filter(
            Answer.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(weeks=1)
        ).count()
        escalations_pending = db.query(Escalation).filter(
            Escalation.status.in_(["open", "in_progress"])
        ).count()

        # Top topics
        top_topics = db.query(
            Document.topic, db.func.count(Document.topic)
        ).group_by(Document.topic).order_by(db.desc(db.func.count(Document.topic))).limit(5).all()

        top_topics_list = [{"topic": topic[0], "count": topic[1]} for topic in top_topics if topic[0]]

        return {
            "total_users": total_users,
            "total_documents": total_documents,
            "total_answers": total_answers,
            "total_escalations": total_escalations,
            "total_searches_today": total_searches_today,
            "total_saved_items": total_saved_items,
            "documents_this_week": documents_this_week,
            "answers_this_week": answers_this_week,
            "escalations_pending": escalations_pending,
            "top_topics": top_topics_list,
        }

    @staticmethod
    def get_documents_analytics(db: Session) -> Dict[str, Any]:
        """Get document analytics."""
        from sqlalchemy import func
        metrics = {
            "total": db.query(Document).count(),
            "by_status": db.query(Document.document_status, func.count(Document.id)).group_by(Document.document_status).all(),
            "by_type": db.query(Document.document_type, func.count(Document.id)).group_by(Document.document_type).all(),
            "by_source_organization": db.query(Document.source_organization, func.count(Document.id)).group_by(Document.source_organization).all(),
        }
        documents = db.query(Document).order_by(Document.uploaded_at.desc()).limit(10).all()
        recent_activity = [
            {"id": d.id, "title": d.title, "uploaded_at": d.uploaded_at, "status": d.document_status}
            for d in documents
        ]
        return {
            "metrics": metrics,
            "documents": recent_activity,
            "recent_activity": recent_activity,
        }

    @staticmethod
    def get_search_analytics(db: Session) -> Dict[str, Any]:
        """Get search analytics."""
        from sqlalchemy import func
        metrics = {
            "total_queries": db.query(SearchHistory).count(),
            "today": db.query(SearchHistory).filter(
                SearchHistory.timestamp >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count(),
        }
        top_queries = db.query(
            SearchHistory.query, func.count(SearchHistory.id)
        ).group_by(SearchHistory.query).order_by(db.desc(db.func.count(SearchHistory.id))).limit(10).all()
        top_queries_list = [{"query": q[0], "count": q[1]} for q in top_queries]
        return {
            "metrics": metrics,
            "top_queries": top_queries_list,
        }

    @staticmethod
    def get_answers_analytics(db: Session) -> Dict[str, Any]:
        """Get answers analytics."""
        from sqlalchemy import func
        metrics = {
            "total": db.query(Answer).count(),
            "by_status": db.query(Answer.evidence_status, func.count(Answer.id)).group_by(Answer.evidence_status).all(),
        }
        recent_answers = db.query(Answer).order_by(Answer.created_at.desc()).limit(10).all()
        recent_answers_list = [
            {
                "id": a.id,
                "user_id": a.user_id,
                "question": a.question,
                "answer_content": a.answer_content,
                "evidence_status": a.evidence_status,
                "created_at": a.created_at,
            }
            for a in recent_answers
        ]
        return {
            "metrics": metrics,
            "recent_answers": recent_answers_list,
        }

    @staticmethod
    def get_escalations_analytics(db: Session) -> Dict[str, Any]:
        """Get escalation analytics."""
        from sqlalchemy import func
        metrics = {
            "total": db.query(Escalation).count(),
            "by_status": db.query(Escalation.status, func.count(Escalation.id)).group_by(Escalation.status).all(),
            "by_priority": db.query(Escalation.priority, func.count(Escalation.id)).group_by(Escalation.priority).all(),
        }
        escalations = db.query(Escalation).order_by(Escalation.created_at.desc()).limit(10).all()
        escalations_list = [
            {
                "id": e.id,
                "user_id": e.user_id,
                "question": e.question,
                "status": e.status,
                "priority": e.priority,
                "created_at": e.created_at,
            }
            for e in escalations
        ]
        return {
            "metrics": metrics,
            "escalations": escalations_list,
        }
