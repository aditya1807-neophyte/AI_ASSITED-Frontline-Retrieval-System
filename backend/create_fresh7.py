
import sys
sys.path.insert(0, ".")

from app.core.database import Base, engine
from app.models import (
    User, Document, DocumentChunk, SavedItem, SearchHistory,
    Answer, SavedAnswer, Feedback, Escalation, AuditEvent
)

# Get ALL table creation statements
from sqlalchemy import text

print("Tables to create:")
for table_name, table in Base.metadata.tables.items():
    print(f"  {table_name}")

# Use CREATE TABLE IF NOT EXISTS with explicit column definitions
# Let's first try drop_all, then create_all
print("\nDropping all tables...")
Base.metadata.drop_all(bind=engine)

print("Creating all tables...")
Base.metadata.create_all(bind=engine)

print("SUCCESS: Database tables created")

from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print("Tables:", tables)
