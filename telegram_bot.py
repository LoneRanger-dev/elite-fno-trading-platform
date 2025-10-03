"""
🤖 Telegram Bot Integration
Handles all communications with the Telegram Bot API.
"""
import telebot
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- IMPORTANT ---
# Use environment variables in production
TELEGRAM_BOT_TOKEN = "8415230764:AAF0Aaqb21Vkq9eWifB_wHDtkm37WrjJRcs"

# This is the chat ID for signal broadcasting
# You can get your chat ID from @userinfobot
TELEGRAM_CHAT_ID = "7973202689"

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        
        try:
            if not token or token == "YOUR_TELEGRAM_BOT_TOKEN":
                raise ValueError("Telegram Bot Token is not configured")
                
            if not chat_id or chat_id == "YOUR_CHAT_ID":
                raise ValueError("Telegram Chat ID is not configured")
            
            # Initialize bot
            self.bot = telebot.TeleBot(token)
            
            # Send test message to verify connection
            test_msg = "🔄 Signal System Test Message\nBot connection successful!"
            self.send_message(test_msg, is_test=True)
            
            logger.info(f"✅ Telegram Bot initialized successfully with chat_id: {chat_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Telegram Bot: {str(e)}")
            self.bot = None
            self.chat_id = None
        else:
            self.chat_id = chat_id

    def send_message(self, text, parse_mode='Markdown', is_test=False):
        """
        Sends a message to the configured Telegram chat with enhanced error handling.
        """
        if not self.bot or not self.chat_id:
            logger.error(f"❌ Cannot send message: bot={bool(self.bot)}, chat_id={bool(self.chat_id)}")
            return False
            
        try:
            # Clean up message formatting
            text = text.replace('_', '\\_').replace('*', '\\*') if parse_mode == 'Markdown' else text
            
            # Add test indicator if it's a test message
            if is_test:
                text = "🔧 TEST MESSAGE (Debug Mode)\n" + text
                
            # Attempt to send message
            result = self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
            
            # Log success with message details
            logger.info(f"✅ Telegram message sent successfully to chat_id {self.chat_id}")
            logger.debug(f"Message content: {text[:100]}...")
            
            return True
            
        except telebot.apihelper.ApiException as api_error:
            logger.error(f"❌ Telegram API Error: {str(api_error)}")
            if "Bad Request" in str(api_error):
                logger.error("Check your bot token and chat ID")
            elif "Forbidden" in str(api_error):
                logger.error("Bot doesn't have permission to send messages")
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {str(e)}")
            logger.error(f"Bot Token: {self.token[:6]}...{self.token[-4:]}")
            logger.error(f"Chat ID: {self.chat_id}")
            return False

# Global instance of the Telegram bot
# This instance will be imported by other modules.
telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

# For testing purposes
if __name__ == '__main__':
    logger.info("Testing Telegram Bot...")
    if telegram_bot.bot and telegram_bot.chat_id:
        test_message = "*Telegram Bot Test*\n\nThis is a test message from the platform."
        if telegram_bot.send_message(test_message):
            logger.info("Test message sent successfully!")
        else:
            logger.error("Failed to send test message.")
    else:
        logger.warning("Could not run test. Please configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.")
