"""
Premium Trading Bot System Startup
Launch trading bot with premium subscription features
"""

import sys
import os
import threading
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import config, logger
from bot.main import TradingBot
from models.user import UserManager
from services.premium_signals import PremiumSignalManager
from services.payment import PaymentManager

class PremiumTradingSystem:
    """Premium Trading System with subscription management"""
    
    def __init__(self):
        self.config = config
        self.logger = logger
        
        # Initialize trading bot
        self.trading_bot = None
        self.bot_thread = None
        
        # Initialize premium components
        self.user_manager = UserManager(
            db_path=os.path.join(config.DATA_DIR, 'users.db'),
            secret_key=config.FLASK_SECRET_KEY
        )
        
        self.premium_signal_manager = PremiumSignalManager(self.user_manager)
        
        # Initialize payment system
        razorpay_key = os.getenv('RAZORPAY_KEY_ID', 'demo_key')
        razorpay_secret = os.getenv('RAZORPAY_KEY_SECRET', 'demo_secret')
        self.payment_manager = PaymentManager(razorpay_key, razorpay_secret, self.user_manager)
        
        # System status
        self.running = False
        self.start_time = datetime.now()
    
    def start(self):
        """Start the premium trading system"""
        try:
            self.logger.info("🚀 Starting Premium Trading Bot System...")
            
            # Initialize and start trading bot
            self.trading_bot = TradingBot()
            self.bot_thread = threading.Thread(target=self.trading_bot.start)
            self.bot_thread.daemon = True
            self.bot_thread.start()
            
            # Start web application with premium features
            self.start_premium_web_app()
            
            self.running = True
            self.logger.info("✅ Premium Trading System started successfully!")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start premium system: {e}")
            return False
    
    def start_premium_web_app(self):
        """Start the premium web application"""
        try:
            # Import and run premium web app
            from web_app.premium_app import app, socketio, start_background_tasks
            
            self.logger.info("🌐 Starting Premium Web Dashboard...")
            
            # Start background tasks
            start_background_tasks()
            
            # Run the web app in a separate thread
            def run_web_app():
                socketio.run(app, 
                           host=self.config.FLASK_HOST, 
                           port=self.config.FLASK_PORT, 
                           debug=False,  # Set to False for production
                           use_reloader=False)
            
            web_thread = threading.Thread(target=run_web_app)
            web_thread.daemon = True
            web_thread.start()
            
            self.logger.info(f"📊 Premium Web Dashboard: http://localhost:{self.config.FLASK_PORT}")
            self.logger.info("🔐 Features: User Authentication, Premium Subscriptions, Payment Gateway")
            
        except Exception as e:
            self.logger.error(f"Failed to start premium web app: {e}")
    
    def stop(self):
        """Stop the premium trading system"""
        try:
            self.logger.info("🛑 Stopping Premium Trading System...")
            
            if self.trading_bot:
                self.trading_bot.stop()
            
            self.running = False
            self.logger.info("✅ Premium Trading System stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping premium system: {e}")
    
    def get_system_status(self):
        """Get premium system status"""
        uptime = datetime.now() - self.start_time
        
        # Get user statistics
        user_stats = self.user_manager.get_user_stats()
        
        # Get revenue statistics
        revenue_stats = self.payment_manager.get_revenue_stats()
        
        return {
            'running': self.running,
            'uptime': str(uptime),
            'start_time': self.start_time.isoformat(),
            'premium_features': True,
            'user_stats': user_stats,
            'revenue_stats': revenue_stats,
            'bot_running': self.trading_bot.is_running if self.trading_bot else False
        }
    
    def create_admin_user(self, username: str, email: str, phone: str, password: str):
        """Create admin user for system management"""
        try:
            result = self.user_manager.create_user(username, email, phone, password)
            
            if result['success']:
                # Update user role to admin
                import sqlite3
                conn = sqlite3.connect(self.user_manager.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE users SET role = 'admin', subscription_status = 'active' 
                    WHERE id = ?
                ''', (result['user_id'],))
                
                conn.commit()
                conn.close()
                
                self.logger.info(f"✅ Admin user created: {username}")
                return True
            else:
                self.logger.error(f"Failed to create admin user: {result['message']}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating admin user: {e}")
            return False

def main():
    """Main entry point"""
    print("=" * 80)
    print("🚀 PREMIUM INTRADAY TRADING BOT SYSTEM")
    print("=" * 80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Premium Dashboard: http://localhost:{config.FLASK_PORT}")
    print(f"💳 Payment Gateway: Razorpay Integration")
    print(f"👥 User Management: Authentication & Subscriptions")
    print(f"🤖 Bot Status: Starting...")
    print("=" * 80)
    
    # Initialize premium system
    premium_system = PremiumTradingSystem()
    
    # Create admin user if it doesn't exist
    admin_exists = premium_system.user_manager.get_user_by_id(1)
    if not admin_exists:
        print("\n🔧 Setting up admin user...")
        admin_created = premium_system.create_admin_user(
            username="admin",
            email="admin@tradingbot.com", 
            phone="9999999999",
            password="admin123"
        )
        if admin_created:
            print("✅ Admin user created - Username: admin, Password: admin123")
            print("🔐 Please change the admin password after first login!")
    
    try:
        # Start the premium system
        success = premium_system.start()
        
        if success:
            print("\n✅ System started successfully!")
            print("\n📋 Access Points:")
            print(f"   🌐 Web Dashboard: http://localhost:{config.FLASK_PORT}")
            print(f"   🔐 Login Page: http://localhost:{config.FLASK_PORT}/login")
            print(f"   💳 Subscribe: http://localhost:{config.FLASK_PORT}/subscribe")
            print(f"   👑 Admin Panel: http://localhost:{config.FLASK_PORT}/admin")
            print("\n📱 Premium Features:")
            print("   ✅ User Registration & Authentication")
            print("   ✅ Subscription Plans & Payment Gateway")
            print("   ✅ Premium Signal Filtering (9:15 AM - 3:30 PM)")
            print("   ✅ Real-time Telegram Notifications")
            print("   ✅ Admin Dashboard & Analytics")
            print("\n🎯 Ready to serve premium customers!")
            print("\nPress Ctrl+C to stop the system...")
            
            # Keep the main thread alive
            while True:
                time.sleep(1)
                
        else:
            print("❌ Failed to start premium system")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping system...")
        premium_system.stop()
        print("✅ System stopped successfully")
        
    except Exception as e:
        print(f"❌ System error: {e}")
        premium_system.stop()

if __name__ == "__main__":
    main()