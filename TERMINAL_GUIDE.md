# Terminal Setup, Troubleshooting & Revision Guide

> **Quick Summary:** If typing `python` or `streamlit` in your Windows terminal failed with an error like *"The file cannot be accessed by the system"*, *"Python was not found"*, or *"'streamlit' is not recognized"*, don't worry! This is the most common Windows issue when Python is installed via Anaconda. Everything is explained and fixed below.

---

## ⚡ Instant Terminal Command (Copy & Paste Directly)

If you have a PowerShell or CMD terminal open right now and just want to run the project without changing any settings:

### In PowerShell (Default in VS Code / Windows 11):
```powershell
& "C:\ProgramData\anaconda3\python.exe" -m streamlit run "C:\Users\User\.gemini\antigravity\brain\39512d4c-8a7a-4d11-8095-65c5b82b00cd\scratch\icici_dashboard\dashboard\app.py"
```
*(or simply run: `.\run_dashboard.ps1`)*

### In Command Prompt (cmd.exe):
```cmd
"C:\ProgramData\anaconda3\python.exe" -m streamlit run "C:\Users\User\.gemini\antigravity\brain\39512d4c-8a7a-4d11-8095-65c5b82b00cd\scratch\icici_dashboard\dashboard\app.py"
```
*(or simply run: `run_dashboard.bat`)*

---

## 🚀 1. The Instant 1-Click Way (No Setup Needed)

We have created pre-configured batch launchers in this project folder so you can run everything immediately:

| Launcher File | What It Does |
|---|---|
| **`run_dashboard.bat`** | **Double-click to start the Streamlit Dashboard.** Automatically configures Python, checks the database, launches the server, and opens `http://localhost:8501` in your browser. |
| **`start_terminal.bat`** | **Double-click to open a pre-configured Terminal.** Opens a Command Prompt window where `python`, `pip`, `streamlit`, and `pytest` are already loaded into PATH and ready to use. |
| **`run_pipeline.bat`** | **Double-click to re-run the Data Pipeline.** Re-ingests all data, updates `db/bank.db`, and executes the automated quality audit. |
| **`run_tests.bat`** | **Double-click to run Pytest.** Validates all 8 schema and view tests. |

---

## 🔍 2. Why Did Your Terminal Fail? (Root Cause Explanation)

On modern Windows 10 and 11, two things happen that break command-line Python:

### Reason A: The Windows App Execution Alias Trap
* Windows includes a built-in alias at:  
  `C:\Users\<YourUser>\AppData\Local\Microsoft\WindowsApps\python.exe`
* This file is **not a real Python runtime**—it is a 0-byte shortcut designed to open the Microsoft Store.
* When you type `python`, Windows runs this alias first. If it cannot open the Store, it fails with:  
  `Program 'python.exe' failed to run: The file cannot be accessed by the system.`

### Reason B: Anaconda is Installed, but Not in Your System `PATH`
* On your machine, Python 3.14 is installed at:  
  `C:\ProgramData\anaconda3\python.exe`  
  and Streamlit is at:  
  `C:\ProgramData\anaconda3\Scripts\streamlit.exe`
* By default, Anaconda installers do **not** add themselves to Windows `PATH` to avoid interfering with other system software.
* Therefore, your normal PowerShell or Command Prompt does not know where to find `python` or `streamlit`.

---

## 🛠️ 3. How to Fix Your Terminal Permanently (Step-by-Step)

If you want `python` and `streamlit` to work in **any** PowerShell, Command Prompt, or VS Code terminal window forever, follow these two steps:

### Step 1: Disable the Windows Store Python Alias
1. Press the **Windows Key** and open **Settings** (or press `Win + I`).
2. Go to **Apps** → **Advanced app settings** (or *Apps & features*).
3. Click on **App execution aliases**.
4. Scroll down and **Turn OFF** both:
   - ❌ `App Installer (python.exe)`
   - ❌ `App Installer (python3.exe)`

