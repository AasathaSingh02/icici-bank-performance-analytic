.PHONY: all setup ingest test dashboard export clean

PYTHON = C:\ProgramData\anaconda3\python.exe

all: ingest test dashboard

setup:
	$(PYTHON) -m pip install -r requirements.txt

ingest:
	$(PYTHON) -m src.ingest.run_pipeline

test:
	$(PYTHON) -m pytest tests/test_views.py -v

dashboard:
	$(PYTHON) -m streamlit run dashboard/app.py --server.port=8501

export:
	$(PYTHON) -c "import sqlite3, pandas as pd; conn=sqlite3.connect('db/bank.db'); [pd.read_sql(f'SELECT * FROM {v}', conn).to_csv(f'exports/{v}.csv', index=False) for v in ['v_kpi_wide', 'v_peer_rank', 'v_profit_bridge']]; print('Views exported to exports/')"

clean:
	rm -rf db/bank.db docs/quality_report.md

