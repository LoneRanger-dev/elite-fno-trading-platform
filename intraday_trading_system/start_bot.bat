@echo off
title Intraday Trading Bot System

echo ===============================================
echo    INTRADAY TRADING BOT SYSTEM - STARTUP
echo ===============================================
echo.

echo [1/3] Checking Python environment...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

echo [2/3] Installing dependencies...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [3/3] Starting Trading Bot System...
echo.
echo ===============================================
echo   SYSTEM STARTING - DO NOT CLOSE THIS WINDOW
echo ===============================================
echo.
echo Web Dashboard will be available at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the system
echo.

python main.py

echo.
echo System stopped.
pause