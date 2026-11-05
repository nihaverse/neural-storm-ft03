import streamlit as st

from state import initialize_session_state
from sidebar import render_sidebar

st.set_page_config(
    page_title="NEURAL STORM | FT-03",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

initialize_session_state()

# Define pages
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

# Register pages BEFORE rendering custom sidebar
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

# Render custom sidebar
render_sidebar(
    overview_page,
    live_monitoring_page,
    alerts_page
)

# Run selected page
selected_page.run()