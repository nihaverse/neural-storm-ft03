
import pandas as pd


def prepare_data():

    # Load engineered datasets
    train_df = pd.read_csv(
        "data/processed/train_features.csv"
    )

    val_df = pd.read_csv(
        "data/processed/val_features.csv"
    )

    # Columns that must not be model inputs
    excluded_columns = [
        "engine_id",
        "cycle",
        "RUL"
    ]

    # Separate features (X) and target (y)
    X_train = train_df.drop(
        columns=excluded_columns
    )

    y_train = train_df["RUL"]

    X_val = val_df.drop(
        columns=excluded_columns
    )

    y_val = val_df["RUL"]

    # Ensure training and validation have identical features
    assert list(X_train.columns) == list(X_val.columns), (
        "Training and validation features do not match!"
    )

    # Return prepared datasets
    return X_train, X_val, y_train, y_val


if __name__ == "__main__":

    X_train, X_val, y_train, y_val = prepare_data()

    print("Data preparation completed!")

    print("\nTraining features:", X_train.shape)
    print("Validation features:", X_val.shape)

    print("\nTraining target:", y_train.shape)
    print("Validation target:", y_val.shape)

    print("\nNumber of input features:", X_train.shape[1])

    print("\nTraining RUL range:")
    print(y_train.min(), "to", y_train.max())

    print("\nValidation RUL range:")
    print(y_val.min(), "to", y_val.max())
