# Backend - AI-Assisted Frontline Document and Knowledge Retrieval Workspace

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in `.env`:
   ```env
   DATABASE_URL=sqlite:///./data/frontline.db
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```

4. Run database migrations (Phase 2):
   ```bash
   uv run alembic revision --autogenerate -m "init"
   uv run alembic upgrade head
   ```

5. Start the backend:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

The backend will be available at http://localhost:8000.

## Technology Stack

- FastAPI
- SQLAlchemy
- Pydantic / Pydantic Settings
- SQLite (local development)

## Directory Structure

- `app/main.py` — FastAPI application entry point
- `app/core/` — configuration, database, security
- `app/models/` — SQLAlchemy models
- `app/schemas/` — Pydantic schemas
- `app/api/` — API routers
- `app/services/` — business logic
- `app/rag/` — RAG pipeline (Phase 2)
- `app/repositories/` — data access
- `app/utils/` — helpers
- `tests/` — test suite
