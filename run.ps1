# Run.ps1 — GillPay launcher (Windows PowerShell)
# Creates .venv if missing, installs deps, sets env, launches GUI as a module.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# 1) Work from the script's folder (project root)
Set-Location -Path $PSScriptRoot

# 2) Select a Python launcher (prefer 'py')
function Get-Python {
  try {
    $ver = (py --version) 2>$null
    if ($LASTEXITCODE -eq 0) { return @("py") }
  } catch {}
  return @("python")
}
$PyCmd = Get-Python

# 3) Create venv if missing (prefer 3.13+, fall back gracefully)
$VenvDir = ".\.venv_local"
$VenvPy  = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPy)) {
  Write-Host "[setup] Creating virtual environment..." -ForegroundColor Cyan
  if ($PyCmd[0] -eq "py") {
    & $PyCmd -3.13 -m venv $VenvDir ; if ($LASTEXITCODE) { & $PyCmd -3 -m venv $VenvDir }
  } else {
    & $PyCmd -m venv $VenvDir
  }
  if ($LASTEXITCODE) { exit $LASTEXITCODE }
  & $VenvPy -m pip install --upgrade pip setuptools wheel
}

# 4) Install dependencies
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
if (Test-Path ".\requirements.txt") {
  Write-Host "[setup] Installing requirements.txt..." -ForegroundColor Cyan
  & $VenvPy -m pip install -r ".\requirements.txt"
} else {
  Write-Host "[setup] Installing minimal runtime (pandas, matplotlib)..." -ForegroundColor Yellow
  & $VenvPy -m pip install pandas matplotlib
}
if ($LASTEXITCODE) { exit $LASTEXITCODE }

# 5) Environment for runtime
$env:PYTHONPATH = $PSScriptRoot
$env:PANDAS_COPY_ON_WRITE = "1"  # align with your app behavior

# 6) Launch GUI as a module (pass through any args)
Write-Host "[run] Launching GillPay GUI..." -ForegroundColor Green
& $VenvPy -m gui.app @args
exit $LASTEXITCODE
