# Work from the script's folder (project root)
Set-Location $PSScriptRoot

# Find Python (prefer the launcher)
$HavePy = Get-Command py -ErrorAction SilentlyContinue
$HavePython = Get-Command python -ErrorAction SilentlyContinue
if (-not $HavePy -and -not $HavePython) {
  Write-Host "Python 3.13+ required. Install from https://www.python.org/downloads/windows/ (include pip & tcl/tk)."
  exit 1
}

# Create venv if missing
$VenvDir = ".\.venv_local"
$VenvPy  = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $VenvPy)) {
  if ($HavePy) {
    & py -3.13 -m venv $VenvDir
    if ($LASTEXITCODE) { & py -3 -m venv $VenvDir }
    if ($LASTEXITCODE) { & py -m venv $VenvDir }
  } else {
    & python -m venv $VenvDir
  }
  if ($LASTEXITCODE) { exit $LASTEXITCODE }
}

# Install/upgrade tools + deps
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"
& $VenvPy -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE) { exit $LASTEXITCODE }

if (Test-Path ".\requirements.txt") {
  & $VenvPy -m pip install -r ".\requirements.txt"
  if ($LASTEXITCODE) { exit $LASTEXITCODE }
}

# Ensure top-level imports (like "src") resolve, then run
$env:PYTHONPATH = $PSScriptRoot
& $VenvPy -m gui.app
exit $LASTEXITCODE
