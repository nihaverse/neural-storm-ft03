import streamlit as st

from state import initialize_session_state


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
# SHARED SESSION STATE
# --------------------------------------------------

initialize_session_state()


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


# --------------------------------------------------
# RUN SELECTED PAGE
# --------------------------------------------------

selected_page = st.navigation(
    {
        "NEURAL STORM": [
            overview_page,
            live_monitoring_page,
            alerts_page
        ]
    },
    position="sidebar"
)

selected_page.run()