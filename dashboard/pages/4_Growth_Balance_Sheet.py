"""
dashboard/pages/4_Growth_Balance_Sheet.py - Balance Sheet Expansion & Liquidity
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dashboard.components.ui_styles import (
    apply_custom_styles,
    render_header,
    render_analyst_box,
    render_footer
)
from dashboard.components.filters import render_sidebar_filters
from dashboard.components.data_loader import (
    load_kpi_wide,
    load_kpi_growth,
    load_cd_ratio
)
from dashboard.components.charts import (
    create_trend_line_chart,
    create_growth_bar_chart,
    apply_chart_theme
)

apply_custom_styles()
filters = render_sidebar_filters()

render_header(
    title="Growth & Balance Sheet Dynamics",
    subtitle="Advances Expansion, Deposit Mobilization, CASA Franchise & Credit-Deposit (CD) Ratio"
)

df_kpi = load_kpi_wide()
df_growth = load_kpi_growth()
df_cd = load_cd_ratio()

icici_p = df_kpi[df_kpi["bank"] == "ICICI"]
icici_g = df_growth[df_growth["bank"] == "ICICI"]
icici_cd = df_cd[df_cd["bank"] == "ICICI"]

# 1. Total Advances & Deposits (₹ Lakh Crore)
st.markdown("#### 1. Balance Sheet Scale (Advances vs Deposits)")
fig_scale = go.Figure()
fig_scale.add_trace(go.Scatter(
    x=icici_p["period_label"],
    y=icici_p["advances_cr"] / 100000,
    mode="lines+markers",
    name="Total Advances (Lakh Cr)",
    line={"width": 3, "color": "#e35205"},
    hovertemplate="<b>Advances</b>: ₹%{y:.2f} Lakh Cr<extra></extra>"
))
fig_scale.add_trace(go.Scatter(
    x=icici_p["period_label"],
    y=icici_p["deposits_cr"] / 100000,
    mode="lines+markers",
    name="Total Deposits (Lakh Cr)",
    line={"width": 3, "color": "#0f2942"},
    hovertemplate="<b>Deposits</b>: ₹%{y:.2f} Lakh Cr<extra></extra>"
))
apply_chart_theme(fig_scale, "ICICI Bank Advances & Deposits Scale (₹ Lakh Crore)")
fig_scale.update_layout(yaxis_title="₹ Lakh Crore")
st.plotly_chart(fig_scale, use_container_width=True)

# 2. Credit-Deposit Ratio & CASA %
st.markdown("#### 2. Liquidity & Funding Mix (CASA % & CD Ratio %)")
col1, col2 = st.columns(2)

with col1:
    fig_cd = go.Figure()
    fig_cd.add_trace(go.Scatter(
        x=icici_cd["period_label"],
        y=icici_cd["cd_ratio_pct"],
        mode="lines+markers",
        name="Credit-to-Deposit Ratio (%)",
        line={"width": 2.5, "color": "#0f2942"},
        hovertemplate="<b>CD Ratio</b>: %{y:.2f}%<extra></extra>"
    ))
    # Optimal band between 82% and 87%
    fig_cd.add_hrect(y0=82, y1=87, fillcolor="rgba(16, 185, 129, 0.1)", line_width=0, annotation_text="Optimal CD Band (82-87%)")
    apply_chart_theme(fig_cd, "Credit-to-Deposit Ratio Evolution (%)")
    fig_cd.update_layout(yaxis_title="CD Ratio (%)")
    st.plotly_chart(fig_cd, use_container_width=True)

with col2:
    fig_casa = create_trend_line_chart(
        icici_p,
        x_col="period_label",
        y_cols=["casa_ratio_pct"],
        labels=["CASA Ratio (%)"],
        title="Current & Savings Account (CASA) Ratio (%)",
        y_title="CASA (%)",
        is_pct=True
    )
    st.plotly_chart(fig_casa, use_container_width=True)

# 3. YoY Growth Comparison
st.markdown("#### 3. Advances vs Deposits YoY Growth Trajectory (%)")
fig_growth_bars = create_growth_bar_chart(
    icici_g,
    x_col="period_label",
    y_cols=["advances_yoy_pct", "deposits_yoy_pct"],
    labels=["Advances YoY Growth (%)", "Deposits YoY Growth (%)"],
    title="Year-on-Year Growth Momentum Comparison"
)
st.plotly_chart(fig_growth_bars, use_container_width=True)

# Balance Sheet Data Table
st.markdown("#### Balance Sheet & Funding Series")
bs_table = icici_p[["period_label", "advances_cr", "deposits_cr", "casa_ratio_pct", "crar_pct"]]
bs_merged = bs_table.merge(icici_cd[["period_label", "cd_ratio_pct"]], on="period_label")
st.dataframe(bs_merged, use_container_width=True, hide_index=True)

render_analyst_box(
    title="Growth & Balance Sheet Analyst Takeaways",
    takeaways=[
        "**Credit Expansion Pace:** Advances expanded from ₹10.57 lakh crore in Q1 FY24 to over ₹16.54 lakh crore in Q2 FY27, sustaining a 13%–16% YoY growth pace driven by retail mortgages, SME lending, and high-rated corporates.",
        "**Deposit Discipline:** Total deposits reached ₹19.12 lakh crore, maintaining a balanced Credit-Deposit ratio within the healthy 85%–87% threshold without excessive reliance on wholesale certificates of deposit.",
        "**CASA Resilience:** The CASA ratio settled around 40.5%–41.4%, effectively absorbing systemic shifts toward higher-yielding term deposits while defending low-cost funding advantages."
    ]
)

render_footer()

