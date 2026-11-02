# ===============================================================================
#            ICICI Bank Performance Intelligence Platform - PowerShell Launcher
# ===============================================================================

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "           ICICI Bank Performance Intelligence Platform" -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

$PythonPath = "C:\ProgramData\anaconda3"
$PythonExe  = "$PythonPath\python.exe"
$ProjDir    = "C:\Users\User\.gemini\antigravity\brain\39512d4c-8a7a-4d11-8095-65c5b82b00cd\scratch\icici_dashboard"
$ScratchDb  = "$ProjDir\db\bank.db"
$LocalDb    = Join-Path $PSScriptRoot "db\bank.db"

# 1. Stop any old stuck Streamlit process on port 8501
Write-Host "[*] Checking for previous running dashboard instances..." -ForegroundColor Yellow
try {
    $conns = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue
    foreach ($c in $conns) {
        Write-Host "[*] Stopping previous instance PID: $($c.OwningProcess)" -ForegroundColor Yellow
        Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
    }
} catch {}

# 2. Sync DB to local directory
if (Test-Path $ScratchDb) {
    Write-Host "[*] Syncing verified institutional database (1.25 MB)..." -ForegroundColor Yellow
    try {
        Copy-Item -Path $ScratchDb -Destination $LocalDb -Force -ErrorAction SilentlyContinue
    } catch {}
}

# 3. Prepend Python to current session PATH
$env:PATH = "$PythonPath;$PythonPath\Scripts;$PythonPath\Library\bin;$env:PATH"

# 4. Navigate to operational project root
Set-Location -Path $ProjDir
Write-Host "[1/3] Project Root: $ProjDir" -ForegroundColor Green

# 5. Verify Python
if (-not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] Anaconda Python not found at $PythonExe" -ForegroundColor Red
    Read-Host "Press Enter to exit..."
    exit 1
}

$PyVer = & $PythonExe --version 2>&1
Write-Host "[2/3] Python detected: $PyVer" -ForegroundColor Green

# 6. Verify DB
$DbFile = Join-Path $ProjDir "db\bank.db"
if (-not (Test-Path $DbFile)) {
    Write-Host "[*] Building bank.db database..." -ForegroundColor Yellow
    & $PythonExe -m src.ingest.run_pipeline
} else {
    Write-Host "[3/3] SQLite Database ready: db\bank.db" -ForegroundColor Green
}

Write-Host ""
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "  Starting Streamlit Dashboard on http://localhost:8501" -ForegroundColor Yellow
Write-Host "  Opening default browser..." -ForegroundColor Yellow
Write-Host "  Press Ctrl+C in this terminal to stop the dashboard server." -ForegroundColor Yellow
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

Start-Process "http://localhost:8501"
& $PythonExe -m streamlit run dashboard\app.py --server.port=8501 --server.runOnSave=true --browser.gatherUsageStats=false
