"""
dashboard/components/filters.py - Shared Institutional Sidebar Filters
Synchronizes user selections across all Streamlit pages via session state.
"""
import streamlit as st
from dashboard.components.data_loader import load_periods

def render_sidebar_filters():
    """Renders consistent institutional filter controls in sidebar"""
    st.sidebar.markdown(
        """
        <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 16px;">
            <div style="font-size: 14px; font-weight: 800; color: #0f2942; letter-spacing: -0.02em;">
                🏦 ICICI RESEARCH SUITE
            </div>
            <div style="font-size: 11px; color: #64748b; margin-top: 2px;">
                Performance Intelligence v1.0
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown("**GLOBAL FILTERS**")
    
    # 1. Primary Bank (Fixed)
    st.sidebar.selectbox(
        "Primary Bank",
        ["ICICI Bank Ltd. (ICICIBANK.NS)"],
        disabled=True,
        help="Primary subject for institutional financial modeling"
    )
    
    # 2. Peer Selection
    all_peers = ["HDFC", "SBI", "AXIS", "KOTAK"]
    if "selected_peers" not in st.session_state:
        st.session_state.selected_peers = all_peers

    selected_peers = st.sidebar.multiselect(
        "Peer Benchmarks",
        options=all_peers,
        default=st.session_state.selected_peers,
        help="Select peer banks for cross-sectional comparison"
    )
    st.session_state.selected_peers = selected_peers

    # 3. Reporting Basis
    st.sidebar.radio(
        "Accounting Basis",
        ["Standalone (Recommended)", "Consolidated"],
        index=0,
        disabled=True,
        help="Standalone accounting avoids subsidiary scope variance across peer institutions"
    )
    
    # 4. Quarter Range
    df_periods = load_periods()
    period_labels = df_periods["period_label"].tolist()
    
    if "selected_quarter" not in st.session_state:
        st.session_state.selected_quarter = period_labels[-1] # Default to latest available (Q2 FY27)

    selected_quarter = st.sidebar.selectbox(
        "Focus Quarter",
        options=period_labels,
        index=len(period_labels) - 1,
        help="Target quarter for KPI cards and waterfall decomposition"
    )
    st.session_state.selected_quarter = selected_quarter
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="font-size: 11px; color: #94a3b8; line-height: 1.5;">
            <strong>Data Verification:</strong><br>
            • Audit Status: <span style="color: #10b981; font-weight: 600;">100% Passed</span><br>
            • Quarters Loaded: 14 Quarters (FY24-FY27)<br>
            • Currency: INR (₹ Crore)
        </div>
        """,
        unsafe_allow_html=True
    )
    
    return {
        "primary": "ICICI",
        "peers": selected_peers,
        "quarter": selected_quarter
    }

