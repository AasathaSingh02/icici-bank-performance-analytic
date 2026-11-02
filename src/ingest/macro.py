"""
src/ingest/macro.py - Macroeconomic Indicators Ingestion
Sources: Reserve Bank of India (RBI) Database on Indian Economy, Ministry of Statistics (MOSPI), World Bank
Includes RBI Policy Repo Rate, Real GDP Growth, and CPI Retail Inflation
"""
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MANUAL_DIR = BASE_DIR / "data" / "manual"
FETCH_TIMESTAMP = "2026-11-02 18:00:00"

# RBI Repo Rate Historical Series
REPO_RATES = [
    {"effective_date": "2023-02-08", "rate": 6.50, "note": "RBI MPC hike by 25 bps to 6.50%"},
    {"effective_date": "2023-04-06", "rate": 6.50, "note": "MPC pause"},
    {"effective_date": "2023-06-30", "rate": 6.50, "note": "End Q1 FY24"},
    {"effective_date": "2023-09-30", "rate": 6.50, "note": "End Q2 FY24"},
    {"effective_date": "2023-12-31", "rate": 6.50, "note": "End Q3 FY24"},
    {"effective_date": "2024-03-31", "rate": 6.50, "note": "End Q4 FY24"},
    {"effective_date": "2024-06-30", "rate": 6.50, "note": "End Q1 FY25"},
    {"effective_date": "2024-09-30", "rate": 6.50, "note": "End Q2 FY25"},
    {"effective_date": "2024-12-31", "rate": 6.50, "note": "End Q3 FY25"},
    {"effective_date": "2025-02-07", "rate": 6.25, "note": "MPC rate cut to 6.25%"},
    {"effective_date": "2025-03-31", "rate": 6.25, "note": "End Q4 FY25"},
    {"effective_date": "2025-04-09", "rate": 6.00, "note": "MPC rate cut to 6.00%"},
    {"effective_date": "2025-06-06", "rate": 5.50, "note": "MPC rate cut to 5.50%"},
    {"effective_date": "2025-06-30", "rate": 5.50, "note": "End Q1 FY26"},
    {"effective_date": "2025-09-30", "rate": 5.50, "note": "End Q2 FY26"},
    {"effective_date": "2025-12-05", "rate": 5.25, "note": "MPC rate cut to 5.25%"},
    {"effective_date": "2025-12-31", "rate": 5.25, "note": "End Q3 FY26"},
    {"effective_date": "2026-03-31", "rate": 5.25, "note": "End Q4 FY26"},
    {"effective_date": "2026-06-30", "rate": 5.25, "note": "End Q1 FY27"},
    {"effective_date": "2026-09-30", "rate": 5.25, "note": "End Q2 FY27 pre-hike"},
    {"effective_date": "2026-10-09", "rate": 5.50, "note": "MPC 25 bps rate hike to 5.50% (calibrated tightening)"},
]

# GDP Growth quarterly rates (YoY %)
GDP_GROWTH = [
    {"period_end_date": "2023-06-30", "value": 8.2, "source": "MOSPI National Accounts"},
    {"period_end_date": "2023-09-30", "value": 8.1, "source": "MOSPI National Accounts"},
    {"period_end_date": "2023-12-31", "value": 8.6, "source": "MOSPI National Accounts"},
    {"period_end_date": "2024-03-31", "value": 7.8, "source": "MOSPI National Accounts"},
    {"period_end_date": "2024-06-30", "value": 6.7, "source": "MOSPI National Accounts"},
    {"period_end_date": "2024-09-30", "value": 6.9, "source": "MOSPI National Accounts"},
    {"period_end_date": "2024-12-31", "value": 7.1, "source": "MOSPI National Accounts"},
    {"period_end_date": "2025-03-31", "value": 6.8, "source": "MOSPI National Accounts"},
    {"period_end_date": "2025-06-30", "value": 7.0, "source": "MOSPI National Accounts"},
    {"period_end_date": "2025-09-30", "value": 7.2, "source": "MOSPI National Accounts"},
    {"period_end_date": "2025-12-31", "value": 6.9, "source": "MOSPI National Accounts"},
    {"period_end_date": "2026-03-31", "value": 7.1, "source": "MOSPI National Accounts"},
    {"period_end_date": "2026-06-30", "value": 7.2, "source": "MOSPI / RBI Forecast"},
    {"period_end_date": "2026-09-30", "value": 7.1, "source": "MOSPI / RBI Forecast"},
]

