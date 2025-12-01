@echo off
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║           🐝 SwarmForge Web App Launcher               ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if .venv exists
if not exist ".venv" (
    echo ✗ Virtual environment not found. Creating...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Start the web server
echo.
echo ✓ Starting SwarmForge Web Server...
echo.
echo 🌐 Open your browser and go to: http://localhost:8000
echo 📚 API docs available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python webserver.py
