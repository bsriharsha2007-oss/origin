@echo off
cls
color 0B
title SwarmForge Web App - Starting...

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║                                                        ║
echo ║         🐝 SwarmForge Web App Launcher                ║
echo ║          Starting up... please wait...               ║
echo ║                                                        ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Get the directory where this script is located
pushd "%~dp0"

REM Check if virtual environment exists
if not exist ".venv" (
    echo [*] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo.
        echo ✗ ERROR: Failed to create virtual environment
        echo   Make sure Python is installed and in your PATH
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install/upgrade dependencies silently
echo [*] Checking dependencies...
pip install -r requirements.txt --quiet --disable-pip-version-check

if errorlevel 1 (
    echo.
    echo ✗ ERROR: Failed to install dependencies
    echo   Try running: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Clear screen and show startup message
cls
color 0B

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║                                                        ║
echo ║         ✓ SwarmForge Web App Ready!                   ║
echo ║                                                        ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo 🌐 Opening http://localhost:8000 in your browser...
echo.
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo ⏸  Press Ctrl+C in this window to stop the server
echo.
echo ═══════════════════════════════════════════════════════════
echo.

REM Try to open browser automatically
timeout /t 2 /nobreak

start http://localhost:8000

REM Start the web server
python webserver.py

REM If we get here, the server stopped
echo.
echo Server stopped. Press any key to close this window...
pause
