
from pathlib import Path
from src.streaming_features import StreamingFeatureEngineer
from src.inference import load_models, predict_engine_state

import pandas as pd


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

    engine_df = engine_df.sort_values("cycle").reset_index(drop=True)

    ground_truth_rul = engine_df["RUL"].copy()

    sensor_readings = engine_df.drop(columns=["RUL"])

    return sensor_readings, ground_truth_rul


class EngineSimulation:
    """
    Processes one engine's validation readings sequentially.

    This class is independent of Streamlit.
    Each instance maintains its own feature-engineering history.
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

    def process_next_cycle(self):
        """
        Process exactly one new reading.

        Returns None if the engine has completed its available cycles.
        """

        if self.is_finished:
            return None

        # Read the next observation without advancing the position yet.
        reading = self.readings.iloc[self.position]

        cycle = int(reading["cycle"])

        # Generate streaming features.
        features = self.feature_engineer.process_reading(reading)

        # Convert to a single-row DataFrame for inference.
        feature_row = pd.DataFrame([features])

        # Run XGBoost and Isolation Forest.
        prediction = predict_engine_state(
            feature_row,
            self.xgb_model,
            self.anomaly_model,
            self.sensor_columns
        )

        # Keep ground truth separate from model inputs.
        actual_rul = int(
            self.ground_truth_rul.iloc[self.position]
        )

        result = {
            "engine_id": self.engine_id,
            "cycle": cycle,
            "sensor_readings": {
                sensor: float(reading[sensor])
                for sensor in self.sensor_columns
            },
            "prediction": prediction,
            "actual_rul": actual_rul,
        }

        # Commit progress only after successful inference.
        self.history.append(result)
        self.position += 1

        return result

class FleetSimulationManager:
    """
    Manages independent simulations for all validation engines.

    Each call to process_next_cycle() advances every unfinished
    engine by exactly one cycle.
    """

    def __init__(self, df, models):
        self.engine_ids = get_engine_ids(df)

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
        Advance every unfinished engine by one cycle.

        Returns:
            Dictionary mapping engine IDs to their cycle results.
        """

        results = {}

        for engine_id, simulation in self.simulations.items():
            result = simulation.process_next_cycle()

            if result is not None:
                results[engine_id] = result

        return results

    