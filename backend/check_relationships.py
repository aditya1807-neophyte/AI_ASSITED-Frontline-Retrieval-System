import sys
sys.path.insert(0, ".")
from app.models import Document, DocumentChunk, User
from sqlalchemy import inspect

# Print Document relationships
print("=== Document class ===")
print("Table:", Document.__tablename__)
print("Columns:", [c.name for c in Document.__table__.columns])
print("Relationships:")
for attr in dir(Document):
    if attr.startswith('_') or attr in ['id', 'chunks']:
        continue
    v = getattr(Document, attr)
    if hasattr(v, 'property'):
        print("  ", attr)
print()

# Print DocumentChunk relationships
print("=== DocumentChunk class ===")
print("Table:", DocumentChunk.__tablename__)
print("Columns:", [c.name for c in DocumentChunk.__table__.columns])
print("Relationships:")
for attr in dir(DocumentChunk):
    if attr.startswith('_') or attr in ['id', 'document']:
        continue
    v = getattr(DocumentChunk, attr)
    if hasattr(v, 'property'):
        print("  ", attr)
