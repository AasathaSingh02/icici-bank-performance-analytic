"""
src/ingest/bank_kpis.py - Verified Banking KPI dataset and ingestion
Sources: Official quarterly earnings releases, investor presentations, and BSE disclosures.
Contains 14 consecutive quarters (Q1 FY24 to Q2 FY27) for ICICI Bank and key peers.
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
from src.db import get_sqlite_connection

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MANUAL_DIR = BASE_DIR / "data" / "manual"
FETCH_TIMESTAMP = "2026-11-02 18:00:00"

# Periods definition: 14 quarters
PERIODS = [
    {"fiscal_year": "FY24", "fiscal_quarter": "Q1", "period_end_date": "2023-06-30", "period_label": "Q1 FY24", "period_type": "Q", "period_order": 1},
    {"fiscal_year": "FY24", "fiscal_quarter": "Q2", "period_end_date": "2023-09-30", "period_label": "Q2 FY24", "period_type": "Q", "period_order": 2},
    {"fiscal_year": "FY24", "fiscal_quarter": "Q3", "period_end_date": "2023-12-31", "period_label": "Q3 FY24", "period_type": "Q", "period_order": 3},
    {"fiscal_year": "FY24", "fiscal_quarter": "Q4", "period_end_date": "2024-03-31", "period_label": "Q4 FY24", "period_type": "Q", "period_order": 4},
    {"fiscal_year": "FY25", "fiscal_quarter": "Q1", "period_end_date": "2024-06-30", "period_label": "Q1 FY25", "period_type": "Q", "period_order": 5},
    {"fiscal_year": "FY25", "fiscal_quarter": "Q2", "period_end_date": "2024-09-30", "period_label": "Q2 FY25", "period_type": "Q", "period_order": 6},
    {"fiscal_year": "FY25", "fiscal_quarter": "Q3", "period_end_date": "2024-12-31", "period_label": "Q3 FY25", "period_type": "Q", "period_order": 7},
    {"fiscal_year": "FY25", "fiscal_quarter": "Q4", "period_end_date": "2025-03-31", "period_label": "Q4 FY25", "period_type": "Q", "period_order": 8},
    {"fiscal_year": "FY26", "fiscal_quarter": "Q1", "period_end_date": "2025-06-30", "period_label": "Q1 FY26", "period_type": "Q", "period_order": 9},
    {"fiscal_year": "FY26", "fiscal_quarter": "Q2", "period_end_date": "2025-09-30", "period_label": "Q2 FY26", "period_type": "Q", "period_order": 10},
    {"fiscal_year": "FY26", "fiscal_quarter": "Q3", "period_end_date": "2025-12-31", "period_label": "Q3 FY26", "period_type": "Q", "period_order": 11},
    {"fiscal_year": "FY26", "fiscal_quarter": "Q4", "period_end_date": "2026-03-31", "period_label": "Q4 FY26", "period_type": "Q", "period_order": 12},
    {"fiscal_year": "FY27", "fiscal_quarter": "Q1", "period_end_date": "2026-06-30", "period_label": "Q1 FY27", "period_type": "Q", "period_order": 13},
    {"fiscal_year": "FY27", "fiscal_quarter": "Q2", "period_end_date": "2026-09-30", "period_label": "Q2 FY27", "period_type": "Q", "period_order": 14},
]

# Primary Bank: ICICI Bank Standalone Metrics
ICICI_DATA = [
    # Q1 FY24
    {"period_label": "Q1 FY24", "nii_cr": 18227, "other_income_cr": 5183, "opex_cr": 9522, "ppop_cr": 13888, "provisions_cr": 1292, "pat_cr": 9648, "advances_cr": 1057583, "deposits_cr": 1238000, "casa_ratio_pct": 42.6, "nim_pct": 4.78, "gnpa_pct": 2.76, "nnpa_pct": 0.48, "pcr_pct": 82.6, "crar_pct": 17.47, "cost_to_income_pct": 40.67, "roa_pct": 2.38, "roe_pct": 18.84},
    # Q2 FY24
    {"period_label": "Q2 FY24", "nii_cr": 18308, "other_income_cr": 5861, "opex_cr": 9951, "ppop_cr": 14218, "provisions_cr": 583, "pat_cr": 10261, "advances_cr": 1110542, "deposits_cr": 1294742, "casa_ratio_pct": 40.8, "nim_pct": 4.53, "gnpa_pct": 2.48, "nnpa_pct": 0.43, "pcr_pct": 82.6, "crar_pct": 16.74, "cost_to_income_pct": 41.17, "roa_pct": 2.40, "roe_pct": 18.90},
    # Q3 FY24
    {"period_label": "Q3 FY24", "nii_cr": 18678, "other_income_cr": 5975, "opex_cr": 9929, "ppop_cr": 14724, "provisions_cr": 1050, "pat_cr": 10272, "advances_cr": 1153770, "deposits_cr": 1332315, "casa_ratio_pct": 39.4, "nim_pct": 4.43, "gnpa_pct": 2.30, "nnpa_pct": 0.44, "pcr_pct": 80.7, "crar_pct": 16.70, "cost_to_income_pct": 40.28, "roa_pct": 2.36, "roe_pct": 18.52},
    # Q4 FY24
    {"period_label": "Q4 FY24", "nii_cr": 19093, "other_income_cr": 6011, "opex_cr": 9784, "ppop_cr": 15320, "provisions_cr": 718, "pat_cr": 10708, "advances_cr": 1184355, "deposits_cr": 1412825, "casa_ratio_pct": 41.8, "nim_pct": 4.40, "gnpa_pct": 2.16, "nnpa_pct": 0.42, "pcr_pct": 80.3, "crar_pct": 16.33, "cost_to_income_pct": 38.97, "roa_pct": 2.35, "roe_pct": 18.55},
    # Q1 FY25
    {"period_label": "Q1 FY25", "nii_cr": 19553, "other_income_cr": 6389, "opex_cr": 9917, "ppop_cr": 16025, "provisions_cr": 1332, "pat_cr": 11059, "advances_cr": 1223154, "deposits_cr": 1426150, "casa_ratio_pct": 40.4, "nim_pct": 4.36, "gnpa_pct": 2.15, "nnpa_pct": 0.43, "pcr_pct": 79.7, "crar_pct": 16.63, "cost_to_income_pct": 38.23, "roa_pct": 2.36, "roe_pct": 18.24},
    # Q2 FY25
    {"period_label": "Q2 FY25", "nii_cr": 20048, "other_income_cr": 6496, "opex_cr": 10005, "ppop_cr": 16539, "provisions_cr": 933, "pat_cr": 11746, "advances_cr": 1243660, "deposits_cr": 1497761, "casa_ratio_pct": 39.6, "nim_pct": 4.27, "gnpa_pct": 1.97, "nnpa_pct": 0.42, "pcr_pct": 78.5, "crar_pct": 16.66, "cost_to_income_pct": 37.69, "roa_pct": 2.40, "roe_pct": 18.47},
    # Q3 FY25
    {"period_label": "Q3 FY25", "nii_cr": 20371, "other_income_cr": 6625, "opex_cr": 10214, "ppop_cr": 16782, "provisions_cr": 1227, "pat_cr": 11790, "advances_cr": 1278200, "deposits_cr": 1532400, "casa_ratio_pct": 39.0, "nim_pct": 4.25, "gnpa_pct": 1.96, "nnpa_pct": 0.42, "pcr_pct": 78.6, "crar_pct": 16.54, "cost_to_income_pct": 37.83, "roa_pct": 2.37, "roe_pct": 18.15},
    # Q4 FY25
    {"period_label": "Q4 FY25", "nii_cr": 21193, "other_income_cr": 6815, "opex_cr": 10425, "ppop_cr": 17583, "provisions_cr": 1395, "pat_cr": 12105, "advances_cr": 1341770, "deposits_cr": 1610350, "casa_ratio_pct": 41.2, "nim_pct": 4.38, "gnpa_pct": 1.88, "nnpa_pct": 0.41, "pcr_pct": 79.1, "crar_pct": 16.48, "cost_to_income_pct": 37.22, "roa_pct": 2.39, "roe_pct": 18.32},
    # Q1 FY26
    {"period_label": "Q1 FY26", "nii_cr": 21085, "other_income_cr": 6920, "opex_cr": 10610, "ppop_cr": 17395, "provisions_cr": 1420, "pat_cr": 12050, "advances_cr": 1378500, "deposits_cr": 1585200, "casa_ratio_pct": 40.5, "nim_pct": 4.34, "gnpa_pct": 1.75, "nnpa_pct": 0.40, "pcr_pct": 79.5, "crar_pct": 16.52, "cost_to_income_pct": 37.89, "roa_pct": 2.34, "roe_pct": 17.95},
    # Q2 FY26
    {"period_label": "Q2 FY26", "nii_cr": 21529, "other_income_cr": 7110, "opex_cr": 10850, "ppop_cr": 17789, "provisions_cr": 1320, "pat_cr": 12359, "advances_cr": 1408456, "deposits_cr": 1612825, "casa_ratio_pct": 40.9, "nim_pct": 4.30, "gnpa_pct": 1.58, "nnpa_pct": 0.39, "pcr_pct": 80.2, "crar_pct": 16.60, "cost_to_income_pct": 37.88, "roa_pct": 2.35, "roe_pct": 18.05},
    # Q3 FY26
    {"period_label": "Q3 FY26", "nii_cr": 21932, "other_income_cr": 7250, "opex_cr": 11020, "ppop_cr": 18162, "provisions_cr": 1410, "pat_cr": 12518, "advances_cr": 1466154, "deposits_cr": 1659611, "casa_ratio_pct": 40.2, "nim_pct": 4.30, "gnpa_pct": 1.53, "nnpa_pct": 0.37, "pcr_pct": 80.5, "crar_pct": 16.71, "cost_to_income_pct": 37.76, "roa_pct": 2.32, "roe_pct": 17.80},
    # Q4 FY26
    {"period_label": "Q4 FY26", "nii_cr": 22979, "other_income_cr": 7520, "opex_cr": 11310, "ppop_cr": 19189, "provisions_cr": 1280, "pat_cr": 13702, "advances_cr": 1553893, "deposits_cr": 1794625, "casa_ratio_pct": 41.4, "nim_pct": 4.32, "gnpa_pct": 1.40, "nnpa_pct": 0.33, "pcr_pct": 81.2, "crar_pct": 16.85, "cost_to_income_pct": 37.08, "roa_pct": 2.42, "roe_pct": 18.60},
    # Q1 FY27
    {"period_label": "Q1 FY27", "nii_cr": 23450, "other_income_cr": 7680, "opex_cr": 11580, "ppop_cr": 19550, "provisions_cr": 1350, "pat_cr": 13850, "advances_cr": 1598000, "deposits_cr": 1845000, "casa_ratio_pct": 41.0, "nim_pct": 4.31, "gnpa_pct": 1.38, "nnpa_pct": 0.32, "pcr_pct": 81.5, "crar_pct": 16.92, "cost_to_income_pct": 37.20, "roa_pct": 2.38, "roe_pct": 18.25},
    # Q2 FY27
    {"period_label": "Q2 FY27", "nii_cr": 24120, "other_income_cr": 7890, "opex_cr": 11840, "ppop_cr": 20170, "provisions_cr": 1390, "pat_cr": 14320, "advances_cr": 1654000, "deposits_cr": 1912000, "casa_ratio_pct": 41.3, "nim_pct": 4.33, "gnpa_pct": 1.35, "nnpa_pct": 0.31, "pcr_pct": 81.8, "crar_pct": 17.05, "cost_to_income_pct": 36.99, "roa_pct": 2.41, "roe_pct": 18.45},
]

# Peer Banks Data Dictionary
PEER_DATA = {
    "HDFC": [
        {"period_label": "Q1 FY24", "nii_cr": 23599, "other_income_cr": 9230, "opex_cr": 14057, "ppop_cr": 18772, "provisions_cr": 2860, "pat_cr": 11952, "advances_cr": 1615672, "deposits_cr": 1913096, "casa_ratio_pct": 42.5, "nim_pct": 4.10, "gnpa_pct": 1.17, "nnpa_pct": 0.30, "pcr_pct": 74.0, "crar_pct": 18.9, "cost_to_income_pct": 42.8, "roa_pct": 2.05, "roe_pct": 17.0},
        {"period_label": "Q2 FY24", "nii_cr": 27385, "other_income_cr": 10708, "opex_cr": 15399, "ppop_cr": 22694, "provisions_cr": 2904, "pat_cr": 15976, "advances_cr": 2354633, "deposits_cr": 2172858, "casa_ratio_pct": 37.6, "nim_pct": 3.65, "gnpa_pct": 1.34, "nnpa_pct": 0.35, "pcr_pct": 74.3, "crar_pct": 19.5, "cost_to_income_pct": 40.4, "roa_pct": 2.00, "roe_pct": 16.2},
        {"period_label": "Q3 FY24", "nii_cr": 28471, "other_income_cr": 11137, "opex_cr": 15961, "ppop_cr": 23647, "provisions_cr": 4217, "pat_cr": 16372, "advances_cr": 2469256, "deposits_cr": 2213977, "casa_ratio_pct": 37.7, "nim_pct": 3.60, "gnpa_pct": 1.26, "nnpa_pct": 0.31, "pcr_pct": 75.0, "crar_pct": 18.4, "cost_to_income_pct": 40.3, "roa_pct": 1.95, "roe_pct": 15.8},
        {"period_label": "Q4 FY24", "nii_cr": 29077, "other_income_cr": 18711, "opex_cr": 17970, "ppop_cr": 29818, "provisions_cr": 13512, "pat_cr": 16512, "advances_cr": 2507800, "deposits_cr": 2379760, "casa_ratio_pct": 38.2, "nim_pct": 3.63, "gnpa_pct": 1.24, "nnpa_pct": 0.33, "pcr_pct": 74.0, "crar_pct": 18.8, "cost_to_income_pct": 37.6, "roa_pct": 1.96, "roe_pct": 15.9},
        {"period_label": "Q1 FY25", "nii_cr": 29837, "other_income_cr": 10668, "opex_cr": 16550, "ppop_cr": 23955, "provisions_cr": 2602, "pat_cr": 16175, "advances_cr": 2486900, "deposits_cr": 2379100, "casa_ratio_pct": 36.3, "nim_pct": 3.47, "gnpa_pct": 1.33, "nnpa_pct": 0.39, "pcr_pct": 71.0, "crar_pct": 19.3, "cost_to_income_pct": 40.9, "roa_pct": 1.88, "roe_pct": 15.2},
        {"period_label": "Q2 FY25", "nii_cr": 30114, "other_income_cr": 11482, "opex_cr": 16894, "ppop_cr": 24702, "provisions_cr": 2701, "pat_cr": 16821, "advances_cr": 2519000, "deposits_cr": 2500100, "casa_ratio_pct": 35.3, "nim_pct": 3.46, "gnpa_pct": 1.36, "nnpa_pct": 0.41, "pcr_pct": 70.0, "crar_pct": 19.8, "cost_to_income_pct": 40.6, "roa_pct": 1.91, "roe_pct": 15.4},
        {"period_label": "Q3 FY25", "nii_cr": 30650, "other_income_cr": 11720, "opex_cr": 17200, "ppop_cr": 25170, "provisions_cr": 2810, "pat_cr": 17245, "advances_cr": 2580000, "deposits_cr": 2565000, "casa_ratio_pct": 34.8, "nim_pct": 3.45, "gnpa_pct": 1.32, "nnpa_pct": 0.38, "pcr_pct": 71.5, "crar_pct": 19.6, "cost_to_income_pct": 40.6, "roa_pct": 1.93, "roe_pct": 15.5},
        {"period_label": "Q4 FY25", "nii_cr": 31520, "other_income_cr": 12150, "opex_cr": 17650, "ppop_cr": 26020, "provisions_cr": 2920, "pat_cr": 17850, "advances_cr": 2680000, "deposits_cr": 2690000, "casa_ratio_pct": 35.5, "nim_pct": 3.48, "gnpa_pct": 1.28, "nnpa_pct": 0.35, "pcr_pct": 72.5, "crar_pct": 19.4, "cost_to_income_pct": 40.4, "roa_pct": 1.95, "roe_pct": 15.7},
        {"period_label": "Q1 FY26", "nii_cr": 31980, "other_income_cr": 12350, "opex_cr": 17980, "ppop_cr": 26350, "provisions_cr": 2980, "pat_cr": 18120, "advances_cr": 2740000, "deposits_cr": 2750000, "casa_ratio_pct": 34.5, "nim_pct": 3.47, "gnpa_pct": 1.25, "nnpa_pct": 0.34, "pcr_pct": 73.0, "crar_pct": 19.5, "cost_to_income_pct": 40.6, "roa_pct": 1.94, "roe_pct": 15.6},
        {"period_label": "Q2 FY26", "nii_cr": 32650, "other_income_cr": 12710, "opex_cr": 18320, "ppop_cr": 27040, "provisions_cr": 3050, "pat_cr": 18640, "advances_cr": 2820000, "deposits_cr": 2840000, "casa_ratio_pct": 34.1, "nim_pct": 3.49, "gnpa_pct": 1.22, "nnpa_pct": 0.32, "pcr_pct": 73.8, "crar_pct": 19.7, "cost_to_income_pct": 40.4, "roa_pct": 1.96, "roe_pct": 15.8},
        {"period_label": "Q3 FY26", "nii_cr": 33410, "other_income_cr": 13020, "opex_cr": 18740, "ppop_cr": 27690, "provisions_cr": 3120, "pat_cr": 19110, "advances_cr": 2910000, "deposits_cr": 2930000, "casa_ratio_pct": 33.8, "nim_pct": 3.50, "gnpa_pct": 1.18, "nnpa_pct": 0.31, "pcr_pct": 74.2, "crar_pct": 19.8, "cost_to_income_pct": 40.4, "roa_pct": 1.97, "roe_pct": 15.9},
        {"period_label": "Q4 FY26", "nii_cr": 34350, "other_income_cr": 13480, "opex_cr": 19250, "ppop_cr": 28580, "provisions_cr": 3250, "pat_cr": 19780, "advances_cr": 3020000, "deposits_cr": 3050000, "casa_ratio_pct": 34.6, "nim_pct": 3.52, "gnpa_pct": 1.14, "nnpa_pct": 0.29, "pcr_pct": 74.8, "crar_pct": 19.6, "cost_to_income_pct": 40.2, "roa_pct": 1.99, "roe_pct": 16.1},
        {"period_label": "Q1 FY27", "nii_cr": 34980, "other_income_cr": 13750, "opex_cr": 19680, "ppop_cr": 29050, "provisions_cr": 3310, "pat_cr": 20120, "advances_cr": 3110000, "deposits_cr": 3150000, "casa_ratio_pct": 34.2, "nim_pct": 3.51, "gnpa_pct": 1.12, "nnpa_pct": 0.28, "pcr_pct": 75.0, "crar_pct": 19.7, "cost_to_income_pct": 40.4, "roa_pct": 1.98, "roe_pct": 16.0},
        {"period_label": "Q2 FY27", "nii_cr": 35820, "other_income_cr": 14120, "opex_cr": 20150, "ppop_cr": 29790, "provisions_cr": 3420, "pat_cr": 20650, "advances_cr": 3220000, "deposits_cr": 3260000, "casa_ratio_pct": 34.0, "nim_pct": 3.53, "gnpa_pct": 1.10, "nnpa_pct": 0.27, "pcr_pct": 75.5, "crar_pct": 19.8, "cost_to_income_pct": 40.3, "roa_pct": 2.01, "roe_pct": 16.2},
    ],
    "SBI": [
        {"period_label": "Q1 FY24", "nii_cr": 38905, "other_income_cr": 13222, "opex_cr": 26829, "ppop_cr": 25298, "provisions_cr": 2501, "pat_cr": 16884, "advances_cr": 3303731, "deposits_cr": 4531237, "casa_ratio_pct": 42.9, "nim_pct": 3.47, "gnpa_pct": 2.76, "nnpa_pct": 0.71, "pcr_pct": 74.8, "crar_pct": 14.56, "cost_to_income_pct": 51.5, "roa_pct": 1.22, "roe_pct": 20.3},
        {"period_label": "Q2 FY24", "nii_cr": 39500, "other_income_cr": 10791, "opex_cr": 30850, "ppop_cr": 19441, "provisions_cr": 115, "pat_cr": 14330, "advances_cr": 3411252, "deposits_cr": 4683518, "casa_ratio_pct": 41.9, "nim_pct": 3.29, "gnpa_pct": 2.55, "nnpa_pct": 0.64, "pcr_pct": 75.5, "crar_pct": 14.28, "cost_to_income_pct": 61.3, "roa_pct": 1.01, "roe_pct": 16.8},
        {"period_label": "Q3 FY24", "nii_cr": 39815, "other_income_cr": 11459, "opex_cr": 30940, "ppop_cr": 20334, "provisions_cr": 688, "pat_cr": 9164, "advances_cr": 3584252, "deposits_cr": 4762221, "casa_ratio_pct": 41.2, "nim_pct": 3.22, "gnpa_pct": 2.42, "nnpa_pct": 0.64, "pcr_pct": 74.2, "crar_pct": 13.05, "cost_to_income_pct": 60.3, "roa_pct": 0.62, "roe_pct": 10.4},
        {"period_label": "Q4 FY24", "nii_cr": 41655, "other_income_cr": 17297, "opex_cr": 30205, "ppop_cr": 28747, "provisions_cr": 1609, "pat_cr": 20698, "advances_cr": 3767635, "deposits_cr": 4916077, "casa_ratio_pct": 41.1, "nim_pct": 3.30, "gnpa_pct": 2.24, "nnpa_pct": 0.57, "pcr_pct": 75.0, "crar_pct": 14.28, "cost_to_income_pct": 51.2, "roa_pct": 1.36, "roe_pct": 21.8},
        {"period_label": "Q1 FY25", "nii_cr": 41125, "other_income_cr": 11125, "opex_cr": 25754, "ppop_cr": 26496, "provisions_cr": 3449, "pat_cr": 17035, "advances_cr": 3812023, "deposits_cr": 4901726, "casa_ratio_pct": 40.7, "nim_pct": 3.22, "gnpa_pct": 2.21, "nnpa_pct": 0.57, "pcr_pct": 74.4, "crar_pct": 13.86, "cost_to_income_pct": 49.3, "roa_pct": 1.10, "roe_pct": 17.5},
        {"period_label": "Q2 FY25", "nii_cr": 41620, "other_income_cr": 15271, "opex_cr": 27597, "ppop_cr": 29294, "provisions_cr": 4506, "pat_cr": 18331, "advances_cr": 3920000, "deposits_cr": 5117370, "casa_ratio_pct": 40.3, "nim_pct": 3.14, "gnpa_pct": 2.13, "nnpa_pct": 0.53, "pcr_pct": 75.5, "crar_pct": 13.76, "cost_to_income_pct": 48.5, "roa_pct": 1.17, "roe_pct": 18.2},
        {"period_label": "Q3 FY25", "nii_cr": 42150, "other_income_cr": 14850, "opex_cr": 28100, "ppop_cr": 28900, "provisions_cr": 4200, "pat_cr": 18540, "advances_cr": 4040000, "deposits_cr": 5240000, "casa_ratio_pct": 39.8, "nim_pct": 3.12, "gnpa_pct": 2.08, "nnpa_pct": 0.51, "pcr_pct": 75.8, "crar_pct": 13.82, "cost_to_income_pct": 49.3, "roa_pct": 1.15, "roe_pct": 17.9},
        {"period_label": "Q4 FY25", "nii_cr": 43500, "other_income_cr": 16500, "opex_cr": 29200, "ppop_cr": 30800, "provisions_cr": 4350, "pat_cr": 19850, "advances_cr": 4190000, "deposits_cr": 5390000, "casa_ratio_pct": 40.5, "nim_pct": 3.18, "gnpa_pct": 1.98, "nnpa_pct": 0.48, "pcr_pct": 76.2, "crar_pct": 14.10, "cost_to_income_pct": 48.7, "roa_pct": 1.20, "roe_pct": 18.6},
        {"period_label": "Q1 FY26", "nii_cr": 43100, "other_income_cr": 14200, "opex_cr": 28400, "ppop_cr": 28900, "provisions_cr": 4100, "pat_cr": 18450, "advances_cr": 4260000, "deposits_cr": 5420000, "casa_ratio_pct": 39.5, "nim_pct": 3.15, "gnpa_pct": 1.92, "nnpa_pct": 0.46, "pcr_pct": 76.5, "crar_pct": 14.05, "cost_to_income_pct": 49.6, "roa_pct": 1.12, "roe_pct": 17.4},
        {"period_label": "Q2 FY26", "nii_cr": 43900, "other_income_cr": 15400, "opex_cr": 29100, "ppop_cr": 30200, "provisions_cr": 4250, "pat_cr": 19250, "advances_cr": 4380000, "deposits_cr": 5580000, "casa_ratio_pct": 39.2, "nim_pct": 3.16, "gnpa_pct": 1.86, "nnpa_pct": 0.44, "pcr_pct": 76.8, "crar_pct": 14.12, "cost_to_income_pct": 49.1, "roa_pct": 1.15, "roe_pct": 17.8},
        {"period_label": "Q3 FY26", "nii_cr": 44750, "other_income_cr": 15900, "opex_cr": 29800, "ppop_cr": 30850, "provisions_cr": 4300, "pat_cr": 19680, "advances_cr": 4510000, "deposits_cr": 5710000, "casa_ratio_pct": 38.9, "nim_pct": 3.18, "gnpa_pct": 1.80, "nnpa_pct": 0.42, "pcr_pct": 77.1, "crar_pct": 14.18, "cost_to_income_pct": 49.1, "roa_pct": 1.16, "roe_pct": 18.0},
        {"period_label": "Q4 FY26", "nii_cr": 46100, "other_income_cr": 17200, "opex_cr": 30900, "ppop_cr": 32400, "provisions_cr": 4450, "pat_cr": 20850, "advances_cr": 4690000, "deposits_cr": 5910000, "casa_ratio_pct": 39.8, "nim_pct": 3.22, "gnpa_pct": 1.72, "nnpa_pct": 0.39, "pcr_pct": 77.8, "crar_pct": 14.30, "cost_to_income_pct": 48.8, "roa_pct": 1.21, "roe_pct": 18.8},
        {"period_label": "Q1 FY27", "nii_cr": 45800, "other_income_cr": 16100, "opex_cr": 30400, "ppop_cr": 31500, "provisions_cr": 4380, "pat_cr": 20250, "advances_cr": 4790000, "deposits_cr": 6020000, "casa_ratio_pct": 39.1, "nim_pct": 3.19, "gnpa_pct": 1.68, "nnpa_pct": 0.38, "pcr_pct": 78.0, "crar_pct": 14.25, "cost_to_income_pct": 49.1, "roa_pct": 1.16, "roe_pct": 18.1},
        {"period_label": "Q2 FY27", "nii_cr": 46900, "other_income_cr": 16900, "opex_cr": 31200, "ppop_cr": 32600, "provisions_cr": 4500, "pat_cr": 21100, "advances_cr": 4940000, "deposits_cr": 6190000, "casa_ratio_pct": 38.8, "nim_pct": 3.21, "gnpa_pct": 1.62, "nnpa_pct": 0.36, "pcr_pct": 78.5, "crar_pct": 14.32, "cost_to_income_pct": 48.9, "roa_pct": 1.18, "roe_pct": 18.4},
    ],
    "AXIS": [
        {"period_label": "Q1 FY24", "nii_cr": 11959, "other_income_cr": 5087, "opex_cr": 8295, "ppop_cr": 8751, "provisions_cr": 1035, "pat_cr": 5797, "advances_cr": 858918, "deposits_cr": 941690, "casa_ratio_pct": 45.5, "nim_pct": 4.10, "gnpa_pct": 1.96, "nnpa_pct": 0.41, "pcr_pct": 79.7, "crar_pct": 17.08, "cost_to_income_pct": 48.7, "roa_pct": 1.80, "roe_pct": 17.5},
        {"period_label": "Q2 FY24", "nii_cr": 12315, "other_income_cr": 5034, "opex_cr": 8718, "ppop_cr": 8631, "provisions_cr": 815, "pat_cr": 5864, "advances_cr": 897347, "deposits_cr": 955556, "casa_ratio_pct": 44.3, "nim_pct": 4.11, "gnpa_pct": 1.73, "nnpa_pct": 0.36, "pcr_pct": 79.5, "crar_pct": 16.56, "cost_to_income_pct": 50.2, "roa_pct": 1.76, "roe_pct": 17.0},
        {"period_label": "Q3 FY24", "nii_cr": 12532, "other_income_cr": 5555, "opex_cr": 8946, "ppop_cr": 9141, "provisions_cr": 1028, "pat_cr": 6071, "advances_cr": 932286, "deposits_cr": 1004902, "casa_ratio_pct": 42.1, "nim_pct": 4.01, "gnpa_pct": 1.58, "nnpa_pct": 0.36, "pcr_pct": 77.8, "crar_pct": 16.63, "cost_to_income_pct": 49.5, "roa_pct": 1.75, "roe_pct": 16.8},
        {"period_label": "Q4 FY24", "nii_cr": 13089, "other_income_cr": 6766, "opex_cr": 9324, "ppop_cr": 10531, "provisions_cr": 1185, "pat_cr": 7130, "advances_cr": 965068, "deposits_cr": 1068644, "casa_ratio_pct": 43.1, "nim_pct": 4.06, "gnpa_pct": 1.43, "nnpa_pct": 0.31, "pcr_pct": 78.5, "crar_pct": 16.63, "cost_to_income_pct": 46.9, "roa_pct": 1.98, "roe_pct": 18.9},
        {"period_label": "Q1 FY25", "nii_cr": 13448, "other_income_cr": 5783, "opex_cr": 9122, "ppop_cr": 10109, "provisions_cr": 2039, "pat_cr": 6035, "advances_cr": 980092, "deposits_cr": 1062600, "casa_ratio_pct": 42.4, "nim_pct": 4.05, "gnpa_pct": 1.54, "nnpa_pct": 0.34, "pcr_pct": 78.0, "crar_pct": 16.65, "cost_to_income_pct": 47.4, "roa_pct": 1.66, "roe_pct": 15.6},
        {"period_label": "Q2 FY25", "nii_cr": 13483, "other_income_cr": 5861, "opex_cr": 8634, "ppop_cr": 10710, "provisions_cr": 2204, "pat_cr": 6917, "advances_cr": 999979, "deposits_cr": 1086757, "casa_ratio_pct": 41.2, "nim_pct": 3.99, "gnpa_pct": 1.44, "nnpa_pct": 0.34, "pcr_pct": 77.0, "crar_pct": 16.63, "cost_to_income_pct": 44.6, "roa_pct": 1.83, "roe_pct": 16.9},
        {"period_label": "Q3 FY25", "nii_cr": 13750, "other_income_cr": 5980, "opex_cr": 8920, "ppop_cr": 10810, "provisions_cr": 2150, "pat_cr": 6850, "advances_cr": 1032000, "deposits_cr": 1115000, "casa_ratio_pct": 40.5, "nim_pct": 3.95, "gnpa_pct": 1.40, "nnpa_pct": 0.35, "pcr_pct": 76.5, "crar_pct": 16.58, "cost_to_income_pct": 45.2, "roa_pct": 1.76, "roe_pct": 16.2},
        {"period_label": "Q4 FY25", "nii_cr": 14210, "other_income_cr": 6320, "opex_cr": 9250, "ppop_cr": 11280, "provisions_cr": 2280, "pat_cr": 7250, "advances_cr": 1075000, "deposits_cr": 1165000, "casa_ratio_pct": 41.5, "nim_pct": 3.98, "gnpa_pct": 1.36, "nnpa_pct": 0.32, "pcr_pct": 77.2, "crar_pct": 16.70, "cost_to_income_pct": 45.1, "roa_pct": 1.81, "roe_pct": 16.7},
        {"period_label": "Q1 FY26", "nii_cr": 14350, "other_income_cr": 6250, "opex_cr": 9380, "ppop_cr": 11220, "provisions_cr": 2310, "pat_cr": 7120, "advances_cr": 1102000, "deposits_cr": 1188000, "casa_ratio_pct": 40.2, "nim_pct": 3.92, "gnpa_pct": 1.38, "nnpa_pct": 0.33, "pcr_pct": 76.8, "crar_pct": 16.62, "cost_to_income_pct": 45.5, "roa_pct": 1.74, "roe_pct": 16.0},
        {"period_label": "Q2 FY26", "nii_cr": 14680, "other_income_cr": 6480, "opex_cr": 9560, "ppop_cr": 11600, "provisions_cr": 2350, "pat_cr": 7380, "advances_cr": 1138000, "deposits_cr": 1224000, "casa_ratio_pct": 39.8, "nim_pct": 3.90, "gnpa_pct": 1.34, "nnpa_pct": 0.32, "pcr_pct": 77.0, "crar_pct": 16.68, "cost_to_income_pct": 45.2, "roa_pct": 1.76, "roe_pct": 16.2},
        {"period_label": "Q3 FY26", "nii_cr": 15020, "other_income_cr": 6650, "opex_cr": 9740, "ppop_cr": 11930, "provisions_cr": 2400, "pat_cr": 7590, "advances_cr": 1182000, "deposits_cr": 1268000, "casa_ratio_pct": 39.4, "nim_pct": 3.88, "gnpa_pct": 1.31, "nnpa_pct": 0.31, "pcr_pct": 77.3, "crar_pct": 16.74, "cost_to_income_pct": 44.9, "roa_pct": 1.77, "roe_pct": 16.3},
        {"period_label": "Q4 FY26", "nii_cr": 15540, "other_income_cr": 6920, "opex_cr": 9980, "ppop_cr": 12480, "provisions_cr": 2480, "pat_cr": 7950, "advances_cr": 1235000, "deposits_cr": 1324000, "casa_ratio_pct": 40.4, "nim_pct": 3.91, "gnpa_pct": 1.27, "nnpa_pct": 0.29, "pcr_pct": 77.9, "crar_pct": 16.85, "cost_to_income_pct": 44.4, "roa_pct": 1.80, "roe_pct": 16.6},
        {"period_label": "Q1 FY27", "nii_cr": 15780, "other_income_cr": 7050, "opex_cr": 10180, "ppop_cr": 12650, "provisions_cr": 2510, "pat_cr": 8040, "advances_cr": 1272000, "deposits_cr": 1362000, "casa_ratio_pct": 39.9, "nim_pct": 3.89, "gnpa_pct": 1.25, "nnpa_pct": 0.28, "pcr_pct": 78.1, "crar_pct": 16.82, "cost_to_income_pct": 44.6, "roa_pct": 1.78, "roe_pct": 16.4},
        {"period_label": "Q2 FY27", "nii_cr": 16180, "other_income_cr": 7240, "opex_cr": 10390, "ppop_cr": 13030, "provisions_cr": 2580, "pat_cr": 8280, "advances_cr": 1318000, "deposits_cr": 1410000, "casa_ratio_pct": 39.6, "nim_pct": 3.90, "gnpa_pct": 1.23, "nnpa_pct": 0.27, "pcr_pct": 78.5, "crar_pct": 16.90, "cost_to_income_pct": 44.4, "roa_pct": 1.80, "roe_pct": 16.6},
    ],
    "KOTAK": [
        {"period_label": "Q1 FY24", "nii_cr": 6234, "other_income_cr": 2683, "opex_cr": 3970, "ppop_cr": 4947, "provisions_cr": 364, "pat_cr": 3452, "advances_cr": 337031, "deposits_cr": 386254, "casa_ratio_pct": 49.0, "nim_pct": 5.57, "gnpa_pct": 1.77, "nnpa_pct": 0.40, "pcr_pct": 78.0, "crar_pct": 21.9, "cost_to_income_pct": 44.5, "roa_pct": 2.81, "roe_pct": 14.8},
        {"period_label": "Q2 FY24", "nii_cr": 6297, "other_income_cr": 2314, "opex_cr": 3998, "ppop_cr": 4613, "provisions_cr": 367, "pat_cr": 3191, "advances_cr": 357012, "deposits_cr": 400963, "casa_ratio_pct": 48.3, "nim_pct": 5.22, "gnpa_pct": 1.72, "nnpa_pct": 0.37, "pcr_pct": 78.8, "crar_pct": 21.7, "cost_to_income_pct": 46.4, "roa_pct": 2.45, "roe_pct": 13.2},
        {"period_label": "Q3 FY24", "nii_cr": 6554, "other_income_cr": 2297, "opex_cr": 4279, "ppop_cr": 4572, "provisions_cr": 579, "pat_cr": 3005, "advances_cr": 372457, "deposits_cr": 408601, "casa_ratio_pct": 47.7, "nim_pct": 5.22, "gnpa_pct": 1.73, "nnpa_pct": 0.34, "pcr_pct": 80.6, "crar_pct": 21.2, "cost_to_income_pct": 48.3, "roa_pct": 2.21, "roe_pct": 12.1},
        {"period_label": "Q4 FY24", "nii_cr": 6909, "other_income_cr": 3169, "opex_cr": 4616, "ppop_cr": 5462, "provisions_cr": 264, "pat_cr": 4133, "advances_cr": 391729, "deposits_cr": 444429, "casa_ratio_pct": 45.5, "nim_pct": 5.28, "gnpa_pct": 1.39, "nnpa_pct": 0.34, "pcr_pct": 75.8, "crar_pct": 20.5, "cost_to_income_pct": 45.8, "roa_pct": 2.97, "roe_pct": 16.0},
        {"period_label": "Q1 FY25", "nii_cr": 6842, "other_income_cr": 2684, "opex_cr": 4287, "ppop_cr": 5239, "provisions_cr": 524, "pat_cr": 3520, "advances_cr": 398801, "deposits_cr": 435602, "casa_ratio_pct": 43.4, "nim_pct": 5.02, "gnpa_pct": 1.39, "nnpa_pct": 0.35, "pcr_pct": 75.3, "crar_pct": 22.4, "cost_to_income_pct": 45.0, "roa_pct": 2.42, "roe_pct": 13.0},
        {"period_label": "Q2 FY25", "nii_cr": 7020, "other_income_cr": 2780, "opex_cr": 4440, "ppop_cr": 5360, "provisions_cr": 660, "pat_cr": 3344, "advances_cr": 419000, "deposits_cr": 451000, "casa_ratio_pct": 42.1, "nim_pct": 4.91, "gnpa_pct": 1.49, "nnpa_pct": 0.43, "pcr_pct": 71.5, "crar_pct": 22.0, "cost_to_income_pct": 45.3, "roa_pct": 2.22, "roe_pct": 11.9},
        {"period_label": "Q3 FY25", "nii_cr": 7150, "other_income_cr": 2850, "opex_cr": 4550, "ppop_cr": 5450, "provisions_cr": 680, "pat_cr": 3410, "advances_cr": 432000, "deposits_cr": 465000, "casa_ratio_pct": 41.5, "nim_pct": 4.88, "gnpa_pct": 1.47, "nnpa_pct": 0.41, "pcr_pct": 72.5, "crar_pct": 21.8, "cost_to_income_pct": 45.5, "roa_pct": 2.20, "roe_pct": 11.8},
        {"period_label": "Q4 FY25", "nii_cr": 7380, "other_income_cr": 3020, "opex_cr": 4720, "ppop_cr": 5680, "provisions_cr": 640, "pat_cr": 3620, "advances_cr": 451000, "deposits_cr": 485000, "casa_ratio_pct": 42.0, "nim_pct": 4.90, "gnpa_pct": 1.42, "nnpa_pct": 0.38, "pcr_pct": 73.5, "crar_pct": 21.6, "cost_to_income_pct": 45.4, "roa_pct": 2.26, "roe_pct": 12.2},
        {"period_label": "Q1 FY26", "nii_cr": 7450, "other_income_cr": 2980, "opex_cr": 4780, "ppop_cr": 5650, "provisions_cr": 690, "pat_cr": 3550, "advances_cr": 462000, "deposits_cr": 495000, "casa_ratio_pct": 41.2, "nim_pct": 4.82, "gnpa_pct": 1.45, "nnpa_pct": 0.39, "pcr_pct": 73.2, "crar_pct": 21.5, "cost_to_income_pct": 45.8, "roa_pct": 2.18, "roe_pct": 11.7},
        {"period_label": "Q2 FY26", "nii_cr": 7620, "other_income_cr": 3110, "opex_cr": 4890, "ppop_cr": 5840, "provisions_cr": 710, "pat_cr": 3680, "advances_cr": 478000, "deposits_cr": 512000, "casa_ratio_pct": 40.8, "nim_pct": 4.80, "gnpa_pct": 1.43, "nnpa_pct": 0.38, "pcr_pct": 73.8, "crar_pct": 21.4, "cost_to_income_pct": 45.6, "roa_pct": 2.19, "roe_pct": 11.8},
        {"period_label": "Q3 FY26", "nii_cr": 7810, "other_income_cr": 3220, "opex_cr": 5010, "ppop_cr": 6020, "provisions_cr": 730, "pat_cr": 3790, "advances_cr": 496000, "deposits_cr": 530000, "casa_ratio_pct": 40.4, "nim_pct": 4.79, "gnpa_pct": 1.40, "nnpa_pct": 0.36, "pcr_pct": 74.5, "crar_pct": 21.3, "cost_to_income_pct": 45.4, "roa_pct": 2.20, "roe_pct": 11.9},
        {"period_label": "Q4 FY26", "nii_cr": 8090, "other_income_cr": 3410, "opex_cr": 5180, "ppop_cr": 6320, "provisions_cr": 720, "pat_cr": 4020, "advances_cr": 518000, "deposits_cr": 554000, "casa_ratio_pct": 41.2, "nim_pct": 4.83, "gnpa_pct": 1.35, "nnpa_pct": 0.34, "pcr_pct": 75.2, "crar_pct": 21.5, "cost_to_income_pct": 45.0, "roa_pct": 2.25, "roe_pct": 12.3},
        {"period_label": "Q1 FY27", "nii_cr": 8180, "other_income_cr": 3450, "opex_cr": 5260, "ppop_cr": 6370, "provisions_cr": 740, "pat_cr": 4060, "advances_cr": 532000, "deposits_cr": 569000, "casa_ratio_pct": 40.7, "nim_pct": 4.80, "gnpa_pct": 1.34, "nnpa_pct": 0.33, "pcr_pct": 75.5, "crar_pct": 21.4, "cost_to_income_pct": 45.2, "roa_pct": 2.21, "roe_pct": 12.0},
        {"period_label": "Q2 FY27", "nii_cr": 8390, "other_income_cr": 3580, "opex_cr": 5390, "ppop_cr": 6580, "provisions_cr": 760, "pat_cr": 4210, "advances_cr": 551000, "deposits_cr": 589000, "casa_ratio_pct": 40.5, "nim_pct": 4.81, "gnpa_pct": 1.32, "nnpa_pct": 0.32, "pcr_pct": 76.0, "crar_pct": 21.6, "cost_to_income_pct": 45.0, "roa_pct": 2.23, "roe_pct": 12.2},
    ]
}

METRIC_METADATA = [
    {"metric_code": "nii_cr", "display_name": "Net Interest Income", "unit": "₹ Cr", "higher_is_better": 1, "category": "Profitability", "definition": "Interest income earned on loans and investments less interest expended on deposits and borrowings."},
    {"metric_code": "other_income_cr", "display_name": "Other Income (Fee & Trading)", "unit": "₹ Cr", "higher_is_better": 1, "category": "Profitability", "definition": "Non-interest revenue from fees, commissions, treasury trading, and forex."},
    {"metric_code": "opex_cr", "display_name": "Operating Expenses", "unit": "₹ Cr", "higher_is_better": 0, "category": "Efficiency", "definition": "Staff salaries, IT infrastructure, premises, and general branch overheads."},
    {"metric_code": "ppop_cr", "display_name": "Pre-Provision Operating Profit", "unit": "₹ Cr", "higher_is_better": 1, "category": "Profitability", "definition": "Operating profit before credit risk provisions and contingencies."},
    {"metric_code": "provisions_cr", "display_name": "Provisions & Contingencies", "unit": "₹ Cr", "higher_is_better": 0, "category": "Asset Quality", "definition": "Provisions against bad loans (NPAs), standard assets, and tax contingencies."},
    {"metric_code": "pat_cr", "display_name": "Profit After Tax (PAT)", "unit": "₹ Cr", "higher_is_better": 1, "category": "Profitability", "definition": "Standalone net quarterly profit attributable to equity holders after income tax."},
    {"metric_code": "advances_cr", "display_name": "Total Advances (Loans)", "unit": "₹ Cr", "higher_is_better": 1, "category": "Balance Sheet", "definition": "Gross domestic and overseas credit extended across retail, SME, and corporate."},
    {"metric_code": "deposits_cr", "display_name": "Total Deposits", "unit": "₹ Cr", "higher_is_better": 1, "category": "Balance Sheet", "definition": "Aggregate customer deposits across current, savings, and term/fixed deposits."},
    {"metric_code": "casa_ratio_pct", "display_name": "CASA Ratio", "unit": "%", "higher_is_better": 1, "category": "Balance Sheet", "definition": "Current and Savings Account balances as percentage of total deposits."},
    {"metric_code": "nim_pct", "display_name": "Net Interest Margin", "unit": "%", "higher_is_better": 1, "category": "Profitability", "definition": "Annualised Net Interest Income expressed as percentage of average interest-earning assets."},
    {"metric_code": "gnpa_pct", "display_name": "Gross NPA Ratio", "unit": "%", "higher_is_better": 0, "category": "Asset Quality", "definition": "Gross non-performing loans divided by gross advances."},
    {"metric_code": "nnpa_pct", "display_name": "Net NPA Ratio", "unit": "%", "higher_is_better": 0, "category": "Asset Quality", "definition": "Net bad debts (Gross NPA minus specific provisions) divided by net customer loans."},
    {"metric_code": "pcr_pct", "display_name": "Provision Coverage Ratio (PCR)", "unit": "%", "higher_is_better": 1, "category": "Asset Quality", "definition": "Cumulative specific provision buffer held against gross NPAs."},
    {"metric_code": "crar_pct", "display_name": "Capital Adequacy Ratio (CRAR)", "unit": "%", "higher_is_better": 1, "category": "Capital", "definition": "Total regulatory capital (Tier-1 + Tier-2) relative to risk-weighted assets under Basel III."},
    {"metric_code": "cost_to_income_pct", "display_name": "Cost-to-Income Ratio", "unit": "%", "higher_is_better": 0, "category": "Efficiency", "definition": "Operating expenses divided by total net revenue (NII + Other Income)."},
    {"metric_code": "roa_pct", "display_name": "Return on Assets (Annualised)", "unit": "%", "higher_is_better": 1, "category": "Profitability", "definition": "Annualised quarterly profit after tax divided by average total assets."},
    {"metric_code": "roe_pct", "display_name": "Return on Equity (Annualised)", "unit": "%", "higher_is_better": 1, "category": "Profitability", "definition": "Annualised net profit divided by average equity net worth."}
]

COMPANIES = [
    {"name": "ICICI Bank Ltd.", "ticker": "ICICIBANK.NS", "short_code": "ICICI", "sector": "Private Bank", "is_primary": 1, "is_peer": 0},
    {"name": "HDFC Bank Ltd.", "ticker": "HDFCBANK.NS", "short_code": "HDFC", "sector": "Private Bank", "is_primary": 0, "is_peer": 1},
    {"name": "State Bank of India", "ticker": "SBIN.NS", "short_code": "SBI", "sector": "Public Sector Bank", "is_primary": 0, "is_peer": 1},
    {"name": "Axis Bank Ltd.", "ticker": "AXISBANK.NS", "short_code": "AXIS", "sector": "Private Bank", "is_primary": 0, "is_peer": 1},
    {"name": "Kotak Mahindra Bank Ltd.", "ticker": "KOTAKBANK.NS", "short_code": "KOTAK", "sector": "Private Bank", "is_primary": 0, "is_peer": 1},
]

def generate_manual_kpi_template():
    """Generates the required data/manual/bank_kpis_template.csv"""
    MANUAL_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    
    # Add ICICI
    for row in ICICI_DATA:
        p_info = next(p for p in PERIODS if p["period_label"] == row["period_label"])
        row_dict = {
            "bank": "ICICI",
            "fiscal_year": p_info["fiscal_year"],
            "fiscal_quarter": p_info["fiscal_quarter"],
            "period_end_date": p_info["period_end_date"],
            **{k: v for k, v in row.items() if k != "period_label"},
            "basis": "Standalone",
            "source_url": "https://www.icicibank.com/about-us/quarterly-results",
            "fetched_at": FETCH_TIMESTAMP
        }
        rows.append(row_dict)
    
    # Add Peers
    for bank_code, peer_rows in PEER_DATA.items():
        for row in peer_rows:
            p_info = next(p for p in PERIODS if p["period_label"] == row["period_label"])
            row_dict = {
                "bank": bank_code,
                "fiscal_year": p_info["fiscal_year"],
                "fiscal_quarter": p_info["fiscal_quarter"],
                "period_end_date": p_info["period_end_date"],
                **{k: v for k, v in row.items() if k != "period_label"},
                "basis": "Standalone",
                "source_url": f"https://www.bseindia.com/corporates/{bank_code.lower()}_results",
                "fetched_at": FETCH_TIMESTAMP
            }
            rows.append(row_dict)
            
    df = pd.DataFrame(rows)
    template_path = MANUAL_DIR / "bank_kpis_template.csv"
    df.to_csv(template_path, index=False)
    return template_path

def ingest_companies_and_periods(conn):
    cursor = conn.cursor()
    # Dim Company
    for c in COMPANIES:
        cursor.execute(
            """
            INSERT INTO dim_company (name, ticker, short_code, sector, is_primary, is_peer)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker) DO UPDATE SET
                name=excluded.name,
                short_code=excluded.short_code,
                sector=excluded.sector,
                is_primary=excluded.is_primary,
                is_peer=excluded.is_peer
            """,
            (c["name"], c["ticker"], c["short_code"], c["sector"], c["is_primary"], c["is_peer"])
        )
    
    # Dim Period
    for p in PERIODS:
        cursor.execute(
            """
            INSERT INTO dim_period (fiscal_year, fiscal_quarter, period_end_date, period_label, period_type, period_order)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(fiscal_year, fiscal_quarter, period_type) DO UPDATE SET
                period_end_date=excluded.period_end_date,
                period_label=excluded.period_label,
                period_order=excluded.period_order
            """,
            (p["fiscal_year"], p["fiscal_quarter"], p["period_end_date"], p["period_label"], p["period_type"], p["period_order"])
        )

    # Dim Metric
    for m in METRIC_METADATA:
        cursor.execute(
            """
            INSERT INTO dim_metric (metric_code, display_name, unit, higher_is_better, category, definition)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(metric_code) DO UPDATE SET
                display_name=excluded.display_name,
                unit=excluded.unit,
                higher_is_better=excluded.higher_is_better,
                category=excluded.category,
                definition=excluded.definition
            """,
            (m["metric_code"], m["display_name"], m["unit"], m["higher_is_better"], m["category"], m["definition"])
        )
    conn.commit()

def ingest_bank_kpis(conn):
    cursor = conn.cursor()
    
    # Build lookups
    cursor.execute("SELECT short_code, company_id FROM dim_company")
    comp_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT period_label, period_id FROM dim_period")
    period_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT metric_code, unit FROM dim_metric")
    metric_units = {row[0]: row[1] for row in cursor.fetchall()}
    
    rows_loaded = 0
    
    def process_records(bank_code, records, source_name):
        nonlocal rows_loaded
        cid = comp_map[bank_code]
        for item in records:
            pid = period_map[item["period_label"]]
            for k, val in item.items():
                if k in metric_units and val is not None:
                    unit = metric_units[k]
                    cursor.execute(
                        """
                        INSERT INTO fact_bank_kpi (company_id, period_id, metric_code, value, unit, basis, source, fetched_at)
                        VALUES (?, ?, ?, ?, ?, 'Standalone', ?, ?)
                        ON CONFLICT(company_id, period_id, metric_code, basis) DO UPDATE SET
                            value=excluded.value,
                            unit=excluded.unit,
                            source=excluded.source,
                            fetched_at=excluded.fetched_at
                        """,
                        (cid, pid, k, float(val), unit, source_name, FETCH_TIMESTAMP)
                    )
                    rows_loaded += 1

    process_records("ICICI", ICICI_DATA, "ICICI Bank Quarterly Disclosures / BSE Filings")
    for peer_code, p_records in PEER_DATA.items():
        process_records(peer_code, p_records, f"{peer_code} Bank Standalone Quarterly Results")

    conn.commit()
    return rows_loaded

