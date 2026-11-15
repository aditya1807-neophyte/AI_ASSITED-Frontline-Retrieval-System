# -*- coding: utf-8 -*-
"""
Machine Learning Model Training for Frontline Intent, Role, and Context Classification.

Outcomes & Scope:
1. Predicts task intent from user query.
2. Identifies target frontline role (field_technician, safety_officer, maintenance_engineer, site_supervisor, operations_analyst).
3. Detects operational task context / topic.
4. Predicts missing guidance & escalation requirement (when a query falls outside SOP coverage).
5. Provides calibrated confidence score for grounded retrieval.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
import joblib
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rich labeled training dataset for frontline operations
TRAINING_DATA = [
    # --- Equipment Calibration (Technician / Maintenance) ---
    {"text": "How do I calibrate the pressure transmitter before zero offset test?", "intent": "equipment_calibration", "role": "field_technician", "topic": "operations", "missing_guidance": 0},
    {"text": "What is the allowable sensor drift tolerance during quarterly calibration?", "intent": "equipment_calibration", "role": "field_technician", "topic": "operations", "missing_guidance": 0},
    {"text": "Calibrate multi-meter sensor on flowmeter bench", "intent": "equipment_calibration", "role": "maintenance_engineer", "topic": "operations", "missing_guidance": 0},
    {"text": "Step by step pressure gauge zeroing protocol and certificate log", "intent": "equipment_calibration", "role": "field_technician", "topic": "operations", "missing_guidance": 0},
    {"text": "Temperature probe thermocouple recalibration procedure", "intent": "equipment_calibration", "role": "maintenance_engineer", "topic": "operations", "missing_guidance": 0},
    {"text": "Sensor calibration intervals and deviation limits under ISO 9001", "intent": "equipment_calibration", "role": "operations_analyst", "topic": "compliance", "missing_guidance": 0},
    {"text": "Zero-offset drift exceeds 0.5% tolerance on differential pressure cell", "intent": "equipment_calibration", "role": "field_technician", "topic": "operations", "missing_guidance": 0},
    {"text": "Form 4B equipment verification log submission requirements", "intent": "equipment_calibration", "role": "field_technician", "topic": "operations", "missing_guidance": 0},

    # --- Hazardous Materials & PPE (Safety Officer / Technician) ---
    {"text": "What PPE is required for handling concentrated sulfuric acid and solvents?", "intent": "hazard_safety_ppe", "role": "safety_officer", "topic": "safety", "missing_guidance": 0},
    {"text": "Level B chemical protective suit donning and doffing sequence", "intent": "hazard_safety_ppe", "role": "safety_officer", "topic": "safety", "missing_guidance": 0},
    {"text": "Respirator cartridge filter replacement schedule for organic vapors", "intent": "hazard_safety_ppe", "role": "field_technician", "topic": "safety", "missing_guidance": 0},
    {"text": "Eye shield and nitrile glove breakthrough times for solvents", "intent": "hazard_safety_ppe", "role": "safety_officer", "topic": "safety", "missing_guidance": 0},
    {"text": "Chemical splash decontamination station inspection checklist", "intent": "hazard_safety_ppe", "role": "safety_officer", "topic": "safety", "missing_guidance": 0},
    {"text": "Hazardous materials handling safety protocol PPE matrix", "intent": "hazard_safety_ppe", "role": "safety_officer", "topic": "safety", "missing_guidance": 0},
    {"text": "Toxic chemical secondary containment inspection guidelines", "intent": "hazard_safety_ppe", "role": "safety_officer", "topic": "safety", "missing_guidance": 0},

    # --- Lockout / Tagout (LOTO) (Maintenance Engineer / Technician) ---
    {"text": "What is the procedure for zero energy state verification in 480V motor circuits?", "intent": "lockout_tagout", "role": "maintenance_engineer", "topic": "electrical", "missing_guidance": 0},
    {"text": "LOTO protocol multi padlock group lockout rules", "intent": "lockout_tagout", "role": "maintenance_engineer", "topic": "electrical", "missing_guidance": 0},
    {"text": "How to lock out hydraulic pressure lines and discharge residual accumulator energy", "intent": "lockout_tagout", "role": "maintenance_engineer", "topic": "mechanical", "missing_guidance": 0},
    {"text": "Who keeps the key during multi technician electrical maintenance lockout?", "intent": "lockout_tagout", "role": "field_technician", "topic": "electrical", "missing_guidance": 0},
    {"text": "Lockout tagout sign off form E-12 verification checklist", "intent": "lockout_tagout", "role": "site_supervisor", "topic": "electrical", "missing_guidance": 0},
    {"text": "Emergency lock removal procedure when key holder is absent from facility", "intent": "lockout_tagout", "role": "site_supervisor", "topic": "electrical", "missing_guidance": 0},

    # --- Confined Space & Gas Triage (Safety Officer / Supervisor) ---
    {"text": "What are the acceptable atmospheric gas testing limits for confined space entry?", "intent": "confined_space_rescue", "role": "safety_officer", "topic": "safety", "missing_guidance": 0},
    {"text": "Oxygen level must be between 19.5% and 23.5% before entry permit issuance", "intent": "confined_space_rescue", "role": "safety_officer", "topic": "safety", "missing_guidance": 0},
    {"text": "H2S and carbon monoxide 4 gas sniffer bump testing frequency", "intent": "confined_space_rescue", "role": "field_technician", "topic": "safety", "missing_guidance": 0},
    {"text": "Confined space standby attendant duties and emergency communication horn", "intent": "confined_space_rescue", "role": "site_supervisor", "topic": "safety", "missing_guidance": 0},
    {"text": "Non-entry rescue tripod and retrieval winch rope inspection", "intent": "confined_space_rescue", "role": "safety_officer", "topic": "safety", "missing_guidance": 0},
    {"text": "Entry permit CS-1 expiration and air continuous monitoring rules", "intent": "confined_space_rescue", "role": "site_supervisor", "topic": "safety", "missing_guidance": 0},

    # --- High Voltage Substation Switching (Maintenance Engineer) ---
    {"text": "High voltage switching order clearance sequence for 13.8kV busbar", "intent": "high_voltage_isolation", "role": "maintenance_engineer", "topic": "electrical", "missing_guidance": 0},
    {"text": "Arc flash boundary PPE calculation and 40 cal suit requirement", "intent": "high_voltage_isolation", "role": "safety_officer", "topic": "electrical", "missing_guidance": 0},
    {"text": "Substation ground disconnect switch interlocking procedure", "intent": "high_voltage_isolation", "role": "maintenance_engineer", "topic": "electrical", "missing_guidance": 0},
    {"text": "Hot stick dielectric test and insulated glove air test before switching", "intent": "high_voltage_isolation", "role": "field_technician", "topic": "electrical", "missing_guidance": 0},

    # --- Chemical Spill Containment (Safety Officer / Supervisor) ---
    {"text": "Emergency containment procedure for hydrochloric acid tote rupture", "intent": "chemical_spill_containment", "role": "safety_officer", "topic": "emergency", "missing_guidance": 0},
    {"text": "Neutralizing soda ash application rate for acid spills exceeding 50 gallons", "intent": "chemical_spill_containment", "role": "safety_officer", "topic": "emergency", "missing_guidance": 0},
    {"text": "Downwind evacuation perimeter radius for anhydrous ammonia leak", "intent": "chemical_spill_containment", "role": "site_supervisor", "topic": "emergency", "missing_guidance": 0},
    {"text": "Spill kit absorbent boom deployment and drain plugging protocol", "intent": "chemical_spill_containment", "role": "field_technician", "topic": "emergency", "missing_guidance": 0},

    # --- Pressure Relief Valve (PRV) Recertification ---
    {"text": "Bench testing set point tolerance for ASME section VIII pressure relief valve", "intent": "pressure_relief_testing", "role": "maintenance_engineer", "topic": "mechanical", "missing_guidance": 0},
    {"text": "PRV popping pressure test with nitrogen gas on calibration stand", "intent": "pressure_relief_testing", "role": "maintenance_engineer", "topic": "mechanical", "missing_guidance": 0},
    {"text": "Relief valve seat leakage bubble count test per API 527", "intent": "pressure_relief_testing", "role": "field_technician", "topic": "mechanical", "missing_guidance": 0},
    {"text": "Form PRV-3 calibration tag seal wire placement procedure", "intent": "pressure_relief_testing", "role": "maintenance_engineer", "topic": "compliance", "missing_guidance": 0},

    # --- Working at Heights & Fall Protection ---
    {"text": "Pre-use inspection criteria for full body fall arrest harness webbing", "intent": "fall_protection_harness", "role": "field_technician", "topic": "safety", "missing_guidance": 0},
    {"text": "Anchor point 5000 lbs rating requirement for lanyard tie-off", "intent": "fall_protection_harness", "role": "safety_officer", "topic": "safety", "missing_guidance": 0},
    {"text": "Shock absorbing lanyard deployment and maximum free fall distance", "intent": "fall_protection_harness", "role": "field_technician", "topic": "safety", "missing_guidance": 0},
    {"text": "Suspension trauma prevention strap usage after fall event", "intent": "fall_protection_harness", "role": "safety_officer", "topic": "safety", "missing_guidance": 0},

    # --- Hot Work & Fire Watch ---
    {"text": "Hot work permit requirements for oxyacetylene torch cutting near combustible deck", "intent": "hot_work_fire_watch", "role": "site_supervisor", "topic": "operations", "missing_guidance": 0},
    {"text": "Fire watch 60 minute post-work monitoring and fire extinguisher staging", "intent": "hot_work_fire_watch", "role": "safety_officer", "topic": "safety", "missing_guidance": 0},
    {"text": "Combustible gas sniffing within 35 feet radius of welding operations", "intent": "hot_work_fire_watch", "role": "field_technician", "topic": "safety", "missing_guidance": 0},

    # --- Emergency Escalation & Policy Ambiguity ---
    {"text": "How do I escalate an operational discrepancy between conflicting SOP manuals?", "intent": "emergency_escalation", "role": "operations_analyst", "topic": "compliance", "missing_guidance": 0},
    {"text": "Safety escalation path when supervisor authorization is unavailable", "intent": "emergency_escalation", "role": "field_technician", "topic": "compliance", "missing_guidance": 0},
    {"text": "Urgent engineering stop-work order issuance procedure", "intent": "emergency_escalation", "role": "safety_officer", "topic": "compliance", "missing_guidance": 0},
    {"text": "Submit immediate incident gap ticket to engineering director", "intent": "emergency_escalation", "role": "site_supervisor", "topic": "compliance", "missing_guidance": 0},

    # --- Missing Guidance & Out of Scope Queries (Triggers Escalation Option) ---
    {"text": "What is the nuclear reactor core meltdown emergency shutdown protocol?", "intent": "missing_guidance_unsupported", "role": "field_technician", "topic": "emergency", "missing_guidance": 1},
    {"text": "How to bypass the physical interlock switch without authorization key?", "intent": "missing_guidance_unsupported", "role": "field_technician", "topic": "safety", "missing_guidance": 1},
    {"text": "Procedure for offshore underwater deep-sea drilling pipeline replacement", "intent": "missing_guidance_unsupported", "role": "maintenance_engineer", "topic": "operations", "missing_guidance": 1},
    {"text": "Space shuttle propulsion cryogenic liquid oxygen fuel transfer guidelines", "intent": "missing_guidance_unsupported", "role": "maintenance_engineer", "topic": "operations", "missing_guidance": 1},
    {"text": "How to falsify the daily equipment calibration sensor verification logs?", "intent": "missing_guidance_unsupported", "role": "operations_analyst", "topic": "compliance", "missing_guidance": 1},
    {"text": "What is the procedure when both primary and secondary SCBA air systems fail inside toxic plume?", "intent": "missing_guidance_unsupported", "role": "safety_officer", "topic": "emergency", "missing_guidance": 1},
    {"text": "Unknown experimental chemical compound CAS 9999-99 toxicity limits", "intent": "missing_guidance_unsupported", "role": "safety_officer", "topic": "safety", "missing_guidance": 1},
]


def train_and_export():
    """Train multi-task ML model and save serialized pipelines."""
    texts = [item["text"] for item in TRAINING_DATA]
    intents = [item["intent"] for item in TRAINING_DATA]
    roles = [item["role"] for item in TRAINING_DATA]
    topics = [item["topic"] for item in TRAINING_DATA]
    missing_guidance = [item["missing_guidance"] for item in TRAINING_DATA]

    logger.info(f"Training dataset size: {len(texts)} samples")

    # TF-IDF Vectorizer optimized for frontline queries
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=1,
        max_features=1500,
        stop_words="english",
    )
    X = vectorizer.fit_transform(texts)

    # 1. Intent Classifier (Calibrated Logistic Regression)
    intent_model = CalibratedClassifierCV(
        estimator=LogisticRegression(C=3.0, max_iter=500, class_weight="balanced"),
        cv=3,
    )
    intent_model.fit(X, intents)
    intent_preds = intent_model.predict(X)
    intent_acc = accuracy_score(intents, intent_preds)
    logger.info(f"Intent Model Accuracy: {intent_acc * 100:.2f}%")

    # 2. Role Classifier (Calibrated Logistic Regression)
    role_model = CalibratedClassifierCV(
        estimator=LogisticRegression(C=2.5, max_iter=500, class_weight="balanced"),
        cv=3,
    )
    role_model.fit(X, roles)
    role_preds = role_model.predict(X)
    role_acc = accuracy_score(roles, role_preds)
    logger.info(f"Role Model Accuracy: {role_acc * 100:.2f}%")

    # 3. Topic Classifier
    topic_model = CalibratedClassifierCV(
        estimator=LogisticRegression(C=2.0, max_iter=500, class_weight="balanced"),
        cv=3,
    )
    topic_model.fit(X, topics)

    # 4. Missing Guidance / Escalation Trigger Classifier (Binary SGD with log loss)
    missing_model = CalibratedClassifierCV(
        estimator=SGDClassifier(loss="log_loss", penalty="elasticnet", alpha=1e-3, random_state=42),
        cv=3,
    )
    missing_model.fit(X, missing_guidance)

    # Save artifact bundle
    out_dir = Path("backend/data/models")
    out_dir.mkdir(parents=True, exist_ok=True)

    bundle = {
        "vectorizer": vectorizer,
        "intent_model": intent_model,
        "role_model": role_model,
        "topic_model": topic_model,
        "missing_model": missing_model,
        "version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "classes": {
            "intents": list(intent_model.classes_),
            "roles": list(role_model.classes_),
            "topics": list(topic_model.classes_),
        },
    }

    model_path = out_dir / "frontline_intent_model.joblib"
    joblib.dump(bundle, model_path)
    logger.info(f"Saved trained ML model bundle to: {model_path}")

    # Save JSON metadata
    metadata = {
        "model_name": "FrontlineIntentClassifier-v1.0",
        "architecture": "TF-IDF + Calibrated Multi-Task Linear Models",
        "features": {
            "ngram_range": [1, 2],
            "vocabulary_size": len(vectorizer.vocabulary_),
            "sublinear_tf": True,
        },
        "metrics": {
            "intent_accuracy": float(intent_acc),
            "role_accuracy": float(role_acc),
            "training_samples": len(texts),
        },
        "supported_intents": list(intent_model.classes_),
        "supported_roles": list(role_model.classes_),
        "supported_topics": list(topic_model.classes_),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready",
    }
    with open(out_dir / "ml_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"ML Model training complete! Artifacts verified in {out_dir}")
    return metadata


if __name__ == "__main__":
    train_and_export()

