# -*- coding: utf-8 -*-
"""
Frontline Knowledge Repository Seeder.

Builds a structured knowledge repository for frequently used frontline documents,
procedures, and forms with role, topic, and source metadata.
"""

import sys
import os
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models import User, Document, DocumentChunk, Escalation, SavedItem, Answer
from app.core.vector_store import VectorStore

REPOS_DOCS = [
    {
        "title": "SOP-001: Standard Operating Procedure for Field Equipment Calibration",
        "description": "Standardized quarterly sensor drift verification, zero-offset tolerances, and laboratory master instrument calibration protocols for field technicians.",
        "document_type": "SOP",
        "topic": "operations",
        "intended_role": "field_technician",
        "source_organization": "Field Operations & Metrology Division",
        "original_filename": "SOP-001-Equipment-Calibration.pdf",
        "version": "3.2",
        "status": "active",
        "tags": ["calibration", "sensors", "drift-tolerance", "Form-4B", "metrology"],
        "num_pages": 14,
        "chunks": [
            {
                "section": "§1.1 Scope and Frequency",
                "page": 1,
                "content": "This Standard Operating Procedure applies to all field pressure transmitters, digital multimeters, thermocouple probes, and differential flowcells. All active instrumentation must undergo verification every 90 calendar days or immediately following any mechanical shock event exceeding 5G.",
            },
            {
                "section": "§2.4 Zero-Offset Drift Tolerance",
                "page": 4,
                "content": "Before taking field measurements, technicians must perform a zero-offset baseline test. The maximum permissible drift for gauge pressure sensors is ±0.25% of full scale. If measured drift exceeds 0.50%, the sensor must be removed from field service immediately and routed to the central metrology lab.",
            },
            {
                "section": "§3.2 Environmental Compensation & Form 4B",
                "page": 7,
                "content": "Ambient temperature fluctuations above 35°C (95°F) require thermal compensation coefficient adjustment before logging readings. Technicians must record all calibration standards, ambient humidity, and reference gauge IDs in Calibration Log Form 4B and obtain supervisory sign-off.",
            },
        ],
    },
    {
        "title": "SOP-002: Hazardous Materials & Chemical Protective Equipment Protocols",
        "description": "Mandatory safety procedures, personal protective equipment (PPE Level B/C), chemical breakthrough thresholds, and respirator cartridge standards.",
        "document_type": "Policy",
        "topic": "safety",
        "intended_role": "safety_officer",
        "source_organization": "Safety & Environmental Directorate",
        "original_filename": "SOP-002-Hazardous-PPE.pdf",
        "version": "2.1",
        "status": "active",
        "tags": ["hazmat", "PPE", "Level-B", "chemical-safety", "respirators"],
        "num_pages": 18,
        "chunks": [
            {
                "section": "§1.2 Chemical Risk Assessment and PPE Levels",
                "page": 2,
                "content": "Handling concentrated corrosive chemicals (hydrochloric acid >30%, sulfuric acid >50%, or caustic lye) mandates Level B protective equipment including a vapor-tight hooded chemical suit, butyl rubber gloves, chemical-resistant steel-toe boots, and positive-pressure SCBA or supplied-air respirator.",
            },
            {
                "section": "§2.1 Glove Breakthrough and Inspection",
                "page": 5,
                "content": "Nitrile disposable gloves provide splash protection only (<15 minutes breakthrough time for aromatic solvents). For prolonged solvent immersion, neoprene or heavy butyl gloves must be inspected for pinholes using the air-roll test prior to entering the chemical transfer zone.",
            },
            {
                "section": "§4.3 Eye Wash and Decontamination Station Rules",
                "page": 11,
                "content": "Emergency eyewash stations must be located within 10 seconds (unobstructed walking distance) of all chemical dispensing points. In case of chemical splash contact, flush affected areas continuously with tepid water for a minimum of 15 minutes before medical triage transfer.",
            },
        ],
    },
    {
        "title": "SOP-003: Lockout / Tagout (LOTO) & Zero-Energy State Verification",
        "description": "Hazardous electrical, mechanical, and pneumatic energy control procedures, group lockout stations, and zero-energy state verification.",
        "document_type": "Procedure",
        "topic": "electrical",
        "intended_role": "maintenance_engineer",
        "source_organization": "Engineering & Electrical Safety Committee",
        "original_filename": "SOP-003-LOTO-Zero-Energy.pdf",
        "version": "4.0",
        "status": "active",
        "tags": ["LOTO", "electrical", "zero-energy", "480V", "Form-E12"],
        "num_pages": 22,
        "chunks": [
            {
                "section": "§1.4 Golden Rules of Electrical Isolation",
                "page": 3,
                "content": "Never work on equipment until zero-energy state has been verified with a calibrated high-voltage multimeter tested against a known live source immediately before and after measurement (Test-Before-Touch / Live-Dead-Live method).",
            },
            {
                "section": "§2.2 Multi-Padlock Group Lockout Protocols",
                "page": 8,
                "content": "When multiple craft teams service common machinery, each authorized technician must place their personal identifiable safety lock on the group lockout hasp. No employee may remove another worker's lock except under the Emergency Lock Removal Protocol with written approval from the Plant Manager.",
            },
            {
                "section": "§3.1 Pneumatic and Hydraulic Energy Dissipation",
                "page": 14,
                "content": "Bleed all hydraulic accumulators and discharge air receiver tanks to 0 psig. Insert mechanical positive-blocking pins into raised pneumatic rams or counterweights before allowing personnel underneath elevated machinery.",
            },
        ],
    },
    {
        "title": "SOP-004: Confined Space Atmospheric Gas Triage & Rescue Protocol",
        "description": "Multi-gas atmospheric testing, permit-required confined space entry prerequisites, continuous ventilation, and non-entry rescue retrieval systems.",
        "document_type": "Standard",
        "topic": "safety",
        "intended_role": "site_supervisor",
        "source_organization": "OSHA & Corporate Safety Division",
        "original_filename": "SOP-004-Confined-Space.pdf",
        "version": "3.1",
        "status": "active",
        "tags": ["confined-space", "gas-sniffing", "O2-levels", "rescue", "Permit-CS1"],
        "num_pages": 16,
        "chunks": [
            {
                "section": "§2.1 Permissible Atmospheric Entry Limits",
                "page": 4,
                "content": "Atmospheric testing must confirm: Oxygen between 19.5% and 23.5%, Combustible Gas (LEL) below 10%, Carbon Monoxide below 25 ppm, and Hydrogen Sulfide (H2S) below 10 ppm. Testing must be performed at top, middle, and bottom strata before entry.",
            },
            {
                "section": "§3.3 Standby Attendant and Non-Entry Rescue",
                "page": 9,
                "content": "A designated safety attendant must remain stationed outside the confined space opening at all times. Entrants must be secured to a mechanical tripod retrieval winch via chest or dorsal D-ring harness. Under no circumstances may an attendant enter to attempt rescue without backup entry teams.",
            },
        ],
    },
    {
        "title": "SOP-005: High-Voltage Substation Switching & Arc Flash Boundary Protocols",
        "description": "13.8kV electrical switching orders, arc flash incident energy calculations, 40-cal arc flash suits, and ground disconnect interlocking.",
        "document_type": "Procedure",
        "topic": "electrical",
        "intended_role": "maintenance_engineer",
        "source_organization": "High Voltage Engineering Division",
        "original_filename": "SOP-005-High-Voltage-Arc-Flash.pdf",
        "version": "1.5",
        "status": "active",
        "tags": ["high-voltage", "13.8kV", "arc-flash", "substation", "hot-stick"],
        "num_pages": 24,
        "chunks": [
            {
                "section": "§1.3 Arc Flash Boundary Distances and Suit Ratings",
                "page": 5,
                "content": "Within the 13.8kV arc flash boundary (minimum 12 feet clearance), personnel must wear a minimum 40 cal/cm² arc flash suit with hood, face shield, and Class 2 insulated dielectric gloves. Racking circuit breakers must be performed remotely whenever umbilical control cords are fitted.",
            },
            {
                "section": "§3.2 Ground Cluster Attachment Sequence",
                "page": 12,
                "content": "When applying safety grounds to de-energized busbars: always connect the ground clamp to the earth bus first, then use a tested fiberglass hot stick to attach phase clamps. When removing, detach phase clamps first before disconnecting earth.",
            },
        ],
    },
    {
        "title": "SOP-006: Emergency Incident Escalation & Safety Discrepancy Reporting Matrix",
        "description": "Protocols for raising immediate stop-work orders, escalating policy contradictions between manuals, and tracking engineering resolution.",
        "document_type": "Policy",
        "topic": "compliance",
        "intended_role": "operations_analyst",
        "source_organization": "Operational Risk & Compliance Board",
        "original_filename": "SOP-006-Incident-Escalation.pdf",
        "version": "2.0",
        "status": "active",
        "tags": ["escalation", "stop-work", "ambiguity", "compliance", "Form-ESC1"],
        "num_pages": 10,
        "chunks": [
            {
                "section": "§1.1 Stop-Work Authority & Escalation Triggers",
                "page": 2,
                "content": "Any frontline technician, engineer, or contractor possesses full stop-work authority when encountering unmanaged hazards, unverified zero-energy conditions, or direct conflicts between manufacturer specifications and company procedures. Work must cease without fear of reprisal.",
            },
            {
                "section": "§2.4 Technical Escalation Submission Window",
                "page": 6,
                "content": "Safety discrepancies and ungrounded procedural gaps must be submitted through the Escalation Center within 2 hours of occurrence. The assigned Engineering Reviewer must acknowledge high-priority cases within 30 minutes and issue written corrective directives.",
            },
        ],
    },
    {
        "title": "SOP-007: Remote Field Vehicle Telematics & Lone Worker Check-in Procedure",
        "description": "Satellite check-in protocols, emergency distress beacons, automated geo-fence alerts, and extreme weather transit guidelines.",
        "document_type": "Standard",
        "topic": "operations",
        "intended_role": "field_technician",
        "source_organization": "Field Logistics & Regional Dispatch",
        "original_filename": "SOP-007-Lone-Worker.pdf",
        "version": "1.8",
        "status": "active",
        "tags": ["lone-worker", "dispatch", "telematics", "satellite", "check-in"],
        "num_pages": 12,
        "chunks": [
            {
                "section": "§2.2 Mandatory Check-in Intervals",
                "page": 4,
                "content": "Technicians operating solo at remote field substations or pipeline valve stations must complete an automated check-in via handheld satellite telematics every 120 minutes. Missing two consecutive check-in pings initiates Level 2 dispatch emergency response.",
            },
        ],
    },
    {
        "title": "SOP-008: Pressure Relief Valve (PRV) Recertification & Bench Calibration",
        "description": "ASME Section VIII set-point tolerance verification, nitrogen popping stand tests, and bubble-leak tightness testing per API 527.",
        "document_type": "SOP",
        "topic": "mechanical",
        "intended_role": "maintenance_engineer",
        "source_organization": "Mechanical Integrity & Pressure Systems",
        "original_filename": "SOP-008-PRV-Recertification.pdf",
        "version": "2.3",
        "status": "active",
        "tags": ["PRV", "ASME", "pressure-relief", "API-527", "nitrogen"],
        "num_pages": 20,
        "chunks": [
            {
                "section": "§2.3 Set Pressure Tolerance Limits",
                "page": 6,
                "content": "For relief valves with set pressure up to 70 psig, allowable tolerance is ±2 psig. For set pressures exceeding 70 psig, allowable set tolerance is ±3%. Each valve must achieve 3 consecutive pops within tolerance before lead sealing wire and Form PRV-3 inspection tag are attached.",
            },
        ],
    },
]


