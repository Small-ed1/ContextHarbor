$AppDir = Split-Path -Parent $PSCommandPath
$AppDir = Split-Path -Parent $AppDir  # Go up to project root

# Check if API is running
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 5 -ErrorAction Stop
} catch {
    Write-Host "Warning: API server may not be running."
    Write-Host "Start with: .\scripts\servers.ps1 start"
    Write-Host "Or run manually: uvicorn app:app"
    Write-Host ""
}

# Run TUI
& python (Join-Path $AppDir "router_tui.py")