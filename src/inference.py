
from pathlib import Path
from functools import lru_cache
import json

import joblib
import numpy as np
import pandas as pd


MODEL_DIR = Path("models")
SAFETY_MARGIN_PATH = MODEL_DIR / "safety_margin.json"


def load_models():
    """Load saved ML models without retraining."""

    xgb_model = joblib.load(
        MODEL_DIR / "xgboost_rul_model.pkl"
    )

    anomaly_artifact = joblib.load(
        MODEL_DIR / "isolation_forest.pkl"
    )

    anomaly_model = anomaly_artifact["model"]

    # Avoid parallel scheduling overhead for single-row inference.
    anomaly_model.set_params(n_jobs=1)

    sensor_columns = anomaly_artifact["sensor_columns"]

    return xgb_model, anomaly_model, sensor_columns


@lru_cache(maxsize=1)
def load_safety_margin():
    """Load the calibrated safety margin once per process."""

    if not SAFETY_MARGIN_PATH.exists():
        raise FileNotFoundError(
            f"Safety margin file not found: {SAFETY_MARGIN_PATH}"
        )

    with open(SAFETY_MARGIN_PATH, "r", encoding="utf-8") as file:
        config = json.load(file)

    margin = float(config["safety_margin"])

    if not np.isfinite(margin) or not 0 <= margin <= 15:
        raise ValueError(
            f"Invalid safety margin: {margin}. Expected a value from 0 to 15."
        )

    return margin


def predict_engine_states(
    feature_rows: pd.DataFrame,
    xgb_model,
    anomaly_model,
    sensor_columns
):
    """
    Perform batch RUL prediction and anomaly detection.

    Each row represents one engine's current sequential reading.
    Returns one prediction dictionary per input row, in the same order.
    """

    if feature_rows.empty:
        return []

    # Validate XGBoost features.
    expected_features = list(xgb_model.feature_names_in_)

    missing_features = [
        col for col in expected_features
        if col not in feature_rows.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing XGBoost features: {missing_features}"
        )

    # Validate anomaly detection sensor columns.
    missing_sensors = [
        col for col in sensor_columns
        if col not in feature_rows.columns
    ]

    if missing_sensors:
        raise ValueError(
            f"Missing anomaly detection sensors: {missing_sensors}"
        )

    # Preserve the exact feature order used during training.
    xgb_input = feature_rows.loc[:, expected_features]
    anomaly_input = feature_rows.loc[:, sensor_columns]

    # Perform batch inference.
    raw_predictions = np.asarray(
        xgb_model.predict(xgb_input),
        dtype=float
    )

    anomaly_scores = np.asarray(
        anomaly_model.decision_function(anomaly_input),
        dtype=float
    )

    if len(raw_predictions) != len(feature_rows):
        raise RuntimeError("XGBoost returned an unexpected number of predictions.")

    if len(anomaly_scores) != len(feature_rows):
        raise RuntimeError("Isolation Forest returned an unexpected number of scores.")

    # Apply safety calibration exactly once.
    safety_margin = load_safety_margin()

    final_predictions = np.clip(
        raw_predictions - safety_margin,
        0,
        125
    )

    health_indices = np.clip(
        (final_predictions / 125) * 100,
        0,
        100
    )

    results = []

    for raw_rul, final_rul, health, anomaly_score in zip(
        raw_predictions,
        final_predictions,
        health_indices,
        anomaly_scores
    ):
        results.append({
            "raw_rul": float(raw_rul),
            "safety_margin": safety_margin,
            "final_rul": float(final_rul),
            "health_index": float(health),
            "is_anomaly": bool(anomaly_score < 0),
            "anomaly_score": float(anomaly_score)
        })

    return results


def predict_engine_state(
    feature_row: pd.DataFrame,
    xgb_model,
    anomaly_model,
    sensor_columns
):
    """
    Perform single-row inference using the batch inference function.

    Preserves the existing function interface and return format.
    """

    results = predict_engine_states(
        feature_row,
        xgb_model,
        anomaly_model,
        sensor_columns
    )

    if not results:
        raise ValueError(
            "Cannot predict an empty feature row."
        )

    return results[0]


if __name__ == "__main__":

    # Smoke test using one existing validation observation.
    from src.train_model import prepare_data

    X_train, X_val, y_train, y_val = prepare_data()

    xgb_model, anomaly_model, sensor_columns = load_models()

    sample = X_val.iloc[[0]]

    result = predict_engine_state(
        sample,
        xgb_model,
        anomaly_model,
        sensor_columns
    )

    print("\nINFERENCE TEST")
    print("--------------")
    print("Actual RUL:", int(y_val.iloc[0]))
    print("Raw predicted RUL:", round(result["raw_rul"], 2))
    print("Safety margin:", round(result["safety_margin"], 4))
    print("Final RUL:", round(result["final_rul"], 2))
    print("Health Index (RUL-based):", round(result["health_index"], 2))
    print("Anomaly detected:", result["is_anomaly"])
    print("Anomaly score:", round(result["anomaly_score"], 4))