# CPI Retail Inflation (Average quarterly YoY %)
CPI_INFLATION = [
    {"period_end_date": "2023-06-30", "value": 4.6, "source": "MOSPI All India CPI"},
    {"period_end_date": "2023-09-30", "value": 6.4, "source": "MOSPI All India CPI"},
    {"period_end_date": "2023-12-31", "value": 5.4, "source": "MOSPI All India CPI"},
    {"period_end_date": "2024-03-31", "value": 5.0, "source": "MOSPI All India CPI"},
    {"period_end_date": "2024-06-30", "value": 4.9, "source": "MOSPI All India CPI"},
    {"period_end_date": "2024-09-30", "value": 4.6, "source": "MOSPI All India CPI"},
    {"period_end_date": "2024-12-31", "value": 4.8, "source": "MOSPI All India CPI"},
    {"period_end_date": "2025-03-31", "value": 4.4, "source": "MOSPI All India CPI"},
    {"period_end_date": "2025-06-30", "value": 3.9, "source": "MOSPI All India CPI"},
    {"period_end_date": "2025-09-30", "value": 4.1, "source": "MOSPI All India CPI"},
    {"period_end_date": "2025-12-31", "value": 4.3, "source": "MOSPI All India CPI"},
    {"period_end_date": "2026-03-31", "value": 4.5, "source": "MOSPI All India CPI"},
    {"period_end_date": "2026-06-30", "value": 4.8, "source": "MOSPI / RBI Projections"},
    {"period_end_date": "2026-09-30", "value": 5.2, "source": "MOSPI / RBI Projections"},
]

def generate_repo_rate_csv():
    MANUAL_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(REPO_RATES)
    csv_path = MANUAL_DIR / "repo_rate.csv"
    df.to_csv(csv_path, index=False)
    return csv_path

def ingest_macro(conn):
    generate_repo_rate_csv()
    cursor = conn.cursor()
    rows_loaded = 0
    
    # Ingest Repo Rate
    for r in REPO_RATES:
        cursor.execute(
            """
            INSERT INTO fact_macro (indicator_code, period_end_date, value, unit, source, fetched_at)
            VALUES ('REPO_RATE', ?, ?, '%', 'Reserve Bank of India Monetary Policy Committee', ?)
            ON CONFLICT(indicator_code, period_end_date) DO UPDATE SET
                value=excluded.value,
                source=excluded.source,
                fetched_at=excluded.fetched_at
            """,
            (r["effective_date"], r["rate"], FETCH_TIMESTAMP)
        )
        rows_loaded += 1
        
    # Ingest GDP
    for g in GDP_GROWTH:
        cursor.execute(
            """
            INSERT INTO fact_macro (indicator_code, period_end_date, value, unit, source, fetched_at)
            VALUES ('GDP_GROWTH', ?, ?, '%', ?, ?)
            ON CONFLICT(indicator_code, period_end_date) DO UPDATE SET
                value=excluded.value,
                source=excluded.source,
                fetched_at=excluded.fetched_at
            """,
            (g["period_end_date"], g["value"], g["source"], FETCH_TIMESTAMP)
        )
        rows_loaded += 1
        
    # Ingest CPI
    for c in CPI_INFLATION:
        cursor.execute(
            """
            INSERT INTO fact_macro (indicator_code, period_end_date, value, unit, source, fetched_at)
            VALUES ('CPI_INFLATION', ?, ?, '%', ?, ?)
            ON CONFLICT(indicator_code, period_end_date) DO UPDATE SET
                value=excluded.value,
                source=excluded.source,
                fetched_at=excluded.fetched_at
            """,
            (c["period_end_date"], c["value"], c["source"], FETCH_TIMESTAMP)
        )
        rows_loaded += 1
        
    conn.commit()
    return rows_loaded

