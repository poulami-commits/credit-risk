"""Unit tests for src/features/engineer.py"""
import numpy as np
import pandas as pd
import pytest

from src.features.engineer import add_features


def test_add_features_returns_copy(sample_df):
    """add_features must not mutate the input DataFrame."""
    original_cols = set(sample_df.columns)
    enriched = add_features(sample_df)
    assert set(sample_df.columns) == original_cols, "Input DataFrame was mutated"
    assert set(enriched.columns) > original_cols


def test_engineered_columns_present(sample_df):
    result = add_features(sample_df)
    expected = {
        "income_loan_ratio",
        "monthly_payment",
        "payment_to_income",
        "high_revol_util",
        "acc_diversity",
        "fico_bucket",
    }
    assert expected.issubset(result.columns)


def test_income_loan_ratio_positive(sample_df):
    result = add_features(sample_df)
    assert (result["income_loan_ratio"] > 0).all()


def test_monthly_payment_positive(sample_df):
    result = add_features(sample_df)
    assert (result["monthly_payment"] > 0).all()


def test_high_revol_util_binary(sample_df):
    result = add_features(sample_df)
    assert set(result["high_revol_util"].unique()).issubset({0, 1})


def test_fico_bucket_range(sample_df):
    result = add_features(sample_df)
    assert result["fico_bucket"].between(0, 5).all()


def test_no_nan_in_engineered_cols(sample_df):
    result = add_features(sample_df)
    eng_cols = ["income_loan_ratio", "monthly_payment", "payment_to_income",
                "high_revol_util", "acc_diversity", "fico_bucket"]
    assert result[eng_cols].isnull().sum().sum() == 0
