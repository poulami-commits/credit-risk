"""
Credit-domain feature engineering.

All transformations are deterministic and reversible so they can be
applied identically during training and online inference.
"""
import numpy as np
import pandas as pd


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive six credit-domain features from raw loan application columns.

    New columns
    -----------
    income_loan_ratio   : Annual income relative to requested loan — proxy for
                          repayment capacity.
    monthly_payment     : Estimated monthly instalment using the standard
                          amortisation formula.
    payment_to_income   : Annual debt service as fraction of gross income —
                          a lending version of DTI at loan level.
    high_revol_util     : Binary flag for revolving utilisation > 80 %,
                          a strong delinquency predictor.
    acc_diversity       : Ratio of total accounts ever opened to currently open
                          accounts — proxy for credit history depth.
    fico_bucket         : FICO score bucketed into 6 risk bands (0 = best).
    """
    df = df.copy()

    # Income-to-loan ratio
    df["income_loan_ratio"] = df["annual_income"] / (df["loan_amount"] + 1)

    # Monthly payment via amortisation formula  P·r / (1 - (1+r)^-n)
    r = df["interest_rate"] / 100 / 12
    has_rate = r > 0
    df["monthly_payment"] = np.where(
        has_rate,
        df["loan_amount"] * r / (1 - (1 + r) ** (-df["loan_term"])),
        df["loan_amount"] / df["loan_term"],  # zero-interest fallback
    )

    # Annual debt service as fraction of income
    df["payment_to_income"] = (df["monthly_payment"] * 12) / (df["annual_income"] + 1)

    # High revolving utilisation flag (>80 % → binary 1)
    df["high_revol_util"] = (df["revol_util"] > 80).astype(int)

    # Account diversity: total accounts ever / currently open accounts
    df["acc_diversity"] = df["total_acc"] / (df["open_acc"] + 1)

    # FICO bucket: 0 (740–850, prime) … 5 (300–579, deep subprime)
    df["fico_bucket"] = (
        pd.cut(
            df["fico_score"],
            bins=[0, 579, 619, 659, 699, 739, 901],
            labels=[5, 4, 3, 2, 1, 0],
        )
        .astype(float)
        .fillna(5.0)
    )

    return df
