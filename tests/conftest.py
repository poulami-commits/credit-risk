"""Shared pytest fixtures."""
from __future__ import annotations

import pytest

from src.data.generator import generate_loan_data


@pytest.fixture(scope="session")
def sample_df():
    """100-row synthetic loan DataFrame (session-scoped for speed)."""
    return generate_loan_data(n_samples=100, random_state=0)


@pytest.fixture
def sample_application() -> dict:
    """Valid loan application matching LoanApplication schema."""
    return {
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
