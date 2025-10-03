@echo off
TITLE FnO Trading Platform - Premium Edition
echo Starting FnO Trading Platform (Premium Edition)...

REM Set environment variables
set PLATFORM_MODE=premium
set PREMIUM_PORT=5500

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found, using system Python
)

REM Check Python availability
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check configuration
if not exist "config\secure\api_credentials.py" (
    echo Error: API credentials not found
    echo Please copy config_template.py to config\secure\api_credentials.py
    echo and update with your API keys
    pause
    exit /b 1
)

REM Create required directories
if not exist "logs" mkdir logs
if not exist "data" mkdir data

REM Start the premium trading platform
echo Starting premium trading platform on port %PREMIUM_PORT%...
python run_premium.py

REM Keep the window open if there's an error
if %errorlevel% neq 0 (
    echo.
    echo Error: Premium platform failed to start
    echo Check logs/trading_platform.log for details
    pause
)