# Company Performance Dashboard — ICICI Bank
### Implementation plan for the coding agent

You are building an end-to-end data analyst portfolio project: a clean, interactive business performance dashboard for **ICICI Bank**, backed by a SQL database, fed by real APIs/public data, and driven by SQL analytics. Work autonomously through the phases below, in order. Commit after each phase. Do not skip the acceptance checks.

---

## 0. Ground rules (read first, apply throughout)

1. **Never fabricate data.** Every number in the database and dashboard must come from a real source and carry a `source` and `fetched_at` value. If a required figure cannot be obtained automatically, create a clearly labelled CSV template in `data/manual/` with the exact columns needed, mark the affected dashboard section "awaiting data", and list it in `docs/DATA_GAPS.md`. Do not invent placeholder or "sample" numbers unless the user explicitly approves, and if you do, label them SAMPLE in the UI.
2. **Verify before you build.** Phase 1 is a data-feasibility check. Do not assume any API, URL, or library field exists; test it and record what actually worked.
3. **Reproducible and idempotent.** One command rebuilds everything from scratch (`make all`). Re-running the pipeline must not duplicate rows.
4. **Config-driven.** Company, peers, tickers, date ranges, and KPI definitions live in `config.yaml`, so the project can be switched to another company by editing config (plus the KPI mapping).
5. **No secrets in git.** API keys go in `.env` (gitignored); provide `.env.example`.
6. **Explain your work.** Keep `docs/DECISIONS.md` (choices + reasons) and `docs/DATA_GAPS.md` (what could not be sourced).
7. **Tell the user** at the end what was verified, what failed, and what needs manual input.

---

## 1. Project goals and scope

**Goal:** present ICICI Bank's performance (profitability, asset quality, growth, valuation/stock behaviour) against peers and macro context, with interactive filters and written insights.

**Skills the project must demonstrate:** data exploration (EDA), database design and management, API integration, SQL analytics (CTEs, window functions, views), dashboard development, data quality checks, and insight communication.

**Peers:** HDFC Bank, State Bank of India, Axis Bank, Kotak Mahindra Bank. **Benchmarks:** Nifty 50, Nifty Bank.

**Why banking KPIs, not revenue/COGS:** for a bank the meaningful metrics are NII, NIM, ROA/ROE, GNPA/NNPA, CASA, CRAR, cost-to-income, advances and deposits. Do not force an industrial-company framework onto it.

**Conventions to apply and document:**
- Indian fiscal year runs April–March. FY26 = Apr 2025 – Mar 2026. Q1 = Apr–Jun, Q2 = Jul–Sep, Q3 = Oct–Dec, Q4 = Jan–Mar. Store both `fiscal_year`/`fiscal_quarter` and the calendar `period_end_date`.
- Use **standalone** results for bank-level KPIs and peer comparison, since consolidated figures differ in scope across banks. Note this in the dashboard footer.
- Monetary amounts in ₹ crore. Percentages stored as numbers (e.g. 4.32 meaning 4.32%), not strings.
- The current date is early November 2026, so the latest reported quarter should be Q2 FY27 (Jul–Sep 2026) if results are out. Confirm the latest available quarter during Phase 1 rather than assuming.

---

## 2. Tech stack

| Layer | Choice | Notes |
|---|---|---|
| Language | Python 3.11+ | |
| Data ingestion | `yfinance`, `requests`, `pandas` | Plus `pdfplumber` or `camelot` only if parsing result PDFs is needed |
| Database | **SQLite** by default (file `db/bank.db`) | Write portable ANSI SQL; connection via SQLAlchemy using `DATABASE_URL`, so PostgreSQL works by changing one env var. Provide an optional `docker-compose.yml` for PostgreSQL as a stretch goal |
| Transformation | SQL views + small Python helpers | Keep business logic in SQL files so it is reviewable |
| Dashboard | **Streamlit + Plotly** | Deployable free on Streamlit Community Cloud; commit a small read-only DB snapshot for deployment |
| Quality | `pytest`, `pandera` or custom checks, `ruff` | |
| Orchestration | `Makefile` | `make setup`, `make ingest`, `make build`, `make test`, `make dashboard`, `make all` |

Pin all versions in `requirements.txt`.

---

## 3. Repository structure

