"""
Credit risk model evaluation metrics.

Beyond standard ML metrics (AUC, Brier), the module implements the three
metrics regulators and credit teams care about:

  KS statistic  — maximum separation between cumulative good/bad distributions.
                  KS > 0.40 is considered a good scorecard.
  Gini coeff.   — 2 × AUC − 1.  Gini > 0.60 is considered good.
  PSI           — Population Stability Index. Detects score distribution shift
                  between training and deployment populations.
                  PSI < 0.10 → stable; 0.10–0.25 → minor shift; > 0.25 → rebuild.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    brier_score_loss,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)


# ── Core metrics ──────────────────────────────────────────────────────────────

def ks_statistic(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """KS = max |TPR − FPR| across all thresholds."""
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    return float(np.max(tpr - fpr))


def gini_coefficient(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Gini = 2 × AUC − 1."""
    return 2.0 * roc_auc_score(y_true, y_prob) - 1.0


def population_stability_index(
    expected: np.ndarray,
    actual: np.ndarray,
    n_buckets: int = 10,
) -> float:
    """
    PSI compares score distribution between two populations.

    Typically *expected* = scores on training set, *actual* = scores on
    a monitoring window.
    """
    eps = 1e-6  # avoid log(0)

    def _bucket_props(scores: np.ndarray) -> pd.Series:
        buckets = pd.qcut(scores, n_buckets, labels=False, duplicates="drop")
        counts = pd.Series(buckets).value_counts(normalize=True).sort_index()
        return counts.clip(lower=eps)

    e_props = _bucket_props(expected)
    a_props = _bucket_props(actual)
    # align on shared bucket indices
    idx = e_props.index.union(a_props.index)
    e_props = e_props.reindex(idx, fill_value=eps)
    a_props = a_props.reindex(idx, fill_value=eps)

    psi = float(((e_props - a_props) * np.log(e_props / a_props)).sum())
    return psi


# ── Full evaluation report ────────────────────────────────────────────────────

def evaluate_model(pipeline: Any, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, Any]:
    """
    Return a comprehensive evaluation dict for a fitted sklearn Pipeline.

    Keys
    ----
    auc_roc, ks_statistic, gini_coefficient, brier_score,
    confusion_matrix, classification_report
    """
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    y_pred = pipeline.predict(X_test)

    return {
        "auc_roc": round(roc_auc_score(y_test, y_prob), 4),
        "ks_statistic": round(ks_statistic(y_test, y_prob), 4),
        "gini_coefficient": round(gini_coefficient(y_test, y_prob), 4),
        "brier_score": round(brier_score_loss(y_test, y_prob), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
    }
