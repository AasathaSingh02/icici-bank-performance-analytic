# Banking KPI Definitions & Financial Methodologies

This document outlines the standard mathematical formulations, operational meanings, and regulatory benchmarks for banking performance metrics used throughout the platform.

---

## 1. Profitability & Margin Metrics

### Net Interest Margin (NIM)
* **Mathematical Formula:**  
  $$\text{NIM (\%)} = \frac{\text{Net Interest Income (Annualised)}}{\text{Average Interest-Earning Assets}} \times 100$$
* **Operational Meaning:** The core spread earned by the bank from borrowing low-cost customer funds and lending or investing them at higher asset yields.
* **Interpretation:** A NIM above 4.0% reflects strong pricing power, superior retail asset mix, and a sticky low-cost deposit franchise.

### Cost-to-Income Ratio
* **Mathematical Formula:**  
  $$\text{Cost-to-Income (\%)} = \frac{\text{Operating Expenses (Opex)}}{\text{Net Interest Income} + \text{Other / Non-Interest Income}} \times 100$$
* **Operational Meaning:** The proportion of total net operating income consumed by operating overheads (employee salaries, technology infrastructure, branch leases).
* **Interpretation:** Lower is better. Ratios below 40% signify lean digital operations and high operating leverage.

### Return on Assets (ROA) & Return on Equity (ROE)
* **ROA Formula:**  
  $$\text{ROA (\%)} = \frac{\text{Annualised Profit After Tax (PAT)}}{\text{Average Total Balance Sheet Assets}} \times 100$$
* **ROE Formula:**  
  $$\text{ROE (\%)} = \frac{\text{Annualised Profit After Tax (PAT)}}{\text{Average Shareholders' Equity (Net Worth)}} \times 100$$
* **Interpretation:** Tier-1 Indian private banks target an ROA > 2.0% and an ROE > 15.0%. ICICI Bank operates at ~2.35% ROA and ~18.2% ROE.

---

## 2. Asset Quality & Risk Metrics

### Gross Non-Performing Asset (GNPA) Ratio
* **Formula:**  
  $$\text{GNPA (\%)} = \frac{\text{Gross NPA Loans}}{\text{Gross Advances Extended}} \times 100$$
* **Operational Meaning:** The fraction of loan accounts where interest or principal installments have remained overdue past the 90-day delinquency threshold.
* **Interpretation:** Lower is better. A GNPA ratio below 2.0% denotes institutional-grade underwriting.

### Net Non-Performing Asset (NNPA) Ratio
* **Formula:**  
  $$\text{NNPA (\%)} = \frac{\text{Gross NPAs} - \text{Specific Provisions Held}}{\text{Gross Advances} - \text{Specific Provisions Held}} \times 100$$
* **Interpretation:** Reflects bad debts that remain unbuffered by cash reserves. Ratios below 0.50% reflect negligible balance-sheet vulnerability.

### Provision Coverage Ratio (PCR)
* **Formula:**  
  $$\text{PCR (\%)} = \frac{\text{Cumulative Specific Provisions Held}}{\text{Gross NPAs}} \times 100$$
* **Interpretation:** Higher is better. A PCR > 75% indicates that the bank can absorb potential complete loss-given-default scenarios without touching current earnings.

---

## 3. Balance Sheet & Liquidity Metrics

### Current and Savings Account (CASA) Ratio
* **Formula:**  
  $$\text{CASA Ratio (\%)} = \frac{\text{Current Account Balances} + \text{Savings Account Balances}}{\text{Total Customer Deposits}} \times 100$$
* **Operational Meaning:** Measures the proportion of deposits that carry low or zero interest expenses.
* **Interpretation:** CASA above 40% provides an insulating cushion against central bank rate hike cycles.

### Credit-to-Deposit (CD) Ratio
* **Formula:**  
  $$\text{CD Ratio (\%)} = \frac{\text{Total Customer Advances}}{\text{Total Customer Deposits}} \times 100$$
* **Interpretation:** Indicates how much of the loan portfolio is funded directly by customer deposits. The RBI monitors CD ratios above 88% as potential liquidity concentration risks.

### Capital Adequacy Ratio (CRAR / Basel III)
* **Formula:**  
  $$\text{CRAR (\%)} = \frac{\text{Tier-1 Capital} + \text{Tier-2 Capital}}{\text{Total Risk-Weighted Assets (RWA)}} \times 100$$
* **Regulatory Benchmark:** RBI mandates a minimum CRAR of 11.5% (including Capital Conservation Buffer). ICICI maintains > 16.5%.

