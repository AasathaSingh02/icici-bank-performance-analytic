"""
tests/test_pipeline.py - Automated Test Suite for Pipeline Validation
"""
import sys
import os
import sqlite3
import pytest
from pathlib import Path

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# We'll use the scratch DB for tests
SCRATCH_DIR = Path(r"C:\Users\User\.gemini\antigravity\brain\39512d4c-8a7a-4d11-8095-65c5b82b00cd\scratch")
TEST_DB_PATH = SCRATCH_DIR / "test_bank.db"

def get_test_conn():
    """Get a connection to the test database"""
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@pytest.fixture(scope="session", autouse=True)
def run_pipeline():
    """Run the full pipeline once before all tests"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_pipeline", BASE_DIR / "src" / "ingest" / "run_pipeline.py")
    # Override DB path to test path
    os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
    
    # Direct import and run
    from src.ingest.run_pipeline import run_pipeline as _run
    _run()
    yield
    # Cleanup
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

class TestSchemaIntegrity:
    def test_dim_company_loaded(self):
        conn = get_test_conn()
        rows = conn.execute("SELECT COUNT(*) FROM dim_company").fetchone()[0]
        conn.close()
        assert rows == 5, f"Expected 5 companies, found {rows}"

    def test_dim_period_loaded(self):
        conn = get_test_conn()
        rows = conn.execute("SELECT COUNT(*) FROM dim_period WHERE period_type = 'Q'").fetchone()[0]
        conn.close()
        assert rows == 14, f"Expected 14 quarters, found {rows}"

    def test_dim_metric_loaded(self):
        conn = get_test_conn()
        rows = conn.execute("SELECT COUNT(*) FROM dim_metric").fetchone()[0]
        conn.close()
        assert rows >= 17

    def test_no_null_primary_keys(self):
        conn = get_test_conn()
        null_kpi = conn.execute(
            "SELECT COUNT(*) FROM fact_bank_kpi WHERE company_id IS NULL OR period_id IS NULL"
        ).fetchone()[0]
        conn.close()
        assert null_kpi == 0

class TestKPIData:
    def test_icici_14_quarters(self):
        conn = get_test_conn()
        rows = conn.execute(
            "SELECT COUNT(DISTINCT period_id) FROM fact_bank_kpi WHERE company_id = 1"
        ).fetchone()[0]
        conn.close()
        assert rows == 14, f"ICICI needs 14 quarters, found {rows}"

    def test_nnpa_leq_gnpa(self):
        conn = get_test_conn()
        violations = conn.execute(
            "SELECT COUNT(*) FROM v_kpi_wide WHERE nnpa_pct > gnpa_pct"
        ).fetchone()[0]
        conn.close()
        assert violations == 0, f"{violations} quarters where Net NPA > Gross NPA"

    def test_spot_q4_fy26(self):
        conn = get_test_conn()
        row = conn.execute(
            "SELECT pat_cr, nii_cr, gnpa_pct FROM v_kpi_wide WHERE bank = 'ICICI' AND period_label = 'Q4 FY26'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == 13702.0
        assert row[1] == 22979.0
        assert row[2] == 1.40

class TestStockData:
    def test_prices_loaded(self):
        conn = get_test_conn()
        rows = conn.execute("SELECT COUNT(*) FROM fact_stock_price").fetchone()[0]
        conn.close()
        assert rows > 4000  # 5 banks * ~880 trading days

    def test_no_negative_prices(self):
        conn = get_test_conn()
        neg = conn.execute(
            "SELECT COUNT(*) FROM fact_stock_price WHERE close < 0 OR volume < 0"
        ).fetchone()[0]
        conn.close()
        assert neg == 0

    def test_high_gte_low(self):
        conn = get_test_conn()
        bad = conn.execute(
            "SELECT COUNT(*) FROM fact_stock_price WHERE high < low"
        ).fetchone()[0]
        conn.close()
        assert bad == 0

class TestMacroData:
    def test_repo_rate_loaded(self):
        conn = get_test_conn()
        rows = conn.execute(
            "SELECT COUNT(*) FROM fact_macro WHERE indicator_code = 'REPO_RATE'"
        ).fetchone()[0]
        conn.close()
        assert rows >= 10

class TestSQLViews:
    def test_v_kpi_wide_returns_rows(self):
        conn = get_test_conn()
        rows = conn.execute("SELECT COUNT(*) FROM v_kpi_wide").fetchone()[0]
        conn.close()
        assert rows > 0

    def test_v_kpi_growth_returns_rows(self):
        conn = get_test_conn()
        rows = conn.execute("SELECT COUNT(*) FROM v_kpi_growth").fetchone()[0]
        conn.close()
        assert rows > 0

    def test_v_peer_rank_returns_rows(self):
        conn = get_test_conn()
        rows = conn.execute("SELECT COUNT(*) FROM v_peer_rank").fetchone()[0]
        conn.close()
        assert rows > 0

    def test_v_macro_context_returns_rows(self):
        conn = get_test_conn()
        rows = conn.execute("SELECT COUNT(*) FROM v_macro_context").fetchone()[0]
        conn.close()
        assert rows > 0

