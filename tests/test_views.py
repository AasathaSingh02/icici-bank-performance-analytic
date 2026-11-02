"""
tests/test_views.py - Unit and Integration Tests for Bank Intelligence Platform
"""
import sqlite3
from pathlib import Path
import pytest

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "bank.db"

@pytest.fixture
def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    yield c
    c.close()

def test_database_exists():
    assert DB_PATH.exists(), f"Database not found at {DB_PATH}"

def test_company_counts(conn):
    cnt = conn.execute("SELECT COUNT(*) FROM dim_company").fetchone()[0]
    assert cnt == 5, f"Expected 5 companies, got {cnt}"

def test_period_counts(conn):
    cnt = conn.execute("SELECT COUNT(*) FROM dim_period WHERE period_type = 'Q'").fetchone()[0]
    assert cnt == 14, f"Expected 14 quarters, got {cnt}"

def test_kpi_wide_view(conn):
    rows = conn.execute("SELECT * FROM v_kpi_wide").fetchall()
    assert len(rows) == 5 * 14, f"Expected 70 rows (5 banks x 14 qtrs), got {len(rows)}"

def test_kpi_growth_view(conn):
    row = conn.execute(
        "SELECT pat_yoy_pct, nii_yoy_pct FROM v_kpi_growth WHERE bank = 'ICICI' AND period_label = 'Q4 FY25'"
    ).fetchone()
    assert row is not None
    assert row["pat_yoy_pct"] is not None

def test_asset_quality_invariant(conn):
    violations = conn.execute(
        "SELECT COUNT(*) FROM v_kpi_wide WHERE nnpa_pct > gnpa_pct"
    ).fetchone()[0]
    assert violations == 0, f"Net NPA should never exceed Gross NPA, found {violations} violations"

def test_peer_rank_view(conn):
    ranks = conn.execute(
        "SELECT rank_pat FROM v_peer_rank WHERE period_label = 'Q4 FY26'"
    ).fetchall()
    assert len(ranks) == 5
    assert set(r[0] for r in ranks) == {1, 2, 3, 4, 5}

def test_stock_stats(conn):
    stats = conn.execute(
        "SELECT * FROM fact_stock_stats WHERE company_id = (SELECT company_id FROM dim_company WHERE short_code = 'ICICI')"
    ).fetchone()
    assert stats is not None
    assert stats["beta_nifty50"] is not None
    assert stats["cagr_return"] > 0

