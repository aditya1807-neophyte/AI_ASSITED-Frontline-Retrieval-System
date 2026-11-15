
import sys
sys.path.insert(0, ".")

# Test import
from app.core.database import Base, engine
from app.models import User, Document, DocumentChunk, SavedItem, SearchHistory, Answer, SavedAnswer, Feedback, Escalation, AuditEvent

print("All models imported successfully")

# Create tables
from sqlalchemy import inspect
inspector = inspect(engine)
print("Tables before:", inspector.get_table_names())

Base.metadata.create_all(bind=engine)

inspector2 = inspect(engine)
print("Tables after:", inspector2.get_table_names())
