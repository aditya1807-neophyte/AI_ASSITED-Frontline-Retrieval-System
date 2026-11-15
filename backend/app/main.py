"""
FastAPI application entry point for the knowledge retrieval workspace.

Phase 3 - Complete application setup with all API routers.
Phase 5 - RAG pipeline integration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.core.database import Base, engine
from app.api import health, docs, users, documents, chunks, saved_items, search_history, \
    answers, feedback, escalations, audit_events, analytics
from app.core.database import get_db
from app.models import Base as AllModelsBase
from app.api.rag import router as rag_router

settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(',') if o.strip()] if settings.cors_origins else ["*"],
    allow_origin_regex=r"https://.*\.vercel\.app|https://.*\.onrender\.com|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Include all API routers
app.include_router(users.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(docs.router, prefix="/api", tags=["Documents"])
app.include_router(documents.router, prefix="/api", tags=["Documents"])
app.include_router(chunks.router, prefix="/api", tags=["Document Chunks"])
app.include_router(saved_items.router, prefix="/api", tags=["Saved Items"])
app.include_router(search_history.router, prefix="/api", tags=["Search History"])
app.include_router(answers.router, prefix="/api", tags=["Answers"])
app.include_router(feedback.router, prefix="/api", tags=["Feedback"])
app.include_router(escalations.router, prefix="/api", tags=["Escalations"])
app.include_router(audit_events.router, prefix="/api", tags=["Audit Events"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(rag_router, prefix="/api", tags=["RAG"])

# Create database tables on startup
Base.metadata.create_all(bind=engine)


@app.get('/')
def root():
    """Root endpoint."""
    return {
        'message': 'Frontline Knowledge Workspace API',
        'docs': '/docs',
    }


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc):
    """Handle SQLAlchemy database errors."""
    return JSONResponse(
        status_code=503,
        content={"detail": "Database error. Please try again later."}
    )
