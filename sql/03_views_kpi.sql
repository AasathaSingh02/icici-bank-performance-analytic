-- ============================================================================
-- 03_views_kpi.sql: Banking KPI Analytical Views
-- Uses CTEs, Window Functions (LAG, SUM OVER, AVG OVER), and Pivot logic
-- ============================================================================

-- 1. v_kpi_wide: Wide pivoted quarterly table (1 row per company per quarter)
DROP VIEW IF EXISTS v_kpi_wide;
CREATE VIEW v_kpi_wide AS
SELECT 
    c.company_id,
    c.short_code AS bank,
    c.name AS bank_name,
    c.ticker,
    c.is_primary,
    p.period_id,
    p.fiscal_year,
    p.fiscal_quarter,
    p.period_label,
    p.period_end_date,
    p.period_order,
    MAX(CASE WHEN k.metric_code = 'nii_cr' THEN k.value END) AS nii_cr,
    MAX(CASE WHEN k.metric_code = 'other_income_cr' THEN k.value END) AS other_income_cr,
    MAX(CASE WHEN k.metric_code = 'opex_cr' THEN k.value END) AS opex_cr,
    MAX(CASE WHEN k.metric_code = 'ppop_cr' THEN k.value END) AS ppop_cr,
    MAX(CASE WHEN k.metric_code = 'provisions_cr' THEN k.value END) AS provisions_cr,
    MAX(CASE WHEN k.metric_code = 'pat_cr' THEN k.value END) AS pat_cr,
    MAX(CASE WHEN k.metric_code = 'advances_cr' THEN k.value END) AS advances_cr,
    MAX(CASE WHEN k.metric_code = 'deposits_cr' THEN k.value END) AS deposits_cr,
    MAX(CASE WHEN k.metric_code = 'casa_ratio_pct' THEN k.value END) AS casa_ratio_pct,
    MAX(CASE WHEN k.metric_code = 'nim_pct' THEN k.value END) AS nim_pct,
    MAX(CASE WHEN k.metric_code = 'gnpa_pct' THEN k.value END) AS gnpa_pct,
    MAX(CASE WHEN k.metric_code = 'nnpa_pct' THEN k.value END) AS nnpa_pct,
    MAX(CASE WHEN k.metric_code = 'pcr_pct' THEN k.value END) AS pcr_pct,
    MAX(CASE WHEN k.metric_code = 'crar_pct' THEN k.value END) AS crar_pct,
    MAX(CASE WHEN k.metric_code = 'cost_to_income_pct' THEN k.value END) AS cost_to_income_pct,
    MAX(CASE WHEN k.metric_code = 'roa_pct' THEN k.value END) AS roa_pct,
    MAX(CASE WHEN k.metric_code = 'roe_pct' THEN k.value END) AS roe_pct,
    MAX(k.basis) AS basis,
    MAX(k.source) AS source,
    MAX(k.fetched_at) AS fetched_at
FROM dim_company c
CROSS JOIN dim_period p
LEFT JOIN fact_bank_kpi k 
    ON c.company_id = k.company_id AND p.period_id = k.period_id
WHERE p.period_type = 'Q'
GROUP BY 
    c.company_id, c.short_code, c.name, c.ticker, c.is_primary,
    p.period_id, p.fiscal_year, p.fiscal_quarter, p.period_label, p.period_end_date, p.period_order;

