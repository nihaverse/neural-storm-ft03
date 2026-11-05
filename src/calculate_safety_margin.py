
import numpy as np

from src.inference import load_models
from src.train_model import prepare_data


def print_percentiles(label, errors):
    print(f"\n{label}")
    print("-" * 45)

    if len(errors) == 0:
        print("No over-predictions found in this group.")
        return

    for percentile in (50, 75, 90):
        value = np.percentile(errors, percentile)
        print(f"P{percentile}: {value:.4f} cycles")

    print(f"Over-prediction count: {len(errors)}")


def main():
    # Load existing validation data and trained model.
    _, X_val, _, y_val = prepare_data()
    xgb_model, _, _ = load_models()

    # Predict on held-out validation observations.
    predictions = xgb_model.predict(X_val)

    actual = y_val.to_numpy()
    errors = predictions - actual

    # Keep only positive errors.
    all_overpredictions = errors[errors > 0]

    # Restrict to actual RUL <= 50.
    low_rul_mask = actual <= 50
    low_rul_errors = errors[
        low_rul_mask & (errors > 0)
    ]

    print("\nSAFETY MARGIN EVALUATION")
    print("=" * 45)

    print(f"Total validation observations: {len(actual)}")
    print(f"Actual RUL <= 50 observations: {low_rul_mask.sum()}")

    print_percentiles(
        "LOW-RUL ZONE (Actual RUL <= 50)",
        low_rul_errors
    )

    print_percentiles(
        "ALL VALIDATION CYCLES",
        all_overpredictions
    )

    if len(low_rul_errors) > 0:
        p75 = np.percentile(low_rul_errors, 75)
        proposed_margin = min(float(p75), 15.0)

        print("\nPROPOSED SAFETY MARGIN")
        print("-" * 45)
        print(f"Low-RUL P75: {p75:.4f} cycles")
        print(f"Maximum allowed margin: 15.0000 cycles")
        print(f"Proposed margin: {proposed_margin:.4f} cycles")
    else:
        print("\nCannot calculate proposed margin: no low-RUL over-predictions.")


if __name__ == "__main__":
    main()
