import sys
sys.path.insert(0, ".")
from datetime import datetime, timezone
from app.models import Document, DocumentChunk
from app.core.database import SessionLocal, engine
from sqlalchemy import inspect, text

db = SessionLocal()

# Check documents table columns
with engine.connect() as conn:
    result = conn.execute(text("PRAGMA table_info(documents)"))
    cols = result.fetchall()
    print("Documents columns:", [c[1] for c in cols])

# Try creating a document
doc = Document(
    title="Test Document",
    document_type="standard",
    original_filename="test.pdf",
    storage_reference="test_doc_1",
    uploaded_at=datetime.now(timezone.utc),
    processing_status="indexed",
    content="Test content",
)

db.add(doc)
db.flush()

print("Document created with ID:", doc.id)

# Try creating chunk
chunk = DocumentChunk(
    document_id=doc.id,
    chunk_sequence=0,
    extracted_text="Test chunk",
)
db.add(chunk)

db.commit()
print("Chunk added successfully")
db.close()
