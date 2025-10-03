@echo off
echo =====================================================
echo   PREMIUM TRADING BOT - SIMPLE STARTUP
echo =====================================================
echo.
echo Starting your premium trading bot system...
echo.

cd /d "C:\Users\Tns_Tech_Hub\Desktop\TESTWIN\intraday_trading_system"

echo Activating Python environment...
call "C:\Users\Tns_Tech_Hub\Desktop\TESTWIN\.venv\Scripts\activate.bat"

echo.
echo Starting Premium Trading System...
echo.
echo Your system will start in a few seconds...
echo Web Dashboard will be available at: http://localhost:5000
echo.

python simple_start.py

echo.
echo System stopped. Press any key to exit...
pause