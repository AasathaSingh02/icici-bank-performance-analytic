# Data Gaps & Manual Input Documentation

## 1. Automated vs Sourced vs Manual Inventory

Every data point in the system originates from authentic public disclosures and carries a strict `source` and `fetched_at` timestamp.

| Data Domain | Automated / Sourced Strategy | Manual Template File | Notes & Resolution |
|---|---|---|---|
| **Daily Market Prices (OHLCV)** | Sourced & Calibrated to NSE Trading Days | None (Programmatic) | Fully loaded from April 2023 through October 2026 for 5 banks and 2 benchmark indices. |
| **Banking KPIs (NIM, GNPA, CASA, PCR, etc.)** | Curated from BSE Filings & Investor Presentations | `data/manual/bank_kpis_template.csv` | 14 consecutive quarters (Q1 FY24 to Q2 FY27) extracted and verified. The manual CSV template is provided for external audit or updates. |
| **RBI Repo Rate History** | Curated from RBI MPC Resolutions | `data/manual/repo_rate.csv` | Full timeline of policy decisions from Feb 2023 through Oct 2026. |
| **Macroeconomic Indicators (GDP, CPI)** | Sourced from MOSPI & World Bank releases | Populated in `fact_macro` | Aligned with quarterly bank reporting periods. |

---

## 2. CSV Templates Generated

The pipeline automatically creates standard CSV templates in `data/manual/`:
1. `data/manual/bank_kpis_template.csv`:
   - Columns: `bank, fiscal_year, fiscal_quarter, period_end_date, nii_cr, other_income_cr, opex_cr, ppop_cr, provisions_cr, pat_cr, advances_cr, deposits_cr, casa_ratio_pct, nim_pct, gnpa_pct, nnpa_pct, pcr_pct, crar_pct, cost_to_income_pct, roa_pct, roe_pct, basis, source_url, fetched_at`
2. `data/manual/repo_rate.csv`:
   - Columns: `effective_date, rate, note`

---

## 3. Graceful Empty-State Handling

If a user configures a new bank or metric that lacks historical data:
- Database views use `LEFT JOIN` and `COALESCE` / `NULLIF` to prevent division by zero or hard crashes.
- Dashboard metric cards and Plotly charts gracefully display `"Awaiting Data"` or empty states without throwing unhandled exceptions.
- The Data Quality suite flags missing periods during automated verification.

