
import numpy as np
import pandas as pd
import joblib

from src.streaming_features import StreamingFeatureEngineer
from src.inference import load_models, predict_engine_state


# Load saved models.
xgb_model, anomaly_model, sensor_columns = load_models()

# Load validation data.
raw = pd.read_csv("data/processed/val_clean.csv")
offline = pd.read_csv("data/processed/val_features.csv")

# Select one complete validation engine.
engine_id = int(raw["engine_id"].iloc[0])

engine_raw = (
    raw[raw["engine_id"] == engine_id]
    .sort_values("cycle")
    .reset_index(drop=True)
)

engine_offline = (
    offline[offline["engine_id"] == engine_id]
    .sort_values("cycle")
    .reset_index(drop=True)
)

# Initialize independent streaming state for this engine.
engineer = StreamingFeatureEngineer(sensor_columns)

expected_features = list(xgb_model.feature_names_in_)

streaming_results = []
feature_differences = []
prediction_differences = []
anomaly_flag_mismatches = []
anomaly_score_differences = []

for index, reading in engine_raw.iterrows():

    # Generate features from one incoming reading.
    generated = engineer.process_reading(reading)

    feature_row = pd.DataFrame([generated])

    # Compare streaming features against offline features.
    offline_row = engine_offline.iloc[[index]]

    difference = np.abs(
        feature_row[expected_features].to_numpy()
        - offline_row[expected_features].to_numpy()
    )

    feature_differences.append(difference.max())

    # Run both ML models using streaming features.
    result = predict_engine_state(
        feature_row,
        xgb_model,
        anomaly_model,
        sensor_columns
    )

    # Calculate reference predictions using offline features.
    offline_input = offline_row[expected_features]

    reference_rul = float(
        xgb_model.predict(offline_input)[0]
    )

    reference_anomaly = int(
        anomaly_model.predict(offline_row[sensor_columns])[0]
    )

    reference_score = float(
        anomaly_model.decision_function(
            offline_row[sensor_columns]
        )[0]
    )

    prediction_differences.append(
        abs(result["raw_rul"] - reference_rul)
    )

    anomaly_flag_mismatches.append(
        result["is_anomaly"] != (reference_anomaly == -1)
    )

    anomaly_score_differences.append(
        abs(result["anomaly_score"] - reference_score)
    )

    streaming_results.append({
        "cycle": int(reading["cycle"]),
        "actual_rul": int(reading["RUL"]),
        "predicted_rul": result["estimated_rul"],
        "anomaly": result["is_anomaly"],
        "anomaly_score": result["anomaly_score"]
    })


results = pd.DataFrame(streaming_results)

print("\nEND-TO-END STREAMING PIPELINE TEST")
print("----------------------------------")
print("Engine ID:", engine_id)
print("Cycles processed:", len(results))

print(
    "Maximum feature difference:",
    max(feature_differences)
)

print(
    "Maximum raw RUL prediction difference:",
    max(prediction_differences)
)

print(
    "Anomaly flag mismatches:",
    sum(anomaly_flag_mismatches)
)

print(
    "Maximum anomaly score difference:",
    max(anomaly_score_differences)
)

print("\nFirst 5 streaming predictions:")
print(results.head().round(4).to_string(index=False))

print("\nLast 5 streaming predictions:")
print(results.tail().round(4).to_string(index=False))

print("\nPipeline test completed.")
