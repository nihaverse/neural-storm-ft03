
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


def predict_engine_state(
    feature_row: pd.DataFrame,
    xgb_model,
    anomaly_model,
    sensor_columns
):
    """
    Predict final RUL and detect anomalous sensor behaviour.

    Safety margin is applied exactly once here.
    """

    # Ensure all expected XGBoost features exist.
    expected_features = list(xgb_model.feature_names_in_)

    missing_features = [
        col for col in expected_features
        if col not in feature_row.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing XGBoost features: {missing_features}"
        )

    # Preserve the exact feature order used during training.
    xgb_input = feature_row[expected_features]

    # Raw XGBoost prediction.
    raw_rul = float(xgb_model.predict(xgb_input)[0])

    # Load saved calibration and apply safety margin exactly once.
    safety_margin = load_safety_margin()

    final_rul = float(
        np.clip(raw_rul - safety_margin, 0, 125)
    )

    # Health Index is derived from the same final RUL.
    health_index = float(
        np.clip((final_rul / 125) * 100, 0, 100)
    )

    # Anomaly detection using original sensor readings.
    anomaly_input = feature_row[sensor_columns]

    anomaly_prediction = anomaly_model.predict(
        anomaly_input
    )[0]

    anomaly_score = float(
        anomaly_model.decision_function(anomaly_input)[0]
    )

    return {
        "raw_rul": raw_rul,
        "safety_margin": safety_margin,
        "final_rul": final_rul,
        "health_index": health_index,
        "is_anomaly": bool(anomaly_prediction == -1),
        "anomaly_score": anomaly_score
    }


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
