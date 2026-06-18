"""
API integration tests.

The Predictor singleton is mocked so tests run without a trained model
on disk — keeping the CI pipeline dependency-free.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.schemas import Decision, PredictionResponse, RiskTier, SHAPFactor

client = TestClient(app)


# ── Helper ────────────────────────────────────────────────────────────────────

def _mock_prediction() -> PredictionResponse:
    return PredictionResponse(
        default_probability=0.08,
        risk_tier=RiskTier.LOW,
        risk_score=730,
        decision=Decision.APPROVE,
        top_risk_factors=[
            SHAPFactor(feature="fico_score", impact=-0.45, direction="reduces_risk"),
            SHAPFactor(feature="dti", impact=0.12, direction="increases_risk"),
        ],
        base_value=-1.52,
        model_version="1.0.0",
    )


# ── Health / info ─────────────────────────────────────────────────────────────

def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_returns_version():
    response = client.get("/health")
    assert "version" in response.json()


def test_model_info_keys():
    response = client.get("/model/info")
    assert response.status_code == 200
    body = response.json()
    for key in ("auc_roc", "ks_statistic", "gini_coefficient", "feature_count"):
        assert key in body, f"Missing key: {key}"


# ── Single predict ────────────────────────────────────────────────────────────

@patch("src.api.main.Predictor")
def test_predict_success(MockPredictor, sample_application):
    MockPredictor.get_instance.return_value.predict.return_value = _mock_prediction()
    response = client.post("/predict", json=sample_application)
    assert response.status_code == 200
    body = response.json()
    assert "default_probability" in body
    assert "risk_tier" in body
    assert "decision" in body
    assert isinstance(body["top_risk_factors"], list)


@patch("src.api.main.Predictor")
def test_predict_response_fields(MockPredictor, sample_application):
    MockPredictor.get_instance.return_value.predict.return_value = _mock_prediction()
    body = client.post("/predict", json=sample_application).json()
    assert 0.0 <= body["default_probability"] <= 1.0
    assert 300 <= body["risk_score"] <= 850
    assert body["decision"] in ("APPROVE", "REVIEW", "DECLINE")


def test_predict_invalid_fico_rejected():
    """FICO score must be in [300, 850]."""
    bad_app = {
        "age": 30, "annual_income": 60_000, "employment_length": 3,
        "home_ownership": "RENT", "loan_amount": 10_000, "loan_term": 36,
        "interest_rate": 10.0, "purpose": "other", "fico_score": 200,  # INVALID
        "dti": 15.0, "delinq_2yrs": 0, "open_acc": 5, "revol_util": 30.0,
        "total_acc": 10, "revol_bal": 5_000,
    }
    response = client.post("/predict", json=bad_app)
    assert response.status_code == 422


def test_predict_invalid_loan_term_rejected(sample_application):
    """loan_term must be 36 or 60."""
    bad_app = {**sample_application, "loan_term": 48}  # invalid
    response = client.post("/predict", json=bad_app)
    assert response.status_code == 422


# ── Batch predict ─────────────────────────────────────────────────────────────

@patch("src.api.main.Predictor")
def test_batch_predict_returns_counts(MockPredictor, sample_application):
    MockPredictor.get_instance.return_value.predict_batch.return_value = [
        _mock_prediction(), _mock_prediction()
    ]
    payload = {"applications": [sample_application, sample_application]}
    response = client.post("/predict/batch", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["total_applications"] == 2
    assert body["approval_count"] + body["review_count"] + body["decline_count"] == 2


def test_batch_predict_over_limit_rejected(sample_application):
    """Batches over 100 should return 422."""
    payload = {"applications": [sample_application] * 101}
    response = client.post("/predict/batch", json=payload)
    assert response.status_code == 422
