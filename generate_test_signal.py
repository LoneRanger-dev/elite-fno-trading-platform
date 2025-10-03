"""
Generate a test trading signal for validation
"""

from live_signal_engine import LiveSignalEngine
from market_data_provider import initialize_market_data_provider
from telegram_bot import TelegramBot, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_test_signal():
    """Generate a test signal for validation"""
    try:
        # Initialize components
        telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        market_data_provider = initialize_market_data_provider({})
        
        # Initialize signal engine
        signal_engine = LiveSignalEngine(market_data_provider, telegram_bot)
        
        # Generate and send test signal
        signal_engine.generate_test_signal()
        
        logger.info("Test signal sent successfully")
        
    except Exception as e:
        logger.error(f"Error generating test signal: {e}")

if __name__ == "__main__":
    print("Generating test signal for validation...")
    generate_test_signal()
    print("Done! Check your Telegram for the test signal.")