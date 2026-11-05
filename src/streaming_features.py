
from collections import deque

import numpy as np
import pandas as pd


class StreamingFeatureEngineer:

    def __init__(self, sensor_columns):
        self.sensor_columns = sensor_columns

        # Maintain the latest 10 readings for every sensor.
        self.history = {
            sensor: deque(maxlen=10)
            for sensor in sensor_columns
        }

        # Maintain the recursive EMA state.
        self.ema = {
            sensor: None
            for sensor in sensor_columns
        }

    def process_reading(self, reading):
        """
        Process exactly one incoming engine reading.
        Returns the original columns plus 6 features per sensor.
        """

        if isinstance(reading, pd.Series):
            reading = reading.to_dict()

        features = dict(reading)

        for sensor in self.sensor_columns:

            current_value = float(reading[sensor])

            # Add current reading to rolling history.
            self.history[sensor].append(current_value)

            values = list(self.history[sensor])

            # Rolling means.
            features[f"{sensor}_mean_5"] = float(
                np.mean(values[-5:])
            )

            features[f"{sensor}_mean_10"] = float(
                np.mean(values[-10:])
            )

            # Rolling sample standard deviations.
            # Pandas rolling().std() uses ddof=1.
            features[f"{sensor}_std_5"] = (
                float(np.std(values[-5:], ddof=1))
                if len(values[-5:]) >= 2 else 0.0
            )

            features[f"{sensor}_std_10"] = (
                float(np.std(values[-10:], ddof=1))
                if len(values[-10:]) >= 2 else 0.0
            )

            # Recursive EMA: span=5 gives alpha=1/3.
            previous_ema = self.ema[sensor]

            if previous_ema is None:
                current_ema = current_value
            else:
                current_ema = (
                    (1 / 3) * current_value
                    + (2 / 3) * previous_ema
                )

            self.ema[sensor] = current_ema

            features[f"{sensor}_ema_5"] = float(current_ema)

            # Difference from exactly 5 cycles ago.
            features[f"{sensor}_trend_5"] = (
                (current_value - values[-6]) / 5
                if len(values) >= 6 else 0.0
            )

        return features
