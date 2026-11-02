"""
dashboard/pages/2_Profitability.py - Profitability & Earnings Quality
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
    create_profit_waterfall,
    create_trend_line_chart,
    apply_chart_theme
)

apply_custom_styles()
filters = render_sidebar_filters()

render_header(
    title="Profitability & Operating Leverage",
    subtitle="Core Revenue Drivers, Net Interest Margin (NIM) Dynamics & Profit Decomposition Waterfall"
)

df_kpi = load_kpi_wide()
df_bridge = load_profit_bridge()
qtr = filters["quarter"]

# 1. Waterfall Chart for Focus Quarter
st.markdown(f"#### 1. Profit Decomposition Waterfall — {qtr}")
bridge_row = df_bridge[df_bridge["period_label"] == qtr]
if not bridge_row.empty:
    fig_wf = create_profit_waterfall(bridge_row.iloc[0], qtr)
    st.plotly_chart(fig_wf, use_container_width=True)

# 2. Revenue Breakdown & NIM Trend
st.markdown("#### 2. Core Revenue Composition & Margin Trajectory")
col_l, col_r = st.columns(2)

with col_l:
    # Stacked Bar: NII vs Other Income
    icici_p = df_kpi[df_kpi["bank"] == "ICICI"]
    fig_rev = go.Figure()
    fig_rev.add_trace(go.Bar(
        x=icici_p["period_label"],
        y=icici_p["nii_cr"],
        name="Net Interest Income",
        marker_color="#0f2942"
    ))
    fig_rev.add_trace(go.Bar(
        x=icici_p["period_label"],
        y=icici_p["other_income_cr"],
        name="Other / Non-Interest Income",
        marker_color="#e35205"
    ))
    apply_chart_theme(fig_rev, "Net Total Income Breakdown (₹ Crore)")
    fig_rev.update_layout(barmode="stack", yaxis_title="₹ Crore")
    st.plotly_chart(fig_rev, use_container_width=True)

with col_r:
    # Line chart: NIM % across quarters
    fig_nim = create_trend_line_chart(
        icici_p,
        x_col="period_label",
        y_cols=["nim_pct"],
        labels=["Net Interest Margin (%)"],
        title="Net Interest Margin (NIM) Trend (%)",
        y_title="NIM (%)",
        is_pct=True
    )
    st.plotly_chart(fig_nim, use_container_width=True)

# 3. Efficiency & Returns: Cost-to-Income, ROA, ROE
st.markdown("#### 3. Operating Efficiency & Shareholder Returns")
c1, c2 = st.columns(2)

with c1:
    fig_eff = create_trend_line_chart(
        icici_p,
        x_col="period_label",
        y_cols=["cost_to_income_pct"],
        labels=["Cost-to-Income Ratio (%)"],
        title="Cost-to-Income Efficiency Ratio (%)",
        y_title="%",
        is_pct=True
    )
    st.plotly_chart(fig_eff, use_container_width=True)

with c2:
    fig_returns = create_trend_line_chart(
        icici_p,
        x_col="period_label",
        y_cols=["roe_pct", "roa_pct"],
        labels=["Return on Equity (ROE %)", "Return on Assets (ROA %)"],
        title="Annualized ROE & ROA Trajectory (%)",
        y_title="%",
        is_pct=True
    )
    st.plotly_chart(fig_returns, use_container_width=True)

# Profit Bridge Table
st.markdown("#### P&L Decomposition Matrix (₹ Crore)")
bridge_table = df_bridge[[
    "period_label", "nii_cr", "other_income_cr", "total_income_net_cr",
    "opex_cr", "ppop_cr", "provisions_cr", "pbt_cr", "pat_cr", "calculated_cost_to_income_pct"
]]
st.dataframe(bridge_table, use_container_width=True, hide_index=True)

st.download_button(
    label="📥 Download Profit Bridge Data (CSV)",
    data=bridge_table.to_csv(index=False).encode('utf-8'),
    file_name="ICICI_Profit_Bridge.csv",
    mime="text/csv"
)

render_analyst_box(
    title="Profitability Analyst Takeaways",
    takeaways=[
        "**NIM Compression & Stabilization:** ICICI's standalone NIM normalized from a cyclical high of 4.78% (Q1 FY24) toward 4.30%–4.33% by FY26–FY27 as the RBI's prolonged rate pause and subsequent easing transmitted into deposit repricing.",
        "**Exceptional Operating Leverage:** Cost-to-income improved structurally from 40.7% in Q1 FY24 to sub-37% in recent quarters, reflecting extensive digital automation (iMobile Pay, InstaBIZ) and branch productivity gains.",
        "**Best-in-Class Returns Profile:** Annualized Return on Assets (ROA) has consistently stayed in the top tier at 2.30%–2.42%, while Return on Equity (ROE) exceeded 18%, placing ICICI Bank among the most profitable lenders globally."
    ]
)

render_footer()

