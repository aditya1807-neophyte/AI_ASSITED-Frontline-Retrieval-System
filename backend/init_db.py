"""
Database initialization script for the frontend-retrieval backend.

Phase 3 — Database initialization.
"""

import os
import sys
from pathlib import Path


def main():
    """Initialize the database with all schema tables."""
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Add the backend directory to the path
    backend_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(backend_dir))

    from app.core.config import get_settings
    from app.core.database import Base, engine
    from app.models import Base as AllModelsBase

    settings = get_settings()

    # Ensure the data directory exists
    db_path = settings.database_url.replace("sqlite:///", "")
    if not db_path.startswith("/"):
        db_path = os.path.abspath(db_path)
    db_dir = os.path.dirname(db_path)
    os.makedirs(db_dir, exist_ok=True)

    logger.info(f"Initializing database at: {db_path}")

    # Create all tables
    AllModelsBase.metadata.create_all(bind=engine)

    # Count tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Tables created/verified: {', '.join(tables)}")

    # Insert demo data if the database is empty
    from sqlalchemy.orm import Session
    from app.models import User, Document, SearchHistory

    with Session(engine) as session:
        user_count = session.query(User).count()
        if user_count == 0:
            # Create demo admin user
            from datetime import datetime, timezone
            admin_user = User(
                display_name="Admin User",
                login_identifier="admin",
                password_hash="",
                role="admin",
                account_status="active",
                created_at=datetime.now(timezone.utc),
            )
            session.add(admin_user)
            session.commit()
            logger.info("Created demo admin user: admin")

            # Create demo analyst user
            analyst_user = User(
                display_name="Analyst User",
                login_identifier="analyst",
                password_hash="",
                role="analyst",
                account_status="active",
                created_at=datetime.now(timezone.utc),
            )
            session.add(analyst_user)
            session.commit()
            logger.info("Created demo analyst user: analyst")

            # Create demo documents
            from app.models import Document
            import datetime as dt
            doc1 = Document(
                title="Standard Operating Procedure: Field Equipment Calibration",
                description="SOP for field equipment calibration procedures",
                document_type="PDF",
                topic="Operations",
                intended_role="Field Technician",
                source_organization="Field Operations Division",
                original_filename="SOP-Field-Equipment-Calibration.pdf",
                storage_reference="s3://fieldguide-docs/sop-calibration-2026.pdf",
                language="en",
                tags="['calibration', 'SOP', 'field-equipment']",
                version="3.2",
                document_status="active",
                effective_date=dt.datetime(2026, 6, 15),
                review_date=dt.datetime(2027, 6, 15),
                processing_status="active",
                uploaded_at=dt.datetime.now(timezone.utc),
            )
            session.add(doc1)

            doc2 = Document(
                title="Safety Protocol for Hazardous Materials Handling",
                description="Safety requirements for hazardous materials handling",
                document_type="PDF",
                topic="Safety",
                intended_role="All Staff",
                source_organization="Safety & Compliance Team",
                original_filename="Safety-Hazmat-Protocol.pdf",
                storage_reference="s3://fieldguide-docs/safety-hazmat-v2.1.pdf",
                language="en",
                tags="['safety', 'hazardous-materials', 'compliance']",
                version="2.1",
                document_status="active",
                effective_date=dt.datetime(2026, 9, 1),
                review_date=dt.datetime(2027, 9, 1),
                processing_status="active",
                uploaded_at=dt.datetime.now(timezone.utc),
            )
            session.add(doc2)

            session.commit()
            logger.info(f"Database initialized with {len(tables)} tables")
        else:
            logger.info(f"Database already has {user_count} users")

    logger.info("Database initialization complete.")


if __name__ == "__main__":
    main()
