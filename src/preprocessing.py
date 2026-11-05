import pandas as pd
from pathlib import Path

from sklearn.model_selection import GroupShuffleSplit
from src.data_loader import load_data


def create_rul(df):

    max_cycles = (
        df.groupby("engine_id")["cycle"]
        .max()
        .rename("max_cycle")
    )

    df = df.join(max_cycles, on="engine_id")

    df["RUL"] = df["max_cycle"] - df["cycle"]

    # Cap RUL at 125
    df["RUL"] = df["RUL"].clip(upper=125)

    df.drop(columns=["max_cycle"], inplace=True)

    return df


def split_by_engine(df):

    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.2,
        random_state=42
    )

    train_idx, val_idx = next(
        splitter.split(df, groups=df["engine_id"])
    )

    train_df = df.iloc[train_idx].copy()
    val_df = df.iloc[val_idx].copy()

    # Verify no engine leakage
    assert set(train_df["engine_id"]).isdisjoint(
        set(val_df["engine_id"])
    )

    return train_df, val_df


def remove_constant_sensors(train_df, val_df):

    sensor_columns = [
        col for col in train_df.columns
        if col.startswith("sensor_")
    ]

    constant_sensors = [
        col for col in sensor_columns
        if train_df[col].nunique() <= 1
    ]

    print("Constant sensors:", constant_sensors)

    train_df.drop(columns=constant_sensors, inplace=True)
    val_df.drop(columns=constant_sensors, inplace=True)

    return train_df, val_df


def preprocess_data():

    df = load_data()

    # Step 1: Create RUL labels
    df = create_rul(df)

    # Step 2: Split by engine
    train_df, val_df = split_by_engine(df)

    # Step 3: Remove constant sensors
    train_df, val_df = remove_constant_sensors(
        train_df, val_df
    )

    # Step 4: Save processed datasets
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    train_df.to_csv(
        output_dir / "train_clean.csv",
        index=False
    )

    val_df.to_csv(
        output_dir / "val_clean.csv",
        index=False
    )

    print("\nTraining engines:", train_df["engine_id"].nunique())
    print("Validation engines:", val_df["engine_id"].nunique())

    print("\nTraining shape:", train_df.shape)
    print("Validation shape:", val_df.shape)

    print("\nRUL statistics:")
    print(train_df["RUL"].describe())

    print("\nPreprocessing completed successfully!")


if __name__ == "__main__":
    preprocess_data()