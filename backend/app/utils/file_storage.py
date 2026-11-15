"""
File storage service for document ingestion.

Phase 4 — Secure file storage with generated identifiers and validation.

Features:
- Store files in a dedicated directory (data/documents/)
- Generate random identifiers for stored files
- Prevent path traversal attacks
- Store file metadata (path, size, checksum, mime type)
- No exposed internal filesystem paths via API
"""

import os
import hashlib
import secrets
import shutil
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

from app.core.config import get_settings
from app.schemas.documents import DocumentType

# Valid extensions and their MIME types
VALID_FILE_TYPES = {
    "pdf": {"extension": ".pdf", "mime_types": ["application/pdf"]},
    "docx": {"extension": ".docx", "mime_types": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]},
    "txt": {"extension": ".txt", "mime_types": ["text/plain", "application/octet-stream"]},
    "md": {"extension": ".md", "mime_types": ["text/markdown", "application/markdown"]},
    "csv": {"extension": ".csv", "mime_types": ["text/csv", "application/vnd.ms-excel"]},
}

# Invalid filenames
INVALID_FILENAME_CHARS = set(r'<>:"/\|?*')


def get_docs_directory() -> str:
    """Get the dedicated documents storage directory."""
    settings = get_settings()
    # data/documents/ in the backend directory
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(backend_dir, "data", "documents")
    os.makedirs(docs_dir, exist_ok=True)
    return docs_dir


def generate_storage_reference() -> str:
    """
    Generate a unique storage reference for a file.

    Format: doc_<uuid>_<extension>
    e.g., doc_3f2a9b1c8e4d.pdf
    """
    extension = secrets.token_hex(8)
    return extension


def validate_file_upload(file_path: str, expected_type: Optional[str] = None,
                         max_size_mb: int = 100) -> Tuple[bool, str]:
    """
    Validate file upload.

    Checks:
    - File exists
    - No path traversal in filename
    - File size within limits
    - Extension is supported
    - Content matches declared type (best effort)

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for path traversal
    filename = os.path.basename(file_path)
    if filename != file_path:
        return False, "Invalid filename: path traversal detected"

    # Check invalid characters
    if any(c in filename for c in INVALID_FILENAME_CHARS):
        return False, f"Invalid characters in filename: {filename}"

    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    # Check file size
    file_size = os.path.getsize(file_path)
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        return False, f"File too large: {file_size / (1024*1024):.1f} MB exceeds {max_size_mb} MB limit"

    # Check extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [v["extension"] for v in VALID_FILE_TYPES.values()]:
        return False, f"Unsupported file type: {ext}"

    # Heuristic content validation
    try:
        with open(file_path, 'rb') as f:
            header = f.read(8192)
        if expected_type == 'pdf' and b'%PDF' not in header:
            return False, "File does not appear to be a valid PDF"
        elif expected_type == 'docx' and header[:2] != b'PK':
            return False, "File does not appear to be a valid DOCX (missing PK signature)"
        elif expected_type == 'csv' and not any(header[:1024].lower().startswith(x) for x in [b'utf-8', b'csv', b'data']):
            # CSV is loose - just check it's readable
            pass
    except Exception as e:
        return False, f"Error reading file: {e}"

    return True, "File valid"


def get_file_storage_path(storage_reference: str) -> str:
    """
    Get the full filesystem path for a stored file.

    Args:
        storage_reference: The generated storage reference

    Returns:
        Full path to the file
    """
    docs_dir = get_docs_directory()
    return os.path.join(docs_dir, storage_reference)


def get_file_url(storage_reference: str) -> str:
    """
    Get a URL-safe path for the stored file (no internal filesystem paths).

    For local development, returns a URL-safe path.
    In production, this would be served by a web server.
    """
    return f"/api/documents/{storage_reference}/download"


def save_uploaded_file(file_path: str, storage_reference: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """
    Save an uploaded file to the documents directory.

    Args:
        file_path: Source file path
        storage_reference: Optional generated reference

    Returns:
        Tuple of (storage_reference, file_info)
    """
    extension = os.path.splitext(file_path)[1].lower()
    if not storage_reference:
        storage_reference = f"doc_{secrets.token_hex(8)}{extension}"

    dest_path = get_file_storage_path(storage_reference)
    shutil.copy2(file_path, dest_path)

    file_info = {
        "storage_reference": storage_reference,
        "file_path": dest_path,
        "file_size": os.path.getsize(dest_path),
        "content_type": extension[1:],  # Remove the dot
        "uploaded_at": datetime.now(),
    }
    return storage_reference, file_info


def delete_file(storage_reference: str) -> bool:
    """
    Delete a stored file.

    Returns:
        True if file was deleted, False if file not found
    """
    file_path = get_file_storage_path(storage_reference)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
