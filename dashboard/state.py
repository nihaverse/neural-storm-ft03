import streamlit as st


def initialize_session_state():
    """
    Initialize shared dashboard state.

    Actual engine data and predictions will be populated
    later by the simulation and inference pipeline.
    """

    defaults = {
        # Per-engine source of truth
        "engine_states": {},

        # Latest 10 sensor readings for each engine
        "engine_history": {},

        # Independent streaming feature engineer for each engine
        "streaming_feature_engineers": {},

        # Alert escalation and recovery events
        "recent_alert_activity": [],

        # Simulation controls
        "simulation_running": False,
        "simulation_speed": 1.0,

        # Alert persistence thresholds
        "warning_threshold": 3,
        "critical_threshold": 5,

        # Selected engine in Live Monitoring
        "selected_engine": None,

        # Track when heavy charts were last refreshed
        "last_chart_update_cycle": {},

        # Track simulation progress independently per engine
        "simulation_positions": {},
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value