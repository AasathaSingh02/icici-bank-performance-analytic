"""
dashboard/components/charts.py - Plotly Visualization Generators
Styled with high-contrast institutional color palette, clean gridlines, and rich hovercards.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Palette: ICICI Primary Orange, Institutional Navy, Cool Slate, Emerald, Crimson
COLORS = {
    "ICICI": "#e35205",
    "HDFC": "#004c8f",
    "SBI": "#228b22",
    "AXIS": "#97144d",
    "KOTAK": "#ed1c24",
    "^NSEBANK": "#475569",
    "^NSEI": "#0284c7",
    "positive": "#10b981",
    "negative": "#ef4444",
    "neutral": "#64748b",
    "bg_light": "#ffffff",
    "grid": "#f1f5f9"
}

def apply_chart_theme(fig, title="", height=400):
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "font": {"size": 14, "color": "#0f2942", "family": "Plus Jakarta Sans, sans-serif"},
            "x": 0.01,
            "xanchor": "left"
        },
        height=height,
        margin={"l": 40, "r": 20, "t": 50, "b": 40},
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font={"family": "Plus Jakarta Sans, sans-serif", "color": "#475569", "size": 12},
        hoverlabel={"bgcolor": "#0f2942", "font_color": "#ffffff", "font_size": 12},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        xaxis={
            "showgrid": True,
            "gridcolor": "#f1f5f9",
            "linecolor": "#cbd5e1",
            "ticks": "outside",
            "tickfont": {"size": 11}
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "#f1f5f9",
            "linecolor": "#cbd5e1",
            "ticks": "outside",
            "tickfont": {"size": 11}
        }
    )
    return fig

def create_profit_waterfall(row, quarter_label):
    """Creates an institutional P&L decomposition waterfall chart"""
    nii = row["nii_cr"]
    other_inc = row["other_income_cr"]
    opex = -row["opex_cr"]
    provisions = -row["provisions_cr"]
    pbt = row["pbt_cr"]
    pat = row["pat_cr"]
    taxes = -(pbt - pat)

    x_labels = [
        "Net Interest Income",
        "Other Income",
        "Operating Expenses",
        "PPOP (Subtotal)",
        "Provisions",
        "PBT (Subtotal)",
        "Taxes / Other",
        "Net PAT"
    ]
    
    y_values = [nii, other_inc, opex, 0, provisions, 0, taxes, 0]
    measure = ["relative", "relative", "relative", "total", "relative", "total", "relative", "total"]

    fig = go.Figure(go.Waterfall(
        name="P&L Bridge",
        orientation="v",
        measure=measure,
        x=x_labels,
        textposition="outside",
        text=[f"₹{abs(v):,.0f}" if m != "total" else f"₹{row['ppop_cr']:,.0f}" if i==3 else f"₹{pbt:,.0f}" if i==5 else f"₹{pat:,.0f}" for i, (v, m) in enumerate(zip(y_values, measure))],
        y=y_values,
        connector={"line": {"color": "#94a3b8", "dash": "dot"}},
        decreasing={"marker": {"color": "#ef4444"}},
        increasing={"marker": {"color": "#10b981"}},
        totals={"marker": {"color": "#0f2942"}}
    ))
    
    apply_chart_theme(fig, f"ICICI Bank Profit Bridge Waterfall — {quarter_label} (₹ Crore)", height=420)
    fig.update_layout(yaxis_title="₹ Crore", showlegend=False)
    return fig

def create_trend_line_chart(df, x_col, y_cols, labels, title, y_title="", is_pct=False):
    fig = go.Figure()
    for col, lbl in zip(y_cols, labels):
        color = COLORS.get(col, None)
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[col],
            mode="lines+markers",
            name=lbl,
            line={"width": 2.5, "color": color},
            marker={"size": 6},
            hovertemplate=f"<b>{lbl}</b>: %{{y:,.2f}}{'%' if is_pct else ''}<extra></extra>"
        ))
    apply_chart_theme(fig, title)
    fig.update_layout(yaxis_title=y_title)
    return fig

def create_growth_bar_chart(df, x_col, y_cols, labels, title, y_title="% YoY"):
    fig = go.Figure()
    for col, lbl in zip(y_cols, labels):
        fig.add_bar(
            x=df[x_col],
            y=df[col],
            name=lbl,
            hovertemplate=f"<b>{lbl}</b>: %{{y:.2f}}%<extra></extra>"
        )
    apply_chart_theme(fig, title)
    fig.update_layout(barmode="group", yaxis_title=y_title)
    return fig

def create_drawdown_chart(df_asset, asset_name):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_asset["date"],
        y=df_asset["drawdown_pct"],
        mode="lines",
        fill="tozeroy",
        line={"color": "#dc2626", "width": 1.5},
        fillcolor="rgba(220, 38, 38, 0.15)",
        name="Drawdown %",
        hovertemplate="<b>Date</b>: %{x}<br><b>Drawdown</b>: %{y:.2f}%<extra></extra>"
    ))
    apply_chart_theme(fig, f"{asset_name} Peak-to-Trough Drawdown (%)", height=320)
    fig.update_layout(yaxis_title="Drawdown from All-Time High (%)")
    return fig

def create_relative_strength_chart(df_rel):
    fig = go.Figure()
    for asset in df_rel["asset"].unique():
        sub = df_rel[df_rel["asset"] == asset]
        color = COLORS.get(asset, None)
        width = 3.0 if asset == "ICICI" else 1.8
        fig.add_trace(go.Scatter(
            x=sub["date"],
            y=sub["rebased_nav"],
            mode="lines",
            name=asset,
            line={"color": color, "width": width},
            hovertemplate=f"<b>{asset}</b>: %{{y:.1f}}<extra></extra>"
        ))
    apply_chart_theme(fig, "Cumulative Relative Return Rebased to 100 (April 2023 Base)", height=420)
    fig.update_layout(yaxis_title="Rebased Performance (Base = 100)")
    return fig

def create_monthly_heatmap(df_monthly, asset_code="ICICI"):
    sub = df_monthly[df_monthly["asset"] == asset_code]
    pivot = sub.pivot(index="year", columns="month", values="monthly_return_pct")
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pivot.columns = [month_names[int(m)-1] for m in pivot.columns]

    fig = px.imshow(
        pivot,
        labels={"x": "Month", "y": "Year", "color": "Return %"},
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        text_auto=".1f",
        aspect="auto"
    )
    apply_chart_theme(fig, f"{asset_code} Calendar Month Returns Heatmap (%)", height=320)
    return fig

def create_peer_radar_chart(df_latest, primary_code="ICICI", peer_codes=None):
    """Generates radar / spider chart across fundamental pillars"""
    metrics = ["NIM (%)", "ROE (%)", "CASA (%)", "Low GNPA (Inv)", "PCR (%)"]
    
    fig = go.Figure()
    
    # Process primary bank
    row_primary = df_latest[df_latest["bank"] == primary_code].iloc[0]
    vals_primary = [
        row_primary["nim_pct"],
        row_primary["roe_pct"],
        row_primary["casa_ratio_pct"],
        max(0, 5.0 - row_primary["gnpa_pct"]) * 20, # Inverted GNPA score (higher is cleaner)
        row_primary["pcr_pct"]
    ]
    vals_primary.append(vals_primary[0])
    
    fig.add_trace(go.Scatterpolar(
        r=vals_primary,
        theta=metrics + [metrics[0]],
        fill="toself",
        name=primary_code,
        line={"color": COLORS["ICICI"], "width": 3},
        fillcolor="rgba(227, 82, 5, 0.2)"
    ))
    
    if peer_codes:
        for p in peer_codes:
            sub = df_latest[df_latest["bank"] == p]
            if not sub.empty:
                r_peer = sub.iloc[0]
                vals_p = [
                    r_peer["nim_pct"],
                    r_peer["roe_pct"],
                    r_peer["casa_ratio_pct"],
                    max(0, 5.0 - r_peer["gnpa_pct"]) * 20,
                    r_peer["pcr_pct"]
                ]
                vals_p.append(vals_p[0])
                fig.add_trace(go.Scatterpolar(
                    r=vals_p,
                    theta=metrics + [metrics[0]],
                    name=p,
                    line={"color": COLORS.get(p, "#94a3b8"), "width": 1.5, "dash": "dot"}
                ))

    fig.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 100]}},
        title={"text": "<b>Cross-Sectional Banking Radar Comparison</b>", "font": {"size": 14, "color": "#0f2942"}},
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=420,
        margin={"l": 40, "r": 40, "t": 60, "b": 40}
    )
    return fig

