
import numpy as np

from src.simulation import (
    EngineSimulation,
    FleetSimulationManager,
    load_simulation_data,
)
from src.inference import load_models


TEST_CYCLES = 10
TOLERANCE = 1e-6


def test_batch_equivalence():

    print("\nBATCH VS SEQUENTIAL INFERENCE TEST")
    print("----------------------------------")

    # Load data and trained models.
    df = load_simulation_data()
    models = load_models()

    engine_ids = sorted(df["engine_id"].unique().tolist())

    # Initialize the batch fleet.
    fleet = FleetSimulationManager(df, models)

    # Initialize independent sequential reference simulations.
    reference_simulations = {
        engine_id: EngineSimulation(
            engine_id=engine_id,
            df=df,
            models=models,
        )
        for engine_id in engine_ids
    }

    prediction_fields = [
        "raw_rul",
        "final_rul",
        "health_index",
        "anomaly_score",
        "safety_margin",
    ]

    maximum_differences = {
        field: 0.0 for field in prediction_fields
    }

    anomaly_mismatches = 0
    readings_compared = 0

    # Compare multiple fleet ticks.
    for tick in range(TEST_CYCLES):

        batch_results = fleet.process_next_cycle()

        for engine_id in engine_ids:

            reference_result = (
                reference_simulations[engine_id].process_next_cycle()
            )

            # Both simulations should advance together.
            if reference_result is None:
                if engine_id in batch_results:
                    raise AssertionError(
                        f"Engine {engine_id}: unexpected batch result."
                    )
                continue

            if engine_id not in batch_results:
                raise AssertionError(
                    f"Engine {engine_id}: missing batch result."
                )

            batch_prediction = batch_results[engine_id]["prediction"]
            sequential_prediction = reference_result["prediction"]

            # Compare numerical predictions.
            for field in prediction_fields:

                difference = abs(
                    batch_prediction[field]
                    - sequential_prediction[field]
                )

                maximum_differences[field] = max(
                    maximum_differences[field],
                    difference,
                )

                if not np.isclose(
                    batch_prediction[field],
                    sequential_prediction[field],
                    atol=TOLERANCE,
                    rtol=TOLERANCE,
                ):
                    raise AssertionError(
                        f"Mismatch in {field} for engine {engine_id}, "
                        f"tick {tick + 1}: "
                        f"batch={batch_prediction[field]}, "
                        f"sequential={sequential_prediction[field]}"
                    )

            # Anomaly classification must match exactly.
            if (
                batch_prediction["is_anomaly"]
                != sequential_prediction["is_anomaly"]
            ):
                anomaly_mismatches += 1

                raise AssertionError(
                    f"Anomaly mismatch for engine {engine_id}, "
                    f"tick {tick + 1}."
                )

            # Confirm cycle and actual RUL alignment.
            assert (
                batch_results[engine_id]["cycle"]
                == reference_result["cycle"]
            )

            assert (
                batch_results[engine_id]["actual_rul"]
                == reference_result["actual_rul"]
            )

            readings_compared += 1

    print("Engines tested:", len(engine_ids))
    print("Fleet ticks tested:", TEST_CYCLES)
    print("Readings compared:", readings_compared)

    print("\nMaximum prediction differences:")

    for field, difference in maximum_differences.items():
        print(f"{field}: {difference:.12f}")

    print("Anomaly flag mismatches:", anomaly_mismatches)

    print("\nBatch and sequential inference are equivalent.")


if __name__ == "__main__":
    test_batch_equivalence()
