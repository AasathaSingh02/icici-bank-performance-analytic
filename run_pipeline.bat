@echo off
title ICICI Bank Analytics - Pipeline Execution
color 0B
echo ===============================================================================
echo            ICICI Bank Analytics - Data Pipeline Execution
echo ===============================================================================
echo.

set "PYTHON_PATH=C:\ProgramData\anaconda3"
set "PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PYTHON_PATH%\Library\bin;%PATH%"
set "PROJ_DIR=C:\Users\User\.gemini\antigravity\brain\39512d4c-8a7a-4d11-8095-65c5b82b00cd\scratch\icici_dashboard"

cd /d "%PROJ_DIR%"
echo Working Directory: %CD%
echo.

echo Running end-to-end data ingestion, star-schema creation and quality checks...
echo.

"%PYTHON_PATH%\python.exe" -m src.ingest.run_pipeline
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Pipeline failed with error code %ERRORLEVEL%.
) else (
    echo.
    echo [SUCCESS] Pipeline completed successfully! Database db\bank.db is updated.
)

pause
