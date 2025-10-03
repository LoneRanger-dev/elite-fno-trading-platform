"""
Configuration Management for Intraday Trading System
Centralizes all configuration settings and environment variables
"""

import os
import logging
from datetime import datetime, time
from typing import List, Dict, Any
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

class Config:
    """Main configuration class"""
    
    def __init__(self):
        # Base paths
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.DATA_DIR = os.path.join(self.BASE_DIR, 'data')
        self.LOGS_DIR = os.path.join(self.BASE_DIR, 'logs')
        
        # Create directories if they don't exist
        os.makedirs(self.DATA_DIR, exist_ok=True)
        os.makedirs(self.LOGS_DIR, exist_ok=True)
        
        # Telegram Configuration
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8415230764:AAF0Aaqb21Vkq9eWifB_wHDtkm37WrjJRcs')
        self.TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '7973202689')
        self.TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', '7973202689')
        
        # Zerodha Kite Configuration
        self.KITE_API_KEY = os.getenv('KITE_API_KEY', 'zfz6i2qjh9zjl26m')
        self.KITE_API_SECRET = os.getenv('KITE_API_SECRET', 'esdsumpztnzmry8rl1e411b95qt86v2m')
        self.KITE_ACCESS_TOKEN = os.getenv('KITE_ACCESS_TOKEN', '9tB7VtbqUGu4btfKkX7E4zO6t7wNOtbt')
        
        # News API Configuration
        self.NEWS_API_KEY = os.getenv('NEWS_API_KEY')
        
        # Payment Gateway Configuration (Razorpay)
        self.RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', 'rzp_test_ROCO0lEjsGV5nV')
        self.RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', 'ZCRd29hmvPla1F0rZUMX8dOn')
        
        # Database Configuration
        self.DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(self.DATA_DIR, "trading_bot.db")}')
        
        # Trading Configuration
        self.MAX_SIGNALS_PER_DAY = int(os.getenv('MAX_SIGNALS_PER_DAY', 10))
        self.MIN_CONFIDENCE_THRESHOLD = float(os.getenv('MIN_CONFIDENCE_THRESHOLD', 70))
        self.RISK_REWARD_RATIO = float(os.getenv('RISK_REWARD_RATIO', 1.5))
        self.MIN_SIGNAL_INTERVAL = int(os.getenv('MIN_SIGNAL_INTERVAL', 300))  # seconds
        
        # Schedule Configuration
        self.MORNING_NEWS_TIME = os.getenv('MORNING_NEWS_TIME', '06:30')
        self.PRE_MARKET_TIME = os.getenv('PRE_MARKET_TIME', '08:30')
        self.MARKET_OPEN_TIME = os.getenv('MARKET_OPEN_TIME', '09:15')
        self.MARKET_CLOSE_TIME = os.getenv('MARKET_CLOSE_TIME', '15:30')
        self.EVENING_NEWS_TIME = os.getenv('EVENING_NEWS_TIME', '18:30')
        
        # Market Configuration
        self.MARKET_TIMEZONE = pytz.timezone(os.getenv('MARKET_TIMEZONE', 'Asia/Kolkata'))
        self.INSTRUMENTS = os.getenv('INSTRUMENTS', 'NIFTY,BANKNIFTY').split(',')
        
        # Web App Configuration
        self.FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
        self.FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
        self.FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
        self.FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
        
        # Redis Configuration
        self.REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.path.join(self.LOGS_DIR, 'trading_bot.log')
        
        # API Configuration
        self.API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000/api')
        self.MOBILE_API_KEY = os.getenv('MOBILE_API_KEY')
        
        # Technical Analysis Parameters
        self.TA_PARAMS = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'bb_period': 20,
            'bb_std': 2,
            'volume_threshold': 1.5  # Volume surge threshold
        }
        
        # Market Hours
        self.market_open = time(9, 15)  # 9:15 AM
        self.market_close = time(15, 30)  # 3:30 PM
        
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        now = datetime.now(self.MARKET_TIMEZONE).time()
        return self.market_open <= now <= self.market_close
    
    def is_trading_day(self) -> bool:
        """Check if today is a trading day (Monday-Friday)"""
        today = datetime.now(self.MARKET_TIMEZONE).weekday()
        return today < 5  # Monday=0, Friday=4
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        status = {
            'telegram_configured': bool(self.TELEGRAM_BOT_TOKEN and self.TELEGRAM_CHAT_ID),
            'kite_configured': bool(self.KITE_API_KEY and self.KITE_API_SECRET),
            'news_configured': bool(self.NEWS_API_KEY),
            'database_configured': bool(self.DATABASE_URL),
            'errors': []
        }
        
        if not status['telegram_configured']:
            status['errors'].append('Telegram configuration missing')
        
        if not status['kite_configured']:
            status['errors'].append('Kite Connect configuration missing')
        
        if not status['news_configured']:
            status['errors'].append('News API configuration missing')
        
        return status

class LoggingConfig:
    """Logging configuration"""
    
    @staticmethod
    def setup_logging(config: Config):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        # Create logger
        logger = logging.getLogger('TradingBot')
        logger.info("Logging initialized")
        return logger

# Global configuration instance
config = Config()
logger = LoggingConfig.setup_logging(config)

# Export commonly used items
__all__ = ['config', 'logger', 'Config', 'LoggingConfig']