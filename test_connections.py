"""
Verify all API connections
"""
import requests
import logging
from kiteconnect import KiteConnect
import json

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Credentials
TELEGRAM_CONFIG = {
    'token': "8415230764:AAF0Aaqb21Vkq9eWifB_wHDtkm37WrjJRcs",
    'chat_id': "7973202689"
}

KITE_CONFIG = {
    'api_key': "zfz6i2qjh9zjl26m",
    'api_secret': "esdsumpztnzmry8rl1e411b95qt86v2m",
    'access_token': "9tB7VtbqUGu4btfKkX7E4zO6t7wNOtbt"
}

def test_telegram():
    """Test Telegram connection"""
    print("\n🔄 Testing Telegram Connection...")
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_CONFIG['token']}/sendMessage"
        message = (
            "🔄 *Connection Test*\n\n"
            "Testing signal system connection...\n"
            "If you see this message, Telegram is working!\n\n"
            "_Please respond with 'OK' if you received this._"
        )
        
        response = requests.post(url, {
            'chat_id': TELEGRAM_CONFIG['chat_id'],
            'text': message,
            'parse_mode': 'Markdown'
        })
        
        if response.status_code == 200:
            print("✅ Telegram: Message sent successfully!")
            return True
        else:
            print(f"❌ Telegram Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram Exception: {str(e)}")
        return False

def test_kite():
    """Test Kite Connect"""
    print("\n🔄 Testing Kite Connection...")
    
    try:
        kite = KiteConnect(api_key=KITE_CONFIG['api_key'])
        kite.set_access_token(KITE_CONFIG['access_token'])
        
        # Try to get profile info
        profile = kite.profile()
        print("✅ Kite: Connection successful!")
        print(f"Connected as: {profile['user_name']}")
        return True
        
    except Exception as e:
        print(f"❌ Kite Exception: {str(e)}")
        return False

def main():
    print("\n🔧 API Connection Tester")
    print("=" * 50)
    
    # Test Telegram
    telegram_ok = test_telegram()
    
    # Test Kite
    kite_ok = test_kite()
    
    # Summary
    print("\n📋 Connection Summary:")
    print(f"Telegram: {'✅' if telegram_ok else '❌'}")
    print(f"Kite Connect: {'✅' if kite_ok else '❌'}")
    
    if telegram_ok and kite_ok:
        print("\n✨ All connections working! Ready to start signal generation.")
    else:
        print("\n⚠️ Some connections failed. Please check the errors above.")

if __name__ == "__main__":
    main()