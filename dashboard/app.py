
import sys
from pathlib import Path

import streamlit as st

# --------------------------------------------------
# PROJECT IMPORTS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from state import initialize_session_state, update_engine_state
from sidebar import render_sidebar

from src.simulation import (
    load_simulation_data,
    FleetSimulationManager,
)
from src.inference import load_models


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="NEURAL STORM | FT-03",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# SHARED RESOURCES
# --------------------------------------------------

@st.cache_resource
def load_shared_resources():
    """Load dataset and trained models once per server."""

    df = load_simulation_data()
    models = load_models()

    return df, models


initialize_session_state()

df, models = load_shared_resources()

st.session_state["total_simulation_cycles"] = len(df)

# --------------------------------------------------
# FLEET MANAGER INITIALIZATION
# --------------------------------------------------

if "fleet_manager" not in st.session_state:
    st.session_state["fleet_manager"] = FleetSimulationManager(
        df=df,
        models=models
    )


# --------------------------------------------------
# ENGINE STATE INITIALIZATION
# --------------------------------------------------

def initialize_fleet_states():
    """Initialize all engines from their first available cycle."""

    # Clear previous engine and alert state.
    st.session_state["engine_states"] = {}
    st.session_state["engine_history"] = {}
    st.session_state["streaming_feature_engineers"] = {}
    st.session_state["recent_alert_activity"] = []
    st.session_state["simulation_positions"] = {}
    st.session_state["last_chart_update_cycle"] = {}

    fleet_manager = st.session_state["fleet_manager"]

    # Process the first reading of every engine.
    first_cycle_results = fleet_manager.process_next_cycle()

    for engine_id, result in first_cycle_results.items():
        update_engine_state(
            engine_id=engine_id,
            cycle=result["cycle"],
            prediction=result["prediction"]
        )

    st.session_state["fleet_initialized"] = True


if not st.session_state.get("fleet_initialized", False):
    initialize_fleet_states()


# --------------------------------------------------
# SIMULATION ADVANCEMENT
# --------------------------------------------------

def advance_fleet_one_tick():
    """
    Advance every unfinished engine by one reading.

    Prediction and alert calculations remain centralized
    inside update_engine_state().
    """

    fleet_manager = st.session_state["fleet_manager"]

    if fleet_manager.is_finished:
        st.session_state["simulation_running"] = False
        return

    cycle_results = fleet_manager.process_next_cycle()

    for engine_id, result in cycle_results.items():
        update_engine_state(
            engine_id=engine_id,
            cycle=result["cycle"],
            prediction=result["prediction"]
        )

    if fleet_manager.is_finished:
        st.session_state["simulation_running"] = False


# --------------------------------------------------
# PAGE NAVIGATION
# --------------------------------------------------

overview_page = st.Page(
    "pages/overview.py",
    title="Overview",
    default=True
)

live_monitoring_page = st.Page(
    "pages/live_monitoring.py",
    title="Live Monitoring"
)

alerts_page = st.Page(
    "pages/alerts.py",
    title="Alerts"
)

selected_page = st.navigation(
    {
        "NEURAL STORM": [
            overview_page,
            live_monitoring_page,
            alerts_page
        ]
    },
    position="hidden"
)


# --------------------------------------------------
# CUSTOM SIDEBAR
# --------------------------------------------------

render_sidebar(
    overview_page,
    live_monitoring_page,
    alerts_page
)


# --------------------------------------------------
# SIMULATION CONTROLS
# --------------------------------------------------

simulation_running = st.session_state["simulation_running"]
fleet_finished = st.session_state["fleet_manager"].is_finished

control_col1, control_col2, control_col3 = st.columns([1, 1, 1])

with control_col1:
    if st.button(
        "Start",
        disabled=simulation_running or fleet_finished,
        use_container_width=True
    ):
        st.session_state["simulation_running"] = True
        st.session_state["simulation_status"] = "Running"
        st.rerun()

with control_col2:
    if st.button(
        "Pause",
        disabled=not simulation_running,
        use_container_width=True
    ):
        st.session_state["simulation_running"] = False
        st.session_state["simulation_status"] = "Paused"
        st.rerun()

with control_col3:
    if st.button("Reset", use_container_width=True):
        st.session_state["simulation_running"] = False
        st.session_state["simulation_status"] = "Paused"
        st.session_state["simulation_tick_count"] = 0
        st.session_state.pop("cached_rul_histogram", None)

        st.session_state["fleet_manager"] = FleetSimulationManager(
            df=df,
            models=models
        )

        initialize_fleet_states()
        st.rerun()

# --------------------------------------------------
# RUN SELECTED PAGE
# --------------------------------------------------

selected_page.run()
