"""
🚀 Elite FnO Trading Platform - Quick Start Script
Installs dependencies and starts the complete trading system
"""

import subprocess
import sys
import os
import time

def install_package(package):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"⚠️ Python {version.major}.{version.minor}.{version.micro} detected. Python 3.8+ recommended")
        return False

def main():
    print("🚀 Elite FnO Trading Platform - Quick Start")
    print("=" * 60)
    
    # Check Python version
    check_python_version()
    
    print("\\n📦 Installing required packages...")
    
    # Essential packages for the trading platform
    packages = [
        "flask",
        "requests", 
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "pillow",
        "python-telegram-bot",
        "kiteconnect",
        "yfinance",
        "pandas-ta",
        "pytz",
        "python-dotenv",
        "razorpay",
        "schedule",
        "beautifulsoup4",
        "newsapi-python",
        "psutil",
        "asyncio"
    ]
    
    # Install packages
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
        time.sleep(0.5)  # Brief pause between installations
    
    print(f"\\n📊 Installation Summary:")
    print(f"✅ Successfully installed: {success_count}/{len(packages)} packages")
    
    if success_count == len(packages):
        print("\\n🎉 All packages installed successfully!")
    else:
        print(f"\\n⚠️ {len(packages) - success_count} packages failed to install")
        print("The system may still work with reduced functionality")
    
    print("\\n🔧 Setting up directories...")
    
    # Create necessary directories
    directories = [
        "data",
        "logs", 
        "temp",
        "web_app/static/images",
        "web_app/static/css",
        "web_app/static/js"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"📁 Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
    
    print("\n🌐 Starting the Elite FnO Trading Platform (Premium Edition)...")
    print("=" * 60)
    print("🚀 Your trading platform is ready!")
    print("\\n📋 Available URLs:")
    print("   🏠 Landing Page: http://localhost:5000")
    print("   📊 Trading Dashboard: http://localhost:5000/dashboard") 
    print("   🧪 Testing Dashboard: http://localhost:5000/test-system")
    print("\\n💡 Testing Instructions:")
    print("   1. Go to http://localhost:5000/test-system")
    print("   2. Click 'Test Market Data' to verify live data")
    print("   3. Click 'Test Bot Connection' to verify Telegram")
    print("   4. Click 'Send Test Signal' to test signal delivery")
    print("   5. Click 'Run Complete Test Suite' for full testing")
    print("\\n🤖 Telegram Bot Setup:")
    print("   - Your bot token: 8415230764:AAF0Aaqb21Vkq9eWifB_wHDtkm37WrjJRcs")
    print("   - Your chat ID: 7973202689")
    print("   - Test signals will be sent to your Telegram")
    print("\\n⚠️ Important Notes:")
    print("   - This uses demo/test data for market prices")
    print("   - For live market data, connect your Zerodha API")
    print("   - All trades are paper trades (virtual money)")
    print("   - Your API keys are already configured")
    print("=" * 60)
    # Launch premium app
    try:
        print("\n🔄 Starting Flask web server with live signals...")
        print("🎯 Initializing signal generation engine...")
        from live_signal_engine import signal_engine
        signal_engine.start_signal_generation()
        print("✅ Signal generation started successfully!")

        print("🚀 Launching premium application (app_premium.py)...")
        import app_premium as premium_app

        print("\n🧭 Registered Routes (Premium):")
        for rule in sorted(premium_app.app.url_map.iter_rules(), key=lambda r: r.rule):
            methods = ','.join(m for m in rule.methods if m not in ('HEAD','OPTIONS'))
            print(f"   {rule.rule:35s} -> {methods}")
        print("\n✅ Premium routes loaded. Serving on http://localhost:5500 (to avoid old 5000 server).")

        # Run premium app on alternate port to guarantee we are hitting the correct instance
        premium_app.app.run(debug=True, host='0.0.0.0', port=5500)
    except Exception as e:
        print(f"❌ Could not auto-launch premium app: {e}")
        print("\n🔧 Manual Start Instructions:")
        print("   1. Activate venv if any: .venv\\Scripts\\activate")
        print("   2. Run: python app_premium.py")
    print("   3. Open: http://localhost:5500")

if __name__ == "__main__":
    main()