"""Database engine, session, and base configuration.

SQLAlchemy setup for SQLite local development.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

db_url = settings.database_url
connect_args: dict = {}
if db_url.startswith('sqlite'):
    connect_args = {'check_same_thread': False}
    clean_url = db_url.replace("sqlite:///", "")
    if clean_url.startswith("./"):
        clean_url = clean_url[2:]
    if not os.path.exists(clean_url) and os.path.exists(os.path.join("backend", clean_url)):
        clean_url = os.path.join("backend", clean_url)
        db_url = f"sqlite:///{clean_url}"
    parent_dir = os.path.dirname(clean_url)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

engine = create_engine(
    db_url,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
