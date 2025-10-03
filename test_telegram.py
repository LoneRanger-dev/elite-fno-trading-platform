"""
🔧 Test Telegram Bot Connection
"""

import logging
from telegram_bot import TelegramBot, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_telegram_connection():
    """Test Telegram bot connection and message sending"""
    
    print("\n🔄 Testing Telegram Bot Connection...")
    print(f"Bot Token: {TELEGRAM_BOT_TOKEN[:6]}...{TELEGRAM_BOT_TOKEN[-4:]}")
    print(f"Chat ID: {TELEGRAM_CHAT_ID}")
    
    try:
        # Initialize bot
        bot = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        
        # Prepare test message
        test_message = (
            "🎯 *Signal System Test*\n\n"
            "This is a test message to verify:\n"
            "1. Bot connection\n"
            "2. Message formatting\n"
            "3. Signal delivery\n\n"
            "If you see this message, the bot is working correctly!\n\n"
            "Time: {current_time}"
        )
        
        # Send test message
        success = bot.send_message(
            test_message,
            parse_mode='Markdown',
            is_test=True
        )
        
        if success:
            print("\n✅ Test message sent successfully!")
            print("📱 Check your Telegram for the test message")
        else:
            print("\n❌ Failed to send test message")
            print("Check the logs above for detailed error information")
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        print(f"\n❌ Test failed: {str(e)}")
        print("Please check your bot token and chat ID")

if __name__ == "__main__":
    print("\n🤖 Telegram Bot Connection Tester")
    print("=" * 40)
    test_telegram_connection()
    print("=" * 40)