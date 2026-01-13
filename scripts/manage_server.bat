@echo off
setlocal enabledelayedexpansion

set "PID_FILE=%TEMP%\router_server.pid"
set "LOG_FILE=%~dp0logs\server.log"

if "%1"=="start" goto start_server
if "%1"=="stop" goto stop_server
if "%1"=="restart" goto restart_server
if "%1"=="status" goto status_server
if "%1"=="logs" goto logs_server
goto usage

:start_server
if exist "%PID_FILE%" (
    set /p pid=<"%PID_FILE%"
    tasklist /FI "PID eq !pid!" 2>nul | find /i "!pid!" >nul
    if !errorlevel! equ 0 (
        echo Server is already running (PID: !pid!)
        goto end
    )
)

echo Starting Router Phase 1 server...
cd /d "%~dp0"
start /b uvicorn app:app --host 0.0.0.0 --port 8003 > "%LOG_FILE%" 2>&1
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq uvicorn.exe" /NH') do set SERVER_PID=%%i
if defined SERVER_PID (
    echo !SERVER_PID! > "%PID_FILE%"
    timeout /t 2 >nul
    curl -s http://localhost:8003/health | findstr /c:"\"ok\":true" >nul
    if !errorlevel! equ 0 (
        echo ✅ Server started successfully on http://localhost:8003
        echo PID: !SERVER_PID!
    ) else (
        echo ❌ Server failed to start. Check logs: %LOG_FILE%
        del /q "%PID_FILE%" 2>nul
    )
) else (
    echo ❌ Failed to start server
)
goto end

:stop_server
if not exist "%PID_FILE%" (
    echo No PID file found. Server may not be running.
    goto end
)

set /p PID=<"%PID_FILE%"
tasklist /FI "PID eq !PID!" 2>nul | find /i "!PID!" >nul
if !errorlevel! equ 0 (
    echo Stopping server (PID: !PID!)...
    taskkill /PID !PID! /T >nul 2>&1
    timeout /t 2 >nul

    tasklist /FI "PID eq !PID!" 2>nul | find /i "!PID!" >nul
    if !errorlevel! equ 0 (
        echo Force killing server...
        taskkill /PID !PID! /T /F >nul 2>&1
    )

    del /q "%PID_FILE%" 2>nul
    echo ✅ Server stopped
) else (
    echo Server process not found
    del /q "%PID_FILE%" 2>nul
)
goto end

:restart_server
call :stop_server
timeout /t 1 >nul
goto start_server

:status_server
if exist "%PID_FILE%" (
    set /p PID=<"%PID_FILE%"
    tasklist /FI "PID eq !PID!" 2>nul | find /i "!PID!" >nul
    if !errorlevel! equ 0 (
        echo ✅ Server is running (PID: !PID!)
        echo 🌐 URL: http://localhost:8003

        curl -s http://localhost:8003/health | findstr /c:"\"ok\":true" >nul
        if !errorlevel! equ 0 (
            echo 🏥 Health: OK
        ) else (
            echo 🏥 Health: FAILED
        )
    ) else (
        echo ❌ Server is not running
        del /q "%PID_FILE%" 2>nul
    )
) else (
    echo ❌ Server is not running
)
goto end

:logs_server
if exist "%LOG_FILE%" (
    powershell Get-Content "%LOG_FILE%" -Wait
) else (
    echo No log file found
)
goto end

:usage
echo Usage: %0 {start^|stop^|restart^|status^|logs}
echo.
echo Commands:
echo   start   - Start the server
echo   stop    - Stop the server
echo   restart - Restart the server
echo   status  - Show server status
echo   logs    - Show server logs
goto end

:end