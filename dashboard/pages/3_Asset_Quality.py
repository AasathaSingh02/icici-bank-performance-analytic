"""
dashboard/pages/3_Asset_Quality.py - Credit Risk & Balance Sheet Resilience
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
    load_profit_bridge
)
from dashboard.components.charts import (
    create_trend_line_chart,
    apply_chart_theme
)

apply_custom_styles()
filters = render_sidebar_filters()

render_header(
    title="Asset Quality & Credit Risk",
    subtitle="Non-Performing Asset (NPA) Trends, Provision Coverage (PCR) & Peer Credit Cost Comparison"
)

df_kpi = load_kpi_wide()
df_bridge = load_profit_bridge()
icici_p = df_kpi[df_kpi["bank"] == "ICICI"]

# 1. NPA Trajectory
st.markdown("#### 1. Non-Performing Assets (Gross & Net NPA %)")
c1, c2 = st.columns(2)

with c1:
    fig_npa = create_trend_line_chart(
        icici_p,
        x_col="period_label",
        y_cols=["gnpa_pct", "nnpa_pct"],
        labels=["Gross NPA Ratio (%)", "Net NPA Ratio (%)"],
        title="ICICI Bank GNPA & NNPA Evolution (%)",
        y_title="%",
        is_pct=True
    )
    st.plotly_chart(fig_npa, use_container_width=True)

with c2:
    fig_pcr = create_trend_line_chart(
        icici_p,
        x_col="period_label",
        y_cols=["pcr_pct"],
        labels=["Provision Coverage Ratio (%)"],
        title="Provision Coverage Ratio (PCR %) — Standalone",
        y_title="PCR (%)",
        is_pct=True
    )
    st.plotly_chart(fig_pcr, use_container_width=True)

# 2. Peer Comparison Overlay on Asset Quality
st.markdown("#### 2. Cross-Sectional Peer NPA Comparison")
fig_peer_npa = go.Figure()

banks_to_plot = ["ICICI"] + [p for p in filters["peers"] if p != "ICICI"]
for b in banks_to_plot:
    b_df = df_kpi[df_kpi["bank"] == b]
    width = 3.5 if b == "ICICI" else 1.8
    fig_peer_npa.add_trace(go.Scatter(
        x=b_df["period_label"],
        y=b_df["gnpa_pct"],
        mode="lines+markers",
        name=f"{b} GNPA %",
        line={"width": width},
        hovertemplate=f"<b>{b} GNPA</b>: %{{y:.2f}}%<extra></extra>"
    ))

apply_chart_theme(fig_peer_npa, "Gross NPA Comparison across Selected Peer Banks (%)")
fig_peer_npa.update_layout(yaxis_title="Gross NPA (%)")
st.plotly_chart(fig_peer_npa, use_container_width=True)

# 3. Credit Cost to PPOP Ratio
st.markdown("#### 3. Provisions as % of Operating Profit (PPOP)")
fig_credit_cost = go.Figure()
fig_credit_cost.add_trace(go.Bar(
    x=df_bridge["period_label"],
    y=df_bridge["credit_cost_to_ppop_pct"],
    name="Provisions / PPOP (%)",
    marker_color="#0f2942",
    hovertemplate="<b>Provisions / PPOP</b>: %{y:.2f}%<extra></extra>"
))
apply_chart_theme(fig_credit_cost, "Provisions as % of Pre-Provision Operating Profit (PPOP)")
fig_credit_cost.update_layout(yaxis_title="Provisions / PPOP (%)")
st.plotly_chart(fig_credit_cost, use_container_width=True)

# Table
st.markdown("#### Asset Quality & Provisioning Series")
aq_table = icici_p[["period_label", "gnpa_pct", "nnpa_pct", "pcr_pct", "provisions_cr", "ppop_cr"]]
st.dataframe(aq_table, use_container_width=True, hide_index=True)

render_analyst_box(
    title="Asset Quality Analyst Takeaways",
    takeaways=[
        "**Multi-Year De-risking:** ICICI Bank reduced its Gross NPA ratio from 2.76% in Q1 FY24 down to 1.35% in Q2 FY27, representing a total reduction of over 140 basis points.",
        "**Conservative Provisioning:** Net NPA has remained firmly anchored in the 0.31%–0.44% corridor, backed by a fortified Provision Coverage Ratio (PCR) consistently above 80%.",
        "**Credit Cost Absorption:** Total provisions as a percentage of PPOP have stabilized at a benign 6%–9%, ensuring that operating profits flow directly to net profit without balance-sheet friction."
    ]
)

render_footer()