def seed_database():
    """Seed users, documents, and document chunks."""
    db = SessionLocal()
    try:
        print("Seeding Users...")
        # 1. Seed standard frontline users
        existing_users = {u.login_identifier: u for u in db.query(User).all()}

        default_users = [
            {"login_identifier": "jordan.diaz", "display_name": "Jordan Diaz", "role": "analyst"},
            {"login_identifier": "sarah.chen", "display_name": "Sarah Chen", "role": "safety_officer"},
            {"login_identifier": "marcus.vance", "display_name": "Marcus Vance", "role": "maintenance_engineer"},
            {"login_identifier": "elena.rostova", "display_name": "Elena Rostova", "role": "site_supervisor"},
            {"login_identifier": "carlos.mendez", "display_name": "Carlos Mendez", "role": "field_technician"},
        ]

        for u_data in default_users:
            if u_data["login_identifier"] not in existing_users:
                user = User(
                    login_identifier=u_data["login_identifier"],
                    display_name=u_data["display_name"],
                    role=u_data["role"],
                    account_status="active",
                )
                db.add(user)
        db.commit()

        # Refresh users map
        users_map = {u.login_identifier: u for u in db.query(User).all()}
        admin_user_id = users_map["jordan.diaz"].id

        print("Seeding Structured Knowledge Repository Documents...")
        existing_doc_titles = {d.title for d in db.query(Document).all()}

        total_chunks_added = 0
        total_docs_added = 0

        for doc_data in REPOS_DOCS:
            if doc_data["title"] in existing_doc_titles:
                continue

            doc = Document(
                user_id=admin_user_id,
                title=doc_data["title"],
                description=doc_data["description"],
                document_type=doc_data["document_type"],
                topic=doc_data["topic"],
                intended_role=doc_data["intended_role"],
                source_organization=doc_data["source_organization"],
                original_filename=doc_data["original_filename"],
                version=doc_data["version"],
                document_status=doc_data["status"],
                tags=json.dumps(doc_data["tags"]),
                num_pages=doc_data["num_pages"],
                processing_status="completed",
                processed_at=datetime.now(timezone.utc),
                content="\n\n".join(c["content"] for c in doc_data["chunks"]),
                is_semantic_enabled=True,
            )
            db.add(doc)
            db.flush()  # assign doc.id

            total_docs_added += 1

            for idx, c_data in enumerate(doc_data["chunks"]):
                chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_sequence=idx + 1,
                    extracted_text=c_data["content"],
                    page_reference=str(c_data["page"]),
                    section_heading=c_data["section"],
                    chunk_metadata=json.dumps({
                        "token_count": len(c_data["content"].split()),
                        "checksum": f"chk-{doc.id}-{idx}"
                    }),
                )
                db.add(chunk)
                total_chunks_added += 1

        db.commit()
        print(f"Added {total_docs_added} new documents with {total_chunks_added} structured chunks.")

        # Seed initial open escalation for demo
        existing_esc = db.query(Escalation).count()
        if existing_esc == 0:
            esc = Escalation(
                user_id=admin_user_id,
                question="Conflicting instructions between SOP-003 and manufacturer breaker manual regarding 480V auxiliary trip test sequence.",
                context="During quarterly outage in Substation B, the primary breaker trip unit failed to indicate trip flag when manual lever was depressed.",
                evidence_references="[SOP-003 §1.4] vs [GE-Breaker-Man p.42]",
                status="open",
                priority="high",
                assigned_reviewer=users_map["sarah.chen"].id,
                review_notes="Assigned to Senior Safety Officer. Stop-work advisory issued for Substation B motor control center.",
            )
            db.add(esc)
            db.commit()
            print("Seeded default active escalation ticket.")

        # Total counts
        doc_count = db.query(Document).count()
        chunk_count = db.query(DocumentChunk).count()
        user_count = db.query(User).count()
        print(f"Repository state: {doc_count} documents, {chunk_count} chunks, {user_count} users.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
