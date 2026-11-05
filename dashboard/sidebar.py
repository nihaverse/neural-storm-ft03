
import streamlit as st


def render_sidebar(overview_page, live_monitoring_page, alerts_page):
    """Render the shared NEURAL STORM sidebar."""

    # Sidebar styling
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: #0B1220;
            border-right: 1px solid #1E293B;
        }

        [data-testid="stSidebar"] > div:first-child {
            background-color: #0B1220;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #CBD5E1;
        }

        .ns-brand {
            display: flex;
            align-items: center;
            gap: 9px;
            margin: 8px 0 32px 0;
        }

        .ns-brand-name {
            color: #F8FAFC;
            font-size: 18px;
            font-weight: 650;
            letter-spacing: 0.3px;
        }

        .ns-brand-tag {
            color: #94A3B8;
            border: 1px solid #334155;
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 10px;
            font-weight: 600;
        }

        .ns-section-label {
            color: #64748B;
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 1px;
            margin: 12px 0 8px 0;
            text-transform: uppercase;
        }

        [data-testid="stSidebar"] a {
            border-radius: 4px;
            color: #CBD5E1 !important;
            font-size: 13px;
        }

        [data-testid="stSidebar"] a[aria-current="page"] {
            background-color: #17243A;
            border-left: 3px solid #3B82F6;
            border-radius: 3px;
            color: #F8FAFC !important;
        }

        [data-testid="stSidebar"] a:hover {
            background-color: #17243A;
        }

        .ns-online {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #CBD5E1;
            font-size: 12px;
            margin-top: 24px;
        }

        .ns-online-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #10B981;
        }

        [data-testid="stSidebar"] hr {
            border-color: #263449;
            margin: 18px 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar:

        # Brand
        st.markdown(
            """
            <div class="ns-brand">
                <span class="ns-brand-name">NEURAL STORM</span>
                <span class="ns-brand-tag">FT-03</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Navigation
               
        st.markdown(
            '<div class="ns-section-label">Workspace</div>',
            unsafe_allow_html=True
        )

        st.page_link(
            overview_page,
            label="Overview",
            icon=":material/dashboard:"
        )

        st.page_link(
            live_monitoring_page,
            label="Live Monitoring",
            icon=":material/monitor_heart:"
        )

        st.page_link(
            alerts_page,
            label="Alerts",
            icon=":material/notifications:"
        )

        st.divider()

        # Simulation settings
        st.markdown(
            '<div class="ns-section-label">Simulation Settings</div>',
            unsafe_allow_html=True
        )

        st.slider(
            "Simulation Speed",
            min_value=0.5,
            max_value=3.0,
            step=0.5,
            format="%.1fx",
            key="simulation_speed"
        )

        warning_threshold = st.slider(
            "Warning after (consecutive cycles)",
            min_value=1,
            max_value=10,
            step=1,
            key="warning_threshold"
        )

        # Critical must always occur after Warning.
        if st.session_state["critical_threshold"] <= warning_threshold:
            st.session_state["critical_threshold"] = warning_threshold + 1

        st.slider(
            "Critical after (consecutive cycles)",
            min_value=warning_threshold + 1,
            max_value=15,
            step=1,
            key="critical_threshold"
        )

        st.divider()

        # System status
        st.markdown(
            """
            <div class="ns-online">
                <span class="ns-online-dot"></span>
                <span>System Online</span>
            </div>
            """,
            unsafe_allow_html=True
        )
