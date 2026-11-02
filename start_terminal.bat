@echo off
title Data Analyst Development Terminal (Anaconda Python 3.14)
color 0F
cd /d "%~dp0"
set "PYTHON_PATH=C:\ProgramData\anaconda3"
set "PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PYTHON_PATH%\Library\bin;%PATH%"

echo ===============================================================================
echo            Data Analyst Project Terminal (Pre-configured Environment)
echo ===============================================================================
echo  Working Directory: %CD%
echo  Python Path:       %PYTHON_PATH%\python.exe
echo.
echo  Quick Commands you can run here:
echo    - streamlit run dashboard/app.py       (Launch Dashboard)
echo    - python -m src.ingest.run_pipeline    (Re-run Ingestion & Quality Audit)
echo    - pytest tests/test_views.py -v        (Run Test Suite)
echo    - python --version                     (Verify Python)
echo ===============================================================================
echo.

cmd /k

