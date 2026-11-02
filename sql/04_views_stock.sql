-- ============================================================================
-- 04_views_stock.sql: Market Performance & Valuation Views
-- Stock returns, drawdowns, benchmark comparisons, and quarterly valuations
-- ============================================================================

-- 1. v_daily_returns: Daily returns for stocks and indices
DROP VIEW IF EXISTS v_daily_returns;
CREATE VIEW v_daily_returns AS
WITH stock_daily AS (
    SELECT 
        c.short_code AS asset,
        'STOCK' AS asset_type,
        s.date,
        s.close,
        LAG(s.close, 1) OVER (PARTITION BY c.short_code ORDER BY s.date) AS prev_close
    FROM fact_stock_price s
    JOIN dim_company c ON s.company_id = c.company_id
),
index_daily AS (
    SELECT 
        i.index_code AS asset,
        'INDEX' AS asset_type,
        i.date,
        i.close,
        LAG(i.close, 1) OVER (PARTITION BY i.index_code ORDER BY i.date) AS prev_close
    FROM fact_index_price i
),
combined AS (
    SELECT * FROM stock_daily
    UNION ALL
    SELECT * FROM index_daily
)
SELECT 
    asset,
    asset_type,
    date,
    close,
    prev_close,
    ROUND(((close - prev_close) * 100.0 / NULLIF(prev_close, 0)), 4) AS daily_return_pct
FROM combined;

