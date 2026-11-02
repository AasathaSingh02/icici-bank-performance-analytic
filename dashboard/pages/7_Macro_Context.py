"""
dashboard/pages/7_Macro_Context.py - Macroeconomic Alignment & Transmission
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
from dashboard.components.data_loader import load_macro_context
from dashboard.components.charts import apply_chart_theme

apply_custom_styles()
filters = render_sidebar_filters()

render_header(
    title="Macroeconomic Environment & Transmission",
    subtitle="RBI Monetary Policy Cycle, India GDP Growth & CPI Inflation Impact on Banking Dynamics"
)

df_macro = load_macro_context()

# 1. Dual-Axis: RBI Repo Rate vs ICICI Standalone NIM
st.markdown("#### 1. RBI Policy Rate Cycle vs ICICI Standalone NIM (%)")
fig_rate_nim = go.Figure()

fig_rate_nim.add_trace(go.Scatter(
    x=df_macro["period_label"],
    y=df_macro["rbi_repo_rate"],
    mode="lines+markers",
    name="RBI Repo Rate (%)",
    line={"color": "#dc2626", "width": 3, "dash": "dash"},
    hovertemplate="<b>RBI Repo Rate</b>: %{y:.2f}%<extra></extra>"
))
fig_rate_nim.add_trace(go.Scatter(
    x=df_macro["period_label"],
    y=df_macro["icici_nim_pct"],
    mode="lines+markers",
    name="ICICI Standalone NIM (%)",
    line={"color": "#e35205", "width": 3},
    hovertemplate="<b>ICICI NIM</b>: %{y:.2f}%<extra></extra>"
))

apply_chart_theme(fig_rate_nim, "RBI Policy Repo Rate vs ICICI Net Interest Margin (%)")
fig_rate_nim.update_layout(yaxis_title="Rate / Margin (%)")
st.plotly_chart(fig_rate_nim, use_container_width=True)

# 2. Dual-Axis: India GDP Growth & Inflation vs Credit Growth
st.markdown("#### 2. Macro Growth vs Commercial Bank Credit Expansion")
fig_gdp_credit = go.Figure()

fig_gdp_credit.add_trace(go.Bar(
    x=df_macro["period_label"],
    y=df_macro["icici_credit_growth_yoy"],
    name="ICICI Credit Growth YoY (%)",
    marker_color="#0f2942"
))
fig_gdp_credit.add_trace(go.Scatter(
    x=df_macro["period_label"],
    y=df_macro["gdp_growth_rate"],
    mode="lines+markers",
    name="India Real GDP Growth (%)",
    line={"color": "#10b981", "width": 2.5}
))
fig_gdp_credit.add_trace(go.Scatter(
    x=df_macro["period_label"],
    y=df_macro["cpi_inflation_rate"],
    mode="lines+markers",
    name="CPI Inflation (%)",
    line={"color": "#f59e0b", "width": 2, "dash": "dot"}
))

apply_chart_theme(fig_gdp_credit, "Credit Growth vs India GDP & CPI Inflation")
fig_gdp_credit.update_layout(yaxis_title="% YoY")
st.plotly_chart(fig_gdp_credit, use_container_width=True)

# Macro Context Table
st.markdown("#### Aligned Macro & Banking Data Matrix")
st.dataframe(df_macro, use_container_width=True, hide_index=True)

render_analyst_box(
    title="Macro Transmission Analyst Takeaways",
    takeaways=[
        "**Monetary Transmission Lag:** During the prolonged 6.50% repo rate pause (2023–2024), deposit repricing lagged loan floating-rate resets, causing NIM to compress moderately before stabilizing around 4.30%.",
        "**Credit Multiplier Effect:** ICICI's credit growth (13%–16% YoY) consistently expanded at approximately 2x India's real GDP growth (~7%), highlighting ongoing financial deepening and formal credit market share gains.",
        "**Methodological Caution:** Correlation does not imply direct causation. While monetary policy and GDP growth provide systemic tailwinds, individual bank NIM and credit metrics are heavily influenced by internal asset liability management (ALM) duration and credit risk appetite."
    ]
)

render_footer()

