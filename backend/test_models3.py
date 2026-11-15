
import sys
sys.path.insert(0, ".")

from app.models import User, Document, DocumentChunk, SavedItem, SearchHistory, Answer, SavedAnswer, Feedback, Escalation, AuditEvent

print("All models imported successfully!")
print("User:", User.__name__)
print("Document:", Document.__name__)
print("DocumentChunk:", DocumentChunk.__name__)
print("SavedItem:", SavedItem.__name__)
print("SearchHistory:", SearchHistory.__name__)
print("Answer:", Answer.__name__)
print("SavedAnswer:", SavedAnswer.__name__)
print("Feedback:", Feedback.__name__)
print("Escalation:", Escalation.__name__)
print("AuditEvent:", AuditEvent.__name__)