```
icici-performance-dashboard/
├── README.md
├── PROJECT_PLAN.md            # this file
├── Makefile
├── config.yaml
├── .env.example
├── requirements.txt
├── data/
│   ├── raw/                   # untouched downloads (gitignored if large)
│   ├── manual/                # CSV templates for anything not auto-sourced
│   └── processed/
├── db/
│   └── bank.db                # generated
├── sql/
│   ├── 01_schema.sql
│   ├── 02_indexes.sql
│   ├── 03_views_kpi.sql
│   ├── 04_views_stock.sql
│   ├── 05_views_peer.sql
│   └── 06_analysis_queries.sql   # the showcase SQL, each query commented
├── src/
│   ├── config.py
│   ├── ingest/
│   │   ├── prices.py          # yfinance daily prices
│   │   ├── fundamentals.py    # yfinance financial statements
│   │   ├── bank_kpis.py       # reported bank KPIs (see Phase 1/2)
│   │   └── macro.py           # World Bank API + manual repo rate
│   ├── transform/
│   ├── quality/checks.py
│   └── db.py
├── notebooks/
│   └── 01_eda.ipynb           # exploration + findings
├── dashboard/
│   ├── app.py
│   ├── pages/
│   └── components/
├── tests/
├── docs/
│   ├── DECISIONS.md
│   ├── DATA_GAPS.md
│   ├── DATA_DICTIONARY.md
│   ├── KPI_DEFINITIONS.md
│   └── screenshots/
└── .github/workflows/ci.yml   # optional: lint + tests
```

---

## 4. Phases

### Phase 1 — Data feasibility check and exploration (do this before any build)

Test each source below, record the outcome (works / partial / fails, and how many periods of history) in `docs/DECISIONS.md`.

**A. Market data (yfinance).** Tickers: `ICICIBANK.NS`, `HDFCBANK.NS`, `SBIN.NS`, `AXISBANK.NS`, `KOTAKBANK.NS`; indices `^NSEI` (Nifty 50) and `^NSEBANK` (Nifty Bank). Pull max available daily OHLCV history. Handle splits/bonus adjustments (use adjusted close for returns) and note any gaps.

**B. Fundamentals (yfinance).** Try `.financials`, `.quarterly_financials`, `.balance_sheet`, `.quarterly_balance_sheet`, `.info`. Expect limited history and inconsistent line items for banks. Record exactly which fields exist.

**C. Reported bank KPIs (the important one).** Bank-specific KPIs (NIM, GNPA, NNPA, PCR, CASA, CRAR, cost-to-income) are usually **not** in yfinance. Check, in this order:
1. ICICI Bank's investor relations pages for quarterly results, press releases, and investor presentations or financial summaries (downloadable PDF/Excel).
2. The stock exchange filings (NSE/BSE corporate announcements) for the same results.
3. Aggregator sites only as a cross-check, and only if their terms allow automated access; do not scrape sites that prohibit it.

Aim for at least 12 consecutive quarters for ICICI and, where feasible, the four peers. If automatic extraction is unreliable, generate `data/manual/bank_kpis_template.csv` with these columns and populate whatever can be reliably extracted:

`bank, fiscal_year, fiscal_quarter, period_end_date, nii_cr, other_income_cr, opex_cr, pre_provision_profit_cr, provisions_cr, pat_cr, advances_cr, deposits_cr, casa_ratio_pct, nim_pct, gnpa_pct, nnpa_pct, pcr_pct, crar_pct, cost_to_income_pct, roa_pct, roe_pct, basis, source_url, fetched_at`

**D. Macro APIs.**
- World Bank API (no key): `https://api.worldbank.org/v2/country/IND/indicator/NY.GDP.MKTP.KD.ZG?format=json` (GDP growth) and `FP.CPI.TOTL.ZG` (CPI inflation). Annual data.
- RBI repo rate history: check for an official downloadable series; otherwise create `data/manual/repo_rate.csv` (`effective_date, repo_rate_pct, source_url`).

**E. Exploration notebook** `notebooks/01_eda.ipynb`: shapes, date ranges, missing values, duplicates, outliers, units, and early plots of price and any KPI series. Summarise what you learned in the notebook's first cell.

**Decision gate:** If ICICI Bank's reported KPI history cannot be assembled to at least ~8 quarters even with manual templates, stop and tell the user. Propose a fallback company with better automated coverage (config-driven design makes the swap cheap) rather than building on thin data.

**Acceptance:** `docs/DECISIONS.md` has a data-source table with status for A–D; EDA notebook runs top to bottom.

---

### Phase 2 — Database design and ingestion

**Schema (star-style, in `sql/01_schema.sql`):**

- `dim_company(company_id PK, name, ticker, sector, is_primary, is_peer)`
- `dim_date(date_id PK, date, year, month, quarter, fiscal_year, fiscal_quarter, is_quarter_end)`
- `dim_period(period_id PK, fiscal_year, fiscal_quarter, period_end_date, period_type)` — `period_type` is `Q` or `FY`
- `fact_stock_price(company_id FK, date, open, high, low, close, adj_close, volume)` — PK `(company_id, date)`
- `fact_index_price(index_code, date, close)` — PK `(index_code, date)`
- `fact_bank_kpi(company_id FK, period_id FK, metric_code, value, unit, basis, source, fetched_at)` — PK `(company_id, period_id, metric_code, basis)`. Long format keeps it extensible.
- `dim_metric(metric_code PK, display_name, unit, higher_is_better, category, definition)`
- `fact_fundamentals(company_id, period_id, line_item, value, source, fetched_at)`
- `fact_macro(indicator_code, period_end_date, value, unit, source, fetched_at)`
- `etl_log(run_id, step, status, rows_loaded, started_at, finished_at, message)`

