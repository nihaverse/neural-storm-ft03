
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

from src.train_model import prepare_data


def train_anomaly_detector(X_train, y_train):
    # Use original sensor readings only.
    sensor_columns = [
        col for col in X_train.columns
        if col.startswith("sensor_")
        and "_mean_" not in col
        and "_std_" not in col
        and "_ema_" not in col
        and "_trend" not in col
    ]

    # Healthy baseline: observations with RUL >= 100.
    healthy_mask = y_train >= 100
    X_healthy = X_train.loc[healthy_mask, sensor_columns]

    print("\nIsolation Forest Training")
    print("-------------------------")
    print("Sensor features:", len(sensor_columns))
    print("Healthy training observations:", len(X_healthy))

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_healthy)

    return model, sensor_columns


def evaluate_anomalies(model, X_val, y_val, sensor_columns):
    predictions = model.predict(X_val[sensor_columns])

    # Isolation Forest: -1 = anomaly, +1 = normal.
    anomaly_mask = predictions == -1

    print("\nValidation Anomaly Analysis")
    print("---------------------------")

    groups = {
        "Healthy (RUL >= 100)": y_val >= 100,
        "Middle (RUL 31-99)": (y_val > 30) & (y_val < 100),
        "Near failure (RUL <= 30)": y_val <= 30
    }

    for label, mask in groups.items():
        if mask.sum() == 0:
            continue

        anomaly_rate = np.mean(anomaly_mask[mask.to_numpy()]) * 100

        print(
            f"{label}: "
            f"{anomaly_rate:.2f}% observations flagged as anomalies"
        )


if __name__ == "__main__":
    X_train, X_val, y_train, y_val = prepare_data()

    model, sensor_columns = train_anomaly_detector(
        X_train, y_train
    )

    evaluate_anomalies(
        model, X_val, y_val, sensor_columns
    )

    model_dir = Path("models")
    model_dir.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model": model,
        "sensor_columns": sensor_columns
    }

    model_path = model_dir / "isolation_forest.pkl"
    joblib.dump(artifact, model_path)

    print(f"\nIsolation Forest saved at: {model_path}")
