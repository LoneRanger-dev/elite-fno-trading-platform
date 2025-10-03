"""Configuration settings for Elite FnO Trading Platform"""

# Kite (Zerodha) API Configuration
kite_api_key = 'zfz6i2qjh9zjl26m'
kite_api_secret = 'esdsumpztnzmry8rl1e411b95qt86v2m'
kite_access_token = '9tB7VtbqUGu4btfKkX7E4zO6t7wNOtbt'

# Telegram Bot Configuration
telegram_bot_token = '8415230764:AAF0Aaqb21Vkq9eWifB_wHDtkm37WrjJRcs'
telegram_chat_id = '7973202689'
# Telegram Bot Configuration
BOT_TOKEN = '8415230764:AAF0Aaqb21Vkq9eWifB_wHDtkm37WrjJRcs'
CHAT_ID = '7973202689'

# For backwards compatibility
telegram_bot_token = BOT_TOKEN
telegram_chat_id = CHAT_ID

TELEGRAM_CONFIG = {
    'BOT_TOKEN': BOT_TOKEN,
    'CHAT_ID': CHAT_ID
}

# Razorpay Configuration
RAZORPAY_CONFIG = {
    'KEY_ID': 'rzp_test_ROCO0lEjsGV5nV',
    'KEY_SECRET': 'ZCRd29hmvPla1F0rZUMX8dOn'
}

# Flask Secret Key
SECRET_KEY = 'elite-fno-secret-key-2024'