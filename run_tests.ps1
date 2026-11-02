# ===============================================================================
#            ICICI Bank Analytics - Automated Pytest Suite (PowerShell)
# ===============================================================================

Write-Host "===============================================================================" -ForegroundColor Yellow
Write-Host "         ICICI Bank Analytics - Automated Test Suite (pytest)" -ForegroundColor Yellow
Write-Host "===============================================================================" -ForegroundColor Yellow
Write-Host ""

$PythonPath = "C:\ProgramData\anaconda3"
$PythonExe  = "$PythonPath\python.exe"
$ProjDir    = "C:\Users\User\.gemini\antigravity\brain\39512d4c-8a7a-4d11-8095-65c5b82b00cd\scratch\icici_dashboard"

$env:PATH = "$PythonPath;$PythonPath\Scripts;$PythonPath\Library\bin;$env:PATH"

Set-Location -Path $ProjDir
Write-Host "[1/2] Working directory: $ProjDir" -ForegroundColor Green
Write-Host "[2/2] Running 8 analytical view invariant tests..." -ForegroundColor Green
Write-Host ""

& $PythonExe -m pytest tests/test_views.py -v

