
import sys
sys.path.insert(0, ".")

from app.core.database import Base, engine
from app.models import User, Document, DocumentChunk, SavedItem, SearchHistory, Answer, SavedAnswer, Feedback, Escalation, AuditEvent

print("Checking tables...")
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print("Existing tables:", tables)

if not tables:
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("SUCCESS: Database tables created")
else:
    print("Warning: Tables exist:", tables)
