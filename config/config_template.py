"""
Configuration Template for FnO Trading Platform
Replace placeholder values with your actual credentials
DO NOT commit the actual credentials file to version control
"""

# Telegram Bot Configuration
TELEGRAM_CONFIG = {
    'BOT_TOKEN': 'your_bot_token_here',  # Get from @BotFather
    'CHAT_ID': 'your_chat_id_here',      # Get from @userinfobot
    'ADMIN_USERS': [],                    # List of admin user IDs
    'BROADCAST_CHANNEL': None,            # Optional channel ID for broadcasts
    'NOTIFICATION_SETTINGS': {
        'trade_alerts': True,             # Enable/disable trade alerts
        'market_updates': True,           # Enable/disable market updates
        'risk_warnings': True             # Enable/disable risk warnings
    }
}

# Zerodha Kite Connect Configuration
KITE_CONFIG = {
    'API_KEY': 'your_kite_api_key',      # From Kite developer console
    'API_SECRET': 'your_kite_secret',    # From Kite developer console
    'REQUEST_TIMEOUT': 7,                # API request timeout in seconds
    'ACCESS_TOKEN': None,                # Will be populated during runtime
    'INSTRUMENTS': [                     # Default instruments to track
        'NIFTY50',
        'BANKNIFTY',
    ],
    'API_URL': 'https://api.kite.trade'  # API endpoint
}

# Payment Gateway Configuration (Razorpay)
RAZORPAY_CONFIG = {
    'KEY_ID': 'your_razorpay_key_id',    # From Razorpay dashboard
    'KEY_SECRET': 'your_razorpay_secret', # From Razorpay dashboard
    'WEBHOOK_SECRET': None,               # For webhook verification
    'TEST_MODE': True                     # Set False in production
}

# Trading Parameters
TRADING_CONFIG = {
    'RISK_MANAGEMENT': {
        'max_position_size': 5000,        # Maximum position size in rupees
        'max_trades_per_day': 5,          # Maximum trades per day
        'risk_per_trade': 1.0,            # Risk percentage per trade
        'stop_loss_percent': 2.0,         # Default stop loss percentage
        'target_profit_percent': 4.0      # Default target profit percentage
    },
    'TRADING_HOURS': {
        'start': '09:15',                 # Market open time
        'end': '15:30',                   # Market close time
        'pre_market_scan': '08:45',       # Pre-market analysis time
        'position_squareoff': '15:15'     # Position square off time
    },
    'TIMEFRAMES': {
        'intraday': ['1m', '5m', '15m'],  # Intraday timeframes
        'swing': ['1h', '1d'],            # Swing trading timeframes
        'default': '5m'                   # Default analysis timeframe
    }
}

# Technical Analysis Parameters
ANALYSIS_CONFIG = {
    'INDICATORS': {
        'RSI': {'period': 14, 'overbought': 70, 'oversold': 30},
        'MACD': {'fast': 12, 'slow': 26, 'signal': 9},
        'Supertrend': {'period': 10, 'multiplier': 3},
        'Volume_SMA': {'period': 20}
    },
    'STRATEGY_PARAMS': {
        'trend_strength': 0.7,            # Minimum trend strength
        'volume_factor': 1.5,             # Volume surge factor
        'breakout_atr_factor': 2.0        # Breakout ATR multiplier
    }
}

# Premium Subscription Plans
SUBSCRIPTION_PLANS = {
    'basic': {
        'price': 0,
        'features': [
            'Basic market signals',
            'Daily market summary',
            'Limited historical data'
        ],
        'signal_delay': 300  # 5 minutes delay
    },
    'premium': {
        'price': 999,
        'features': [
            'Real-time trading signals',
            'Advanced technical analysis',
            'Paper trading simulator',
            'Priority support'
        ],
        'signal_delay': 0  # Real-time
    },
    'pro': {
        'price': 2999,
        'features': [
            'All premium features',
            'Custom strategy builder',
            'Real-time market scanner',
            'One-on-one consultation',
            '24/7 priority support'
        ],
        'signal_delay': 0
    }
}

# Web Application Settings
WEB_CONFIG = {
    'DEBUG': False,
    'HOST': '0.0.0.0',
    'PORT': 5500,
    'SECRET_KEY': 'your_secret_key_here',  # Change in production
    'SESSION_LIFETIME': 86400,             # 24 hours in seconds
    'CORS_ORIGINS': ['http://localhost:5500'],
    'API_RATE_LIMIT': {
        'DEFAULT': '100/hour',
        'PREMIUM': '1000/hour'
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    'VERSION': 1,
    'HANDLERS': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/trading_platform.log'
        }
    },
    'ROOT_LOGGER': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}

# Database Configuration
DATABASE_CONFIG = {
    'TYPE': 'sqlite',
    'NAME': 'data/trading_platform.db',
    'BACKUP_ENABLED': True,
    'BACKUP_INTERVAL': 86400,  # Daily backup
    'MAX_BACKUPS': 7          # Keep last 7 days
}

# Email Configuration (for alerts and reports)
EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.gmail.com',
    'SMTP_PORT': 587,
    'USERNAME': 'your_email@gmail.com',
    'PASSWORD': 'your_app_specific_password',
    'USE_TLS': True,
    'FROM_EMAIL': 'noreply@yourplatform.com',
    'ADMIN_EMAIL': 'admin@yourplatform.com'
}