@echo off
title ICICI Bank Analytics - Automated Test Suite
color 0E
echo ===============================================================================
echo            ICICI Bank Analytics - Automated Test Suite (pytest)
echo ===============================================================================
echo.

set "PYTHON_PATH=C:\ProgramData\anaconda3"
set "PATH=%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PYTHON_PATH%\Library\bin;%PATH%"
set "PROJ_DIR=C:\Users\User\.gemini\antigravity\brain\39512d4c-8a7a-4d11-8095-65c5b82b00cd\scratch\icici_dashboard"

cd /d "%PROJ_DIR%"

echo [1/2] Working directory set to: %CD%
echo [2/2] Running 8 pytest verification checks on analytical views & invariants...
echo.

"%PYTHON_PATH%\python.exe" -m pytest tests/test_views.py -v

echo.
echo ===============================================================================
echo Pytest verification finished.
echo ===============================================================================
pause
