
from pathlib import Path
from copy import deepcopy

import pandas as pd

from src.streaming_features import StreamingFeatureEngineer
from src.inference import (
    load_models,
    predict_engine_state,
    predict_engine_states,
)


VALIDATION_DATA_PATH = Path("data/processed/val_clean.csv")


def load_simulation_data():
    """Load and prepare validation data for sequential simulation."""

    if not VALIDATION_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Validation dataset not found: {VALIDATION_DATA_PATH}"
        )

    df = pd.read_csv(VALIDATION_DATA_PATH)

    required_columns = {"engine_id", "cycle", "RUL"}

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Validation data is missing columns: {sorted(missing)}"
        )

    df = df.sort_values(
        ["engine_id", "cycle"]
    ).reset_index(drop=True)

    return df


def get_engine_ids(df):
    """Return actual engine IDs available in the dataset."""

    return sorted(df["engine_id"].unique().tolist())


def get_engine_readings(df, engine_id):
    """
    Return one engine's readings in chronological cycle order.

    Ground-truth RUL is kept separate from sensor inputs.
    """

    engine_df = df[df["engine_id"] == engine_id].copy()

    if engine_df.empty:
        raise ValueError(
            f"Engine {engine_id} not found in simulation data."
        )

    engine_df = engine_df.sort_values(
        "cycle"
    ).reset_index(drop=True)

    ground_truth_rul = engine_df["RUL"].copy()

    sensor_readings = engine_df.drop(columns=["RUL"])

    return sensor_readings, ground_truth_rul


class EngineSimulation:
    """
    Maintains sequential simulation state for one engine.

    Feature generation remains sequential.
    Model inference can be performed individually or in batches.
    """

    def __init__(self, engine_id, df, models):

        self.engine_id = int(engine_id)

        self.readings, self.ground_truth_rul = get_engine_readings(
            df,
            self.engine_id
        )

        self.xgb_model, self.anomaly_model, self.sensor_columns = models

        self.feature_engineer = StreamingFeatureEngineer(
            self.sensor_columns
        )

        self.position = 0
        self.history = []

    @property
    def total_cycles(self):
        return len(self.readings)

    @property
    def is_finished(self):
        return self.position >= self.total_cycles

    def prepare_next_cycle(self):
        """
        Generate features for the next reading without committing state.

        A temporary feature engineer ensures that failed batch inference
        does not corrupt the engine's sequential feature history.
        """

        if self.is_finished:
            return None

        reading = self.readings.iloc[self.position]

        cycle = int(reading["cycle"])

        # Work on a copy so the original state remains unchanged.
        candidate_engineer = deepcopy(
            self.feature_engineer
        )

        features = candidate_engineer.process_reading(
            reading
        )

        actual_rul = int(
            self.ground_truth_rul.iloc[self.position]
        )

        return {
            "feature_engineer": candidate_engineer,
            "features": features,
            "cycle": cycle,
            "actual_rul": actual_rul,
            "sensor_readings": {
                sensor: float(reading[sensor])
                for sensor in self.sensor_columns
            }
        }

    def commit_cycle(self, pending, prediction):
        """
        Commit feature-engineering state and inference results.

        Called only after successful inference.
        """

        if pending is None:
            return None

        if self.is_finished:
            raise RuntimeError(
                f"Engine {self.engine_id} has already finished."
            )

        # Commit the successfully advanced feature engineer.
        self.feature_engineer = pending["feature_engineer"]

        result = {
            "engine_id": self.engine_id,
            "cycle": pending["cycle"],
            "sensor_readings": pending["sensor_readings"],
            "prediction": prediction,
            "actual_rul": pending["actual_rul"],
        }

        self.history.append(result)
        self.position += 1

        return result

    def process_next_cycle(self):
        """
        Process exactly one reading using single-row inference.

        Retained for compatibility with existing single-engine workflows.
        """

        pending = self.prepare_next_cycle()

        if pending is None:
            return None

        feature_row = pd.DataFrame([
            pending["features"]
        ])

        prediction = predict_engine_state(
            feature_row,
            self.xgb_model,
            self.anomaly_model,
            self.sensor_columns
        )

        return self.commit_cycle(
            pending,
            prediction
        )


class FleetSimulationManager:
    """
    Manages independent simulations for all validation engines.

    Each call advances every unfinished engine by one cycle.

    Feature generation is sequential per engine.
    Model inference is performed in batches across the fleet.
    """

    def __init__(self, df, models):

        self.engine_ids = get_engine_ids(df)

        self.models = models

        self.simulations = {
            engine_id: EngineSimulation(
                engine_id=engine_id,
                df=df,
                models=models
            )
            for engine_id in self.engine_ids
        }

    @property
    def total_engines(self):
        return len(self.engine_ids)

    @property
    def is_finished(self):
        return all(
            simulation.is_finished
            for simulation in self.simulations.values()
        )

    def process_next_cycle(self):
        """
        Advance all unfinished engines by one cycle.

        Generates features sequentially, performs batch inference,
        and commits results to their respective engine simulations.

        Returns:
            Dictionary mapping engine IDs to their cycle results.
        """

        pending_cycles = []

        # Step 1: Generate the next feature row for every unfinished engine.
        for engine_id, simulation in self.simulations.items():

            pending = simulation.prepare_next_cycle()

            if pending is not None:
                pending_cycles.append(
                    (engine_id, pending)
                )

        if not pending_cycles:
            return {}

        # Step 2: Combine feature rows into one DataFrame.
        feature_rows = pd.DataFrame([
            pending["features"]
            for _, pending in pending_cycles
        ])

        # Step 3: Perform batch inference.
        predictions = predict_engine_states(
            feature_rows,
            self.models[0],
            self.models[1],
            self.models[2]
        )

        if len(predictions) != len(pending_cycles):
            raise RuntimeError(
                "Batch inference returned an unexpected number of results."
            )

        # Step 4: Commit results to the correct engines.
        results = {}

        for (engine_id, pending), prediction in zip(
            pending_cycles,
            predictions
        ):

            simulation = self.simulations[engine_id]

            result = simulation.commit_cycle(
                pending,
                prediction
            )

            results[engine_id] = result

        return results
