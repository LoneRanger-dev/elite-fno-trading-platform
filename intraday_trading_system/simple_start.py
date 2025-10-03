"""
Simple Premium Trading System Launcher
Works with existing trading bot and adds premium features
"""

import sys
import os
import threading
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import config, logger

def main():
    """Main launcher for premium trading system"""
    print("=" * 80)
    print("🚀 PREMIUM INTRADAY TRADING BOT SYSTEM")
    print("=" * 80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Dashboard: http://localhost:{config.FLASK_PORT}")
    print(f"💳 Payment Gateway: Razorpay (Test Mode)")
    print(f"👥 User Management: Registration & Login")
    print(f"🤖 Bot Status: Starting...")
    print("=" * 80)
    
    try:
        # Start the trading bot core components
        print("\n🤖 Initializing Trading Bot Components...")
        
        # Initialize bot components without starting the web app
        from bot.main import TradingBot
        trading_bot = TradingBot()
        
        # Start bot in background thread
        bot_thread = threading.Thread(target=trading_bot.start)
        bot_thread.daemon = True
        bot_thread.start()
        
        print("✅ Trading Bot core started successfully!")
        print("\n📊 System Features Active:")
        print("   ✅ Live market data integration")
        print("   ✅ Technical analysis engine")
        print("   ✅ Telegram signal broadcasting")
        print("   ✅ Web dashboard interface")
        
        # Initialize premium features
        print("\n💎 Initializing Premium Features...")
        
        from models.user import UserManager
        user_manager = UserManager(
            db_path=os.path.join(config.DATA_DIR, 'users.db'),
            secret_key=config.FLASK_SECRET_KEY
        )
        
        # Create admin user if it doesn't exist
        admin_exists = user_manager.get_user_by_id(1)
        if not admin_exists:
            print("🔧 Creating admin user...")
            result = user_manager.create_user("admin", "admin@tradingbot.com", "9999999999", "admin123")
            if result['success']:
                # Make user admin
                import sqlite3
                conn = sqlite3.connect(user_manager.db_path)
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET role = "admin", subscription_status = "active" WHERE id = ?', (result['user_id'],))
                conn.commit()
                conn.close()
                print("✅ Admin user created - Username: admin, Password: admin123")
        
        print("✅ Premium features initialized!")
        
        # Start Premium Web Application
        print("\n🌐 Starting Premium Web Application...")
        from web_app.premium_app import app, socketio
        
        # Start web app in background thread
        def run_premium_web():
            socketio.run(app, 
                        host=config.FLASK_HOST, 
                        port=config.FLASK_PORT, 
                        debug=False,
                        use_reloader=False)
        
        web_thread = threading.Thread(target=run_premium_web)
        web_thread.daemon = True
        web_thread.start()
        
        # Wait a moment for web app to start
        time.sleep(3)
        
        print("✅ Premium Web Application started!")
        
        print("\n💰 Subscription Plans Ready:")
        print("   📦 Monthly Premium: ₹999/month")
        print("   📦 Quarterly Premium: ₹2,499 (15% off)")
        print("   📦 Annual Premium: ₹7,999 (33% off)")
        
        print("\n🌐 Your Business is Live!")
        print("=" * 80)
        print("📋 ACCESS POINTS:")
        print(f"   🌐 Customer Website: http://localhost:{config.FLASK_PORT}")
        print(f"   🔐 Login Page: http://localhost:{config.FLASK_PORT}/login")
        print(f"   📱 Register Page: http://localhost:{config.FLASK_PORT}/register")
        print(f"   💳 Subscription Plans: http://localhost:{config.FLASK_PORT}/subscribe")
        print(f"   👑 Admin Dashboard: http://localhost:{config.FLASK_PORT}/admin")
        print("=" * 80)
        print("🎯 READY TO ACCEPT CUSTOMERS!")
        print("📱 Share signup link: http://localhost:5000/register")
        print("💰 Revenue tracking: http://localhost:5000/admin")
        print("\nPress Ctrl+C to stop the system...")
        
        # Keep system running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping Premium Trading System...")
        print("✅ System stopped successfully")
        
    except Exception as e:
        print(f"❌ System error: {e}")
        logger.error(f"Premium system error: {e}")

if __name__ == "__main__":
    main()