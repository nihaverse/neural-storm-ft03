
from src.simulation import (
    load_simulation_data,
    get_engine_ids,
    get_engine_readings,
)


df = load_simulation_data()

engine_ids = get_engine_ids(df)

print("Dataset shape:", df.shape)
print("Available engines:", engine_ids)

assert len(engine_ids) == 20
assert df.groupby("engine_id").size().sum() == 4070

# Test one actual engine.
engine_id = engine_ids[0]

readings, ground_truth_rul = get_engine_readings(
    df,
    engine_id
)

assert "RUL" not in readings.columns
assert len(readings) == len(ground_truth_rul)
assert readings["cycle"].is_monotonic_increasing

print("\nTest engine:", engine_id)
print("Number of cycles:", len(readings))
print("Sensor/input columns:", readings.columns.tolist())
print("First cycle:", readings.iloc[0]["cycle"])
print("Last cycle:", readings.iloc[-1]["cycle"])
print("\nAll simulation data loader tests passed.")
