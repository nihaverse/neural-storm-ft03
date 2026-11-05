
import pandas as pd
import joblib
from pathlib import Path
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


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


def evaluate_model(model, X_val, y_val):

    # Generate predictions on validation data
    y_pred = model.predict(X_val)

    # Calculate evaluation metrics
    mae = mean_absolute_error(y_val, y_pred)

    rmse = mean_squared_error(
        y_val,
        y_pred
    ) ** 0.5

    print("\nModel Evaluation Results")
    print("------------------------")
    print(f"MAE:  {mae:.2f} cycles")
    print(f"RMSE: {rmse:.2f} cycles")

    # Compare actual and predicted values
    results = pd.DataFrame({
        "Actual_RUL": y_val.values,
        "Predicted_RUL": y_pred
    })

    print("\nSample Predictions:")
    print(results.head(10).round(2))

    return y_pred


def train_model(X_train, y_train):

    model = XGBRegressor(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1
    )

    print("Training XGBoost model...")

    model.fit(X_train, y_train)

    print("Model training completed!")

    model_dir = Path("models")
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "xgboost_rul_model.pkl"

    joblib.dump(model, model_path)

    print(f"Model saved at: {model_path}")

    return model

if __name__ == "__main__":

    X_train, X_val, y_train, y_val = prepare_data()

    print("Training features:", X_train.shape)

    model = train_model(X_train, y_train)

    evaluate_model(model, X_val, y_val)