#!/usr/bin/env bash
# SwarmForge Web App Launcher for Linux/macOS

echo "╔════════════════════════════════════════════════════════╗"
echo "║           🐝 SwarmForge Web App Launcher               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "✗ Virtual environment not found. Creating..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Start the web server
echo
echo "✓ Starting SwarmForge Web Server..."
echo
echo "🌐 Open your browser and go to: http://localhost:8000"
echo "📚 API docs available at: http://localhost:8000/docs"
echo
echo "Press Ctrl+C to stop the server"
echo

python webserver.py
