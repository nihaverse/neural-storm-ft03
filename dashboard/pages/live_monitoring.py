
import streamlit as st

from simulation_controller import run_live_page


def render_live_monitoring():

    st.title("Live Monitoring")
    st.write("Live Monitoring page is connected.")


run_live_page(
    render_page=render_live_monitoring,
    total_cycles=st.session_state["total_simulation_cycles"]
)
