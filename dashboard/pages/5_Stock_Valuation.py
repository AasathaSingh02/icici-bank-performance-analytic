"""
dashboard/pages/5_Stock_Valuation.py - Market Performance & Valuation
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
    load_relative_strength,
    load_drawdowns,
    load_monthly_returns,
    load_stock_stats,
    load_valuations
)
from dashboard.components.charts import (
    create_relative_strength_chart,
    create_drawdown_chart,
    create_monthly_heatmap,
    apply_chart_theme
)

apply_custom_styles()
filters = render_sidebar_filters()

render_header(
    title="Stock Performance & Valuation",
    subtitle="Rebased Benchmark Returns, Peak Drawdowns, Monthly Heatmap & P/E Valuation Multiples"
)

df_rel = load_relative_strength()
df_drawdowns = load_drawdowns()
df_monthly = load_monthly_returns()
df_stats = load_stock_stats()
df_val = load_valuations()

# 1. Rebased Cumulative Return vs Benchmarks
st.markdown("#### 1. Cumulative Total Return vs Nifty Bank & Nifty 50 (Rebased = 100)")
fig_rel = create_relative_strength_chart(df_rel)
st.plotly_chart(fig_rel, use_container_width=True)

# 2. Drawdown & Calendar Monthly Heatmap
st.markdown("#### 2. Downside Risk (Drawdown) & Monthly Returns Heatmap")
col_l, col_r = st.columns(2)

with col_l:
    icici_dd = df_drawdowns[df_drawdowns["asset"] == "ICICI"]
    fig_dd = create_drawdown_chart(icici_dd, "ICICI Bank")
    st.plotly_chart(fig_dd, use_container_width=True)

with col_r:
    fig_heat = create_monthly_heatmap(df_monthly, asset_code="ICICI")
    st.plotly_chart(fig_heat, use_container_width=True)

# 3. Quantitative Risk & Statistical Profile
st.markdown("#### 3. Quantitative Risk & Return Statistics (April 2023 – October 2026)")
stats_table = df_stats[[
    "bank", "name", "beta_nifty50", "beta_niftybank", "corr_nifty50", "corr_niftybank",
    "cagr_return", "annualized_volatility", "max_drawdown", "sharpe_ratio"
]]
stats_table.columns = [
    "Bank", "Institution Name", "Beta (Nifty 50)", "Beta (Nifty Bank)",
    "Corr (N50)", "Corr (Bank)", "CAGR Return (%)", "Ann. Volatility (%)",
    "Max Drawdown (%)", "Sharpe Ratio"
]
st.dataframe(stats_table, use_container_width=True, hide_index=True)

# 4. Valuation Multiples: P/E Trajectory
st.markdown("#### 4. Historical Trailing P/E Valuation Ratio")
fig_pe = go.Figure()
for b in ["ICICI"] + [p for p in filters["peers"] if p != "ICICI"]:
    sub_val = df_val[df_val["bank"] == b]
    fig_pe.add_trace(go.Scatter(
        x=sub_val["period_label"],
        y=sub_val["pe_ratio"],
        mode="lines+markers",
        name=f"{b} TTM P/E",
        hovertemplate=f"<b>{b} P/E</b>: %{{y:.1f}}x<extra></extra>"
    ))
apply_chart_theme(fig_pe, "Trailing Twelve Months (TTM) Price-to-Earnings Multiple (x)")
fig_pe.update_layout(yaxis_title="TTM P/E Multiple (x)")
st.plotly_chart(fig_pe, use_container_width=True)

render_analyst_box(
    title="Market Valuation Analyst Takeaways",
    takeaways=[
        "**Persistent Benchmark Outperformance:** ICICI Bank appreciated from ~₹875 in April 2023 to ~₹1,385 by late 2026, delivering ~14.5% annualized returns and outperforming both Nifty 50 and Nifty Bank indices.",
        "**Controlled Downside Profile:** ICICI Bank's maximum peak-to-trough drawdown during the 3.5-year observation window was contained to ~9.5%, comparing favorably to peer private lenders undergoing regulatory or merger consolidations.",
        "**Valuation Discipline:** ICICI trades at approximately 17x–19x trailing twelve months earnings, supported by consistent 18%+ ROE and clean balance-sheet underwriting."
    ]
)

render_footer()

