"""Unit tests for src/data/preprocessor.py"""
import numpy as np
import pytest
from sklearn.utils.estimator_checks import parametrize_with_checks

from src.data.preprocessor import (
    ALL_FEATURES,
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    build_preprocessor,
)
from src.features.engineer import add_features


def test_feature_list_lengths():
    assert len(NUMERIC_FEATURES) == 19
    assert len(CATEGORICAL_FEATURES) == 2
    assert len(ALL_FEATURES) == 21


def test_all_features_no_duplicates():
    assert len(ALL_FEATURES) == len(set(ALL_FEATURES))


def test_preprocessor_output_shape(sample_df):
    df = add_features(sample_df)
    X = df[ALL_FEATURES]
    preprocessor = build_preprocessor()
    X_t = preprocessor.fit_transform(X)
    assert X_t.shape == (len(df), len(ALL_FEATURES))


def test_preprocessor_no_nan_output(sample_df):
    df = add_features(sample_df)
    X = df[ALL_FEATURES]
    preprocessor = build_preprocessor()
    X_t = preprocessor.fit_transform(X)
    assert not np.isnan(X_t).any()


def test_preprocessor_numeric_scaled(sample_df):
    """After standard scaling, numeric columns should have ~zero mean."""
    df = add_features(sample_df)
    X = df[ALL_FEATURES]
    preprocessor = build_preprocessor()
    X_t = preprocessor.fit_transform(X)
    # First 19 columns are numeric (after standard scaling)
    numeric_block = X_t[:, : len(NUMERIC_FEATURES)]
    assert abs(numeric_block.mean()) < 0.5  # close to zero


def test_preprocessor_handles_unknown_category(sample_df):
    """OrdinalEncoder should not crash on unseen category values."""
    df = add_features(sample_df)
    X_train = df[ALL_FEATURES]
    preprocessor = build_preprocessor()
    preprocessor.fit(X_train)

    import pandas as pd
    X_new = X_train.copy()
    X_new["home_ownership"] = "UNKNOWN_TYPE"
    # Should not raise
    X_t = preprocessor.transform(X_new)
    assert X_t is not None
