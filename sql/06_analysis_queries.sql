-- ============================================================================
-- 06_analysis_queries.sql: Institutional Showcase Analytical SQL Queries
-- Demonstrating CTEs, Window Functions, Rolling Aggregations, and Ranking
-- ============================================================================

-- ============================================================================
-- QUERY 1: Multi-Quarter Operating Profit Bridge & Margin Decomposition
-- Business Question: What specifically drove ICICI's earnings growth across consecutive quarters?
-- Technique: Common Table Expressions (CTEs), Lagged Window Functions, Differential Waterfall
-- How to Read: Shows the exact ₹ Cr contribution of NII expansion, fee income, opex variance,
--              and credit cost changes to bottom-line PAT expansion.
-- ============================================================================
WITH current_qtr AS (
    SELECT 
        period_label,
        period_order,
        nii_cr,
        other_income_cr,
        opex_cr,
        ppop_cr,
        provisions_cr,
        pat_cr
    FROM v_kpi_wide
    WHERE bank = 'ICICI'
),
bridge_diffs AS (
    SELECT 
        period_label,
        period_order,
        nii_cr,
        nii_cr - LAG(nii_cr, 1) OVER (ORDER BY period_order) AS delta_nii,
        other_income_cr - LAG(other_income_cr, 1) OVER (ORDER BY period_order) AS delta_other_income,
        -(opex_cr - LAG(opex_cr, 1) OVER (ORDER BY period_order)) AS delta_opex_impact, -- higher opex drags profit
        -(provisions_cr - LAG(provisions_cr, 1) OVER (ORDER BY period_order)) AS delta_credit_cost_impact,
        pat_cr - LAG(pat_cr, 1) OVER (ORDER BY period_order) AS delta_pat
    FROM current_qtr
)
SELECT 
    period_label,
    delta_nii AS "NII Expansion Impact (Cr)",
    delta_other_income AS "Fee/Other Income Impact (Cr)",
    delta_opex_impact AS "Opex Variance Impact (Cr)",
    delta_credit_cost_impact AS "Provision Reduction Impact (Cr)",
    delta_pat AS "Net PAT Change (Cr)"
FROM bridge_diffs
WHERE period_order > 1
ORDER BY period_order DESC;


-- ============================================================================
-- QUERY 2: Peer Asset Quality Dispersion & Provisioning Resilience
-- Business Question: How does ICICI Bank's Gross NPA and PCR compare against HDFC, SBI, Axis, Kotak?
-- Technique: Cross-Sectional Window Functions (DENSE_RANK, NTILE, PERCENT_RANK)
-- How to Read: Ranks all 5 banks on balance-sheet health. Rank 1 in GNPA represents lowest default rate.
-- ============================================================================
WITH ranked_quality AS (
    SELECT 
        period_label,
        bank,
        gnpa_pct,
        nnpa_pct,
        pcr_pct,
        DENSE_RANK() OVER (PARTITION BY period_label ORDER BY gnpa_pct ASC) AS gnpa_rank,
        DENSE_RANK() OVER (PARTITION BY period_label ORDER BY pcr_pct DESC) AS pcr_rank,
        ROUND(AVG(gnpa_pct) OVER (PARTITION BY period_label), 2) AS peer_avg_gnpa
    FROM v_kpi_wide
)
SELECT 
    period_label,
    bank,
    gnpa_pct AS "GNPA %",
    peer_avg_gnpa AS "Sector Avg GNPA %",
    ROUND(gnpa_pct - peer_avg_gnpa, 2) AS "Spread to Peer Avg (bps)",
    gnpa_rank AS "GNPA Quality Rank (1 = Pristine)",
    pcr_pct AS "PCR %",
    pcr_rank AS "Provision Buffer Rank (1 = Most Buffered)"
FROM ranked_quality
ORDER BY period_label DESC, gnpa_rank ASC;


-- ============================================================================
-- QUERY 3: Credit-to-Deposit Gap & Liquidity Stress Indicator
-- Business Question: Are advances expanding faster than deposits, and what is the risk to NIM?
-- Technique: Window Lag ratios, Dual-Series YoY Growth Delta, Threshold Classification
-- How to Read: A CD ratio above 85% signals liquidity tightness and elevated cost-of-deposit pressure.
-- ============================================================================
SELECT 
    w.period_label,
    w.bank,
    w.advances_cr,
    w.deposits_cr,
    ROUND(w.advances_cr * 100.0 / w.deposits_cr, 2) AS cd_ratio_pct,
    g.advances_yoy_pct,
    g.deposits_yoy_pct,
    ROUND(g.advances_yoy_pct - g.deposits_yoy_pct, 2) AS growth_divergence_pct,
    CASE 
        WHEN (w.advances_cr * 100.0 / w.deposits_cr) > 86.0 THEN 'HIGH STRETCH (Deposit Mobilisation Required)'
        WHEN (w.advances_cr * 100.0 / w.deposits_cr) BETWEEN 80.0 AND 86.0 THEN 'OPTIMAL RANGE'
        ELSE 'SURPLUS LIQUIDITY'
    END AS liquidity_assessment
FROM v_kpi_wide w
JOIN v_kpi_growth g ON w.bank = g.bank AND w.period_label = g.period_label
WHERE w.bank = 'ICICI'
ORDER BY w.period_order DESC;


-- ============================================================================
-- QUERY 4: Stock Risk-Adjusted Return Profile: Drawdowns, Rolling Volatility, and Peak Durations
-- Business Question: What was ICICI Bank's maximum drawdown, how long did it last, and what is current recovery?
-- Technique: Cumulative Running Max Window Functions, Conditional Grouping
-- How to Read: Tracks percentage drop from the highest historical price level to quantify downside risk.
-- ============================================================================
WITH dd_calc AS (
    SELECT 
        date,
        close,
        MAX(close) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS peak_to_date
    FROM fact_stock_price
    WHERE company_id = (SELECT company_id FROM dim_company WHERE short_code = 'ICICI')
),
underwater AS (
    SELECT 
        date,
        close,
        peak_to_date,
        ROUND((close - peak_to_date) * 100.0 / peak_to_date, 2) AS drawdown_pct
    FROM dd_calc
)
SELECT 
    date,
    close AS "Close Price (₹)",
    peak_to_date AS "High Watermark (₹)",
    drawdown_pct AS "Drawdown %"
FROM underwater
WHERE date IN (
    SELECT MAX(date) FROM underwater GROUP BY strftime('%Y-%m', date)
)
ORDER BY date DESC
LIMIT 12;


-- ============================================================================
-- QUERY 5: Macro Rate Cycle Transmission: RBI Repo Rate vs ICICI Net Interest Margin
-- Business Question: Did the RBI rate pause and easing cycle compress or expand ICICI's margins?
-- Technique: Cross-Dimension Subquery Join, Bivariate Correlation Lag
-- How to Read: Shows the lag between central bank rate actions and commercial bank NIM adjustments.
-- ============================================================================
SELECT 
    m.period_label,
    m.rbi_repo_rate AS "RBI Repo Rate (%)",
    m.icici_nim_pct AS "ICICI Standalone NIM (%)",
    ROUND(m.icici_nim_pct - LAG(m.icici_nim_pct, 1) OVER (ORDER BY m.period_order), 2) AS "NIM QoQ Change (bps)",
    m.gdp_growth_rate AS "India GDP Growth (%)",
    m.icici_credit_growth_yoy AS "ICICI Credit Growth YoY (%)"
FROM v_macro_context m
ORDER BY m.period_order ASC;

