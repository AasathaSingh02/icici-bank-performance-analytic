"""
src/ingest/run_pipeline.py - Master Pipeline Orchestrator
Executes end-to-end data ingestion, star-schema creation, view initialization, and quality auditing.
Can be executed repeatedly without duplicating rows (fully idempotent upsert logic).
"""
import uuid
from datetime import datetime
from pathlib import Path
from src.db import get_sqlite_connection, init_schema, log_etl_step
from src.ingest.bank_kpis import (
    ingest_companies_and_periods,
    ingest_bank_kpis,
    generate_manual_kpi_template
)
from src.ingest.prices import ingest_market_prices
from src.ingest.macro import ingest_macro
from src.quality.checks import run_quality_suite

def run_pipeline():
    run_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    print(f"=== Starting Bank Performance Analytics Pipeline [{run_id}] ===")
    
    # Step 1: Initialize Database Schema & Views
    step = "01_init_schema"
    t0 = datetime.now()
    log_etl_step(run_id, step, "STARTED", 0, t0, None, "Executing schema, index, and analytical view creation scripts")
    try:
        init_schema()
        t1 = datetime.now()
        log_etl_step(run_id, step, "SUCCESS", 0, t0, t1, "Schema and all 15 views initialized successfully")
        print(f"[+] Schema, indexes, and analytical views initialized in {(t1 - t0).total_seconds():.2f}s")
    except Exception as e:
        log_etl_step(run_id, step, "FAILED", 0, t0, datetime.now(), str(e))
        raise e

    conn = get_sqlite_connection()
    try:
        # Step 2: Dimensions & Manual Template
        step = "02_dimensions_and_templates"
        t0 = datetime.now()
        log_etl_step(run_id, step, "STARTED", 0, t0, None, "Populating dim_company, dim_period, dim_metric")
        ingest_companies_and_periods(conn)
        generate_manual_kpi_template()
        t1 = datetime.now()
        log_etl_step(run_id, step, "SUCCESS", 5 + 14 + 17, t0, t1, "Dimensions & CSV manual templates ready")
        print(f"[+] Dimensions and manual CSV template ready in {(t1 - t0).total_seconds():.2f}s")

        # Step 3: Ingest Banking KPIs
        step = "03_ingest_bank_kpis"
        t0 = datetime.now()
        log_etl_step(run_id, step, "STARTED", 0, t0, None, "Loading 14 quarters of reported KPIs for ICICI & 4 peers")
        rows = ingest_bank_kpis(conn)
        t1 = datetime.now()
        log_etl_step(run_id, step, "SUCCESS", rows, t0, t1, f"Loaded {rows} KPI metric records across 5 institutions")
        print(f"[+] Ingested {rows} banking KPI data points in {(t1 - t0).total_seconds():.2f}s")

        # Step 4: Ingest Stock & Index Prices
        step = "04_ingest_prices"
        t0 = datetime.now()
        log_etl_step(run_id, step, "STARTED", 0, t0, None, "Generating daily prices & computing market stats")
        p_rows = ingest_market_prices(conn)
        t1 = datetime.now()
        log_etl_step(run_id, step, "SUCCESS", p_rows, t0, t1, f"Loaded {p_rows} daily price rows and computed betas")
        print(f"[+] Ingested {p_rows} stock/index daily prices & stats in {(t1 - t0).total_seconds():.2f}s")

        # Step 5: Ingest Macro Indicators
        step = "05_ingest_macro"
        t0 = datetime.now()
        log_etl_step(run_id, step, "STARTED", 0, t0, None, "Ingesting RBI Repo Rate, GDP, and CPI inflation")
        m_rows = ingest_macro(conn)
        t1 = datetime.now()
        log_etl_step(run_id, step, "SUCCESS", m_rows, t0, t1, f"Loaded {m_rows} macro observations")
        print(f"[+] Ingested {m_rows} macro economic records in {(t1 - t0).total_seconds():.2f}s")

        # Step 6: Data Quality Audit
        step = "06_data_quality_audit"
        t0 = datetime.now()
        log_etl_step(run_id, step, "STARTED", 0, t0, None, "Executing automated quality and accounting audit suite")
        audit_res = run_quality_suite(conn)
        t1 = datetime.now()
        status = "SUCCESS" if audit_res["failures"] == 0 else "WARNING"
        log_etl_step(run_id, step, status, audit_res["passed"], t0, t1, f"{audit_res['passed']}/{audit_res['total']} checks passed")
        print(f"[+] Data Quality Audit completed: {audit_res['passed']}/{audit_res['total']} tests passed (Report: docs/quality_report.md)")

    finally:
        conn.close()

    print(f"=== Pipeline [{run_id}] Finished Successfully ===\n")
    return run_id

if __name__ == "__main__":
    run_pipeline()

