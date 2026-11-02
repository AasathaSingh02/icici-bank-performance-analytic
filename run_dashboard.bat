@echo off
title ICICI Bank Performance Intelligence Platform
color 0A
echo ===============================================================================
echo            ICICI Bank Performance Intelligence Platform
echo ===============================================================================
echo.

:: 1. Set Python Path
set "PYTHON_PATH=C:\ProgramData\anaconda3"
set "PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PYTHON_PATH%\Library\bin;%PATH%"

:: 2. Auto-kill any old frozen Streamlit process on port 8501 to release SQLite lock
echo [*] Checking for previous running dashboard instances...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr :8501 ^| findstr LISTENING') do (
    echo [*] Stopping previous instance (PID: %%a)...
    taskkill /F /PID %%a >nul 2>&1
)

:: 3. Sync Database from scratch into workspace
set "SCRATCH_DB=C:\Users\User\.gemini\antigravity\brain\39512d4c-8a7a-4d11-8095-65c5b82b00cd\scratch\icici_dashboard\db\bank.db"
set "LOCAL_DB=%~dp0db\bank.db"

if exist "%SCRATCH_DB%" (
    echo [*] Syncing verified institutional database (1.25 MB)...
    copy /y "%SCRATCH_DB%" "%LOCAL_DB%" >nul 2>&1
)

:: 4. Primary Operational Project Directory
set "PROJ_DIR=C:\Users\User\.gemini\antigravity\brain\39512d4c-8a7a-4d11-8095-65c5b82b00cd\scratch\icici_dashboard"

cd /d "%PROJ_DIR%"
echo [1/3] Environment Root: %CD%

:: 5. Check Python availability
"%PYTHON_PATH%\python.exe" --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found at %PYTHON_PATH%\python.exe!
    pause
    exit /b 1
)
echo [2/3] Python detected:
"%PYTHON_PATH%\python.exe" --version

:: 6. Check Database
if not exist "db\bank.db" (
    echo [*] Database not found. Building database now...
    "%PYTHON_PATH%\python.exe" -m src.ingest.run_pipeline
) else (
    echo [3/3] SQLite Database ready: db\bank.db
)

:: 7. Launch Streamlit
echo.
echo ===============================================================================
echo   Starting Streamlit Dashboard on http://localhost:8501
echo   Opening in your default browser...
echo   Press Ctrl+C to stop the dashboard server.
echo ===============================================================================
echo.

start "" http://localhost:8501
"%PYTHON_PATH%\python.exe" -m streamlit run dashboard\app.py --server.port=8501 --server.runOnSave=true --browser.gatherUsageStats=false

pause
