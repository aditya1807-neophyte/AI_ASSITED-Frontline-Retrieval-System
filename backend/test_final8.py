
import sys
sys.path.insert(0, ".")

from app.core.database import Base, engine
from app.models import User, Document, DocumentChunk, SavedItem, SearchHistory, Answer, SavedAnswer, Feedback, Escalation, AuditEvent

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)

print("Creating all tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("SUCCESS: Database tables created")
except Exception as e:
    import traceback
    traceback.print_exc()
