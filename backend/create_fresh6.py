
import sys
sys.path.insert(0, ".")

from app.core.database import Base, engine
from app.models import User, Document, DocumentChunk, SavedItem, SearchHistory, Answer, SavedAnswer, Feedback, Escalation, AuditEvent

print("Creating all tables (checkfirst=False)...")
try:
    Base.metadata.create_all(bind=engine, checkfirst=False)
    print("SUCCESS: Database tables created")
except Exception as e:
    print("ERROR:", str(e)[:400])
    import traceback
    traceback.print_exc()
