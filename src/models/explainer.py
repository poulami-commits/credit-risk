"""
SHAP-based explainability for the credit risk scoring pipeline.

Uses TreeExplainer (exact, not kernel — orders of magnitude faster for
XGBoost) on the raw XGBoost model extracted from the sklearn Pipeline,
passing preprocessor-transformed data.

Each call to explain_prediction() returns:
  - base_value        : model's expected output (log-odds) across training set
  - shap_contributions: per-feature SHAP values (additive log-odds contribution)
  - top_risk_factors  : top-10 factors sorted by |SHAP|, with direction labels
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import shap
from sklearn.pipeline import Pipeline


class CreditRiskExplainer:
    """Lazy-initialised SHAP TreeExplainer tied to a fitted Pipeline."""

    def __init__(self, pipeline: Pipeline) -> None:
        self._pipeline = pipeline
        self._preprocessor = pipeline.named_steps["preprocessor"]
        self._xgb_model = pipeline.named_steps["classifier"]
        self._explainer: shap.TreeExplainer | None = None
        self._feature_names: list[str] = self._resolve_feature_names()

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _resolve_feature_names(self) -> list[str]:
        """
        Extract human-readable feature names from the ColumnTransformer.
        sklearn ≥ 1.0 exposes get_feature_names_out(); strip the 'num__' /
        'cat__' prefix so names are display-friendly.
        """
        raw = self._preprocessor.get_feature_names_out()
        return [name.split("__", 1)[-1] for name in raw]

    def _get_explainer(self) -> shap.TreeExplainer:
        if self._explainer is None:
            self._explainer = shap.TreeExplainer(self._xgb_model)
        return self._explainer

    def _preprocess(self, X: pd.DataFrame) -> np.ndarray:
        return self._preprocessor.transform(X)

    # ── Public API ────────────────────────────────────────────────────────────

    def explain_prediction(self, X: pd.DataFrame) -> dict[str, Any]:
        """
        Generate a SHAP explanation for a single-row DataFrame X.

        Returns
        -------
        base_value        : float — expected model output (log-odds)
        shap_contributions: dict[feature -> shap_value]
        top_risk_factors  : list[dict] — top 10 by |SHAP| with direction
        """
        X_t = self._preprocess(X)
        explainer = self._get_explainer()
        shap_vals = explainer.shap_values(X_t)  # shape (1, n_features)

        row = shap_vals[0]  # 1-D array for single prediction

        contributions: dict[str, float] = {
            feat: round(float(val), 4)
            for feat, val in zip(self._feature_names, row)
        }

        top_factors = sorted(contributions.items(), key=lambda kv: abs(kv[1]), reverse=True)[:10]

        return {
            "base_value": round(float(explainer.expected_value), 4),
            "shap_contributions": contributions,
            "top_risk_factors": [
                {
                    "feature": feat,
                    "impact": val,
                    "direction": "increases_risk" if val > 0 else "reduces_risk",
                }
                for feat, val in top_factors
            ],
        }

    def global_feature_importance(self, X: pd.DataFrame) -> list[dict[str, Any]]:
        """
        Mean |SHAP| across a dataset — global feature importance.

        Parameters
        ----------
        X : DataFrame of ALL_FEATURES columns (pre-engineer_features).
        """
        X_t = self._preprocess(X)
        explainer = self._get_explainer()
        shap_vals = explainer.shap_values(X_t)  # shape (n_samples, n_features)

        mean_abs = np.abs(shap_vals).mean(axis=0)
        ranked = sorted(zip(self._feature_names, mean_abs), key=lambda kv: kv[1], reverse=True)

        return [
            {"feature": feat, "mean_abs_shap": round(float(v), 4)}
            for feat, v in ranked
        ]
