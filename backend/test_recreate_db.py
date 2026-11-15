
import sys
sys.path.insert(0, ".")

from app.core.database import Base, engine
from app.models import User, Document, DocumentChunk, SavedItem, SearchHistory, Answer, SavedAnswer, Feedback, Escalation, AuditEvent

from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print("Tables:", tables)

# Verify embedding fields in documents table
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("PRAGMA table_info(documents)"))
    columns = result.fetchall()
    print("Documents table columns:")
    for col in columns:
        print(f"  {col[1]}: {col[2]}")
