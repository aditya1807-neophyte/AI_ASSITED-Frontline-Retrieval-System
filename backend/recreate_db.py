from app.core.database import Base, engine
from app.models import User, Document, DocumentChunk, SavedItem, SearchHistory, Answer, SavedAnswer, Feedback, Escalation, AuditEvent
Base.metadata.create_all(bind=engine)
print("Database tables created successfully")
