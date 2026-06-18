"""
XGBoost training pipeline.

Builds a sklearn Pipeline (ColumnTransformer + XGBClassifier) with
class-weight balancing for the imbalanced credit default dataset.
"""
from __future__ import annotations

import logging
from typing import Any

import pandas as pd
import xgboost as xgb
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline

from src.config import settings
from src.data.preprocessor import ALL_FEATURES, build_preprocessor
from src.features.engineer import add_features

log = logging.getLogger(__name__)


def build_pipeline(scale_pos_weight: float) -> Pipeline:
    """Assemble a fresh unfitted Pipeline."""
    model = xgb.XGBClassifier(
        n_estimators=settings.N_ESTIMATORS,
        max_depth=settings.MAX_DEPTH,
        learning_rate=settings.LEARNING_RATE,
        subsample=settings.SUBSAMPLE,
        colsample_bytree=settings.COLSAMPLE_BYTREE,
        min_child_weight=settings.MIN_CHILD_WEIGHT,
        scale_pos_weight=scale_pos_weight,   # compensates class imbalance
        eval_metric="auc",
        random_state=settings.RANDOM_STATE,
        n_jobs=-1,
        verbosity=0,
    )
    return Pipeline(
        [
            ("preprocessor", build_preprocessor()),
            ("classifier", model),
        ]
    )


def train_model(
    df: pd.DataFrame,
) -> tuple[Pipeline, tuple[pd.DataFrame, pd.Series], dict[str, Any]]:
    """
    Full training run.

    Parameters
    ----------
    df : Raw loan DataFrame (output of generator or real Lending Club data).

    Returns
    -------
    pipeline   : Fitted sklearn Pipeline ready for joblib serialisation.
    test_data  : (X_test, y_test) for post-training evaluation.
    meta       : Metadata dict (cv_auc, feature_names, …).
    """
    df = add_features(df)

    X = df[ALL_FEATURES]
    y = df["loan_status"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=settings.TEST_SIZE,
        random_state=settings.RANDOM_STATE,
        stratify=y,
    )

    neg, pos = (y_train == 0).sum(), (y_train == 1).sum()
    scale_pos_weight = neg / pos
    log.info("Class ratio neg/pos = %.2f → scale_pos_weight=%.2f", neg / pos, scale_pos_weight)

    pipeline = build_pipeline(scale_pos_weight)

    # 5-fold stratified CV on training fold for unbiased AUC estimate
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=settings.RANDOM_STATE)
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="roc_auc", n_jobs=-1)
    log.info("CV AUC: %.4f ± %.4f", cv_scores.mean(), cv_scores.std())

    # Refit on full training fold
    pipeline.fit(X_train, y_train)

    meta = {
        "feature_names": ALL_FEATURES,
        "cv_auc_mean": float(cv_scores.mean()),
        "cv_auc_std": float(cv_scores.std()),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "default_rate": float(y.mean()),
    }

    return pipeline, (X_test, y_test), meta
