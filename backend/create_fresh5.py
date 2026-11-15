
import sys
sys.path.insert(0, ".")

from app.core.database import Base, engine
from app.models import User, Document, DocumentChunk, SavedItem, SearchHistory, Answer, SavedAnswer, Feedback, Escalation, AuditEvent

# Get the DDL for all tables
from sqlalchemy import text

print("Table creation SQL:")
for table in Base.metadata.tables.values():
    print("  Table:", table.name)
    for stmt in table.append_ddl(engine):
        print("    ", stmt)

print("\nCreating tables...")
try:
    Base.metadata.create_all(bind=engine, checkfirst=False)
    print("SUCCESS: Database tables created")
except Exception as e:
    print("ERROR:", str(e)[:300])
    import traceback
    traceback.print_exc()
