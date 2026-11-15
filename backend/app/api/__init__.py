# API routers package
from .health import router as health_router
from .docs import router as docs_router
from .users import router as users_router
from .documents import router as documents_router
from .chunks import router as chunks_router
from .saved_items import router as saved_items_router
from .search_history import router as search_history_router
from .answers import router as answers_router
from .feedback import router as feedback_router
from .escalations import router as escalations_router
from .audit_events import router as audit_events_router
from .analytics import router as analytics_router

__all__ = [
    'health_router', 'docs_router', 'users_router', 'documents_router',
    'chunks_router', 'saved_items_router', 'search_history_router',
    'answers_router', 'feedback_router', 'escalations_router',
    'audit_events_router', 'analytics_router',
]
