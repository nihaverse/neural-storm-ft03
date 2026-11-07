import streamlit as st
import pandas as pd
import html
import altair as alt

from simulation_controller import run_live_page
from src.ui_style import inject_global_styles, render_html


# --------------------------------------------------
# DATA PROCESSING
# --------------------------------------------------

def get_fleet_data():

    engine_states = st.session_state.get("engine_states", {})

    if not isinstance(engine_states, dict):
        raise TypeError(
            "engine_states must be a dictionary keyed by engine ID."
        )

    engines = []

    for engine_id, state in engine_states.items():

        if not isinstance(state, dict):
            continue

        if "final_rul" not in state:
            continue

        final_rul = float(state["final_rul"])

        health_index = max(
            0.0,
            min((final_rul / 125) * 100, 100.0)
        )

        raw_status = str(
            state.get("alert_level", "Healthy")
        ).strip().lower()

        if raw_status == "critical":
            status = "Critical"
        elif raw_status == "warning":
            status = "Warning"
        else:
            status = "Healthy"

        current_cycle = int(
            state.get(
                "current_cycle",
                state.get("cycle", 0)
            )
        )

        last_alert_cycle = state.get("last_alert_cycle")

        if status == "Healthy" or last_alert_cycle is None:
            last_alert = "-"
        else:
            cycles_ago = max(
                0,
                current_cycle - int(last_alert_cycle)
            )
            last_alert = f"{cycles_ago} cycles ago"

        engines.append({
            "engine_id": engine_id,
            "current_cycle": current_cycle,
            "final_rul": max(0.0, min(final_rul, 125.0)),
            "health_index": health_index,
            "status": status,
            "last_alert": last_alert
        })

    return engines


def calculate_fleet_metrics(engines):

    total = len(engines)

    counts = {
        "Healthy": 0,
        "Warning": 0,
        "Critical": 0
    }

    for engine in engines:
        counts[engine["status"]] += 1

    if sum(counts.values()) != total:
        raise ValueError(
            "Fleet status counts do not match total engine count."
        )

    if total == 0:
        fleet_health = 0.0
        average_rul = 0.0
    else:
        fleet_health = sum(
            engine["health_index"] for engine in engines
        ) / total

        average_rul = sum(
            engine["final_rul"] for engine in engines
        ) / total

    return {
        "total": total,
        "counts": counts,
        "fleet_health": fleet_health,
        "average_rul": average_rul
    }


# --------------------------------------------------
# HTML HELPERS
# --------------------------------------------------

def status_pill(status):

    status_class = {
        "Healthy": "healthy",
        "Warning": "warning",
        "Critical": "critical"
    }[status]

    return (
        f'<span class="ns-status-pill ns-pill-{status_class}">'
        f'<span class="ns-dot ns-dot-{status_class}"></span>'
        f'{status}'
        f'</span>'
    )


def render_kpi(label, value, caption, status=None):

    dot = ""

    if status:
        dot = (
            f'<span class="ns-dot ns-dot-{status.lower()}"></span>'
        )

    value_style = ""

    if status == "Warning":
        value_style = "color: #D97706;"
    elif status == "Critical":
        value_style = "color: #DC2626;"

    return (
        '<div class="ns-kpi-card">'
        f'<div class="ns-kpi-label">{dot}{label}</div>'
        f'<div class="ns-kpi-value" style="{value_style}">{value}</div>'
        f'<div class="ns-kpi-caption">{caption}</div>'
        '</div>'
    )


# --------------------------------------------------
# OVERVIEW RENDERING
# --------------------------------------------------