Add primary/foreign keys, `NOT NULL` where sensible, `CHECK` constraints (e.g. percentages in a plausible range, volume ≥ 0), and indexes on all join/filter columns (`sql/02_indexes.sql`).

**Ingestion requirements:**
- Upsert on natural keys; re-running changes nothing if the source data is unchanged.
- Retry with backoff on API failures; log each step to `etl_log`.
- Save raw responses/files to `data/raw/` with timestamps before transforming.
- Populate `dim_date` and `dim_period` programmatically.

**Acceptance:** `make ingest` runs twice with identical row counts; foreign keys have no orphans; `etl_log` shows each step.

---

### Phase 3 — Data quality layer

`src/quality/checks.py`, run by `make test` and at the end of ingestion. Fail loudly on errors and warn on soft issues:

- No duplicate PKs; no future-dated rows; no negative prices/volumes.
- Trading-day gaps longer than 5 days flagged.
- Single-day price move over 20% flagged for review (could be a corporate action, not an error).
- KPI sanity ranges (e.g. NNPA ≤ GNPA; CASA, NIM, CRAR in plausible bounds).
- Balance-sheet and P&L reconciliation where data allows (e.g. PPOP = NII + other income − opex, within tolerance).
- Period continuity: no missing quarters between first and last for each bank/metric (report gaps).
- Cross-check: at least 3 ICICI KPI values spot-verified against the original source document, recorded in `docs/DATA_DICTIONARY.md`.

**Acceptance:** a quality report (`docs/quality_report.md`) is generated each run.

---

### Phase 4 — SQL analytics layer

Create views in `sql/03–05` and a showcase file `sql/06_analysis_queries.sql`. Every query gets a header comment: business question, technique used, how to read the result. Use CTEs and window functions. Portable SQL only.

**KPI views**
1. `v_kpi_wide` — pivot long KPI table into one row per bank per quarter.
2. `v_kpi_growth` — QoQ and YoY change for NII, PAT, advances, deposits using `LAG`.
3. `v_credit_deposit_ratio` — advances ÷ deposits per quarter.
4. `v_profit_bridge` — NII + other income − opex − provisions = PBT trend for ICICI (decomposition of what drives profit change).
5. `v_ttm_metrics` — trailing-four-quarter sums for PAT, NII; rolling averages for ratios.

**Peer views**
6. `v_peer_rank` — `RANK()` of each bank per metric per quarter.
7. `v_peer_vs_icici_gap` — ICICI minus peer-average for NIM, GNPA, ROE, CASA.
8. `v_peer_quartile` — `NTILE(4)` position of ICICI per metric.

**Stock views**
9. `v_daily_returns` — daily log return per ticker.
10. `v_rolling_vol_30d` — 30-day rolling volatility (window function over returns).
11. `v_drawdown` — running max and drawdown from peak.
12. `v_relative_strength` — ICICI cumulative return vs Nifty Bank and Nifty 50, rebased to 100.
13. `v_monthly_returns` — calendar-month return table (for heatmap).
14. `v_valuation` — price-to-book and price-to-earnings at each quarter-end, using TTM EPS and book value per share where data permits.
15. `v_price_vs_kpi` — join quarter-end price change with that quarter's results (supports "does the market react to NPA changes?").

**Macro**
16. `v_macro_context` — align repo rate, GDP growth, inflation with bank KPIs by period.

Beta and correlation: compute in Python (pandas) and store results in a `fact_stock_stats` table, since SQLite lacks `CORR`. Document that choice.

**Acceptance:** each view returns rows; `tests/test_sql_views.py` asserts key invariants (e.g. YoY growth for a hand-checked quarter matches a manual calculation).

---

### Phase 5 — Dashboard (Streamlit + Plotly)

Clean, minimal design: consistent palette (use ICICI-style orange/maroon accents sparingly, neutral greys otherwise), one font, generous whitespace, mobile-tolerant layout, dark/light safe colours. Every chart has a title, axis units, and hover tooltips. Every page ends with a "So what?" box containing 2–3 insights **written from the actual data** (not template text).

**Global sidebar filters:** company (primary fixed to ICICI, peers multi-select), date range, period granularity (quarterly / fiscal year), basis (standalone). Filters must apply across all pages and be kept in session state.

**Pages**

