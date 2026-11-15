# AI-Assisted Frontline Document and Knowledge Retrieval Workspace

## Overview

Phase 1 foundation for a full-stack application that will provide AI-assisted retrieval
over frontline documents (PDFs, manuals, SOPs, field notes) using a Retrieval-Augmented
Generation (RAG) pipeline.

## Project Structure

frontline-retrieval-workspace/
├── frontend/              # React + TypeScript + Vite + Tailwind
│   ├── src/
│   └── package.json
├── backend/               # FastAPI + SQLAlchemy + SQLite
│   ├── app/
│   ├── requirements.txt
│   └── README.md
├── data/
│   └── documents/         # Uploaded documents (gitignored, seed file kept)
├── docs/                  # Documentation
└── README.md              # This file

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### 1. Install dependencies

```bash
# Install frontend dependencies
npm run install:all
```

### 2. Start the backend

```bash
cd backend
source .venv/bin/activate  # or use your preferred venv
uv run uvicorn app.main:app --reload
```

The backend will be available at http://localhost:8000.

### 3. Start the frontend

```bash
# In a separate terminal
npm run dev:frontend
```

The frontend will be available at http://localhost:5173.

## Environment Variables

### Frontend

Copy `frontend/.env.example` to `frontend/.env` (note: `frontend/.env` is committed with defaults).

### Backend

Copy `backend/.env.example` to `backend/.env` and adjust as needed.

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./data/frontline.db` | SQLAlchemy database URL |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Allowed CORS origins (comma-separated) |

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Root endpoint with API info |
| GET | `/health` | Health check |
| GET | `/api/docs` | List documents (placeholder — Phase 2) |

## Scripts

`npm run install:all` — install frontend + backend dependencies
`npm run dev:frontend` — start frontend dev server
`npm run dev:backend` — start backend with auto-reload
