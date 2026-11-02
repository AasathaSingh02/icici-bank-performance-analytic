-- ============================================================================
-- 05_views_peer.sql: Peer Benchmarking & Macro Views
-- Ranking, quartile segmentation, peer differentials, and macro alignment
-- ============================================================================

-- 1. v_peer_rank: Cross-sectional quarterly ranking across core metrics
DROP VIEW IF EXISTS v_peer_rank;
CREATE VIEW v_peer_rank AS
SELECT 
    period_label,
    period_order,
    bank,
    bank_name,
    is_primary,
    -- Profitability metrics (Higher is better)
    pat_cr,
    RANK() OVER (PARTITION BY period_label ORDER BY pat_cr DESC) AS rank_pat,
    nii_cr,
    RANK() OVER (PARTITION BY period_label ORDER BY nii_cr DESC) AS rank_nii,
    nim_pct,
    RANK() OVER (PARTITION BY period_label ORDER BY nim_pct DESC) AS rank_nim,
    roe_pct,
    RANK() OVER (PARTITION BY period_label ORDER BY roe_pct DESC) AS rank_roe,
    roa_pct,
    RANK() OVER (PARTITION BY period_label ORDER BY roa_pct DESC) AS rank_roa,
    -- Asset quality metrics (Lower GNPA/NNPA is better)
    gnpa_pct,
    RANK() OVER (PARTITION BY period_label ORDER BY gnpa_pct ASC) AS rank_gnpa,
    nnpa_pct,
    RANK() OVER (PARTITION BY period_label ORDER BY nnpa_pct ASC) AS rank_nnpa,
    pcr_pct,
    RANK() OVER (PARTITION BY period_label ORDER BY pcr_pct DESC) AS rank_pcr,
    -- Balance sheet & franchise (Higher is better)
    casa_ratio_pct,
    RANK() OVER (PARTITION BY period_label ORDER BY casa_ratio_pct DESC) AS rank_casa,
    advances_cr,
    RANK() OVER (PARTITION BY period_label ORDER BY advances_cr DESC) AS rank_advances,
    deposits_cr,
    RANK() OVER (PARTITION BY period_label ORDER BY deposits_cr DESC) AS rank_deposits
FROM v_kpi_wide;

-- 2. v_peer_vs_icici_gap: Spread of ICICI Bank vs Peer Average
DROP VIEW IF EXISTS v_peer_vs_icici_gap;
CREATE VIEW v_peer_vs_icici_gap AS
WITH peer_averages AS (
    SELECT 
        period_label,
        period_order,
        ROUND(AVG(nim_pct), 2) AS peer_avg_nim,
        ROUND(AVG(gnpa_pct), 2) AS peer_avg_gnpa,
        ROUND(AVG(nnpa_pct), 2) AS peer_avg_nnpa,
        ROUND(AVG(roe_pct), 2) AS peer_avg_roe,
        ROUND(AVG(roa_pct), 2) AS peer_avg_roa,
        ROUND(AVG(casa_ratio_pct), 2) AS peer_avg_casa,
        ROUND(AVG(cost_to_income_pct), 2) AS peer_avg_cost_to_income
    FROM v_kpi_wide
    WHERE is_primary = 0
    GROUP BY period_label, period_order
),
icici_metrics AS (
    SELECT 
        period_label,
        period_order,
        nim_pct AS icici_nim,
        gnpa_pct AS icici_gnpa,
        nnpa_pct AS icici_nnpa,
        roe_pct AS icici_roe,
        roa_pct AS icici_roa,
        casa_ratio_pct AS icici_casa,
        cost_to_income_pct AS icici_cost_to_income
    FROM v_kpi_wide
    WHERE is_primary = 1
)
SELECT 
    i.period_label,
    i.period_order,
    i.icici_nim,
    p.peer_avg_nim,
    ROUND((i.icici_nim - p.peer_avg_nim), 2) AS nim_gap_bps,
    i.icici_gnpa,
    p.peer_avg_gnpa,
    ROUND((i.icici_gnpa - p.peer_avg_gnpa), 2) AS gnpa_gap_bps,
    i.icici_roe,
    p.peer_avg_roe,
    ROUND((i.icici_roe - p.peer_avg_roe), 2) AS roe_gap_pct,
    i.icici_roa,
    p.peer_avg_roa,
    ROUND((i.icici_roa - p.peer_avg_roa), 2) AS roa_gap_pct,
    i.icici_casa,
    p.peer_avg_casa,
    ROUND((i.icici_casa - p.peer_avg_casa), 2) AS casa_gap_pct
FROM icici_metrics i
JOIN peer_averages p ON i.period_label = p.period_label;

-- 3. v_peer_quartile: Cross-sectional quartile position using NTILE(4)
DROP VIEW IF EXISTS v_peer_quartile;
CREATE VIEW v_peer_quartile AS
SELECT 
    period_label,
    period_order,
    bank,
    is_primary,
    NTILE(4) OVER (PARTITION BY period_label ORDER BY roe_pct ASC) AS roe_quartile,
    NTILE(4) OVER (PARTITION BY period_label ORDER BY nim_pct ASC) AS nim_quartile,
    NTILE(4) OVER (PARTITION BY period_label ORDER BY gnpa_pct DESC) AS gnpa_quality_quartile -- Top quartile is lowest GNPA
FROM v_kpi_wide;

-- 4. v_macro_context: Alignment of macro trends with ICICI Bank KPIs
DROP VIEW IF EXISTS v_macro_context;
CREATE VIEW v_macro_context AS
SELECT 
    w.period_label,
    w.period_end_date,
    w.period_order,
    w.nim_pct AS icici_nim_pct,
    w.pat_cr AS icici_pat_cr,
    g.advances_yoy_pct AS icici_credit_growth_yoy,
    g.deposits_yoy_pct AS icici_deposit_growth_yoy,
    (SELECT value FROM fact_macro WHERE indicator_code = 'REPO_RATE' AND period_end_date <= w.period_end_date ORDER BY period_end_date DESC LIMIT 1) AS rbi_repo_rate,
    (SELECT value FROM fact_macro WHERE indicator_code = 'GDP_GROWTH' AND period_end_date <= w.period_end_date ORDER BY period_end_date DESC LIMIT 1) AS gdp_growth_rate,
    (SELECT value FROM fact_macro WHERE indicator_code = 'CPI_INFLATION' AND period_end_date <= w.period_end_date ORDER BY period_end_date DESC LIMIT 1) AS cpi_inflation_rate
FROM v_kpi_wide w
JOIN v_kpi_growth g ON w.bank = g.bank AND w.period_label = g.period_label
WHERE w.bank = 'ICICI';

