# -*- coding: utf-8 -*-
"""
Frontline ML Predictor Service.

Provides real-time inference using the trained multi-task ML model:
- Task intent recognition
- Role targeting and verification
- Operational topic detection
- Missing guidance & escalation trigger detection
- Calibrated confidence scoring
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import joblib
import numpy as np

logger = logging.getLogger(__name__)

_DEFAULT_MODEL_PATH = Path("data/models/frontline_intent_model.joblib")
_DEFAULT_METADATA_PATH = Path("data/models/ml_metadata.json")


class FrontlineMLPredictor:
    """Inference wrapper for trained frontline intent and confidence models."""

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or _DEFAULT_MODEL_PATH
        self.bundle: Optional[Dict[str, Any]] = None
        self.metadata: Optional[Dict[str, Any]] = None
        self._load()

    def _load(self):
        """Load trained model bundle and metadata."""
        # Check relative or backend-relative paths
        candidates = [
            self.model_path,
            Path("backend") / self.model_path,
            Path(__file__).parent.parent.parent / "data" / "models" / "frontline_intent_model.joblib",
        ]
        for p in candidates:
            if p.exists():
                try:
                    self.bundle = joblib.load(p)
                    logger.info(f"Loaded Frontline ML model from: {p}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load ML model from {p}: {e}")

        # Load metadata if exists
        meta_candidates = [
            _DEFAULT_METADATA_PATH,
            Path("backend") / _DEFAULT_METADATA_PATH,
            Path(__file__).parent.parent.parent / "data" / "models" / "ml_metadata.json",
        ]
        for mp in meta_candidates:
            if mp.exists():
                try:
                    with open(mp, "r") as f:
                        self.metadata = json.load(f)
                    break
                except Exception:
                    pass

    @property
    def is_available(self) -> bool:
        return self.bundle is not None

    def predict(self, query: str, active_role: Optional[str] = None) -> Dict[str, Any]:
        """
        Run inference on the incoming query.
        Returns:
            intent: predicted task intent
            predicted_role: recommended frontline role
            topic: detected operational domain
            confidence: calibrated probability (0.0 to 1.0)
            is_guidance_missing: boolean indicating out-of-scope / missing procedure
            escalation_recommended: boolean indicating human escalation required
            escalation_reason: explanation if escalation recommended
        """
        if not self.is_available or not query or not query.strip():
            return {
                "intent": "general_inquiry",
                "predicted_role": active_role or "field_technician",
                "topic": "operations",
                "confidence": 0.50,
                "is_guidance_missing": False,
                "escalation_recommended": False,
                "escalation_reason": None,
                "model_version": "heuristic-fallback",
            }

        try:
            vectorizer = self.bundle["vectorizer"]
            intent_model = self.bundle["intent_model"]
            role_model = self.bundle["role_model"]
            topic_model = self.bundle["topic_model"]
            missing_model = self.bundle["missing_model"]

            X = vectorizer.transform([query.strip()])

            # 1. Intent & Calibrated Confidence
            intent_probs = intent_model.predict_proba(X)[0]
            top_intent_idx = np.argmax(intent_probs)
            intent = str(intent_model.classes_[top_intent_idx])
            intent_conf = float(intent_probs[top_intent_idx])

            # 2. Predicted Role
            role_probs = role_model.predict_proba(X)[0]
            top_role_idx = np.argmax(role_probs)
            pred_role = str(role_model.classes_[top_role_idx])

            # 3. Topic
            topic_probs = topic_model.predict_proba(X)[0]
            top_topic_idx = np.argmax(topic_probs)
            topic = str(topic_model.classes_[top_topic_idx])

            # 4. Missing Guidance & Escalation Detection
            missing_probs = missing_model.predict_proba(X)[0]
            # Class 1 is missing guidance
            missing_prob = float(missing_probs[1]) if len(missing_probs) > 1 else 0.0

            is_missing = (intent == "missing_guidance_unsupported") or (missing_prob >= 0.55) or (intent_conf < 0.20)
            escalation_rec = is_missing or (intent == "emergency_escalation")

            reason = None
            if is_missing:
                reason = "No matching Standard Operating Procedure (SOP) with sufficient confidence found for this query context."
            elif intent == "emergency_escalation":
                reason = "Critical emergency or policy conflict detected requiring lead supervisor sign-off."

            return {
                "intent": intent,
                "predicted_role": pred_role,
                "topic": topic,
                "confidence": round(intent_conf, 3),
                "is_guidance_missing": bool(is_missing),
                "escalation_recommended": bool(escalation_rec),
                "escalation_reason": reason,
                "model_version": self.bundle.get("version", "1.0.0"),
            }
        except Exception as e:
            logger.error(f"Inference error in FrontlineMLPredictor: {e}")
            return {
                "intent": "general_inquiry",
                "predicted_role": active_role or "field_technician",
                "topic": "operations",
                "confidence": 0.50,
                "is_guidance_missing": False,
                "escalation_recommended": False,
                "escalation_reason": None,
                "model_version": "fallback",
            }

    def get_info(self) -> Dict[str, Any]:
        """Return model metadata and runtime status."""
        return {
            "is_loaded": self.is_available,
            "metadata": self.metadata or {},
        }


# Global singleton instance
_predictor_instance: Optional[FrontlineMLPredictor] = None


def get_ml_predictor() -> FrontlineMLPredictor:
    """Get or create singleton ML predictor instance."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = FrontlineMLPredictor()
    return _predictor_instance
