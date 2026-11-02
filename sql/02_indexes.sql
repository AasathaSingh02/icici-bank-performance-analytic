-- ============================================================================
-- 02_indexes.sql: Performance Indexes for Bank Analytics DB
-- Optimized for analytical joins, time-series aggregation, and filtering
-- ============================================================================

-- dim_period indexes
CREATE INDEX IF NOT EXISTS idx_period_order ON dim_period(period_order);
CREATE INDEX IF NOT EXISTS idx_period_label ON dim_period(period_label);
CREATE INDEX IF NOT EXISTS idx_period_end_date ON dim_period(period_end_date);

-- fact_stock_price indexes
CREATE INDEX IF NOT EXISTS idx_stock_price_date ON fact_stock_price(date);
CREATE INDEX IF NOT EXISTS idx_stock_price_comp_date ON fact_stock_price(company_id, date);

-- fact_index_price indexes
CREATE INDEX IF NOT EXISTS idx_index_price_date ON fact_index_price(index_code, date);

-- fact_bank_kpi indexes
CREATE INDEX IF NOT EXISTS idx_bank_kpi_metric ON fact_bank_kpi(metric_code);
CREATE INDEX IF NOT EXISTS idx_bank_kpi_period ON fact_bank_kpi(period_id);
CREATE INDEX IF NOT EXISTS idx_bank_kpi_comp_period ON fact_bank_kpi(company_id, period_id);
CREATE INDEX IF NOT EXISTS idx_bank_kpi_lookup ON fact_bank_kpi(company_id, metric_code, period_id);

-- fact_macro indexes
CREATE INDEX IF NOT EXISTS idx_macro_lookup ON fact_macro(indicator_code, period_end_date);