### Step 2: Add Anaconda to Your User Environment Variables
1. Press **Windows Key**, type **Environment Variables**, and click **"Edit the system environment variables"**.
2. Click the **Environment Variables...** button at the bottom right.
3. In the top section (*User variables for User*), find the variable named **`Path`** (or `PATH`) and click **Edit...**.
4. Click **New** and add these three paths (one by one):
   - `C:\ProgramData\anaconda3`
   - `C:\ProgramData\anaconda3\Scripts`
   - `C:\ProgramData\anaconda3\Library\bin`
5. Click **OK** on all windows to save.
6. **Close all open terminal windows and reopen a new PowerShell or Command Prompt.**

### Step 3: Verify
In your new terminal, type:
```cmd
python --version
streamlit --version
```
You should now see:
```text
Python 3.14.x
Streamlit, version 1.x.x
```

---

## 💻 4. Running Inside VS Code / Cursor / PyCharm

If you use VS Code or Cursor:

1. Open this project folder in VS Code (`File` → `Open Folder...`).
2. Press `Ctrl + Shift + P` and type:
   ```text
   Python: Select Interpreter
   ```
3. Choose:
   ```text
   C:\ProgramData\anaconda3\python.exe ('base': conda)
   ```
4. Open the integrated terminal (`Ctrl + ~`).
5. Run the dashboard:
   ```cmd
   streamlit run dashboard/app.py
   ```

---

## 📚 5. Project Revision & Architecture Cheat Sheet

### Core Workflow Diagram
$$\text{Official BSE/RBI Data} \longrightarrow \text{Python Ingest (src/ingest)} \longrightarrow \text{SQLite Star Schema (db/bank.db)} \longrightarrow \text{15 SQL Views (sql/)} \longrightarrow \text{Streamlit UI}$$

### Key Files & What They Do:
* **`config.yaml`**: Central project settings (tickers, peers, date ranges, metrics).
* **`db/bank.db`**: Relational SQLite database.
* **`sql/01_schema.sql`**: Star schema with dimension tables (`dim_company`, `dim_period`, `dim_metric`, `dim_date`) and fact tables (`fact_bank_kpi`, `fact_stock_price`, `fact_macro`).
* **`sql/03_views_kpi.sql`**:
  - `v_kpi_wide`: Pivoted wide-format financial metrics.
  - `v_kpi_growth`: QoQ and YoY change calculations using `LAG()` window functions.
  - `v_profit_bridge`: P&L Waterfall decomposition ($\text{NII} + \text{Fees} - \text{Opex} - \text{Provisions} = \text{PBT}$).
  - `v_credit_deposit_ratio`: Advances ÷ Deposits liquidity metric.
* **`sql/05_views_peer.sql`**:
  - `v_peer_rank`: `RANK()` across profitability and credit quality.
  - `v_peer_vs_icici_gap`: Margin spreads of ICICI vs peer group average.
* **`sql/06_analysis_queries.sql`**: The 5 showcase analytical queries with business commentary.
* **`dashboard/app.py`**: Multi-page Streamlit portal with 8 specialized analytical pages.
* **`docs/INSIGHTS.md`**: Senior equity research writeup answering key questions with verified data.
* **`docs/quality_report.md`**: Automated 10-check audit validation output.
* **`exports/`**: CSV exports of all views for Power BI / Tableau.

### Common Commands Quick Reference:
```bash
# Start Dashboard
streamlit run dashboard/app.py

# Re-run ETL Data Pipeline
python -m src.ingest.run_pipeline

# Run Unit & Integration Tests
pytest tests/test_views.py -v

# Export Views to CSV
python -c "import sqlite3, pandas as pd; conn=sqlite3.connect('db/bank.db'); [pd.read_sql(f'SELECT * FROM {v}', conn).to_csv(f'exports/{v}.csv', index=False) for v in ['v_kpi_wide', 'v_peer_rank', 'v_profit_bridge']]"
```

