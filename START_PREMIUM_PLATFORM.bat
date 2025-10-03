@echo off
cls
echo.
echo ========================================
echo  🚀 Elite FnO Trading Platform
echo  Premium Edition with All Features
echo ========================================
echo.
echo Starting premium platform with:
echo ✅ Paper Trading System
echo ✅ Weekly ₹350 / Monthly ₹900 Plans  
echo ✅ Bull/Bear Animations
echo ✅ Razorpay Payment Integration
echo ✅ Telegram Bot Integration
echo ✅ Advanced AI Signals
echo ✅ Live Market Data
echo.
echo Please wait while we launch your platform...
echo.

cd /d "C:\Users\Tns_Tech_Hub\Desktop\TESTWIN"

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo 🚀 Launching Elite FnO Premium Platform...
echo.
echo 🌐 Premium Website: http://localhost:5000
echo 📊 Trading Dashboard: http://localhost:5000/dashboard  
echo 💼 Paper Trading: http://localhost:5000/paper-trading
echo.

python "%~dp0\app_premium.py"

pause