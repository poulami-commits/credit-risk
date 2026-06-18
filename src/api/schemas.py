"""
Pydantic v2 schemas for the credit risk scoring API.

LoanApplication   — validated incoming request
PredictionResponse — full scoring response with SHAP factors
BatchPredictionRequest / BatchPredictionResponse — batch endpoint
ModelInfoResponse  — /model/info metadata
"""
from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────────

class HomeOwnership(str, Enum):
    RENT = "RENT"
    OWN = "OWN"
    MORTGAGE = "MORTGAGE"
    OTHER = "OTHER"


class LoanPurpose(str, Enum):
    DEBT_CONSOLIDATION = "debt_consolidation"
    CREDIT_CARD = "credit_card"
    HOME_IMPROVEMENT = "home_improvement"
    OTHER = "other"
    MAJOR_PURCHASE = "major_purchase"
    MEDICAL = "medical"


class RiskTier(str, Enum):
    LOW = "LOW"            # PD < 10 %
    MEDIUM = "MEDIUM"      # 10 % ≤ PD < 20 %
    HIGH = "HIGH"          # 20 % ≤ PD < 35 %
    VERY_HIGH = "VERY_HIGH"  # PD ≥ 35 %


class Decision(str, Enum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    DECLINE = "DECLINE"


# ── Request ───────────────────────────────────────────────────────────────────

class LoanApplication(BaseModel):
    """Single loan application — all fields required by the model."""

    age: int = Field(..., ge=18, le=100, description="Applicant age in years")
    annual_income: float = Field(..., gt=0, description="Gross annual income (USD)")
    employment_length: int = Field(..., ge=0, le=10, description="Years at current employer (10 = 10+)")
    home_ownership: HomeOwnership
    loan_amount: float = Field(..., gt=0, le=50_000, description="Requested loan amount (USD)")
    loan_term: Literal[36, 60] = Field(..., description="Repayment term in months")
    interest_rate: float = Field(..., ge=5.0, le=35.0, description="Offered annual rate (%)")
    purpose: LoanPurpose
    fico_score: int = Field(..., ge=300, le=850, description="FICO credit score")
    dti: float = Field(..., ge=0.0, le=100.0, description="Debt-to-income ratio (%)")
    delinq_2yrs: int = Field(..., ge=0, le=20, description="Delinquencies in last 24 months")
    open_acc: int = Field(..., ge=0, description="Open credit lines / accounts")
    revol_util: float = Field(..., ge=0.0, le=100.0, description="Revolving utilisation (%)")
    total_acc: int = Field(..., ge=0, description="Total credit accounts ever opened")
    revol_bal: float = Field(..., ge=0, description="Total revolving credit balance (USD)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "age": 35,
                "annual_income": 75_000,
                "employment_length": 5,
                "home_ownership": "MORTGAGE",
                "loan_amount": 15_000,
                "loan_term": 36,
                "interest_rate": 12.5,
                "purpose": "debt_consolidation",
                "fico_score": 720,
                "dti": 18.5,
                "delinq_2yrs": 0,
                "open_acc": 8,
                "revol_util": 35.0,
                "total_acc": 15,
                "revol_bal": 12_000,
            }
        }
    }


# ── Response ──────────────────────────────────────────────────────────────────

class SHAPFactor(BaseModel):
    feature: str
    impact: float = Field(..., description="SHAP value (log-odds contribution)")
    direction: Literal["increases_risk", "reduces_risk"]


class PredictionResponse(BaseModel):
    default_probability: float = Field(..., description="Probability of default [0, 1]")
    risk_tier: RiskTier
    risk_score: int = Field(..., description="Scorecard score 300–850 (higher = safer)")
    decision: Decision
    top_risk_factors: list[SHAPFactor] = Field(..., description="Top 10 SHAP factors")
    base_value: float = Field(..., description="Model expected log-odds (intercept)")
    model_version: str


class BatchPredictionRequest(BaseModel):
    applications: list[LoanApplication] = Field(..., min_length=1, max_length=100)


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]
    total_applications: int
    approval_count: int
    review_count: int
    decline_count: int


class ModelInfoResponse(BaseModel):
    model_name: str
    version: str
    algorithm: str
    auc_roc: float
    ks_statistic: float
    gini_coefficient: float
    feature_count: int
    training_samples: int