def render_overview():

    inject_global_styles()

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    if st.session_state["fleet_manager"].is_finished:
        simulation_label = "Completed"
    elif st.session_state.get("simulation_running", False):
        simulation_label = "Running"
    else:
        simulation_label = "Paused"

    simulation_dot = (
        "healthy" if simulation_label == "Running" else "neutral"
    )

    render_html(
        f"""
        <div class="ns-header">
        <div>
        <div class="ns-page-title">Fleet Overview</div>
        <div class="ns-page-subtitle">Real-time health of all monitored engines</div>
        </div>
        <div class="ns-simulation-pill">
        <span class="ns-dot ns-dot-{simulation_dot}"></span>
        Simulation: {simulation_label}
        </div>
        </div>
        """
    )

    # --------------------------------------------------
    # GET ACTUAL FLEET DATA
    # --------------------------------------------------

    engines = get_fleet_data()
    metrics = calculate_fleet_metrics(engines)

    total = metrics["total"]
    counts = metrics["counts"]

    # --------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------

    kpi_columns = st.columns(4, gap="medium")

    kpi_data = [
        ("TOTAL ENGINES", total, "Monitored in simulation", None),
        ("HEALTHY", counts["Healthy"], f"of {total} engines", "Healthy"),
        ("WARNING", counts["Warning"], f"of {total} engines", "Warning"),
        ("CRITICAL", counts["Critical"], f"of {total} engines", "Critical")
    ]

    for column, data in zip(kpi_columns, kpi_data):
        with column:
            render_html(render_kpi(*data))

    render_html('<div style="height:22px;"></div>')

    # --------------------------------------------------
    # FLEET HEALTH SCORE + STATUS DISTRIBUTION
    # --------------------------------------------------

    health_column, distribution_column = st.columns(
        [0.45, 0.55],
        gap="medium"
    )

    with health_column:

        fleet_health = metrics["fleet_health"]
        average_rul = metrics["average_rul"]

        render_html(
            f"""
            <div class="ns-card">
            <div class="ns-section-title">Fleet Health Score</div>
            <div>
            <span class="ns-health-number">{fleet_health:.0f}</span>
            <span class="ns-health-total">/ 100</span>
            </div>
            <div class="ns-progress-track">
            <div class="ns-progress-fill" style="width:{fleet_health:.2f}%"></div>
            </div>
            <div class="ns-caption" style="margin-top:13px;">Health Index (RUL-based)</div>
            <div class="ns-caption" style="margin-top:5px;">Average predicted RUL: {average_rul:.1f} cycles</div>
            </div>
            """
        )

    with distribution_column:

        if total > 0:
            healthy_width = counts["Healthy"] / total * 100
            warning_width = counts["Warning"] / total * 100
            critical_width = counts["Critical"] / total * 100
        else:
            healthy_width = warning_width = critical_width = 0

        render_html(
            f"""
            <div class="ns-card">
            <div class="ns-section-title">Status Distribution</div>
            <div class="ns-stacked-bar">
            <div class="ns-bar-healthy" style="width:{healthy_width}%"></div>
            <div class="ns-bar-warning" style="width:{warning_width}%"></div>
            <div class="ns-bar-critical" style="width:{critical_width}%"></div>
            </div>
            <div class="ns-legend">
            <div class="ns-legend-item"><span class="ns-dot ns-dot-healthy"></span>Healthy ({counts["Healthy"]})</div>
            <div class="ns-legend-item"><span class="ns-dot ns-dot-warning"></span>Warning ({counts["Warning"]})</div>
            <div class="ns-legend-item"><span class="ns-dot ns-dot-critical"></span>Critical ({counts["Critical"]})</div>
            </div>
            </div>
            """
        )

    render_html('<div style="height:22px;"></div>')

    # --------------------------------------------------
    # MAINTENANCE PRIORITY LIST
    # --------------------------------------------------

    priority_order = {
        "Critical": 0,
        "Warning": 1,
        "Healthy": 2
    }

    priority_engines = sorted(
        engines,
        key=lambda engine: (
            priority_order[engine["status"]],
            engine["final_rul"]
        )
    )[:6]

    table_rows = ""

    for engine in priority_engines:

        engine_id = html.escape(str(engine["engine_id"]))
        health = engine["health_index"]
        rul = engine["final_rul"]
        last_alert = html.escape(engine["last_alert"])

        table_rows += (
            '<tr>'
            f'<td class="ns-engine-id">Engine {engine_id}</td>'
            f'<td class="ns-health-cell">{health:.1f}</td>'
            f'<td class="ns-rul-cell">{rul:.1f}</td>'
            f'<td>{status_pill(engine["status"])}</td>'
            f'<td>{last_alert}</td>'
            '</tr>'
        )

    if priority_engines:

        priority_content = f"""
        <div class="ns-table-wrapper">
        <table class="ns-table">
        <thead>
        <tr>
        <th>Engine ID</th>
        <th>Health Score</th>
        <th>Predicted RUL (cycles)</th>
        <th>Status</th>
        <th>Last Alert</th>
        </tr>
        </thead>
        <tbody>
        {table_rows}
        </tbody>
        </table>
        </div>
        """

    else:

        priority_content = """
        <div class="ns-empty-state">
        No engine readings available yet. Start the simulation to populate fleet data.
        </div>
        """

    render_html(
        f"""
        <div class="ns-card">
        <div class="ns-section-title">Maintenance Priority List</div>
        {priority_content}
        </div>
        """
    )

    render_html('<div style="height:22px;"></div>')

    # --------------------------------------------------
    # PREDICTED RUL DISTRIBUTION
    # --------------------------------------------------

    render_html(
        """
        <div class="ns-section-title">Predicted RUL Distribution</div>
        """
    )

    labels = [
        "0-20",
        "21-40",
        "41-60",
        "61-80",
        "81-100",
        "101-125"
    ]

    # Refresh histogram only when requested by controller.
    if st.session_state.get("refresh_histogram", True):

        if engines:

            rul_values = [
                engine["final_rul"] for engine in engines
            ]

            categories = pd.cut(
                rul_values,
                bins=[0, 20, 40, 60, 80, 100, 125],
                labels=labels,
                right=True,
                include_lowest=True
            )

            histogram = (
                pd.Series(categories)
                .value_counts(sort=False)
                .reindex(labels, fill_value=0)
                .rename_axis("RUL Range")
                .reset_index(name="Engines")
            )

        else:

            histogram = pd.DataFrame({
                "RUL Range": labels,
                "Engines": [0, 0, 0, 0, 0, 0]
            })

        st.session_state["cached_rul_histogram"] = histogram

    histogram = st.session_state.get(
        "cached_rul_histogram"
    )

    if histogram is None:
        histogram = pd.DataFrame({
            "RUL Range": labels,
            "Engines": [0, 0, 0, 0, 0, 0]
        })

    chart = (
        alt.Chart(histogram)
        .mark_bar(
            color="#475569",
            cornerRadiusTopLeft=3,
            cornerRadiusTopRight=3
        )
        .encode(
            x=alt.X(
                "RUL Range:N",
                sort=labels,
                axis=alt.Axis(
                    title="Predicted RUL (cycles)",
                    labelAngle=0,
                    labelColor="#475569",
                    titleColor="#475569",
                    labelFontSize=11,
                    titleFontSize=12,
                    ticks=False,
                    domain=False
                )
            ),
            y=alt.Y(
                "Engines:Q",
                axis=alt.Axis(
                    title="Engines",
                    format="d",
                    tickMinStep=1,
                    labelColor="#475569",
                    titleColor="#475569",
                    labelFontSize=11,
                    titleFontSize=12,
                    grid=True,
                    gridColor="#E2E8F0",
                    domain=False
                ),
                scale=alt.Scale(domainMin=0)
            ),
            tooltip=[
                alt.Tooltip("RUL Range:N", title="RUL Range"),
                alt.Tooltip(
                    "Engines:Q",
                    title="Number of Engines",
                    format="d"
                )
            ]
        )
        .properties(
            height=240,
            background="#FFFFFF"
        )
        .configure_view(
            strokeWidth=0,
            fill="#FFFFFF"
        )
        .configure_axis(
            labelFont="Inter",
            titleFont="Inter",
            labelPadding=8,
            titlePadding=10
        )
    )

    with st.container(border=True):
        st.altair_chart(
            chart,
            use_container_width=True,
            theme=None
        )


# --------------------------------------------------
# SHARED LIVE SIMULATION RENDERING
# --------------------------------------------------

run_live_page(
    render_page=render_overview,
    total_cycles=st.session_state["total_simulation_cycles"]
)
