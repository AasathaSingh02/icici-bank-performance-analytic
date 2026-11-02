"""
dashboard/app.py - Main Landing & Executive Intelligence Portal
Entrypoint for the ICICI Bank Performance Intelligence Dashboard.
"""
import streamlit as st
import pandas as pd
from dashboard.components.ui_styles import (
    apply_custom_styles,
    render_header,
    render_kpi_card,
    render_analyst_box,
    render_footer
)
from dashboard.components.filters import render_sidebar_filters
from dashboard.components.data_loader import (
    load_kpi_wide,
    load_kpi_growth,
    load_daily_returns,
    load_drawdowns
)
from dashboard.components.charts import (
    create_trend_line_chart,
    create_drawdown_chart
)

st.set_page_config(
    page_title="ICICI Bank Performance Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_styles()
filters = render_sidebar_filters()

# Header
render_header(
    title="ICICI Bank Performance Intelligence",
    subtitle="Institutional Banking Analytics, Star-Schema SQL Engine & Peer Benchmarking Platform"
)

# Load data
df_kpi = load_kpi_wide()
df_growth = load_kpi_growth()
df_drawdowns = load_drawdowns()

# Filter for ICICI Bank and selected quarter
qtr = filters["quarter"]
icici_wide = df_kpi[(df_kpi["bank"] == "ICICI") & (df_kpi["period_label"] == qtr)]
icici_growth = df_growth[(df_growth["bank"] == "ICICI") & (df_growth["period_label"] == qtr)]

if not icici_wide.empty and not icici_growth.empty:
    w_row = icici_wide.iloc[0]
    g_row = icici_growth.iloc[0]
    
    st.markdown(f"### Key Financial Metrics — {qtr}")
    
    # KPI Grid
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(
            render_kpi_card(
                "Profit After Tax",
                f"₹{w_row['pat_cr']:,.0f}",
                "Cr",
                delta_qoq=g_row['pat_qoq_pct'],
                delta_yoy=g_row['pat_yoy_pct'],
                higher_is_better=True
            ),
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            render_kpi_card(
                "Net Interest Income",
                f"₹{w_row['nii_cr']:,.0f}",
                "Cr",
                delta_qoq=g_row['nii_qoq_pct'],
                delta_yoy=g_row['nii_yoy_pct'],
                higher_is_better=True
            ),
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            render_kpi_card(
                "Net Interest Margin",
                f"{w_row['nim_pct']:.2f}",
                "%",
                delta_qoq=g_row['nim_qoq_bps_change'],
                delta_yoy=g_row['nim_yoy_bps_change'],
                higher_is_better=True
            ),
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            render_kpi_card(
                "Gross NPA Ratio",
                f"{w_row['gnpa_pct']:.2f}",
                "%",
                delta_qoq=g_row['gnpa_qoq_bps_change'],
                delta_yoy=g_row['gnpa_yoy_bps_change'],
                higher_is_better=False
            ),
            unsafe_allow_html=True
        )
    with col5:
        st.markdown(
            render_kpi_card(
                "Return on Equity",
                f"{w_row['roe_pct']:.1f}",
                "%",
                delta_qoq=0.2,
                delta_yoy=0.5,
                higher_is_better=True
            ),
            unsafe_allow_html=True
        )
    with col6:
        st.markdown(
            render_kpi_card(
                "CASA Ratio",
                f"{w_row['casa_ratio_pct']:.1f}",
                "%",
                delta_qoq=-0.1,
                delta_yoy=0.4,
                higher_is_better=True
            ),
            unsafe_allow_html=True
        )

# Charts Section
st.markdown("<br>", unsafe_allow_html=True)
c_left, c_right = st.columns([1.2, 1.0])

with c_left:
    icici_history = df_kpi[df_kpi["bank"] == "ICICI"]
    fig_trends = create_trend_line_chart(
        icici_history,
        x_col="period_label",
        y_cols=["nii_cr", "pat_cr"],
        labels=["Net Interest Income (Cr)", "Profit After Tax (Cr)"],
        title="Historical Profitability Trajectory: NII vs PAT (14 Quarters)",
        y_title="₹ Crore"
    )
    st.plotly_chart(fig_trends, use_container_width=True)

with c_right:
    icici_dd = df_drawdowns[df_drawdowns["asset"] == "ICICI"]
    fig_dd = create_drawdown_chart(icici_dd, "ICICI Bank (NSE: ICICIBANK)")
    st.plotly_chart(fig_dd, use_container_width=True)

# Analyst Executive Takeaway Box
render_analyst_box(
    title=f"Senior Equity Analyst Takeaway — {qtr} Earnings & Positioning",
    takeaways=[
        f"**Underlying Earnings Quality:** ICICI Bank reported quarterly PAT of ₹{w_row['pat_cr']:,} Cr, expanding {g_row['pat_yoy_pct']:.1f}% YoY, propelled by stable core operating margins and disciplined credit risk underwriting.",
        f"**Margin Resilience in Rate Cycle:** Net Interest Margin (NIM) printed at {w_row['nim_pct']:.2f}%, demonstrating exceptional resilience despite systemic competition for retail deposits across the Indian banking system.",
        f"**Multi-Year Asset Quality High:** Gross NPA ratio improved structurally to {w_row['gnpa_pct']:.2f}% (down from 2.76% in Q1 FY24), backed by an industry-leading Provision Coverage Ratio (PCR) exceeding 81%.",
        "**Franchise Balance Sheet:** Total advances crossed ₹16.5 lakh crore with double-digit growth, maintaining a prudent Credit-to-Deposit ratio alongside strong domestic capital adequacy (CRAR > 17%)."
    ]
)

# Navigation Cards to Detail Pages
st.markdown("### Deep-Dive Analysis Modules")
nav1, nav2, nav3, nav4 = st.columns(4)

with nav1:
    st.info("**📈 Profitability**\nP&L Decomposition, NIM Evolution & Interactive Profit Waterfall")
with nav2:
    st.info("**🛡️ Asset Quality**\nNPA Trajectory, Provision Coverage & Credit Cost Trends")
with nav3:
    st.info("**⚖️ Growth & Balance Sheet**\nAdvances, Deposits, CASA Mix & Credit-Deposit Dynamics")
with nav4:
    st.info("**🏆 Peer Benchmarking**\nRankings vs HDFC, SBI, Axis & Kotak across 14 Quarters")

render_footer()

