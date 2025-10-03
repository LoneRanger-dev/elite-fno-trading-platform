"""
Setup script for FnO Trading Platform
Handles environment setup, database initialization, and dependency installation
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path
from subprocess import check_call, CalledProcessError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/setup.log')
    ]
)
logger = logging.getLogger(__name__)

def install_dependencies():
    """Install required Python packages"""
    try:
        packages = [
            "flask==2.3.3",
            "flask-cors==4.0.0",
            "flask-socketio==5.3.6",
            "requests==2.31.0",
            "pandas==2.1.1",
            "numpy==1.24.3",
            "python-dotenv==1.0.0",
            "schedule==1.2.0",
            "kiteconnect==4.2.0",
            "yfinance==0.2.22",
            "plotly==5.16.1",
            "matplotlib==3.7.2",
            "python-telegram-bot==20.5",
            "telegram==0.0.1",
            "razorpay"
        ]
        
        for package in packages:
            logger.info(f"Installing {package}")
            check_call([sys.executable, "-m", "pip", "install", package])
            
        logger.info("All dependencies installed successfully")
        return True
        
    except CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}", exc_info=True)
        return False

def setup_directories():
    """Create required directories"""
    directories = [
        "data",
        "logs",
        "config/secure",
        "static/css",
        "static/js",
        "static/images",
        "templates"
    ]
    
    try:
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create directories: {e}", exc_info=True)
        return False

def init_database():
    """Initialize SQLite databases with schema"""
    try:
        # Users database
        with sqlite3.connect('data/users.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                subscription_type TEXT DEFAULT 'basic',
                subscription_end_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Trading signals database
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                entry_price REAL,
                target_price REAL,
                stop_loss REAL,
                timeframe TEXT,
                strategy TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Paper trading history
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS paper_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                symbol TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                entry_price REAL,
                exit_price REAL,
                quantity INTEGER,
                pnl REAL,
                trade_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        return False

def create_config_template():
    """Create template for configuration files"""
    try:
        template = '''"""
API Credentials and Configuration Template
Replace placeholder values with your actual credentials
"""

TELEGRAM_CONFIG = {
    'BOT_TOKEN': 'your_bot_token_here',
    'CHAT_ID': 'your_chat_id_here'
}

KITE_CONFIG = {
    'API_KEY': 'your_kite_api_key',
    'API_SECRET': 'your_kite_api_secret'
}

RAZORPAY_CONFIG = {
    'KEY_ID': 'your_razorpay_key',
    'KEY_SECRET': 'your_razorpay_secret'
}

# Premium subscription plans
SUBSCRIPTION_PLANS = {
    'basic': {
        'price': 0,
        'features': ['Basic signals', 'Daily market summary']
    },
    'premium': {
        'price': 999,
        'features': ['Advanced signals', 'Real-time alerts', 'Paper trading']
    },
    'pro': {
        'price': 2999,
        'features': ['All premium features', 'Custom strategies', '24/7 support']
    }
}

# Trading parameters
TRADING_CONFIG = {
    'max_trades_per_day': 5,
    'default_quantity': 1,
    'risk_per_trade': 1.0,  # percentage
    'trading_hours': {
        'start': '09:15',
        'end': '15:30'
    }
}
'''
        
        config_path = Path('config/secure/api_credentials_template.py')
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(template)
        
        logger.info("Configuration template created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create config template: {e}", exc_info=True)
        return False

def main():
    """Main setup function"""
    logger.info("Starting FnO Trading Platform setup")
    
    # Setup directories
    if not setup_directories():
        sys.exit(1)
        
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
        
    # Initialize database
    if not init_database():
        sys.exit(1)
        
    # Create config template
    if not create_config_template():
        sys.exit(1)
        
    logger.info("Setup completed successfully!")
    logger.info("Please update config/secure/api_credentials.py with your credentials")
    logger.info("Run START_PLATFORM.bat to start the trading platform")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "init_db":
        init_database()
    else:
        main()