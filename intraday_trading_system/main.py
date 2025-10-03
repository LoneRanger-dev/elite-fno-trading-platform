"""
Main Entry Point for Intraday Trading System
Orchestrates the entire trading bot system with web dashboard
"""

import sys
import os
import threading
import time
import signal
import asyncio
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all components
from config.settings import config, logger
from bot.main import TradingBot
from web_app.app import app, socketio

class TradingSystem:
    """Main trading system orchestrator"""
    
    def __init__(self):
        self.logger = logger
        self.config = config
        self.trading_bot = None
        self.web_app_thread = None
        self.is_running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("Trading System initialized")
    
    def start(self):
        """Start the complete trading system"""
        try:
            self.logger.info("Starting Intraday Trading System...")
            
            # Validate configuration
            validation_result = self.config.validate_config()
            if validation_result['errors']:
                self.logger.error(f"Configuration errors: {validation_result['errors']}")
                self.logger.error("Please fix configuration issues before starting")
                return False
            
            self.is_running = True
            
            # Start web dashboard in a separate thread
            self._start_web_dashboard()
            
            # Wait a moment for web app to initialize
            time.sleep(2)
            
            # Start trading bot
            self._start_trading_bot()
            
            self.logger.info("✅ Trading System started successfully!")
            self.logger.info(f"Web Dashboard: http://localhost:{self.config.FLASK_PORT}")
            self.logger.info("🤖 Trading Bot: Running")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start trading system: {str(e)}")
            return False
    
    def _start_web_dashboard(self):
        """Start web dashboard in background thread"""
        def run_web_app():
            try:
                self.logger.info("Starting web dashboard...")
                socketio.run(
                    app,
                    host=self.config.FLASK_HOST,
                    port=self.config.FLASK_PORT,
                    debug=False,  # Don't use debug mode in production
                    allow_unsafe_werkzeug=True
                )
            except Exception as e:
                self.logger.error(f"Web dashboard error: {str(e)}")
        
        self.web_app_thread = threading.Thread(target=run_web_app, daemon=True)
        self.web_app_thread.start()
        self.logger.info("Web dashboard started in background")
    
    def _start_trading_bot(self):
        """Start trading bot"""
        try:
            self.trading_bot = TradingBot()
            if self.trading_bot.start():
                self.logger.info("Trading bot started successfully")
                return True
            else:
                self.logger.error("Failed to start trading bot")
                return False
        except Exception as e:
            self.logger.error(f"Error starting trading bot: {str(e)}")
            return False
    
    def stop(self):
        """Stop the trading system gracefully"""
        self.logger.info("🛑 Stopping Trading System...")
        
        self.is_running = False
        
        # Stop trading bot
        if self.trading_bot:
            try:
                self.trading_bot.stop()
                self.logger.info("Trading bot stopped")
            except Exception as e:
                self.logger.error(f"Error stopping trading bot: {str(e)}")
        
        # Web app will stop when main thread exits
        self.logger.info("✅ Trading System stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def run(self):
        """Main run loop"""
        if not self.start():
            self.logger.error("Failed to start system")
            return
        
        try:
            # Keep main thread alive
            while self.is_running:
                time.sleep(10)  # Check every 10 seconds
                
                # Health check
                if self.trading_bot and not self.trading_bot.is_running:
                    self.logger.warning("Trading bot stopped unexpectedly")
                    # Could implement restart logic here
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {str(e)}")
        finally:
            self.stop()

def main():
    """Main entry point"""
    print("=" * 80)
    print("🚀 INTRADAY TRADING BOT SYSTEM")
    print("=" * 80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Dashboard: http://localhost:{config.FLASK_PORT}")
    print(f"🤖 Bot Status: Starting...")
    print("=" * 80)
    
    system = TradingSystem()
    system.run()

if __name__ == "__main__":
    main()