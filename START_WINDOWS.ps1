# AirAware demo local start. Requires installed Python 3.10+ and Node.js 18+.
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path '.venv')) { py -3 -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install -e '.[dev]'
$env:AIR_DATA_MODE = 'demo'
Write-Host 'Starting demo API at http://localhost:8000/docs' -ForegroundColor Green
Start-Process powershell -ArgumentList @('-NoExit','-Command',"Set-Location '$PSScriptRoot'; `$env:AIR_DATA_MODE='demo'; & '.\.venv\Scripts\python.exe' -m uvicorn backend.app.main:app --reload")
Set-Location (Join-Path $PSScriptRoot 'frontend')
npm install
Write-Host 'Starting dashboard at http://localhost:5173' -ForegroundColor Green
npm run dev
