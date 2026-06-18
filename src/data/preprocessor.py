"""
Scikit-learn preprocessing pipeline.

The canonical feature lists (NUMERIC_FEATURES, CATEGORICAL_FEATURES, ALL_FEATURES)
are defined here and imported everywhere to guarantee consistency between
training and inference.
"""
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, StandardScaler

# ── Canonical feature lists ───────────────────────────────────────────────────
# Raw features coming from the loan application
RAW_NUMERIC: list[str] = [
    "age",
    "annual_income",
    "employment_length",
    "loan_amount",
    "loan_term",
    "interest_rate",
    "fico_score",
    "dti",
    "delinq_2yrs",
    "open_acc",
    "revol_util",
    "total_acc",
    "revol_bal",
]

# Features created by src/features/engineer.py
ENGINEERED_NUMERIC: list[str] = [
    "income_loan_ratio",
    "monthly_payment",
    "payment_to_income",
    "high_revol_util",
    "acc_diversity",
    "fico_bucket",
]

NUMERIC_FEATURES: list[str] = RAW_NUMERIC + ENGINEERED_NUMERIC
CATEGORICAL_FEATURES: list[str] = ["home_ownership", "purpose"]
ALL_FEATURES: list[str] = NUMERIC_FEATURES + CATEGORICAL_FEATURES


# ── Pipeline builder ──────────────────────────────────────────────────────────
def build_preprocessor() -> ColumnTransformer:
    """
    Return a fitted-ready ColumnTransformer that:
    - Imputes medians and standard-scales numeric columns.
    - Imputes mode and ordinal-encodes categorical columns.
    """
    numeric_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, NUMERIC_FEATURES),
            ("cat", categorical_pipe, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
