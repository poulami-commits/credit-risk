"""
Model serving layer.

Predictor is a singleton that loads the trained pipeline once at startup
and exposes predict() / predict_batch() for the FastAPI handlers.
It also drives the SHAP explainer, converting raw SHAP values into the
human-readable SHAPFactor objects returned in the API response.
"""
from __future__ import annotations

import logging

import joblib
import numpy as np
import pandas as pd

from src.api.schemas import Decision, LoanApplication, PredictionResponse, RiskTier, SHAPFactor
from src.config import settings
from src.data.preprocessor import ALL_FEATURES
from src.features.engineer import add_features
from src.models.explainer import CreditRiskExplainer

log = logging.getLogger(__name__)

# ── Risk classification thresholds ───────────────────────────────────────────
_TIERS: list[tuple[float, RiskTier, Decision]] = [
    (0.10, RiskTier.LOW,       Decision.APPROVE),
    (0.20, RiskTier.MEDIUM,    Decision.APPROVE),
    (0.35, RiskTier.HIGH,      Decision.REVIEW),
    (1.01, RiskTier.VERY_HIGH, Decision.DECLINE),
]


def _classify(prob: float) -> tuple[RiskTier, Decision]:
    for threshold, tier, decision in _TIERS:
        if prob < threshold:
            return tier, decision
    return RiskTier.VERY_HIGH, Decision.DECLINE


def _prob_to_score(prob: float) -> int:
    """
    Map default probability to a 300–850 scorecard score.

    Uses the standard credit scoring log-odds → points formula:
        score = 550 − 50 × ln(p / (1−p))
    Higher score = lower risk (mirrors FICO convention).
    """
    eps = 1e-9
    log_odds = np.log(max(prob, eps) / max(1.0 - prob, eps))
    score = int(round(550.0 - 50.0 * log_odds))
    return max(300, min(850, score))


# ── Singleton ─────────────────────────────────────────────────────────────────

class Predictor:
    """Thread-safe, lazily-loaded model singleton."""

    _instance: Predictor | None = None

    def __init__(self) -> None:
        log.info("Loading model from %s", settings.MODEL_PATH)
        self._pipeline = joblib.load(settings.MODEL_PATH)
        self._explainer = CreditRiskExplainer(self._pipeline)
        self.model_version = settings.APP_VERSION

    @classmethod
    def get_instance(cls) -> Predictor:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── Core predict ──────────────────────────────────────────────────────────

    def predict(self, application: LoanApplication) -> PredictionResponse:
        """Score a single loan application."""
        df = pd.DataFrame([application.model_dump()])
        df = add_features(df)

        prob = float(self._pipeline.predict_proba(df[ALL_FEATURES])[:, 1][0])
        explanation = self._explainer.explain_prediction(df[ALL_FEATURES])

        tier, decision = _classify(prob)
        score = _prob_to_score(prob)

        shap_factors = [
            SHAPFactor(
                feature=f["feature"],
                impact=f["impact"],
                direction=f["direction"],
            )
            for f in explanation["top_risk_factors"]
        ]

        return PredictionResponse(
            default_probability=round(prob, 4),
            risk_tier=tier,
            risk_score=score,
            decision=decision,
            top_risk_factors=shap_factors,
            base_value=explanation["base_value"],
            model_version=self.model_version,
        )

    def predict_batch(self, applications: list[LoanApplication]) -> list[PredictionResponse]:
        """Score a list of loan applications."""
        return [self.predict(app) for app in applications]
