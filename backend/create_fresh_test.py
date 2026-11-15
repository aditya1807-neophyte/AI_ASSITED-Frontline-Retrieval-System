
import sys
sys.path.insert(0, ".")

# Use a unique test database
import tempfile
test_db = tempfile.mktemp(suffix=".db")
print("Using test db:", test_db)

from app.core.database import Base, engine
from app.models import User, Document, DocumentChunk, SavedItem, SearchHistory, Answer, SavedAnswer, Feedback, Escalation, AuditEvent

# Override engine URL to use the temp DB
from sqlalchemy import create_engine
from app.core.database import SessionLocal
import sqlite3

# Delete existing test db
import os
if os.path.exists(test_db):
    os.remove(test_db)

# Recreate engine with test db
engine = create_engine("sqlite:///" + test_db, connect_args={'check_same_thread': False})

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)

print("Creating all tables...")
Base.metadata.create_all(bind=engine)

print("SUCCESS: Database tables created")

from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print("Tables:", tables)
