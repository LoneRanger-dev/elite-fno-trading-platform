@echo off
echo 🚀 Elite FnO Trading Platform - Windows Launcher
echo ================================================

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    echo ✅ Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️ No virtual environment found, using system Python
)

REM Install dependencies and start platform
echo 📦 Installing dependencies and starting PREMIUM platform on port 5500...
echo.
echo If an old server is still running on port 5000 it will NOT show premium features.
echo To free port 5000 (optional):
echo   netstat -ano ^| findstr :5000
echo   taskkill /PID <PID> /F
echo.
python start_platform.py
echo.
echo Open Premium UI: http://localhost:5500
echo (If you still go to :5000 you are hitting the legacy app.)

REM Keep window open
echo.
echo 🎯 Platform startup complete!
echo Press any key to exit...
pause > nul