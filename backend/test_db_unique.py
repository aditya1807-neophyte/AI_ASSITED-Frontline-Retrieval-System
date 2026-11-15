
import sys
sys.path.insert(0, ".")

# Use a unique test database for this test
import tempfile
test_db = tempfile.mkdtemp(prefix="test_db_")
print("Using test DB:", test_db)

from app.core.database import Base, engine
# Override engine URL to use the temp DB
from sqlalchemy import create_engine
engine = create_engine("sqlite:///" + test_db + "/test.db", connect_args={'check_same_thread': False})

from app.models import User, Document, DocumentChunk, SavedItem, SearchHistory, Answer, SavedAnswer, Feedback, Escalation, AuditEvent

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)

print("Creating all tables...")
Base.metadata.create_all(bind=engine)

print("SUCCESS: Database tables created")

from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print("Tables:", tables)
