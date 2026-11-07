
import streamlit as st


def render_sidebar(overview_page, live_monitoring_page, alerts_page):
    """Render the shared NEURAL SENTRY sidebar."""

    if "sidebar_collapsed" not in st.session_state:
        st.session_state["sidebar_collapsed"] = False

    collapsed = st.session_state["sidebar_collapsed"]

    sidebar_width = "90px" if collapsed else "240px"
    toggle_alignment = "center" if collapsed else "flex-end"

    # Separate collapsed CSS to keep the main f-string clean
    collapsed_navigation_css = ""

    if collapsed:
        collapsed_navigation_css = """
        section[data-testid="stSidebar"] a {
            justify-content: center !important;
            min-height: 54px !important;
            padding: 12px 0 !important;
            margin: 8px 0 !important;
            border-radius: 9px !important;
            gap: 0 !important;
        }

        section[data-testid="stSidebar"] a [data-testid="stIconMaterial"] {
            font-size: 24px !important;
        }

        section[data-testid="stSidebar"] a[aria-current="page"] {
            border-left: none !important;
        }
        """

    # ================= SIDEBAR CSS =================

    st.markdown(
        f"""
        <style>

        /* Sidebar container */

        section[data-testid="stSidebar"] {{
            background-color: #0B1220 !important;
            border-right: 1px solid #1E293B !important;
            width: {sidebar_width} !important;
            min-width: {sidebar_width} !important;
            max-width: {sidebar_width} !important;
            flex-shrink: 0 !important;
            transform: none !important;
            visibility: visible !important;
            display: block !important;
        }}

        section[data-testid="stSidebar"] > div {{
            background-color: #0B1220 !important;
            visibility: visible !important;
            width: 100% !important;
        }}

        /* Remove reserved Streamlit sidebar header */

        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
            visibility: visible !important;
            padding-top: 0 !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {{
            padding-top: 0 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: #CBD5E1;
        }}


        /* Toggle button */

        section[data-testid="stSidebar"] [data-testid="stButton"] {{
            display: flex !important;
            justify-content: {toggle_alignment} !important;
            align-items: center !important;
            width: 100% !important;
            margin: 4px 0 8px 0 !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stButton"] button {{
            width: 38px !important;
            min-width: 38px !important;
            height: 38px !important;
            min-height: 38px !important;
            padding: 0 !important;
            border: none !important;
            border-radius: 8px !important;
            background: transparent !important;
            color: #CBD5E1 !important;
            box-shadow: none !important;
            transition: background 0.2s ease !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stButton"] button:hover {{
            background: #17243A !important;
            color: #FFFFFF !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stButton"] button
        [data-testid="stIconMaterial"] {{
            font-size: 24px !important;
        }}


        /* Brand */

        .ns-brand {{
            display: flex;
            align-items: center;
            gap: 9px;
            margin: 0 0 12px 0 !important;
        }}

        .ns-brand-name {{
            color: #F8FAFC;
            font-size: 18px;
            font-weight: 650;
            letter-spacing: 0.3px;
            white-space: nowrap;
        }}

        .ns-brand-tag {{
            color: #94A3B8;
            border: 1px solid #334155;
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 10px;
        }}


        /* Section labels */

        .ns-section-label {{
            color: #64748B;
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 1px;
            margin: 7px 0 5px 0 !important;
            text-transform: uppercase;
        }}


        /* Navigation */

        section[data-testid="stSidebar"] a {{
            display: flex !important;
            align-items: center !important;
            min-height: 36px !important;
            padding: 6px 12px !important;
            margin: 2px 0 !important;
            border-radius: 6px !important;
            color: #CBD5E1 !important;
            font-size: 13px !important;
            gap: 12px !important;
        }}

        section[data-testid="stSidebar"] a [data-testid="stIconMaterial"] {{
            font-size: 20px !important;
        }}

        section[data-testid="stSidebar"] a[aria-current="page"] {{
            background-color: #17243A !important;
            border-left: 3px solid #3B82F6 !important;
            color: #F8FAFC !important;
        }}

        section[data-testid="stSidebar"] a:hover {{
            background-color: #17243A !important;
        }}

        /* Collapsed navigation */

        {collapsed_navigation_css}


        /* Dividers */

        section[data-testid="stSidebar"] hr {{
            border-color: #263449 !important;
            margin: 10px 0 !important;
        }}


        /* Compact slider spacing */

        section[data-testid="stSidebar"] [data-testid="stSlider"] {{
            margin-bottom: -8px !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stSlider"] label {{
            font-size: 13px !important;
        }}


        /* System status */

        .ns-online {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: #CBD5E1;
            font-size: 12px;
            margin-top: 14px;
        }}

        .ns-online-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #10B981;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

    # ================= SIDEBAR CONTENT =================

    with st.sidebar:

        # Collapse / expand toggle

        toggle_icon = (
            ":material/keyboard_double_arrow_right:"
            if collapsed
            else ":material/keyboard_double_arrow_left:"
        )

        if st.button(
            " ",
            icon=toggle_icon,
            key="sidebar_toggle",
            use_container_width=False,
            type="tertiary"
        ):
            st.session_state["sidebar_collapsed"] = not collapsed
            st.rerun()

        # Brand

        if not collapsed:

            st.markdown(
                """
                <div class="ns-brand">
                    <div>
                        <div class="ns-brand-name">NEURAL SENTRY</div>
                        <div style="
                            color: #64748B;
                            font-size: 9px;
                            letter-spacing: 1px;
                            margin-top: 4px;
                        ">
                            PREDICTIVE MAINTENANCE
                        </div>
                    </div>
                    <span class="ns-brand-tag">FT-03</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="ns-section-label">Workspace</div>',
                unsafe_allow_html=True
            )

        # Navigation

        st.page_link(
            overview_page,
            label=" " if collapsed else "Overview",
            icon=":material/dashboard:"
        )

        st.page_link(
            live_monitoring_page,
            label=" " if collapsed else "Live Monitoring",
            icon=":material/monitor_heart:"
        )

        st.page_link(
            alerts_page,
            label=" " if collapsed else "Alerts",
            icon=":material/notifications:"
        )

        # Simulation settings

        if not collapsed:

            st.divider()

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

            st.markdown(
                """
                <div class="ns-online">
                    <span class="ns-online-dot"></span>
                    <span>System Online</span>
                </div>
                """,
                unsafe_allow_html=True
            )
