#!/bin/bash

export HF_HUB_DISABLE_SYMLINKS=1
export HF_HUB_DISABLE_SYMLINKS_WARNING=1

echo ""
echo " ================================================================"
echo " ╔══════════════════════════════════════════════════════════╗"
echo " ║           MOM GENERATOR - AI Meeting Assistant           ║"
echo " ╚══════════════════════════════════════════════════════════╝"
echo " ================================================================"
echo ""

# Get absolute path of the project root
STARTUP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$STARTUP_DIR")"
cd "$ROOT_DIR" || exit 1

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# ----------------------------------------------------------------
# Check Python
# ----------------------------------------------------------------
if ! command -v python3 &> /dev/null; then
    echo " [ERROR] Python not found. Please run install/Installation-MacOS/setup.sh first!"
    read -p " Press [Enter] to exit..."
    exit 1
fi

# ----------------------------------------------------------------
# Check Ollama
# ----------------------------------------------------------------
if ! command -v ollama &> /dev/null; then
    echo " [ERROR] Ollama not found. Please run install/Installation-MacOS/setup.sh first!"
    read -p " Press [Enter] to exit..."
    exit 1
fi

# ----------------------------------------------------------------
# Start Ollama service in background silently
# ----------------------------------------------------------------
echo " Starting Ollama AI engine..."
OLLAMA_HOST=127.0.0.1 ollama serve > /dev/null 2>&1 &
OLLAMA_PID=$!

# Wait for Ollama to become responsive
while ! curl -s http://127.0.0.1:11434/api/tags > /dev/null; do
    sleep 1
done

# ----------------------------------------------------------------
# Launch MOM Generator server + open browser
# ----------------------------------------------------------------
echo ""
echo " Starting MOM Generator server..."
echo ""
echo " ================================================================"
echo " >>> Open your browser at: http://127.0.0.1:5001"
echo " >>> Press CTRL+C in this window to stop the server."
echo " ================================================================"
echo ""

# Open browser (macOS command)
open "http://127.0.0.1:5001" 2>/dev/null || echo "Please open http://127.0.0.1:5001 in your browser"

# Start server in this window
python3 mom_api_server.py

# Cleanup ollama serve on exit
kill $OLLAMA_PID 2>/dev/null
