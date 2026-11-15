
import sys
sys.path.insert(0, ".")

from app.core.database import Base, engine
from app.models import User, Document, DocumentChunk, SavedItem, SearchHistory, Answer, SavedAnswer, Feedback, Escalation, AuditEvent

from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()

# Drop all tables
print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)

# Recreate all tables
print("Creating all tables...")
Base.metadata.create_all(bind=engine)

# Verify tables
inspector2 = inspect(engine)
tables2 = inspector2.get_table_names()
print("Tables:", tables2)

# Check for embedding fields in documents table
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("PRAGMA table_info(documents)"))
    columns = result.fetchall()
    print("\nDocuments table columns:")
    for col in columns:
        print(f"  {col[1]}: {col[2]}")
