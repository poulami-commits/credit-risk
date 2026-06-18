#!/usr/bin/env python3
"""
Evaluate the trained model on a fresh synthetic batch and print a report.

Usage
-----
    python scripts/evaluate.py

Useful for post-deployment monitoring: swap in a recent production sample
for `df` to detect score distribution drift (PSI).
"""
from __future__ import annotations

import sys
from pathlib import Path

import joblib

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import settings
from src.data.generator import generate_loan_data
from src.data.preprocessor import ALL_FEATURES
from src.features.engineer import add_features
from src.models.evaluator import evaluate_model, population_stability_index


def _section(title: str) -> None:
    print("\n" + "─" * 52)
    print(f"  {title}")
    print("─" * 52)


def main() -> None:
    pipeline = joblib.load(settings.MODEL_PATH)

    # Fresh 2,000-sample evaluation set (different seed from training)
    df_eval = add_features(generate_loan_data(n_samples=2_000, random_state=99))
    X_eval = df_eval[ALL_FEATURES]
    y_eval = df_eval["loan_status"]

    metrics = evaluate_model(pipeline, X_eval, y_eval)

    _section("CREDIT RISK MODEL — Evaluation Report")
    print(f"\n  {'Metric':<24} {'Score':>8}  Benchmark")
    print("  " + "─" * 44)
    rows = [
        ("AUC-ROC",           metrics["auc_roc"],          "≥ 0.75"),
        ("KS Statistic",      metrics["ks_statistic"],     "≥ 0.40"),
        ("Gini Coefficient",  metrics["gini_coefficient"], "≥ 0.60"),
        ("Brier Score",       metrics["brier_score"],      "lower = better"),
    ]
    for label, val, bench in rows:
        print(f"  {label:<24} {val:>8.4f}  {bench}")

    _section("Confusion Matrix")
    cm = metrics["confusion_matrix"]
    print(f"  {'':16} Pred: No-def  Pred: Default")
    print(f"  Actual No-def   {cm[0][0]:>10}  {cm[0][1]:>12}")
    print(f"  Actual Default  {cm[1][0]:>10}  {cm[1][1]:>12}")

    _section("Classification Report (threshold = 0.50)")
    cr = metrics["classification_report"]
    for label in ["0", "1"]:
        r = cr[label]
        name = "No default" if label == "0" else "Default   "
        print(
            f"  {name}  precision={r['precision']:.3f}  "
            f"recall={r['recall']:.3f}  f1={r['f1-score']:.3f}  n={int(r['support'])}"
        )

    # PSI on score distributions (training vs eval population)
    df_train = add_features(generate_loan_data(n_samples=8_000, random_state=42))
    p_train = pipeline.predict_proba(df_train[ALL_FEATURES])[:, 1]
    p_eval  = pipeline.predict_proba(X_eval)[:, 1]
    psi = population_stability_index(p_train, p_eval)

    _section("Population Stability Index (PSI)")
    stability = (
        "Stable ✓"           if psi < 0.10 else
        "Minor shift ⚠"       if psi < 0.25 else
        "Significant drift ✗"
    )
    print(f"  PSI = {psi:.4f}  →  {stability}")
    print()


if __name__ == "__main__":
    main()
