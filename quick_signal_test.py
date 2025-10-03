"""
🎯 Quick Signal Test Script
Tests market data and signal generation with Telegram notifications
"""

import logging
from datetime import datetime
from telegram_bot import TelegramBot, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from market_data_provider import initialize_market_data_provider
from live_signal_engine import LiveSignalEngine, TradingSignal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_signal():
    try:
        # Initialize components
        telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        
        # Test market data connection
        kite_config = {
            'api_key': 'zfz6i2qjh9zjl26m',
            'api_secret': 'esdsumpztnzmry8rl1e411b95qt86v2m',
            'access_token': '9tB7VtbqUGu4btfKkX7E4zO6t7wNOtbt'
        }
        market_data = initialize_market_data_provider(kite_config)
        
        # Create test signal
        test_signal = TradingSignal(
            id="TEST_001",
            timestamp=datetime.now(),
            instrument="NIFTY",
            option_symbol="NIFTY 24500 CE",
            signal_type="BUY_CALL",
            strike_price=24500,
            option_entry_price=150.25,
            option_target_price=185.50,
            option_stop_loss=135.75,
            confidence=85.5,
            setup_description="Breakout confirmed with strong momentum",
            technical_indicators={
                "RSI": 65.5,
                "MACD": "Bullish",
                "Trend": "Upward"
            },
            risk_reward_ratio=2.35,
            expiry_date="2024-01-25",
            lot_size=50
        )
        
        # Format and send signal
        signal_msg = (
            "🎯 *FnO Trading Signal (TEST)*\n\n"
            f"Symbol: `{test_signal.instrument}`\n"
            f"Option: `{test_signal.option_symbol}`\n"
            f"Type: `{test_signal.signal_type}`\n\n"
            f"Entry: `₹{test_signal.option_entry_price:.2f}`\n"
            f"Target: `₹{test_signal.option_target_price:.2f}` 🎯\n"
            f"Stop Loss: `₹{test_signal.option_stop_loss:.2f}` 🛑\n\n"
            f"Lot Size: `{test_signal.lot_size}`\n"
            f"Expiry: `{test_signal.expiry_date}`\n"
            f"Confidence: `{test_signal.confidence:.1f}%`\n\n"
            "*Technical Analysis:*\n"
            f"📊 RSI: `{test_signal.technical_indicators['RSI']}`\n"
            f"📈 MACD: `{test_signal.technical_indicators['MACD']}`\n"
            f"🎯 Trend: `{test_signal.technical_indicators['Trend']}`\n\n"
            f"Setup: {test_signal.setup_description}\n\n"
            "⚠️ _This is a test signal to verify system integration._\n"
            f"⏰ `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
        )
        
        # Send test signal
        logger.info("Sending test signal to Telegram...")
        telegram_bot.send_message(signal_msg)
        logger.info("✅ Test signal sent successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running Quick Signal Test")
    print("=" * 50)
    success = test_signal()
    if success:
        print("✅ Test completed successfully!")
        print("📱 Check your Telegram for the test signal")
    else:
        print("❌ Test failed - check logs for details")