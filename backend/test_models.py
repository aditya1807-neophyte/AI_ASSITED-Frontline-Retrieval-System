
import sys
sys.path.insert(0, ".")

try:
    from app.models import User, Document, DocumentChunk, SavedItem, SearchHistory, Answer, SavedAnswer, Feedback, Escalation, AuditEvent
    print("All models imported successfully!")
    print("Models found:", [Name for Name in ["User", "Document", "DocumentChunk", "SavedItem", "SearchHistory", "Answer", "SavedAnswer", "Feedback", "Escalation", "AuditEvent"] if Name in dir()])
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
