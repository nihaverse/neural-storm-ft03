
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


MODEL_DIR = Path("models")


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


def predict_engine_state(
    feature_row: pd.DataFrame,
    xgb_model,
    anomaly_model,
    sensor_columns
):
    """
    Predict RUL and detect anomalous sensor behaviour
    for one engine reading.
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

    # Predict RUL.
    raw_rul = float(xgb_model.predict(xgb_input)[0])

    # Keep dashboard estimate within the training target range.
    estimated_rul = float(np.clip(raw_rul, 0, 125))

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
        "estimated_rul": estimated_rul,
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
    print("Estimated RUL:", round(result["estimated_rul"], 2))
    print("Anomaly detected:", result["is_anomaly"])
    print("Anomaly score:", round(result["anomaly_score"], 4))
