
import numpy as np
import pandas as pd

from src.feature_engineering import create_features
from src.streaming_features import StreamingFeatureEngineer
from src.simulation import load_simulation_data, get_engine_readings


# Load one engine's actual validation readings.
df = load_simulation_data()

engine_id = 1

readings, _ = get_engine_readings(df, engine_id)

# Offline feature calculation.
offline_features = create_features(readings)

sensor_columns = [
    col for col in readings.columns
    if col.startswith("sensor_")
]

# Streaming feature calculation.
engineer = StreamingFeatureEngineer(sensor_columns)

streaming_rows = []

for _, reading in readings.iterrows():
    streaming_rows.append(
        engineer.process_reading(reading)
    )

streaming_features = pd.DataFrame(streaming_rows)

# Compare every engineered feature.
feature_columns = [
    col for col in offline_features.columns
    if any(
        suffix in col
        for suffix in [
            "_mean_5",
            "_mean_10",
            "_std_5",
            "_std_10",
            "_ema_5",
            "_trend_5",
        ]
    )
]

differences = (
    offline_features[feature_columns].to_numpy()
    - streaming_features[feature_columns].to_numpy()
)

max_difference = np.max(np.abs(differences))

print("Engine:", engine_id)
print("Cycles compared:", len(readings))
print("Features compared:", len(feature_columns))
print("Maximum absolute difference:", max_difference)

assert np.allclose(
    offline_features[feature_columns].to_numpy(),
    streaming_features[feature_columns].to_numpy(),
    atol=1e-9
)

print("\nOffline and streaming feature parity verified.")
