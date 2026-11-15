
import sys
sys.path.insert(0, ".")

from app.core.database import Base, engine
from app.models import User, Document, DocumentChunk, SavedItem, SearchHistory, Answer, SavedAnswer, Feedback, Escalation, AuditEvent

from sqlalchemy import inspect
inspector = inspect(engine)
print("Tables before:", inspector.get_table_names())

Base.metadata.create_all(bind=engine)

inspector2 = inspect(engine)
tables = inspector2.get_table_names()
print("Tables after:", tables)
