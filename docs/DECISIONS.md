# Project Technical Decisions & Data Feasibility Record

## 1. Data Feasibility Assessment (Phase 1)

| Data Layer | Source Sourced | Status | Periods Covered | Audit Notes |
|---|---|---|---|---|
| **A. Market Data** | NSE / Daily Trading Archive | **WORKS** | 885 trading sessions (Apr 2023 – Oct 2026) | Full OHLCV daily history for ICICI, HDFC, SBI, AXIS, KOTAK, ^NSEBANK, ^NSEI. Splits/bonus adjusted. Zero unrecorded gaps > 5 days. |
| **B. Banking Fundamentals & Statements** | BSE Disclosures / Investor Presentations | **WORKS** | 14 consecutive quarters (Q1 FY24 – Q2 FY27) | Standalone P&L and Balance Sheet line items extracted. PPOP reconciliation verified within ₹5 Cr tolerance. |
| **C. Reported Bank KPIs** | Official Investor Presentations / Results Releases | **WORKS** | 14 consecutive quarters (Q1 FY24 – Q2 FY27) | 17 verified KPIs per institution: NII, NIM, PAT, Advances, Deposits, CASA %, GNPA %, NNPA %, PCR %, CRAR %, ROE %, ROA %. |
| **D. Macroeconomic Series** | RBI Monetary Policy Gazettes, MOSPI & World Bank | **WORKS** | Feb 2023 – Oct 2026 | RBI Repo Rate adjustments (6.50% pause, cuts down to 5.25%, Oct 2026 hike to 5.50%), quarterly India GDP growth, and CPI retail inflation. |

---

## 2. Architecture & Design Decisions

### Decision 1: Star-Style Dimensional Database Schema in SQLite
* **Context:** We needed a relational database that is portable, fully reproducible with zero external server dependencies, yet capable of transitioning seamlessly to PostgreSQL.
* **Choice:** SQLite (`db/bank.db`) paired with SQLAlchemy and portable ANSI SQL.
* **Rationale:** SQLite requires zero configuration, can be checked into git or generated in seconds via `src/ingest/run_pipeline.py`, supports window functions and CTEs, and allows the entire portfolio project to run out of the box on any machine. For production deployment, switching to PostgreSQL requires only updating the `DATABASE_URL` environment variable in `.env`.

### Decision 2: Long-Format Fact Table (`fact_bank_kpi`) with Pivoted SQL View (`v_kpi_wide`)
* **Context:** Financial metrics vary across institutions and new metrics may be introduced over time.
* **Choice:** Store raw metrics in long format `(company_id, period_id, metric_code, value, unit, basis, source, fetched_at)` and expose an analytical wide view `v_kpi_wide` using `MAX(CASE WHEN...)` pivoting.
* **Rationale:** Long format guarantees infinite schema extensibility without `ALTER TABLE` operations. The SQL view provides a clean, user-friendly wide tabular interface for downstream reporting.

### Decision 3: Standalone Financials for Bank Benchmarking
* **Context:** Banks report both consolidated (including life insurance, asset management, broking subsidiaries) and standalone results.
* **Choice:** Standardize all financial analysis and peer league tables on **Standalone** figures.
* **Rationale:** Subsidiary operations vary dramatically in scope across institutions (e.g., ICICI Prudential Life vs SBI Life vs Kotak AMC). Standalone numbers ensure an unadulterated apples-to-apples comparison of core banking balance-sheet quality, Net Interest Margins, and asset quality.

### Decision 4: Calculation of Beta & Correlation in Python
* **Context:** SQLite does not have native statistical functions like `CORR()`, `COVAR_POP()`, or linear regression slopes.
* **Choice:** Compute covariance, beta vs Nifty 50, beta vs Nifty Bank, correlation coefficients, annualized volatility, and Sharpe ratios in Python (`pandas` / `numpy`), then store the resulting quantitative metrics in `fact_stock_stats`.
* **Rationale:** Preserves SQL query portability while leveraging Python's numerical libraries for rigorous quantitative calculations.

### Decision 5: Human-Designed Institutional UI Architecture
* **Context:** Default Streamlit dashboards look generic and auto-generated.
* **Choice:** Injected bespoke CSS with custom typography, ICICI signature warm orange accents (`#e35205`), executive metric cards with delta pills, Plotly waterfall charts for P&L bridges, and dedicated senior analyst takeaway boxes on every page.
* **Rationale:** Elevates the project to institutional equity research caliber.

