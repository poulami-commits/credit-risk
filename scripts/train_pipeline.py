#!/usr/bin/env python3
"""
End-to-end training pipeline.

Usage
-----
    python scripts/train_pipeline.py

Steps
-----
1. Generate 10,000 synthetic Lending Club-style loan records
2. Run feature engineering (6 derived features)
3. Train XGBoost inside a sklearn Pipeline with 5-fold CV
4. Evaluate on a 20 % held-out test set — AUC, KS, Gini, Brier
5. Serialize the fitted Pipeline to models/xgb_credit_risk.joblib
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

import joblib

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import settings
from src.data.generator import generate_loan_data
from src.models.evaluator import evaluate_model
from src.models.trainer import train_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ── Display helpers ───────────────────────────────────────────────────────────

def _banner(text: str) -> None:
    width = 56
    print("\n" + "═" * width)
    print(f"  {text}")
    print("═" * width)


def _metric_row(label: str, value: float, benchmark: str = "") -> None:
    bench = f"  ← {benchmark}" if benchmark else ""
    print(f"  {label:<22} {value:>8.4f}{bench}")


def _print_metrics(metrics: dict, cv_auc: float) -> None:
    print()
    print(f"  {'Metric':<22} {'Value':>8}  Industry benchmark")
    print("  " + "─" * 48)
    _metric_row("CV AUC (5-fold)",   cv_auc,                    "≥ 0.75 good")
    _metric_row("Test AUC-ROC",      metrics["auc_roc"],         "≥ 0.75 good")
    _metric_row("KS Statistic",      metrics["ks_statistic"],    "≥ 0.40 good")
    _metric_row("Gini Coefficient",  metrics["gini_coefficient"],"≥ 0.60 good")
    _metric_row("Brier Score",       metrics["brier_score"],     "lower = better")

    auc = metrics["auc_roc"]
    grade = (
        "Excellent ✓" if auc >= 0.80 else
        "Good ✓"      if auc >= 0.70 else
        "Fair"         if auc >= 0.60 else
        "Needs improvement"
    )
    print(f"\n  Model grade: {grade}")
    print()

    cm = metrics["confusion_matrix"]
    print("  Confusion matrix (test set):")
    print(f"    Predicted →   No default   Default")
    print(f"    Actual No def  {cm[0][0]:>8}   {cm[0][1]:>6}")
    print(f"    Actual Default {cm[1][0]:>8}   {cm[1][1]:>6}")
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    _banner("CREDIT RISK SCORING ENGINE — Training Pipeline")

    # 1. Data
    log.info("Generating 10,000 synthetic loan records …")
    df = generate_loan_data(n_samples=10_000, random_state=settings.RANDOM_STATE)
    default_rate = df["loan_status"].mean()
    log.info("  Default rate: %.1f %%  |  Features: 15 raw + 6 engineered", default_rate * 100)

    # 2. Train
    log.info("Training XGBoost (5-fold CV) …")
    pipeline, (X_test, y_test), meta = train_model(df)
    log.info(
        "  CV AUC = %.4f ± %.4f  |  train n=%d  test n=%d",
        meta["cv_auc_mean"], meta["cv_auc_std"], meta["n_train"], meta["n_test"],
    )

    # 3. Evaluate
    log.info("Evaluating on held-out test set …")
    metrics = evaluate_model(pipeline, X_test, y_test)
    _banner("Evaluation Results")
    _print_metrics(metrics, cv_auc=meta["cv_auc_mean"])

    # 4. Save
    model_path = Path(settings.MODEL_PATH)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)
    log.info("Pipeline saved → %s", model_path)

    print(f"\n  Next step: make run\n  Docs:      http://localhost:8000/docs\n")


if __name__ == "__main__":
    main()