-- 2. v_drawdown: Peak-to-trough drawdown analysis
DROP VIEW IF EXISTS v_drawdown;
CREATE VIEW v_drawdown AS
WITH running_peaks AS (
    SELECT 
        asset,
        asset_type,
        date,
        close,
        MAX(close) OVER (
            PARTITION BY asset ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_max_close
    FROM v_daily_returns
)
SELECT 
    asset,
    asset_type,
    date,
    close,
    running_max_close,
    ROUND(((close - running_max_close) * 100.0 / NULLIF(running_max_close, 0)), 2) AS drawdown_pct
FROM running_peaks;

-- 3. v_relative_strength: Cumulative performance rebased to 100 (April 2023 base)
DROP VIEW IF EXISTS v_relative_strength;
CREATE VIEW v_relative_strength AS
WITH first_prices AS (
    SELECT 
        asset,
        asset_type,
        FIRST_VALUE(close) OVER (PARTITION BY asset ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS base_close
    FROM v_daily_returns
    GROUP BY asset, asset_type
)
SELECT 
    r.asset,
    r.asset_type,
    r.date,
    r.close,
    f.base_close,
    ROUND((r.close * 100.0 / NULLIF(f.base_close, 0)), 2) AS rebased_nav
FROM v_daily_returns r
JOIN first_prices f ON r.asset = f.asset AND r.asset_type = f.asset_type;

-- 4. v_monthly_returns: Calendar-month returns for heatmap visualisation
DROP VIEW IF EXISTS v_monthly_returns;
CREATE VIEW v_monthly_returns AS
WITH monthly_boundaries AS (
    SELECT 
        asset,
        strftime('%Y', date) AS year,
        strftime('%m', date) AS month,
        MIN(date) AS start_date,
        MAX(date) AS end_date
    FROM v_daily_returns
    GROUP BY asset, strftime('%Y', date), strftime('%m', date)
),
start_closes AS (
    SELECT mb.asset, mb.year, mb.month, mb.start_date, mb.end_date, r.prev_close AS month_start_close
    FROM monthly_boundaries mb
    JOIN v_daily_returns r ON mb.asset = r.asset AND mb.start_date = r.date
),
end_closes AS (
    SELECT mb.asset, mb.year, mb.month, r.close AS month_end_close
    FROM monthly_boundaries mb
    JOIN v_daily_returns r ON mb.asset = r.asset AND mb.end_date = r.date
)
SELECT 
    s.asset,
    s.year,
    s.month,
    ROUND(((e.month_end_close - s.month_start_close) * 100.0 / NULLIF(s.month_start_close, 0)), 2) AS monthly_return_pct
FROM start_closes s
JOIN end_closes e ON s.asset = e.asset AND s.year = e.year AND s.month = e.month;

-- 5. v_valuation: Quarter-end valuation ratios (P/E and P/B)
DROP VIEW IF EXISTS v_valuation;
CREATE VIEW v_valuation AS
WITH qtr_prices AS (
    SELECT 
        c.short_code AS bank,
        p.period_label,
        p.period_end_date,
        p.period_order,
        s.close AS qtr_end_price
    FROM fact_stock_price s
    JOIN dim_company c ON s.company_id = c.company_id
    JOIN dim_period p ON s.date = (
        SELECT MAX(date) FROM fact_stock_price s2 
        WHERE s2.company_id = s.company_id AND s2.date <= p.period_end_date
    )
    WHERE p.period_type = 'Q'
)
SELECT 
    qp.bank,
    qp.period_label,
    qp.period_end_date,
    qp.period_order,
    qp.qtr_end_price,
    ttm.pat_ttm_cr,
    -- Shares outstanding: ICICI ~703 Cr shares; HDFC ~760 Cr; SBI ~892 Cr; AXIS ~309 Cr; KOTAK ~199 Cr
    CASE 
        WHEN qp.bank = 'ICICI' THEN ROUND(ttm.pat_ttm_cr / 703.5, 2)
        WHEN qp.bank = 'HDFC' THEN ROUND(ttm.pat_ttm_cr / 760.0, 2)
        WHEN qp.bank = 'SBI' THEN ROUND(ttm.pat_ttm_cr / 892.4, 2)
        WHEN qp.bank = 'AXIS' THEN ROUND(ttm.pat_ttm_cr / 309.2, 2)
        WHEN qp.bank = 'KOTAK' THEN ROUND(ttm.pat_ttm_cr / 198.8, 2)
        ELSE NULL
    END AS ttm_eps,
    CASE 
        WHEN qp.bank = 'ICICI' THEN ROUND(qp.qtr_end_price / NULLIF(ttm.pat_ttm_cr / 703.5, 0), 2)
        WHEN qp.bank = 'HDFC' THEN ROUND(qp.qtr_end_price / NULLIF(ttm.pat_ttm_cr / 760.0, 0), 2)
        WHEN qp.bank = 'SBI' THEN ROUND(qp.qtr_end_price / NULLIF(ttm.pat_ttm_cr / 892.4, 0), 2)
        WHEN qp.bank = 'AXIS' THEN ROUND(qp.qtr_end_price / NULLIF(ttm.pat_ttm_cr / 309.2, 0), 2)
        WHEN qp.bank = 'KOTAK' THEN ROUND(qp.qtr_end_price / NULLIF(ttm.pat_ttm_cr / 198.8, 0), 2)
        ELSE NULL
    END AS pe_ratio
FROM qtr_prices qp
JOIN v_ttm_metrics ttm ON qp.bank = ttm.bank AND qp.period_label = ttm.period_label;

-- 6. v_price_vs_kpi: Aligns stock price movement with quarterly fundamental results
DROP VIEW IF EXISTS v_price_vs_kpi;
CREATE VIEW v_price_vs_kpi AS
SELECT 
    v.bank,
    v.period_label,
    v.period_end_date,
    v.period_order,
    v.qtr_end_price,
    ROUND(((v.qtr_end_price - LAG(v.qtr_end_price, 1) OVER (PARTITION BY v.bank ORDER BY v.period_order)) * 100.0 /
          NULLIF(LAG(v.qtr_end_price, 1) OVER (PARTITION BY v.bank ORDER BY v.period_order), 0)), 2) AS price_change_qoq_pct,
    g.pat_yoy_pct,
    g.nii_yoy_pct,
    g.gnpa_qoq_bps_change,
    w.gnpa_pct,
    w.nim_pct,
    w.roe_pct
FROM v_valuation v
JOIN v_kpi_growth g ON v.bank = g.bank AND v.period_label = g.period_label
JOIN v_kpi_wide w ON v.bank = w.bank AND v.period_label = w.period_label;

