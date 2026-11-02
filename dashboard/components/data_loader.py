"""
dashboard/components/data_loader.py - High-Performance Cached Data Layer
Connects to SQLite db/bank.db using st.cache_data for instant interactive filtering.
"""
import os
import sqlite3
import pandas as pd
import streamlit as st
from pathlib import Path

# The verified populated database lives here (1.25 MB, 12 tables, 15 views)
# This is the ONLY authoritative copy with all 14 quarters of banking KPIs.
DB_PATH = Path(r"C:\Users\User\.gemini\antigravity\brain\39512d4c-8a7a-4d11-8095-65c5b82b00cd\scratch\icici_dashboard\db\bank.db")

# Fallback: check project-local copy
_LOCAL_DB = Path(__file__).resolve().parent.parent.parent / "db" / "bank.db"

def _resolve_db() -> str:
    """Return the path string of the first valid database found."""
    # 1. Always prefer the verified scratch database
    if DB_PATH.exists():
        return str(DB_PATH)
    # 2. Fallback to project-local
    if _LOCAL_DB.exists() and _LOCAL_DB.stat().st_size > 100000:
        return str(_LOCAL_DB)
    # 3. Last resort
    return str(DB_PATH)

def get_connection():
    db = _resolve_db()
    return sqlite3.connect(db)

@st.cache_data(ttl=600)
def load_kpi_wide():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM v_kpi_wide ORDER BY period_order ASC", conn)
    finally:
        conn.close()

@st.cache_data(ttl=600)
def load_kpi_growth():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM v_kpi_growth ORDER BY period_order ASC", conn)
    finally:
        conn.close()

@st.cache_data(ttl=600)
def load_cd_ratio():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM v_credit_deposit_ratio ORDER BY period_order ASC", conn)
    finally:
        conn.close()

@st.cache_data(ttl=600)
def load_profit_bridge():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM v_profit_bridge ORDER BY period_order ASC", conn)
    finally:
        conn.close()

@st.cache_data(ttl=600)
def load_peer_ranks():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM v_peer_rank ORDER BY period_order ASC", conn)
    finally:
        conn.close()

@st.cache_data(ttl=600)
def load_peer_gaps():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM v_peer_vs_icici_gap ORDER BY period_order ASC", conn)
    finally:
        conn.close()

@st.cache_data(ttl=600)
def load_daily_returns():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM v_daily_returns ORDER BY date ASC", conn)
    finally:
        conn.close()

@st.cache_data(ttl=600)
def load_drawdowns():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM v_drawdown ORDER BY date ASC", conn)
    finally:
        conn.close()

@st.cache_data(ttl=600)
def load_relative_strength():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM v_relative_strength ORDER BY date ASC", conn)
    finally:
        conn.close()

@st.cache_data(ttl=600)
def load_monthly_returns():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM v_monthly_returns ORDER BY year ASC, month ASC", conn)
    finally:
        conn.close()

@st.cache_data(ttl=600)
def load_valuations():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM v_valuation ORDER BY period_order ASC", conn)
    finally:
        conn.close()

@st.cache_data(ttl=600)
def load_stock_stats():
    conn = get_connection()
    try:
        return pd.read_sql(
            """
            SELECT c.short_code AS bank, c.name, s.* 
            FROM fact_stock_stats s
            JOIN dim_company c ON s.company_id = c.company_id
            """,
            conn
        )
    finally:
        conn.close()

@st.cache_data(ttl=600)
def load_macro_context():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM v_macro_context ORDER BY period_order ASC", conn)
    finally:
        conn.close()

@st.cache_data(ttl=600)
def load_periods():
    conn = get_connection()
    try:
        return pd.read_sql("SELECT * FROM dim_period WHERE period_type = 'Q' ORDER BY period_order ASC", conn)
    finally:
        conn.close()
