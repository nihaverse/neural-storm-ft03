from src.simulation import (
    load_simulation_data,
    FleetSimulationManager,
)
from src.inference import load_models


# Load data and models once.
df = load_simulation_data()
models = load_models()

# Initialize the fleet.
fleet = FleetSimulationManager(
    df=df,
    models=models
)

print("Total engines:", fleet.total_engines)

assert fleet.total_engines == 20

# Process the first fleet-wide cycle.
results = fleet.process_next_cycle()

print("\nFirst fleet simulation tick:")
print("Engines processed:", len(results))

assert len(results) == 20

for engine_id, result in results.items():
    assert result["cycle"] == 1

    print(
        f"Engine {engine_id}: "
        f"Cycle {result['cycle']} | "
        f"RUL {result['prediction']['final_rul']:.2f} | "
        f"Health {result['prediction']['health_index']:.2f} | "
        f"Anomaly {result['prediction']['is_anomaly']}"
    )

# Process the second fleet-wide cycle.
second_results = fleet.process_next_cycle()

assert len(second_results) == 20

for result in second_results.values():
    assert result["cycle"] == 2

# Verify independent progression.
for simulation in fleet.simulations.values():
    assert simulation.position == 2
    assert len(simulation.history) == 2

print("\nFleet simulation tests passed.")