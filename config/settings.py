from os import environ, path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = environ.get('TELEGRAM_CHAT_ID')

# Kite (Zerodha) API Configuration
KITE_API_KEY = environ.get('KITE_API_KEY')
KITE_API_SECRET = environ.get('KITE_API_SECRET')
KITE_ACCESS_TOKEN = environ.get('KITE_ACCESS_TOKEN')

# Razorpay Configuration
RAZORPAY_KEY_ID = environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = environ.get('RAZORPAY_KEY_SECRET')

# Flask Secret Key
SECRET_KEY = environ.get('FLASK_SECRET_KEY', 'elite-fno-secret-key-2024')

# Platform Settings
DEBUG = False
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5501       # Premium platform port