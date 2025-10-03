"""
🎯 Signal Testing Script
Tests live market data integration and signal generation
"""

import sys
import os
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our components
from live_signal_engine import LiveSignalEngine
from telegram_bot import TelegramBot, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from market_data_provider import initialize_market_data_provider

def test_live_signals():
    """Test live market data and signal generation"""
    try:
        # Initialize components
        logger.info("🚀 Initializing signal testing system...")
        
        # Initialize Telegram bot
        telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        
        # Test Telegram connection
        logger.info("Testing Telegram connection...")
        test_message = ("🔔 Signal Bot Test\n\n"
                       "System is initializing and will start sending live signals shortly.\n"
                       f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        telegram_bot.send_message(test_message)
        logger.info("✅ Telegram test message sent successfully")
        
        # Initialize market data provider
        logger.info("Connecting to market data feed...")
        kite_config = {
            'api_key': 'zfz6i2qjh9zjl26m',
            'api_secret': 'esdsumpztnzmry8rl1e411b95qt86v2m',
            'access_token': '9tB7VtbqUGu4btfKkX7E4zO6t7wNOtbt'
        }
        market_data_provider = initialize_market_data_provider(kite_config)
        
        # Initialize signal engine
        signal_engine = LiveSignalEngine(market_data_provider, telegram_bot)
        
        # Start signal monitoring
        logger.info("Starting signal monitoring...")
        while True:
            try:
                # Get current market data
                market_data = market_data_provider.get_live_market_data()
                
                # Generate signals
                signals = signal_engine.generate_signals(market_data)
                
                if signals:
                    logger.info(f"Generated {len(signals)} new signals")
                    for signal in signals:
                        # Format and send signal
                        message = format_signal_message(signal)
                        telegram_bot.send_message(message)
                        logger.info(f"Signal sent: {signal['instrument']} - {signal['signal_type']}")
                
                # Wait before next check (5 minutes)
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in signal monitoring loop: {e}")
                time.sleep(60)  # Wait a minute before retrying
                
    except Exception as e:
        logger.error(f"Failed to initialize signal testing: {e}")
        return False
    
    return True

def format_signal_message(signal):
    """Format a signal into a Telegram message"""
    return f"""
🎯 FnO Trading Signal

Symbol: {signal['instrument']}
Type: {signal['signal_type']}
Strike: {signal['option_symbol']}

Entry: ₹{signal['option_entry_price']}
Target: ₹{signal['option_target_price']}
Stop Loss: ₹{signal['option_stop_loss']}

Confidence: {signal['confidence']}%
Setup: {signal['setup_description']}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

if __name__ == "__main__":
    print("🚀 Starting Signal Testing System")
    print("=" * 50)
    print("This will test:")
    print("1. Kite Connect market data feed")
    print("2. Signal generation engine")
    print("3. Telegram bot integration")
    print("\nSignals will be sent to your Telegram:")
    print(f"Bot Token: ...{TELEGRAM_BOT_TOKEN[-8:]}")
    print(f"Chat ID: {TELEGRAM_CHAT_ID}")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)
    
    try:
        test_live_signals()
    except KeyboardInterrupt:
        print("\n\n✅ Signal testing stopped")
        sys.exit(0)