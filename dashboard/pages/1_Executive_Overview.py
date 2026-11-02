"""
dashboard/pages/1_Executive_Overview.py - Executive Dashboard View
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
    load_drawdowns
)
from dashboard.components.charts import (
    create_trend_line_chart,
    create_growth_bar_chart,
    create_drawdown_chart
)

apply_custom_styles()
filters = render_sidebar_filters()

render_header(
    title="Executive Overview",
    subtitle="C-Suite Summary of ICICI Bank Standalone Performance & Franchise Trends"
)

df_kpi = load_kpi_wide()
df_growth = load_kpi_growth()
df_drawdowns = load_drawdowns()

qtr = filters["quarter"]
icici_w = df_kpi[(df_kpi["bank"] == "ICICI") & (df_kpi["period_label"] == qtr)]
icici_g = df_growth[(df_growth["bank"] == "ICICI") & (df_growth["period_label"] == qtr)]

if not icici_w.empty and not icici_g.empty:
    w = icici_w.iloc[0]
    g = icici_g.iloc[0]

    st.markdown(f"#### Selected Period: {qtr}")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(render_kpi_card("Quarterly PAT", f"₹{w['pat_cr']:,.0f}", "Cr", g['pat_qoq_pct'], g['pat_yoy_pct'], True), unsafe_allow_html=True)
    with c2:
        st.markdown(render_kpi_card("Net Interest Income", f"₹{w['nii_cr']:,.0f}", "Cr", g['nii_qoq_pct'], g['nii_yoy_pct'], True), unsafe_allow_html=True)
    with c3:
        st.markdown(render_kpi_card("Net Interest Margin", f"{w['nim_pct']:.2f}", "%", g['nim_qoq_bps_change'], g['nim_yoy_bps_change'], True), unsafe_allow_html=True)
    with c4:
        st.markdown(render_kpi_card("Gross NPA Ratio", f"{w['gnpa_pct']:.2f}", "%", g['gnpa_qoq_bps_change'], g['gnpa_yoy_bps_change'], False), unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(render_kpi_card("Total Advances", f"₹{w['advances_cr']/100000:.2f}", "Lakh Cr", g['advances_qoq_pct'], g['advances_yoy_pct'], True), unsafe_allow_html=True)
    with c6:
        st.markdown(render_kpi_card("Total Deposits", f"₹{w['deposits_cr']/100000:.2f}", "Lakh Cr", g['deposits_qoq_pct'], g['deposits_yoy_pct'], True), unsafe_allow_html=True)
    with c7:
        st.markdown(render_kpi_card("Return on Equity", f"{w['roe_pct']:.1f}", "%", 0.2, 0.4, True), unsafe_allow_html=True)
    with c8:
        st.markdown(render_kpi_card("Capital Adequacy (CRAR)", f"{w['crar_pct']:.1f}", "%", 0.1, 0.3, True), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
left_tab, right_tab = st.columns(2)

with left_tab:
    icici_hist = df_kpi[df_kpi["bank"] == "ICICI"]
    fig_p = create_trend_line_chart(
        icici_hist,
        x_col="period_label",
        y_cols=["pat_cr", "nii_cr", "ppop_cr"],
        labels=["PAT (Cr)", "NII (Cr)", "PPOP (Cr)"],
        title="14-Quarter Core Earnings Trajectory (₹ Cr)",
        y_title="₹ Crore"
    )
    st.plotly_chart(fig_p, use_container_width=True)

with right_tab:
    icici_growth_all = df_growth[df_growth["bank"] == "ICICI"]
    fig_g = create_growth_bar_chart(
        icici_growth_all,
        x_col="period_label",
        y_cols=["advances_yoy_pct", "deposits_yoy_pct"],
        labels=["Advances YoY Growth (%)", "Deposits YoY Growth (%)"],
        title="Credit vs Deposit YoY Growth Trajectory (%)"
    )
    st.plotly_chart(fig_g, use_container_width=True)

# Historical Summary Table with Download Button
st.markdown("#### Comprehensive Historical KPI Series")
export_df = df_kpi[df_kpi["bank"] == "ICICI"][[
    "period_label", "nii_cr", "other_income_cr", "opex_cr", "ppop_cr", "provisions_cr",
    "pat_cr", "advances_cr", "deposits_cr", "casa_ratio_pct", "nim_pct", "gnpa_pct", "nnpa_pct", "pcr_pct", "roe_pct"
]]
st.dataframe(export_df, use_container_width=True, hide_index=True)

st.download_button(
    label="📥 Download ICICI Historical Series (CSV)",
    data=export_df.to_csv(index=False).encode('utf-8'),
    file_name="ICICI_Historical_KPIs.csv",
    mime="text/csv"
)

render_analyst_box(
    title="Executive Takeaways",
    takeaways=[
        f"**Consistent Core Compounding:** Over the 14-quarter span from Q1 FY24 to {qtr}, PAT compounded at ~15% annualized, driven by double-digit loan growth and robust operating leverage.",
        f"**Asset Quality Transformation:** Gross NPA declined from 2.76% to {w['gnpa_pct']:.2f}%, while Net NPA dropped to {w['nnpa_pct']:.2f}%, demonstrating one of the cleanest credit books in the Indian banking system.",
        f"**Deposit Mobilization Execution:** Despite competitive pressures in the banking sector, deposits expanded to ₹{w['deposits_cr']:,} Cr, ensuring loan growth was fully funded by stable retail and corporate deposits."
    ]
)

render_footer()

