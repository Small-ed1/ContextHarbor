@echo off
echo Ollama Web FastAPI - Windows Service Installation
echo.
echo On Windows, services are managed differently than systemd.
echo.
echo To install as a Windows service, you can use tools like:
echo - NSSM (Non-Sucking Service Manager): https://nssm.cc/
echo - Windows Service Wrapper
echo.
echo Example with NSSM:
echo 1. Download and install NSSM
echo 2. nssm install RouterPhase1 "C:\Path\To\Python\python.exe" "C:\Path\To\Project\app.py"
echo 3. nssm start RouterPhase1
echo.
echo Alternatively, use the batch scripts for manual management.
echo.
echo The systemd service file is included for reference only.