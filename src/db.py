"""
src/db.py - Database connection and execution utilities
Supports SQLite (file db/bank.db) and PostgreSQL via DATABASE_URL
"""
import os
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "db"
DB_PATH = DB_DIR / "bank.db"
SQL_DIR = BASE_DIR / "sql"

def get_database_url():
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{DB_PATH.as_posix()}"

def get_sqlite_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def get_engine():
    db_url = get_database_url()
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    return create_engine(db_url, connect_args=connect_args)

def execute_sql_file(file_path):
    path = Path(file_path)
    if not path.is_absolute():
        path = SQL_DIR / file_path
    
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")

    sql_script = path.read_text(encoding="utf-8")
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()
    finally:
        conn.close()

def init_schema():
    """Initializes tables, indexes, and analytical views in order"""
    sql_files = [
        "01_schema.sql",
        "02_indexes.sql",
        "03_views_kpi.sql",
        "04_views_stock.sql",
        "05_views_peer.sql"
    ]
    for sql_file in sql_files:
        execute_sql_file(sql_file)

def log_etl_step(run_id, step, status, rows_loaded, started_at, finished_at, message=""):
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO etl_log (run_id, step, status, rows_loaded, started_at, finished_at, message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, step, status, rows_loaded, started_at, finished_at, message)
        )
        conn.commit()
    finally:
        conn.close()

