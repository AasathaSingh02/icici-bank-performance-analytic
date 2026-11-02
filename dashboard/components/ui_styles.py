"""
dashboard/components/ui_styles.py - Custom Styling & Bespoke UI Components
Crafted to look human-designed, elegant, and institutional.
"""
import streamlit as st

def apply_custom_styles():
    """Injects bespoke CSS styling for high-end institutional banking dashboard"""
    custom_css = """
    <style>
        /* Import clean modern font */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #1e293b;
        }

        /* Top header bar branding */
        .app-header {
            background: linear-gradient(135deg, #0f2942 0%, #1a365d 100%);
            padding: 24px 32px;
            border-radius: 14px;
            color: #ffffff;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px -2px rgba(15, 41, 66, 0.15);
            border-left: 6px solid #e35205;
        }
        .app-header h1 {
            color: #ffffff !important;
            font-size: 26px !important;
            font-weight: 700 !important;
            margin: 0 0 6px 0 !important;
            letter-spacing: -0.02em;
        }
        .app-header p {
            color: #94a3b8 !important;
            font-size: 14px !important;
            margin: 0 !important;
        }

        /* Metric cards */
        .kpi-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .kpi-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease-in-out;
            position: relative;
            overflow: hidden;
        }
        .kpi-card:hover {
            box-shadow: 0 6px 16px -2px rgba(0, 0, 0, 0.08);
            border-color: #cbd5e1;
            transform: translateY(-2px);
        }
        .kpi-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: #e35205;
        }
        .kpi-title {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            margin-bottom: 6px;
        }
        .kpi-value {
            font-size: 26px;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: -0.03em;
            line-height: 1.2;
            margin-bottom: 8px;
        }
        .kpi-unit {
            font-size: 14px;
            font-weight: 500;
            color: #94a3b8;
            margin-left: 4px;
        }
        .pill-badge {
            display: inline-flex;
            align-items: center;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: -0.01em;
        }
        .pill-green {
            background-color: #ecfdf5;
            color: #059669;
            border: 1px solid #a7f3d0;
        }
        .pill-red {
            background-color: #fef2f2;
            color: #dc2626;
            border: 1px solid #fecaca;
        }
        .pill-neutral {
            background-color: #f1f5f9;
            color: #475569;
            border: 1px solid #e2e8f0;
        }

        /* Analyst Note & Insight Boxes */
        .analyst-box {
            background: #fdfefe;
            border-left: 4px solid #e35205;
            border-top: 1px solid #edf2f7;
            border-right: 1px solid #edf2f7;
            border-bottom: 1px solid #edf2f7;
            border-radius: 0 10px 10px 0;
            padding: 16px 20px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        }
        .analyst-box-title {
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #e35205;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .analyst-box ul {
            margin: 0;
            padding-left: 18px;
            color: #334155;
            font-size: 13.5px;
            line-height: 1.6;
        }

        /* Section Cards */
        .section-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 22px 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }
        .section-title {
            font-size: 16px;
            font-weight: 700;
            color: #0f2942;
            margin-bottom: 14px;
            letter-spacing: -0.01em;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        /* Clean Sidebar */
        [data-testid="stSidebar"] {
            background-color: #f8fafc;
            border-right: 1px solid #e2e8f0;
        }

        /* Footer stamp */
        .dashboard-footer {
            margin-top: 48px;
            padding-top: 18px;
            border-top: 1px solid #e2e8f0;
            font-size: 12px;
            color: #94a3b8;
            text-align: center;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_header(title, subtitle, badge_text="ICICI BANK RESEARCH"):
    """Renders a polished institutional header"""
    html = f"""
    <div class="app-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
            <span style="background: rgba(227, 82, 5, 0.2); color: #ff8c42; border: 1px solid rgba(227, 82, 5, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em;">
                {badge_text}
            </span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_kpi_card(title, value, unit="", delta_qoq=None, delta_yoy=None, higher_is_better=True):
    """Renders a single KPI card with QoQ and YoY change indicators"""
    qoq_html = ""
    yoy_html = ""
    
    if delta_qoq is not None:
        is_pos = delta_qoq > 0
        is_good = (is_pos and higher_is_better) or (not is_pos and not higher_is_better)
        css_class = "pill-green" if is_good else ("pill-red" if delta_qoq != 0 else "pill-neutral")
        arrow = "▲" if is_pos else ("▼" if delta_qoq < 0 else "▬")
        qoq_html = f'<span class="pill-badge {css_class}" title="Quarter-on-Quarter Change">{arrow} {abs(delta_qoq):.1f}% QoQ</span>'

    if delta_yoy is not None:
        is_pos = delta_yoy > 0
        is_good = (is_pos and higher_is_better) or (not is_pos and not higher_is_better)
        css_class = "pill-green" if is_good else ("pill-red" if delta_yoy != 0 else "pill-neutral")
        arrow = "▲" if is_pos else ("▼" if delta_yoy < 0 else "▬")
        yoy_html = f'<span class="pill-badge {css_class}" title="Year-on-Year Change">{arrow} {abs(delta_yoy):.1f}% YoY</span>'

    card_html = f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}<span class="kpi-unit">{unit}</span></div>
        <div style="display: flex; gap: 6px; flex-wrap: wrap;">
            {qoq_html}
            {yoy_html}
        </div>
    </div>
    """
    return card_html

def render_analyst_box(title, takeaways):
    """Renders a senior equity research analyst takeaway box"""
    items_html = "".join([f"<li>{t}</li>" for t in takeaways])
    html = f"""
    <div class="analyst-box">
        <div class="analyst-box-title">
            <span>📌</span> {title}
        </div>
        <ul>
            {items_html}
        </ul>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_footer():
    """Renders the standard institutional footer with provenance details"""
    footer_html = """
    <div class="dashboard-footer">
        <strong>ICICI Bank Performance Intelligence Platform</strong> • Standalone Results • Data Curated from BSE Filings, RBI Database & World Bank • Built for Institutional Equity Research
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

