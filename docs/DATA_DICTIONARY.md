# Institutional Data Dictionary

## 1. Relational Database Tables (`db/bank.db`)

### `dim_company`
Dimension holding company profile and classification metadata.
| Column | Type | Constraints | Description | Sample Value |
|---|---|---|---|---|
| `company_id` | INTEGER | PRIMARY KEY | Auto-incrementing identifier | `1` |
| `ticker` | VARCHAR(20) | UNIQUE, NOT NULL | NSE/BSE stock ticker | `'ICICIBANK.NS'` |
| `name` | VARCHAR(100) | NOT NULL | Full corporate legal name | `'ICICI Bank Ltd.'` |
| `short_code` | VARCHAR(20) | UNIQUE, NOT NULL | Common analytical abbreviation | `'ICICI'` |
| `sector` | VARCHAR(50) | NOT NULL | Industry sector | `'Private Bank'` |
| `is_primary` | BOOLEAN | NOT NULL | 1 if focal company, 0 otherwise | `1` |
| `is_peer` | BOOLEAN | NOT NULL | 1 if benchmark peer, 0 otherwise | `0` |

### `dim_period`
Reporting quarter and fiscal year dimension.
| Column | Type | Constraints | Description | Sample Value |
|---|---|---|---|---|
| `period_id` | INTEGER | PRIMARY KEY | Unique period surrogate key | `12` |
| `fiscal_year` | VARCHAR(10) | NOT NULL | Indian fiscal year (Apr–Mar) | `'FY26'` |
| `fiscal_quarter` | VARCHAR(10) | NOT NULL | Fiscal quarter (Q1–Q4) | `'Q4'` |
| `period_end_date` | DATE | NOT NULL | Calendar quarter end date | `'2026-03-31'` |
| `period_label` | VARCHAR(20) | NOT NULL | Standard analytical display label | `'Q4 FY26'` |
| `period_type` | VARCHAR(5) | CHECK IN ('Q', 'FY') | Period granularity | `'Q'` |
| `period_order` | INTEGER | UNIQUE, NOT NULL | Chronological ordering index | `12` |

### `dim_metric`
Master catalogue of banking performance metrics.
| Column | Type | Constraints | Description | Sample Value |
|---|---|---|---|---|
| `metric_code` | VARCHAR(50) | PRIMARY KEY | Standard metric identifier | `'nim_pct'` |
| `display_name` | VARCHAR(100) | NOT NULL | Formatted UI title | `'Net Interest Margin'` |
| `unit` | VARCHAR(20) | NOT NULL | Measurement unit | `'%'` |
| `higher_is_better`| BOOLEAN | NOT NULL | Directional preference for performance | `1` |
| `category` | VARCHAR(50) | NOT NULL | Functional financial pillar | `'Profitability'` |
| `definition` | TEXT | | Mathematical and operational definition | `'Annualised NII / Total Assets'` |

### `fact_bank_kpi`
Long-format normalized banking metric observations.
| Column | Type | Constraints | Description | Sample Value |
|---|---|---|---|---|
| `company_id` | INTEGER | FK -> `dim_company` | Company identifier | `1` |
| `period_id` | INTEGER | FK -> `dim_period` | Reporting period identifier | `12` |
| `metric_code` | VARCHAR(50) | FK -> `dim_metric` | KPI code | `'pat_cr'` |
| `value` | REAL | NOT NULL | Metric quantitative value | `13702.0` |
| `unit` | VARCHAR(20) | NOT NULL | Measurement unit | `'₹ Cr'` |
| `basis` | VARCHAR(20) | DEFAULT 'Standalone' | Accounting consolidation scope | `'Standalone'` |
| `source` | VARCHAR(255) | NOT NULL | Source filing or report | `'ICICI Bank Q4 FY26 Filing'` |
| `fetched_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date and time data was recorded | `'2026-11-02 18:00:00'` |

### `fact_stock_price`
Daily OHLCV trading data.
| Column | Type | Constraints | Description | Sample Value |
|---|---|---|---|---|
| `company_id` | INTEGER | FK -> `dim_company` | Traded company identifier | `1` |
| `date` | DATE | NOT NULL | Trading session date | `'2026-10-30'` |
| `open` | REAL | CHECK >= 0 | Opening price in INR | `1378.50` |
| `high` | REAL | CHECK >= 0 | Intraday high price in INR | `1392.00` |
| `low` | REAL | CHECK >= 0 | Intraday low price in INR | `1372.20` |
| `close` | REAL | CHECK >= 0 | Closing price in INR | `1385.00` |
| `adj_close` | REAL | CHECK >= 0 | Corporate action adjusted close | `1385.00` |
| `volume` | INTEGER | CHECK >= 0 | Trading volume (number of shares) | `8452100` |

---

## 2. Regulatory Spot Verification Table

To verify data fidelity against original regulatory filings, the following values were cross-checked:

| Institution | Period | Metric | Database Value | Official BSE Filing Value | Verification Source Document | Result |
|---|---|---|---|---|---|---|
| **ICICI Bank** | Q4 FY26 | Profit After Tax (PAT) | **₹13,702 Cr** | **₹13,702 Cr** | ICICI Bank Audited Financial Results Q4 FY26, Table 1 | **MATCH (Exact)** |
| **ICICI Bank** | Q4 FY26 | Net Interest Income (NII) | **₹22,979 Cr** | **₹22,979 Cr** | ICICI Bank Investor Presentation Q4 FY26, Slide 6 | **MATCH (Exact)** |
| **ICICI Bank** | Q4 FY26 | Gross NPA Ratio | **1.40%** | **1.40%** | ICICI Bank Performance Review Q4 FY26, Asset Quality Table | **MATCH (Exact)** |
| **ICICI Bank** | Q4 FY24 | Standalone PAT | **₹10,708 Cr** | **₹10,708 Cr** | BSE Corporate Announcement FY24 Financials | **MATCH (Exact)** |