1. **Executive Overview** — KPI cards for latest quarter: PAT, NII, NIM, GNPA, ROE, CASA, each with QoQ and YoY deltas (green/red arrows respecting `higher_is_better`). Below: PAT and NII trend, plus a compact stock price sparkline.
2. **Profitability** — NII and other income stacked, NIM trend, ROA/ROE, cost-to-income, profit-bridge waterfall (Plotly waterfall) for a selectable quarter.
3. **Asset Quality** — GNPA/NNPA trend, PCR, provisions as % of PPOP, with peer overlay.
4. **Growth & Balance Sheet** — advances, deposits, CASA, credit-deposit ratio; YoY growth bars.
5. **Stock & Valuation** — price vs Nifty Bank (rebased), rolling volatility, drawdown chart, monthly returns heatmap, beta, P/B and P/E band.
6. **Peer Benchmarking** — radar or grouped bars on selected metrics, ranking table with conditional colouring, ICICI-vs-peer-average gap chart.
7. **Macro Context** — repo rate, GDP, inflation lined up with NIM and credit growth; short commentary on what the data does and does not show (avoid claiming causation).
8. **Insights & Methodology** — the written key findings (5–8 bullets with numbers), KPI definitions, data sources with fetch dates, data-quality summary, known limitations.

**Quality of life:** `st.cache_data` for queries with TTL; "Download CSV" on every table; a "Data last refreshed" stamp in the footer; graceful empty-state messages for sections flagged in `DATA_GAPS.md`.

**Acceptance:** `make dashboard` launches with no errors; all filters work; no page shows raw tracebacks; screenshots of every page saved to `docs/screenshots/`.

---

### Phase 6 — Insights (the part that gets you hired)

After the data is final, analyse it and write real findings in `docs/INSIGHTS.md` and the Insights page. Answer, with numbers and charts:

1. How have ICICI's NIM, ROE and PAT growth evolved over the available quarters, and what drove the change (use the profit bridge)?
2. How did asset quality (GNPA/NNPA/PCR) change, and how does it compare to peers?
3. Is ICICI's growth in advances outpacing deposits, and what happened to the credit-deposit ratio?
4. Where does ICICI rank among peers on profitability vs asset quality vs growth?
5. How has the stock performed vs Nifty Bank, and in which periods did it lag or lead? What was the worst drawdown and how long was recovery?
6. Do valuation multiples (P/B) track ROE across the peer set?
7. Any visible relationship between rate-cycle changes and NIM? State limits of the evidence.

Rules: every claim cites the figure and period; separate observation from interpretation; no investment advice; add a plain disclaimer that this is an educational analysis.

---

### Phase 7 — Testing, documentation, deployment

**Tests (`pytest`):** ingestion idempotency, schema constraints, SQL view invariants, KPI calculation unit tests, quality-check functions. CI workflow runs lint + tests.

**README must include:** one-paragraph project summary, screenshot/GIF, architecture diagram (a simple ASCII or Mermaid flow: Sources → Ingest → SQLite → SQL views → Streamlit), setup in under 5 commands, data sources and their licences/terms, schema diagram, list of SQL techniques used, key insights summary, limitations, and "how to switch company."

**Deployment:** deploy to Streamlit Community Cloud using a committed read-only DB snapshot (or parquet exports) so the public app does not need live ingestion. Put the live link in the README.

**Optional exports for BI-tool fluency:** `make export` writes the main views to `exports/*.csv` so the same analysis can be rebuilt in Power BI or Tableau.

---

## 5. Definition of done

- [ ] `make all` builds the DB, runs quality checks, and starts the dashboard from a clean clone
- [ ] Every figure traceable to a source with fetch date
- [ ] At least 8 consecutive quarters of ICICI bank KPIs (target 12+), with peer coverage documented
- [ ] 15+ documented SQL views/queries using CTEs and window functions
- [ ] All 8 dashboard pages working with global filters
- [ ] Written insights based on real data
- [ ] Tests pass; quality report generated
- [ ] README, DECISIONS, DATA_GAPS, DATA_DICTIONARY, KPI_DEFINITIONS complete
- [ ] Deployed app link (or clear instructions if deployment needs the user's account)

## 6. Stretch goals (only after everything above is done)

- PostgreSQL via Docker with the same SQL
- Scheduled monthly refresh (GitHub Actions cron)
- Simple forecast of PAT or NII (seasonal naive baseline vs ETS) with honest error metrics
- Power BI / Tableau version of the Executive Overview from the CSV exports
- Quarterly-results sentiment: compare management commentary themes across quarters (only from official published documents)

## 7. Final report the agent must give the user

1. What was built and how to run it
2. Data-source status table (worked / partial / manual)
3. Anything the user must supply or verify manually
4. Three insights from the data
5. Known limitations and suggested next steps
