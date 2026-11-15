
import sys
sys.path.insert(0, ".")

from app.core.database import Base, engine
from app.models import User, Document, DocumentChunk, SavedItem, SearchHistory, Answer, SavedAnswer, Feedback, Escalation, AuditEvent

print("Engine URL:", engine.url)
print("Engine:", engine)

from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print("Existing tables:", tables)

# Try drop_all
print("\nDropping all tables...")
Base.metadata.drop_all(bind=engine)

# Check if tables still exist
inspector2 = inspect(engine)
tables2 = inspector2.get_table_names()
print("Tables after drop:", tables2)

# Try create_all with checkfirst=False
print("\nCreating all tables (checkfirst=False)...")
try:
    Base.metadata.create_all(bind=engine, checkfirst=False)
    print("SUCCESS")
except Exception as e:
    print("ERROR:", str(e)[:300])
