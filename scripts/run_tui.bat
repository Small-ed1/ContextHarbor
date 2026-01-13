@echo off
cd /d "%~dp0"

REM Check if API is running
curl -sf http://127.0.0.1:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: API server may not be running.
    echo Start with: scripts\servers.bat start
    echo Or run manually: uvicorn bin.app:app
    echo.
)

REM Run TUI
python bin\router_tui.py