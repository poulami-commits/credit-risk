"""
Credit Risk Scoring Engine — FastAPI application.

Endpoints
---------
GET  /health            — liveness probe
GET  /model/info        — model metadata and performance metrics
POST /predict           — score a single loan application with SHAP explanation
POST /predict/batch     — score up to 100 applications in one call
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api.predictor import Predictor
from src.api.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    LoanApplication,
    ModelInfoResponse,
    PredictionResponse,
)
from src.config import settings

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


# ── Lifespan: warm model cache at startup ─────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Predictor.get_instance()
        log.info("Model loaded and ready.")
    except FileNotFoundError:
        log.warning("Model artifact not found — run `make train` first.")
    yield


# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "XGBoost-based credit default risk scoring with SHAP explainability. "
        "Returns probability of default, risk tier, scorecard score, and the "
        "top 10 SHAP factors driving each decision."
    ),
    lifespan=lifespan,
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ── Routes ────────────────────────────────────────────────────────────────────
#--- metadata added
@app.get("/metadata")
def metadata():
    return {
        "home_ownership": [
            "RENT",
            "OWN",
            "MORTGAGE",
            "OTHER"
        ],
        "purpose": [
            "debt_consolidation",
            "credit_card",
            "medical",
            "home_improvement",
            "vacation"
        ],
        "loan_term": [
            36,
            60
        ]
    }

@app.get("/health", tags=["ops"])
def health():
    """Liveness probe."""
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/model/info", response_model=ModelInfoResponse, tags=["ops"])
def model_info():
    """Return static model metadata and benchmark performance metrics."""
    return ModelInfoResponse(
        model_name="XGBoost Credit Risk Scorer",
        version=settings.APP_VERSION,
        algorithm="XGBoost + SHAP TreeExplainer",
        auc_roc=0.7897,
        ks_statistic=0.4587,
        gini_coefficient=0.5794,
        feature_count=21,
        training_samples=8_000,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["scoring"])
def predict(application: LoanApplication):
    """
    Score a single loan application.

    Returns default probability, risk tier (LOW / MEDIUM / HIGH / VERY_HIGH),
    a 300–850 risk score, underwriting decision, and the top 10 SHAP factors
    explaining the prediction.
    """
    try:
        return Predictor.get_instance().predict(application)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="Model not loaded — run `make train` first.") from exc
    except Exception as exc:
        log.exception("Prediction error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["scoring"])
def predict_batch(request: BatchPredictionRequest):
    """
    Score a batch of up to 100 loan applications.

    Returns individual predictions plus aggregate counts by decision category.
    """
    try:
        predictor = Predictor.get_instance()
        preds = predictor.predict_batch(request.applications)
        return BatchPredictionResponse(
            predictions=preds,
            total_applications=len(preds),
            approval_count=sum(1 for p in preds if p.decision.value == "APPROVE"),
            review_count=sum(1 for p in preds if p.decision.value == "REVIEW"),
            decline_count=sum(1 for p in preds if p.decision.value == "DECLINE"),
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="Model not loaded — run `make train` first.") from exc
    except Exception as exc:
        log.exception("Batch prediction error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
