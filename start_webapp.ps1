#!/usr/bin/env pwsh

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           🐝 SwarmForge Web App Launcher               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check if .venv exists
if (!(Test-Path ".venv")) {
    Write-Host "✗ Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# Start the web server
Write-Host "`n✓ Starting SwarmForge Web Server..." -ForegroundColor Green
Write-Host "`n🌐 Open your browser and go to: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API docs available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Yellow

python webserver.py
