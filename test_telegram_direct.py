"""
Direct Telegram API Test
"""
import requests
import time

def test_bot_info():
    """Test bot info and existence"""
    BOT_TOKEN = "8415230764:AAF0Aaqb21Vkq9eWifB_wHDtkm37WrjJRcs"
    CHAT_ID = "7973202689"
    
    print("\n🔄 Testing Telegram Bot...")
    print(f"Bot Token: {BOT_TOKEN[:8]}...{BOT_TOKEN[-4:]}")
    print(f"Chat ID: {CHAT_ID}")
    
    try:
        # 1. Check if bot exists
        print("\nChecking bot information...")
        response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe")
        if response.status_code == 200:
            bot_info = response.json()['result']
            print(f"\n✅ Bot Found!")
            print(f"Bot Name: {bot_info.get('first_name')}")
            print(f"Bot Username: @{bot_info.get('username')}")
        else:
            print(f"\n❌ Bot not found or token invalid")
            print(f"Error: {response.text}")
            return
        
        # 2. Try sending a message
        print("\nTrying to send test message...")
        message_text = (
            "🔵 Telegram Bot Test Message\n\n"
            f"Time: {time.strftime('%H:%M:%S')}\n"
            "If you see this message, please reply with 'OK'"
        )
        
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": message_text,
                "parse_mode": "HTML"
            }
        )
        
        if response.status_code == 200:
            print("✅ Message sent successfully!")
            print("\n📱 Please check your Telegram for the test message")
            print("⚠️ Important: You need to:")
            print("1. Find this bot in Telegram using the username above")
            print("2. Click START or send /start to the bot")
            print("3. Then you'll receive messages")
        else:
            print(f"\n❌ Failed to send message")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🤖 Telegram Bot Direct API Tester")
    print("=" * 50)
    test_bot_info()
    print("=" * 50)