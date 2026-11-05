
from src.simulation import (
    load_simulation_data,
    get_engine_ids,
    EngineSimulation,
)

from src.inference import load_models


# Load data and models once.
df = load_simulation_data()
models = load_models()

engine_id = get_engine_ids(df)[0]

simulation = EngineSimulation(
    engine_id=engine_id,
    df=df,
    models=models
)

print("Engine:", engine_id)
print("Total available cycles:", simulation.total_cycles)

# Process exactly three cycles.
results = []

for _ in range(3):
    result = simulation.process_next_cycle()
    results.append(result)

    print(
        f"\nCycle {result['cycle']}"
        f"\nRaw RUL: {result['prediction']['raw_rul']:.2f}"
        f"\nFinal RUL: {result['prediction']['final_rul']:.2f}"
        f"\nHealth Index: {result['prediction']['health_index']:.2f}"
        f"\nAnomaly: {result['prediction']['is_anomaly']}"
        f"\nActual RUL (evaluation only): {result['actual_rul']}"
    )

# Verify sequential processing.
assert [r["cycle"] for r in results] == [1, 2, 3]
assert simulation.position == 3
assert len(simulation.history) == 3

# Verify the model input did not contain ground-truth RUL.
assert "RUL" not in simulation.readings.columns

print("\nEngine simulation tests passed.")
