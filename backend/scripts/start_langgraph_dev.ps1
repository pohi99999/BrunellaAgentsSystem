param(
    [switch]$Reinstall
)

Write-Host "Activating .venv311..." -ForegroundColor Cyan
if (-not (Test-Path ..\..\.venv311)) {
    Write-Host ".venv311 not found, creating with Python 3.11..." -ForegroundColor Yellow
    py -3.11 -m venv ..\..\.venv311
}
. ..\..\.venv311\Scripts\Activate.ps1

if ($Reinstall) {
    Write-Host "Reinstalling backend in editable mode..." -ForegroundColor Cyan
    pip install -e ..\[dev]
}

$cli = Resolve-Path ..\..\.venv311\Scripts\langgraph.exe -ErrorAction SilentlyContinue
if (-not $cli) {
    Write-Host "langgraph.exe not found; attempting to install cli extras..." -ForegroundColor Yellow
    pip install "langgraph-cli[inmem]>=0.1.71"
    $cli = Resolve-Path ..\..\.venv311\Scripts\langgraph.exe -ErrorAction SilentlyContinue
}

if (-not $cli) {
    Write-Host "Still cannot find langgraph.exe; attempting module invocation fallback" -ForegroundColor Red
    python -m langgraph_cli.main dev --config ..\langgraph.json
} else {
    & $cli dev --config ..\langgraph.json
}