-- 2. v_kpi_growth: Quarter-on-Quarter (QoQ) and Year-on-Year (YoY) Growth using LAG()
DROP VIEW IF EXISTS v_kpi_growth;
CREATE VIEW v_kpi_growth AS
WITH lagged AS (
    SELECT 
        bank,
        period_label,
        period_end_date,
        period_order,
        nii_cr,
        pat_cr,
        advances_cr,
        deposits_cr,
        nim_pct,
        gnpa_pct,
        nnpa_pct,
        -- Prior quarter (QoQ)
        LAG(nii_cr, 1) OVER (PARTITION BY bank ORDER BY period_order) AS nii_lag1,
        LAG(pat_cr, 1) OVER (PARTITION BY bank ORDER BY period_order) AS pat_lag1,
        LAG(advances_cr, 1) OVER (PARTITION BY bank ORDER BY period_order) AS adv_lag1,
        LAG(deposits_cr, 1) OVER (PARTITION BY bank ORDER BY period_order) AS dep_lag1,
        LAG(nim_pct, 1) OVER (PARTITION BY bank ORDER BY period_order) AS nim_lag1,
        LAG(gnpa_pct, 1) OVER (PARTITION BY bank ORDER BY period_order) AS gnpa_lag1,
        -- Prior year same quarter (YoY)
        LAG(nii_cr, 4) OVER (PARTITION BY bank ORDER BY period_order) AS nii_lag4,
        LAG(pat_cr, 4) OVER (PARTITION BY bank ORDER BY period_order) AS pat_lag4,
        LAG(advances_cr, 4) OVER (PARTITION BY bank ORDER BY period_order) AS adv_lag4,
        LAG(deposits_cr, 4) OVER (PARTITION BY bank ORDER BY period_order) AS dep_lag4,
        LAG(nim_pct, 4) OVER (PARTITION BY bank ORDER BY period_order) AS nim_lag4,
        LAG(gnpa_pct, 4) OVER (PARTITION BY bank ORDER BY period_order) AS gnpa_lag4
    FROM v_kpi_wide
)
SELECT 
    bank,
    period_label,
    period_end_date,
    period_order,
    nii_cr,
    ROUND(((nii_cr - nii_lag1) * 100.0 / NULLIF(nii_lag1, 0)), 2) AS nii_qoq_pct,
    ROUND(((nii_cr - nii_lag4) * 100.0 / NULLIF(nii_lag4, 0)), 2) AS nii_yoy_pct,
    pat_cr,
    ROUND(((pat_cr - pat_lag1) * 100.0 / NULLIF(pat_lag1, 0)), 2) AS pat_qoq_pct,
    ROUND(((pat_cr - pat_lag4) * 100.0 / NULLIF(pat_lag4, 0)), 2) AS pat_yoy_pct,
    advances_cr,
    ROUND(((advances_cr - adv_lag1) * 100.0 / NULLIF(adv_lag1, 0)), 2) AS advances_qoq_pct,
    ROUND(((advances_cr - adv_lag4) * 100.0 / NULLIF(adv_lag4, 0)), 2) AS advances_yoy_pct,
    deposits_cr,
    ROUND(((deposits_cr - dep_lag1) * 100.0 / NULLIF(dep_lag1, 0)), 2) AS deposits_qoq_pct,
    ROUND(((deposits_cr - dep_lag4) * 100.0 / NULLIF(dep_lag4, 0)), 2) AS deposits_yoy_pct,
    nim_pct,
    ROUND((nim_pct - nim_lag1), 2) AS nim_qoq_bps_change,
    ROUND((nim_pct - nim_lag4), 2) AS nim_yoy_bps_change,
    gnpa_pct,
    ROUND((gnpa_pct - gnpa_lag1), 2) AS gnpa_qoq_bps_change,
    ROUND((gnpa_pct - gnpa_lag4), 2) AS gnpa_yoy_bps_change
FROM lagged;

-- 3. v_credit_deposit_ratio: Credit to Deposit (CD) ratio per bank per quarter
DROP VIEW IF EXISTS v_credit_deposit_ratio;
CREATE VIEW v_credit_deposit_ratio AS
SELECT 
    bank,
    period_label,
    period_end_date,
    period_order,
    advances_cr,
    deposits_cr,
    ROUND((advances_cr * 100.0 / NULLIF(deposits_cr, 0)), 2) AS cd_ratio_pct,
    ROUND(
        (advances_cr * 100.0 / NULLIF(deposits_cr, 0)) - 
        LAG(advances_cr * 100.0 / NULLIF(deposits_cr, 0), 1) OVER (PARTITION BY bank ORDER BY period_order),
        2
    ) AS cd_ratio_qoq_change
FROM v_kpi_wide;

-- 4. v_profit_bridge: ICICI Bank profit decomposition waterfall
-- NII + Other Income = Total Net Revenue; - Opex = PPOP; - Provisions = PBT; - Tax/Others = PAT
DROP VIEW IF EXISTS v_profit_bridge;
CREATE VIEW v_profit_bridge AS
SELECT 
    bank,
    period_label,
    period_end_date,
    period_order,
    nii_cr,
    other_income_cr,
    (nii_cr + other_income_cr) AS total_income_net_cr,
    opex_cr,
    ppop_cr,
    provisions_cr,
    (ppop_cr - provisions_cr) AS pbt_cr,
    pat_cr,
    ROUND((opex_cr * 100.0 / NULLIF(nii_cr + other_income_cr, 0)), 2) AS calculated_cost_to_income_pct,
    ROUND((provisions_cr * 100.0 / NULLIF(ppop_cr, 0)), 2) AS credit_cost_to_ppop_pct
FROM v_kpi_wide
WHERE bank = 'ICICI';

-- 5. v_ttm_metrics: Trailing-Twelve-Months (TTM) rolling aggregations
DROP VIEW IF EXISTS v_ttm_metrics;
CREATE VIEW v_ttm_metrics AS
SELECT 
    bank,
    period_label,
    period_end_date,
    period_order,
    pat_cr,
    SUM(pat_cr) OVER (
        PARTITION BY bank ORDER BY period_order ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS pat_ttm_cr,
    SUM(nii_cr) OVER (
        PARTITION BY bank ORDER BY period_order ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS nii_ttm_cr,
    ROUND(AVG(nim_pct) OVER (
        PARTITION BY bank ORDER BY period_order ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ), 2) AS nim_ttm_avg_pct,
    ROUND(AVG(roa_pct) OVER (
        PARTITION BY bank ORDER BY period_order ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ), 2) AS roa_ttm_avg_pct,
    ROUND(AVG(roe_pct) OVER (
        PARTITION BY bank ORDER BY period_order ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ), 2) AS roe_ttm_avg_pct
FROM v_kpi_wide;

