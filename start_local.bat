@echo off
REM ====================================================================
REM Insurance Voice Agent - Local Startup Script
REM ====================================================================

echo.
echo ========================================
echo  Insurance Voice Agent - Local Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if dependencies are installed
echo Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Dependencies not installed
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [OK] Dependencies are installed
echo.

REM Check if API key is configured
findstr /C:"OPENROUTER_API_KEY=sk-" apikeys.env >nul 2>&1
if errorlevel 1 (
    echo [WARNING] OpenRouter API key not configured
    echo Please edit apikeys.env and add your API key
    echo Get your key from: https://openrouter.ai/
    echo.
    echo Press any key to continue anyway (app may not work)...
    pause >nul
)

echo ========================================
echo  Starting Services...
echo ========================================
echo.

REM Start backend in new window
echo [1/2] Starting Backend API (port 8000)...
start "Insurance Agent - Backend" cmd /k "python api_server.py"
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo [2/2] Starting Frontend Server (port 3000)...
start "Insurance Agent - Frontend" cmd /k "cd frontend && python -m http.server 3000"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo  Services Started!
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo Frontend UI:  http://localhost:3000
echo API Docs:     http://localhost:8000/docs
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul

REM Open browser
start http://localhost:3000

echo.
echo ========================================
echo  Application is running!
echo ========================================
echo.
echo To stop the application:
echo   - Close both terminal windows
echo   - Or press Ctrl+C in each window
echo.
echo Press any key to exit this window...
pause >nul
