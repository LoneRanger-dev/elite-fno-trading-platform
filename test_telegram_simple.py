"""
Simple Telegram Connection Test
"""
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_telegram_connection():
    """Test Telegram connection using direct API call"""
    
    # Bot credentials
    TOKEN = "8415230764:AAF0Aaqb21Vkq9eWifB_wHDtkm37WrjJRcs"
    CHAT_ID = "7973202689"
    
    # Test message
    message = "🔄 Connection Test Message\nTimestamp: {import time; print(time.strftime('%H:%M:%S'))}"
    
    try:
        # Direct API call to Telegram
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        params = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        print(f"\nTesting connection...")
        print(f"Bot Token: {TOKEN[:6]}...{TOKEN[-4:]}")
        print(f"Chat ID: {CHAT_ID}")
        
        # Make the request
        response = requests.post(url, params=params)
        
        # Check response
        if response.status_code == 200:
            print("\n✅ Message sent successfully!")
            print("📱 Check your Telegram for the test message")
            logger.debug(f"Response: {response.json()}")
        else:
            print(f"\n❌ Failed to send message. Status code: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error(f"Exception: {str(e)}", exc_info=True)

if __name__ == "__main__":
    print("\n🤖 Simple Telegram Connection Tester")
    print("=" * 50)
    test_telegram_connection()
    print("=" * 50)