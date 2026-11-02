"""
build_db_only.py - Runs just the ETL pipeline (no Streamlit) for validation
"""
import sys
import os
import shutil
from pathlib import Path

SRC_ROOT = Path(r"C:\Users\User\OneDrive\Desktop\data analyst")
SCRATCH   = Path(r"C:\Users\User\.gemini\antigravity\brain\39512d4c-8a7a-4d11-8095-65c5b82b00cd\scratch")
WORK_DIR  = SCRATCH / "icici_dashboard"
DB_DIR    = WORK_DIR / "db"

print("=" * 65)
print("  ICICI Bank Analytics — Database Build (Pipeline Only)")
print("=" * 65)

# Stage to writable location
if WORK_DIR.exists():
    shutil.rmtree(WORK_DIR, ignore_errors=True)
WORK_DIR.mkdir(parents=True, exist_ok=True)

for item in ["sql", "src", "dashboard", "config.yaml"]:
    src = SRC_ROOT / item
    dst = WORK_DIR / item
    try:
        if src.is_dir():
            shutil.copytree(src, dst)
        elif src.is_file():
            shutil.copy2(src, dst)
    except PermissionError as e:
        print(f"   Skipped {item}: {e}")

DB_DIR.mkdir(parents=True, exist_ok=True)
(WORK_DIR / "data" / "manual").mkdir(parents=True, exist_ok=True)
(WORK_DIR / "data" / "raw").mkdir(parents=True, exist_ok=True)
(WORK_DIR / "docs").mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(WORK_DIR))
os.chdir(WORK_DIR)

from src.db import get_sqlite_connection, init_schema
from src.ingest.bank_kpis import ingest_companies_and_periods, ingest_bank_kpis, generate_manual_kpi_template
from src.ingest.prices import ingest_market_prices
from src.ingest.macro import ingest_macro
from src.quality.checks import run_quality_suite

print("\n[1/6] Schema initialization...")
init_schema()
print("      DONE")

conn = get_sqlite_connection()

print("[2/6] Dimensions + manual templates...")
ingest_companies_and_periods(conn)
generate_manual_kpi_template()
print("      DONE")

print("[3/6] Banking KPIs ingestion...")
k = ingest_bank_kpis(conn)
print(f"      DONE — {k:,} rows")

print("[4/6] Stock & index price generation...")
p = ingest_market_prices(conn)
print(f"      DONE — {p:,} rows")

print("[5/6] Macro indicators...")
m = ingest_macro(conn)
print(f"      DONE — {m:,} rows")

print("[6/6] Quality audit...")
a = run_quality_suite(conn)
conn.close()
print(f"      DONE — {a['passed']}/{a['total']} checks passed\n")

# Verify key SQL views
import sqlite3
vconn = sqlite3.connect(WORK_DIR / "db" / "bank.db")
for view in ["v_kpi_wide", "v_kpi_growth", "v_peer_rank", "v_profit_bridge", "v_macro_context", "v_relative_strength"]:
    cnt = vconn.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]
    print(f"  {view}: {cnt} rows")

print(f"\n  DB built at: {WORK_DIR / 'db' / 'bank.db'}")
vconn.close()
print("\n  ALL GOOD — Run build_and_run.py to launch dashboard!")

