
import sys
sys.path.insert(0, ".")
import os

# Remove any existing test db
db_file = "data/frontline.db"
if os.path.exists(db_file):
    os.remove(db_file)

# Also clear __pycache__ 
import glob
for pc in glob.glob("app/__pycache__/*.pyc") + glob.glob("app/models/__pycache__/*.pyc"):
    if os.path.exists(pc):
        os.remove(pc)

from app.core.database import Base, engine
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
