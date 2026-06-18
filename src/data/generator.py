"""
Synthetic loan application dataset generator.

Mimics Lending Club-style features with a realistic, causal default
generation function so the trained model produces industry-grade metrics.
"""
import numpy as np
import pandas as pd


def generate_loan_data(n_samples: int = 10_000, random_state: int = 42) -> pd.DataFrame:
    """
    Generate synthetic loan application records.

    Default probability is driven by:
    - FICO score (negative effect on risk)
    - Debt-to-income ratio (positive effect)
    - Prior delinquencies (strong positive effect)
    - Revolving utilization (positive effect)
    - Annual income & employment length (negative effects)

    Returns a DataFrame ready for feature engineering + modelling.
    """
    rng = np.random.RandomState(random_state)

    # ── Demographics ──────────────────────────────────────────────
    age = rng.randint(20, 70, n_samples)
    annual_income = np.exp(rng.normal(11.0, 0.6, n_samples)).astype(int)
    employment_length = rng.choice(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        n_samples,
        p=[0.05, 0.08, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.07],
    )
    home_ownership = rng.choice(
        ["RENT", "OWN", "MORTGAGE", "OTHER"],
        n_samples,
        p=[0.45, 0.15, 0.38, 0.02],
    )

    # ── Loan characteristics ──────────────────────────────────────
    loan_amount = rng.randint(1_000, 40_000, n_samples)
    loan_term = rng.choice([36, 60], n_samples, p=[0.60, 0.40])
    interest_rate = rng.uniform(5.0, 30.0, n_samples).round(2)
    purpose = rng.choice(
        ["debt_consolidation", "credit_card", "home_improvement",
         "other", "major_purchase", "medical"],
        n_samples,
        p=[0.35, 0.20, 0.15, 0.10, 0.10, 0.10],
    )

    # ── Credit history ────────────────────────────────────────────
    fico_score = rng.randint(580, 851, n_samples)
    dti = rng.uniform(0.0, 45.0, n_samples).round(2)
    delinq_2yrs = rng.choice([0, 1, 2, 3], n_samples, p=[0.75, 0.15, 0.07, 0.03])
    open_acc = rng.randint(1, 31, n_samples)
    revol_util = rng.uniform(0.0, 100.0, n_samples).round(2)
    total_acc = open_acc + rng.randint(0, 20, n_samples)
    revol_bal = (annual_income * rng.uniform(0.01, 0.5, n_samples)).astype(int)

    # ── Causal default generation ─────────────────────────────────
    log_odds = (
        -0.010 * fico_score
        + 0.020 * dti
        + 0.000_1 * loan_amount
        - 0.001 * annual_income / 1_000
        + 0.300 * delinq_2yrs
        + 0.010 * revol_util
        - 0.020 * employment_length
        + rng.normal(0, 0.3, n_samples)
        + 2.0  # intercept → ~9% average default rate
    )
    default_prob = 1.0 / (1.0 + np.exp(-log_odds))
    loan_status = (rng.uniform(0, 1, n_samples) < default_prob).astype(int)

    return pd.DataFrame(
        {
            "age": age,
            "annual_income": annual_income,
            "employment_length": employment_length,
            "home_ownership": home_ownership,
            "loan_amount": loan_amount,
            "loan_term": loan_term,
            "interest_rate": interest_rate,
            "purpose": purpose,
            "fico_score": fico_score,
            "dti": dti,
            "delinq_2yrs": delinq_2yrs,
            "open_acc": open_acc,
            "revol_util": revol_util,
            "total_acc": total_acc,
            "revol_bal": revol_bal,
            "loan_status": loan_status,
        }
    )
