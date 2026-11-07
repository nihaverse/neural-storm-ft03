
import textwrap
import streamlit as st


def inject_global_styles():
    """Inject shared Neural Storm styles on every page render."""

    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --ns-bg: #F8FAFC;
    --ns-card: #FFFFFF;
    --ns-border: #E2E8F0;
    --ns-text: #0F172A;
    --ns-secondary: #475569;
    --ns-muted: #94A3B8;
    --ns-healthy: #10B981;
    --ns-warning: #D97706;
    --ns-critical: #DC2626;
    --ns-blue: #64748B;
}

/* Main application */
html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main {
    background-color: var(--ns-bg) !important;
    color: var(--ns-text) !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stMain"],
[data-testid="stMain"] p,
[data-testid="stMain"] span,
[data-testid="stMain"] label,
[data-testid="stMain"] div {
    color: var(--ns-text);
}

[data-testid="stHeader"] {
    background: var(--ns-bg) !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 1600px !important;
}

/* Hide Streamlit chrome */
#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stDeployButton"],
[data-testid="stStatusWidget"],
[data-testid="stAppDeployButton"] {
    visibility: hidden !important;
    display: none !important;
}

/* Sidebar: retain dark navy design */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background-color: #0B1220 !important;
}

section[data-testid="stSidebar"] * {
    color: #F8FAFC;
}

/* Page header */
.ns-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
    width: 100%;
}

.ns-page-title {
    font-size: 24px;
    font-weight: 600;
    line-height: 1.35;
    color: #0F172A !important;
    margin: 0;
}

.ns-page-subtitle {
    font-size: 13px;
    color: #475569 !important;
    margin-top: 5px;
}

.ns-simulation-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 7px 12px;
    font-size: 12px;
    font-weight: 500;
    color: #475569 !important;
    white-space: nowrap;
    background: #FFFFFF;
}

.ns-simulation-pill span {
    color: #475569 !important;
}

/* Cards */
.ns-card,
.ns-kpi-card {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 6px !important;
    box-sizing: border-box;
}

.ns-card {
    padding: 18px;
    height: 100%;
}

.ns-kpi-card {
    padding: 17px 18px;
    min-height: 112px;
}

/* KPI content */
.ns-kpi-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: .6px;
    color: #475569 !important;
}

.ns-kpi-value {
    font-size: 28px;
    font-weight: 600;
    line-height: 1.3;
    margin-top: 9px;
    color: #0F172A !important;
    font-variant-numeric: tabular-nums;
}

.ns-kpi-caption {
    font-size: 11px;
    color: #94A3B8 !important;
    margin-top: 3px;
}

/* Status dots */
.ns-dot {
    width: 7px;
    height: 7px;
    min-width: 7px;
    border-radius: 50%;
    display: inline-block;
}

.ns-dot-healthy {
    background: #10B981;
}

.ns-dot-warning {
    background: #D97706;
}

.ns-dot-critical {
    background: #DC2626;
}

.ns-dot-neutral {
    background: #94A3B8;
}

/* Health progress bar */
.ns-progress-track {
    height: 8px;
    width: 100%;
    background: #E2E8F0;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 16px;
}

.ns-progress-fill {
    height: 100%;
    background: #64748B;
    border-radius: 10px;
}

/* Status distribution */
.ns-stacked-bar {
    display: flex;
    height: 24px;
    width: 100%;
    overflow: hidden;
    border-radius: 4px;
    background: #F1F5F9;
    margin-top: 24px;
}

.ns-bar-healthy {
    background: #10B981;
}

.ns-bar-warning {
    background: #D97706;
}

.ns-bar-critical {
    background: #DC2626;
}

.ns-legend {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 18px;
    margin-top: 19px;
}

.ns-legend-item {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 12px;
    color: #475569 !important;
}

/* Sections and labels */
.ns-section-title {
    font-size: 14px;
    font-weight: 600;
    color: #0F172A !important;
    margin: 0 0 16px 0;
}

.ns-label {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: .7px;
    text-transform: uppercase;
    color: #475569 !important;
}

.ns-caption {
    font-size: 11px;
    color: #94A3B8 !important;
}

/* Status pills */
.ns-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 500;
    white-space: nowrap;
}

.ns-pill-healthy {
    background: #ECFDF5;
    color: #047857 !important;
}

.ns-pill-warning {
    background: #FFFBEB;
    color: #B45309 !important;
}

.ns-pill-critical {
    background: #FEF2F2;
    color: #B91C1C !important;
}

/* Table */
.ns-table-wrapper {
    width: 100%;
    overflow-x: auto;
}

.ns-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    text-align: left;
}

.ns-table th {
    background: #F8FAFC;
    color: #475569 !important;
    font-size: 11px;
    font-weight: 600;
    padding: 11px 12px;
    border-bottom: 1px solid #E2E8F0;
    white-space: nowrap;
}

.ns-table td {
    padding: 12px;
    border-bottom: 1px solid #F1F5F9;
    color: #475569 !important;
    white-space: nowrap;
}

.ns-table tr:last-child td {
    border-bottom: none;
}

.ns-engine-id,
.ns-health-cell {
    font-weight: 600;
    color: #0F172A !important;
}

.ns-rul-cell {
    font-variant-numeric: tabular-nums;
}

/* Empty state */
.ns-empty-state {
    padding: 28px 16px;
    text-align: center;
    color: #94A3B8 !important;
    font-size: 13px;
}

/* Streamlit containers and charts */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #E2E8F0;
    border-radius: 6px;
}

[data-testid="stChart"] {
    background: #FFFFFF !important;
}

/* Hide Streamlit chart hover toolbar */
[data-testid="stElementToolbar"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
}

/* Prevent Streamlit stale-element dimming */
[data-stale="true"] {
    opacity: 1 !important;
}

/* Disable fading and animations during fragment updates */
.stApp [data-testid="stAppViewContainer"] * {
    transition: none !important;
    animation: none !important;
}

/* Hide Streamlit's default top header and toolbar */

[data-testid="stToolbar"] {
    display: none !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}
header[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    display: none !important;
}

</style>
        """,
        unsafe_allow_html=True,
    )


def render_html(markup):
    """Render HTML without Markdown code-block indentation."""

    cleaned_markup = textwrap.dedent(markup).strip()

    st.markdown(
        cleaned_markup,
        unsafe_allow_html=True,
    )
