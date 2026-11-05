
import streamlit as st


# RUL-based maintenance risk thresholds.
RUL_WARNING_THRESHOLD = 50
RUL_CRITICAL_THRESHOLD = 20

ALERT_SEVERITY = {
    "Healthy": 0,
    "Watch": 1,
    "Warning": 2,
    "Critical": 3,
}


def initialize_session_state():
    """Initialize shared dashboard state."""

    defaults = {
        "engine_states": {},
        "engine_history": {},
        "streaming_feature_engineers": {},
        "recent_alert_activity": [],
        "simulation_running": False,
        "simulation_speed": 1.0,
        "warning_threshold": 3,
        "critical_threshold": 5,
        "selected_engine": None,
        "last_chart_update_cycle": {},
        "simulation_positions": {},
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def get_rul_zone(final_rul):
    """Classify maintenance risk using Final RUL."""

    if final_rul <= RUL_CRITICAL_THRESHOLD:
        return "Critical"

    if final_rul <= RUL_WARNING_THRESHOLD:
        return "Warning"

    return "Healthy"


def get_persistence_level(consecutive_anomalies):
    """Classify alert severity using anomaly persistence."""

    warning_threshold = int(st.session_state["warning_threshold"])
    critical_threshold = int(st.session_state["critical_threshold"])

    if warning_threshold < 1:
        raise ValueError("Warning threshold must be at least 1.")

    if critical_threshold <= warning_threshold:
        raise ValueError(
            "Critical threshold must be greater than Warning threshold."
        )

    if consecutive_anomalies >= critical_threshold:
        return "Critical"

    if consecutive_anomalies >= warning_threshold:
        return "Warning"

    if consecutive_anomalies >= 1:
        return "Watch"

    return "Healthy"


def get_combined_alert_level(rul_zone, persistence_level):
    """Return the more severe of the two independent alert signals."""

    return max(
        [rul_zone, persistence_level],
        key=lambda level: ALERT_SEVERITY[level]
    )


def update_engine_state(engine_id, cycle, prediction):
    """
    Update one engine's shared state using a completed inference result.

    Final RUL is received from inference.py.
    It is not recalculated or adjusted here.
    """

    engine_id = int(engine_id)
    cycle = int(cycle)

    required_fields = [
        "raw_rul",
        "safety_margin",
        "final_rul",
        "health_index",
        "is_anomaly",
        "anomaly_score",
    ]

    missing_fields = [
        field for field in required_fields
        if field not in prediction
    ]

    if missing_fields:
        raise ValueError(
            f"Missing prediction fields: {missing_fields}"
        )

    final_rul = float(prediction["final_rul"])
    health_index = float(prediction["health_index"])
    is_anomaly = bool(prediction["is_anomaly"])

    if not 0 <= final_rul <= 125:
        raise ValueError("Final RUL must be between 0 and 125.")

    if not 0 <= health_index <= 100:
        raise ValueError("Health Index must be between 0 and 100.")

    engine_states = st.session_state["engine_states"]
    previous_state = engine_states.get(engine_id)

        # Prevent duplicate or out-of-order cycle updates.
    if previous_state is not None:
        previous_cycle = previous_state["current_cycle"]

        if cycle == previous_cycle:
            # Idempotent: do not count the same anomaly twice.
            return previous_state

        if cycle < previous_cycle:
            raise ValueError(
                f"Out-of-order update for Engine {engine_id}: "
                f"received cycle {cycle}, "
                f"but current cycle is {previous_cycle}."
            )
        
    # Maintain consecutive anomaly count.
    previous_count = (
        previous_state["consecutive_anomalies"]
        if previous_state is not None
        else 0
    )

    consecutive_anomalies = (
        previous_count + 1 if is_anomaly else 0
    )

    # Determine independent risk signals.
    rul_zone = get_rul_zone(final_rul)

    persistence_level = get_persistence_level(
        consecutive_anomalies
    )

    # Combine both signals using the more severe level.
    alert_level = get_combined_alert_level(
        rul_zone,
        persistence_level
    )

    previous_level = (
        previous_state["alert_level"]
        if previous_state is not None
        else "Healthy"
    )

    # Preserve the cycle of the latest non-Healthy alert transition.
    last_alert_cycle = (
        previous_state["last_alert_cycle"]
        if previous_state is not None
        else None
    )

    if alert_level != previous_level:
        if alert_level != "Healthy":
            last_alert_cycle = cycle

        # Record every actual alert-level transition, including recovery.
        if previous_state is not None or alert_level != "Healthy":
            st.session_state["recent_alert_activity"].append({
                "engine_id": engine_id,
                "cycle": cycle,
                "previous_level": previous_level,
                "new_level": alert_level,
                "message": (
                    f"Engine {engine_id} changed from "
                    f"{previous_level} to {alert_level} "
                    f"(cycle {cycle})"
                ),
            })

    # Store one authoritative state for this engine.
    engine_state = {
        "engine_id": engine_id,
        "current_cycle": cycle,
        "raw_rul": float(prediction["raw_rul"]),
        "safety_margin": float(prediction["safety_margin"]),
        "final_rul": final_rul,
        "health_index": health_index,
        "anomaly": is_anomaly,
        "anomaly_score": float(prediction["anomaly_score"]),
        "consecutive_anomalies": consecutive_anomalies,
        "rul_zone": rul_zone,
        "persistence_level": persistence_level,
        "alert_level": alert_level,
        "last_alert_cycle": last_alert_cycle,
    }

    engine_states[engine_id] = engine_state

    return engine_state
