
import pandas as pd


def create_features(df):

    df = df.copy()

    # Always sort before calculating temporal features
    df = df.sort_values(
        ["engine_id", "cycle"]
    ).reset_index(drop=True)

    sensor_columns = [
        col for col in df.columns
        if col.startswith("sensor_")
    ]

    grouped = df.groupby("engine_id")

    for sensor in sensor_columns:

        # Rolling mean over 5 cycles
        df[f"{sensor}_mean_5"] = (
            grouped[sensor]
            .transform(
                lambda s: s.rolling(
                    window=5,
                    min_periods=1
                ).mean()
            )
        )

        # Rolling mean over 10 cycles
        df[f"{sensor}_mean_10"] = (
            grouped[sensor]
            .transform(
                lambda s: s.rolling(
                    window=10,
                    min_periods=1
                ).mean()
            )
        )

        # Rolling standard deviation over 5 cycles
        df[f"{sensor}_std_5"] = (
            grouped[sensor]
            .transform(
                lambda s: s.rolling(
                    window=5,
                    min_periods=2
                ).std()
            )
        ).fillna(0)

        # Rolling standard deviation over 10 cycles
        df[f"{sensor}_std_10"] = (
            grouped[sensor]
            .transform(
                lambda s: s.rolling(
                    window=10,
                    min_periods=2
                ).std()
            )
        ).fillna(0)

        # Exponential moving average
        df[f"{sensor}_ema_5"] = (
            grouped[sensor]
            .transform(
                lambda s: s.ewm(
                    span=5,
                    adjust=False
                ).mean()
            )
        )

        # Trend over previous 5 cycles
        previous_value = grouped[sensor].shift(5)

        df[f"{sensor}_trend_5"] = (
            df[sensor] - previous_value
        ) / 5

        df[f"{sensor}_trend_5"] = (
            df[f"{sensor}_trend_5"].fillna(0)
        )

    return df


if __name__ == "__main__":

    train_df = pd.read_csv(
        "data/processed/train_clean.csv"
    )

    val_df = pd.read_csv(
        "data/processed/val_clean.csv"
    )

    train_features = create_features(train_df)
    val_features = create_features(val_df)

    train_features.to_csv(
        "data/processed/train_features.csv",
        index=False
    )

    val_features.to_csv(
        "data/processed/val_features.csv",
        index=False
    )

    print("Feature engineering completed!")

    print("Training shape:", train_features.shape)
    print("Validation shape:", val_features.shape)

    print("\nNew features:")
    print([
        col for col in train_features.columns
        if "_mean_" in col
        or "_std_" in col
        or "_ema_" in col
        or "_trend_" in col
    ][:20])
