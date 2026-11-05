
import streamlit as st

from dashboard.state import (
    initialize_session_state,
    update_engine_state,
)


initialize_session_state()

# Use the actual dashboard defaults.
st.session_state["warning_threshold"] = 3
st.session_state["critical_threshold"] = 5


def make_prediction(final_rul, anomaly):
    return {
        "raw_rul": final_rul + 14.1812,
        "safety_margin": 14.1812,
        "final_rul": final_rul,
        "health_index": (final_rul / 125) * 100,
        "is_anomaly": anomaly,
        "anomaly_score": -0.1 if anomaly else 0.1,
    }


# Engine 1: Healthy initially.
for cycle in range(1, 6):
    result = update_engine_state(
        1,
        cycle,
        make_prediction(100, False)
    )

assert result["alert_level"] == "Healthy"
assert result["consecutive_anomalies"] == 0

# Three consecutive anomalies -> Warning.
for cycle in range(6, 9):
    result = update_engine_state(
        1,
        cycle,
        make_prediction(100, True)
    )

assert result["consecutive_anomalies"] == 3
assert result["persistence_level"] == "Warning"
assert result["alert_level"] == "Warning"

# Five consecutive anomalies -> Critical.
for cycle in range(9, 11):
    result = update_engine_state(
        1,
        cycle,
        make_prediction(100, True)
    )

assert result["consecutive_anomalies"] == 5
assert result["alert_level"] == "Critical"

# Normal reading resets anomaly persistence.
result = update_engine_state(
    1,
    11,
    make_prediction(100, False)
)

assert result["consecutive_anomalies"] == 0
assert result["alert_level"] == "Healthy"

# RUL risk must trigger even without an anomaly.
result = update_engine_state(
    2,
    1,
    make_prediction(45, False)
)

assert result["rul_zone"] == "Warning"
assert result["alert_level"] == "Warning"

result = update_engine_state(
    3,
    1,
    make_prediction(15, False)
)

assert result["rul_zone"] == "Critical"
assert result["alert_level"] == "Critical"

# A normal RUL with one anomaly should produce Watch.
result = update_engine_state(
    4,
    1,
    make_prediction(100, True)
)

assert result["persistence_level"] == "Watch"
assert result["alert_level"] == "Watch"

print("All dashboard state tests passed.")

print("\nEngine 1 recent alert activity:")
for event in st.session_state["recent_alert_activity"]:
    print(event["message"])
