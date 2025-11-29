#!/bin/bash
# ====================================================================
# Insurance Voice Agent - Local Startup Script (Linux/Mac)
# ====================================================================

echo ""
echo "========================================"
echo " Insurance Voice Agent - Local Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python is not installed"
    echo "Please install Python 3.11+ from https://www.python.org/downloads/"
    exit 1
fi

echo "[OK] Python is installed"
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "[WARNING] Dependencies not installed"
    echo "Installing dependencies from requirements.txt..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies"
        exit 1
    fi
fi

echo "[OK] Dependencies are installed"
echo ""

# Check if API key is configured
if ! grep -q "OPENROUTER_API_KEY=sk-" apikeys.env 2>/dev/null; then
    echo "[WARNING] OpenRouter API key not configured"
    echo "Please edit apikeys.env and add your API key"
    echo "Get your key from: https://openrouter.ai/"
    echo ""
    read -p "Press Enter to continue anyway (app may not work)..."
fi

echo "========================================"
echo " Starting Services..."
echo "========================================"
echo ""

# Start backend in background
echo "[1/2] Starting Backend API (port 8000)..."
python3 api_server.py &
BACKEND_PID=$!
sleep 3

# Start frontend in background
echo "[2/2] Starting Frontend Server (port 3000)..."
cd frontend && python3 -m http.server 3000 &
FRONTEND_PID=$!
cd ..
sleep 2

echo ""
echo "========================================"
echo " Services Started!"
echo "========================================"
echo ""
echo "Backend API:  http://localhost:8000"
echo "Frontend UI:  http://localhost:3000"
echo "API Docs:     http://localhost:8000/docs"
echo ""
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Opening browser..."
sleep 2

# Open browser (works on most systems)
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
elif command -v open &> /dev/null; then
    open http://localhost:3000
fi

echo ""
echo "========================================"
echo " Application is running!"
echo "========================================"
echo ""
echo "To stop the application:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Or press Ctrl+C to stop both services"
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
