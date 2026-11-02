"""
build_and_run.py - Master build script that:
1. Copies all project source files to the scratch directory  
2. Runs the full ETL pipeline to build db/bank.db
3. Launches the Streamlit dashboard

Run this from the project root with:
  C:\ProgramData\anaconda3\python.exe build_and_run.py
"""

import sys
import os
import shutil
import sqlite3
import subprocess
from pathlib import Path

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
SRC_ROOT = Path(r"C:\Users\User\OneDrive\Desktop\data analyst")
SCRATCH   = Path(r"C:\Users\User\.gemini\antigravity\brain\39512d4c-8a7a-4d11-8095-65c5b82b00cd\scratch")
WORK_DIR  = SCRATCH / "icici_dashboard"
DB_DIR    = WORK_DIR / "db"
DB_PATH   = DB_DIR / "bank.db"

print("=" * 65)
print("  ICICI Bank Performance Intelligence — Build & Run")
print("=" * 65)

# ─────────────────────────────────────────────
# STEP 0: Copy source tree to writable location
# ─────────────────────────────────────────────
print(f"\n[0/6] Staging project to writable workspace: {WORK_DIR}")
if WORK_DIR.exists():
    shutil.rmtree(WORK_DIR, ignore_errors=True)
WORK_DIR.mkdir(parents=True, exist_ok=True)

DIRS_TO_COPY = ["sql", "src", "dashboard", "docs", "config.yaml", ".env.example"]
for item in DIRS_TO_COPY:
    src = SRC_ROOT / item
    dst = WORK_DIR / item
    try:
        if src.is_dir():
            shutil.copytree(src, dst)
        elif src.is_file():
            shutil.copy2(src, dst)
    except PermissionError:
        print(f"   Skipped (permission): {item}")

DB_DIR.mkdir(parents=True, exist_ok=True)
(WORK_DIR / "data" / "manual").mkdir(parents=True, exist_ok=True)
(WORK_DIR / "data" / "raw").mkdir(parents=True, exist_ok=True)
(WORK_DIR / "docs").mkdir(parents=True, exist_ok=True)

# Add WORK_DIR to sys.path so all imports resolve
sys.path.insert(0, str(WORK_DIR))
os.chdir(WORK_DIR)
print(f"   Working directory: {os.getcwd()}")

# ─────────────────────────────────────────────
# STEP 1 – 6: Run the pipeline inline
# ─────────────────────────────────────────────
from src.db import get_sqlite_connection, init_schema, log_etl_step
from src.ingest.bank_kpis import ingest_companies_and_periods, ingest_bank_kpis, generate_manual_kpi_template
from src.ingest.prices import ingest_market_prices
from src.ingest.macro import ingest_macro
from src.quality.checks import run_quality_suite

import uuid
from datetime import datetime
run_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

print(f"\n[1/6] Initializing database schema + 15 analytical views ...")
init_schema()
print("      ✓ Schema, indexes and views created")

conn = get_sqlite_connection()

print(f"\n[2/6] Loading dimension tables (Companies, Periods, Metrics) ...")
ingest_companies_and_periods(conn)
tpl = generate_manual_kpi_template()
print(f"      ✓ Dimensions loaded | Template → {tpl}")

print(f"\n[3/6] Ingesting 14-quarter banking KPIs (5 institutions, 17 metrics each) ...")
kpi_rows = ingest_bank_kpis(conn)
print(f"      ✓ {kpi_rows:,} KPI data points written")

print(f"\n[4/6] Generating ~880-day daily price series + computing risk statistics ...")
price_rows = ingest_market_prices(conn)
print(f"      ✓ {price_rows:,} daily price rows + Beta/Sharpe/Drawdown stats computed")

print(f"\n[5/6] Loading macroeconomic indicators (RBI Repo, GDP, CPI) ...")
macro_rows = ingest_macro(conn)
print(f"      ✓ {macro_rows:,} macro observations written")

print(f"\n[6/6] Running 10-check automated data quality audit ...")
audit = run_quality_suite(conn)
print(f"      ✓ {audit['passed']}/{audit['total']} tests passed | {audit['warnings']} warnings | {audit['failures']} failures")
print(f"      Report → {WORK_DIR / 'docs' / 'quality_report.md'}")

conn.close()

# ─────────────────────────────────────────────
# LAUNCH STREAMLIT
# ─────────────────────────────────────────────
print(f"\n{'=' * 65}")
print("  Pipeline Complete! Database ready at:")
print(f"    {DB_PATH}")
print(f"\n  Launching Streamlit dashboard on http://localhost:8501 ...")
print(f"{'=' * 65}\n")

app_path = WORK_DIR / "dashboard" / "app.py"
subprocess.run([
    r"C:\ProgramData\anaconda3\python.exe", "-m", "streamlit", "run",
    str(app_path),
    "--server.port=8501",
    "--server.headless=true",
    f"--server.fileWatcherType=none",
    "--browser.gatherUsageStats=false"
])

