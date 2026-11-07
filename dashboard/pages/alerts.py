
import streamlit as st

from simulation_controller import run_live_page


def render_alerts():

    st.title("Alerts")
    st.write("Alerts page is connected.")


run_live_page(
    render_page=render_alerts,
    total_cycles=st.session_state["total_simulation_cycles"]
)
