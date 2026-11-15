
import sys
sys.path.insert(0, ".")

from app.core.database import SessionLocal
from app.models import Document, DocumentChunk
from sqlalchemy import func

db = SessionLocal()

# Count documents
doc_count = db.query(Document).count()
print("Total documents:", doc_count)

# List all documents with basic info
docs = db.query(Document).all()
for doc in docs:
    print(f"  - {doc.title} ({doc.document_type}) - status: {doc.document_status}, processing: {doc.processing_status}")
    print(f"    Description: {doc.description[:50]}...")
    print(f"    Original filename: {doc.original_filename}")
    print(f"    Version: {doc.version}, Tags: {doc.tags}")

# Count chunks
chunk_count = db.query(DocumentChunk).count()
print("Total chunks:", chunk_count)

# Count chunks per document
for doc in docs:
    chunks = db.query(DocumentChunk).filter_by(document_id=doc.id).all()
    print(f"    Chunks for {doc.title}: {len(chunks)}")

db.close()
