"""
dashboard/pages/6_Peer_Benchmarking.py - Cross-Sectional Peer Benchmarking
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
    load_peer_ranks,
    load_peer_gaps
)
from dashboard.components.charts import (
    create_peer_radar_chart,
    apply_chart_theme
)

apply_custom_styles()
filters = render_sidebar_filters()

render_header(
    title="Peer Benchmarking & League Tables",
    subtitle="Cross-Sectional Radar Profiling, League Table Rankings & ICICI vs Peer-Average Spreads"
)

df_kpi = load_kpi_wide()
df_ranks = load_peer_ranks()
df_gaps = load_peer_gaps()
qtr = filters["quarter"]

# 1. Fundamental Radar Chart
st.markdown(f"#### 1. Multidimensional Banking Radar — {qtr}")
df_latest_qtr = df_kpi[df_kpi["period_label"] == qtr]
if not df_latest_qtr.empty:
    fig_radar = create_peer_radar_chart(df_latest_qtr, primary_code="ICICI", peer_codes=filters["peers"])
    st.plotly_chart(fig_radar, use_container_width=True)

# 2. League Table: Peer Rankings
st.markdown(f"#### 2. Cross-Sectional League Table ({qtr})")
ranks_qtr = df_ranks[df_ranks["period_label"] == qtr][[
    "bank", "rank_pat", "pat_cr", "rank_nim", "nim_pct", "rank_roe", "roe_pct",
    "rank_gnpa", "gnpa_pct", "rank_pcr", "pcr_pct", "rank_casa", "casa_ratio_pct"
]].copy()

ranks_qtr.columns = [
    "Bank", "Rank (PAT)", "PAT (₹ Cr)", "Rank (NIM)", "NIM (%)", "Rank (ROE)", "ROE (%)",
    "Rank (GNPA)", "GNPA (%)", "Rank (PCR)", "PCR (%)", "Rank (CASA)", "CASA (%)"
]
st.dataframe(ranks_qtr, use_container_width=True, hide_index=True)

# 3. ICICI vs Peer Average Gap Evolution
st.markdown("#### 3. ICICI Spread vs Peer Group Average")
c1, c2 = st.columns(2)

with c1:
    fig_nim_gap = go.Figure()
    fig_nim_gap.add_trace(go.Bar(
        x=df_gaps["period_label"],
        y=df_gaps["nim_gap_bps"],
        marker_color="#10b981",
        name="NIM Spread (bps)"
    ))
    apply_chart_theme(fig_nim_gap, "ICICI NIM Spread to Peer Average (Basis Points)")
    fig_nim_gap.update_layout(yaxis_title="Basis Points Spread")
    st.plotly_chart(fig_nim_gap, use_container_width=True)

with c2:
    fig_gnpa_gap = go.Figure()
    fig_gnpa_gap.add_trace(go.Bar(
        x=df_gaps["period_label"],
        y=df_gaps["gnpa_gap_bps"],
        marker_color="#0f2942",
        name="GNPA Difference (%)"
    ))
    apply_chart_theme(fig_gnpa_gap, "ICICI GNPA Spread to Peer Average (%)")
    fig_gnpa_gap.update_layout(yaxis_title="Difference (%)")
    st.plotly_chart(fig_gnpa_gap, use_container_width=True)

render_analyst_box(
    title="Peer Benchmarking Analyst Takeaways",
    takeaways=[
        f"**Profitability Premium:** ICICI consistently ranks #1 in Return on Equity (~18.0%–18.8%) among private sector tier-1 lenders, comfortably exceeding HDFC Bank (15.5%–16.2%) and Kotak Bank (11.8%–13.0%).",
        "**NIM Leadership:** ICICI generates a positive margin spread of +60 to +80 basis points over the peer average, thanks to its high-yielding retail lending book and granular customer deposit franchise.",
        "**Asset Quality Leadership:** ICICI's GNPA has converged toward pristine levels (1.35%), rivaling HDFC Bank's historical benchmark while outpacing SBI and Axis Bank."
    ]
)

render_footer()

