"""
🚀 Start Live Signal Generation
"""

from live_signal_engine import LiveSignalEngine
from market_data_provider import initialize_market_data_provider
from telegram_bot import TelegramBot, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_live_signals():
    """Start live signal generation system optimized for quick intraday profits"""
    try:
        # Initialize Telegram bot
        telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        
        # Initialize market data provider with faster updates
        kite_config = {
            'api_key': 'zfz6i2qjh9zjl26m',
            'api_secret': 'esdsumpztnzmry8rl1e411b95qt86v2m',
            'access_token': '9tB7VtbqUGu4btfKkX7E4zO6t7wNOtbt'
        }
        market_data_provider = initialize_market_data_provider(kite_config)
        
        # Initialize signal engine with optimized settings for quick profits
        signal_engine = LiveSignalEngine(market_data_provider, telegram_bot)
        
        # Configure for ultra-aggressive scalping
        signal_engine.signal_cooldown = 60  # 1 minute between signals
        signal_engine.min_confidence = 65  # Lower threshold for more frequent signals
        signal_engine.strategy_params = {
            'vwap': {
                'reversal_confirmation_period': 1,  # Immediate confirmation
                'volume_threshold': 1.1  # Minimal volume requirement
            },
            'momentum': {
                'ema_fast': 3,  # Ultra-fast EMA
                'ema_slow': 8,  # Quick trend following
                'rsi_period': 7,  # Very fast RSI
                'rsi_overbought': 80,  # Wider range for trends
                'rsi_oversold': 20
            },
            'breakout': {
                'volume_surge_threshold': 1.2,  # Quick breakout detection
                'consolidation_periods': 1,  # Immediate pattern recognition
                'minimum_consolidation_width': 0.2  # Very tight ranges
            },
            'risk_management': {
                'max_risk_per_trade': 0.7,  # Slightly higher risk for quick profits
                'minimum_risk_reward': 1.2,  # Faster profit taking
                'trailing_stop': 0.2  # Very tight trailing stop
            }
        }
        }
        
        # Send startup notification
        telegram_bot.send_message(
            "⚡ *ULTRA-AGGRESSIVE Scalping System Activated*\n\n"
            "Optimized for Quick Scalps until 3:30 PM\n\n"
            "Monitoring:\n"
            "🎯 NIFTY Options (Ultra-Fast Scalps)\n"
            "🎯 BANKNIFTY Options (Quick Reversals)\n\n"
            "Aggressive Features:\n"
            "⚡ 1-minute signal frequency\n"
            "� Ultra-fast momentum detection\n"
            "💫 Instant pattern recognition\n"
            "💰 Multiple small profit captures\n"
            "🎯 Cumulative target: ₹500+\n\n"
            "Quick Scalping Rules:\n"
            "⚠️ Use exact entry/exit points\n"
            "🎯 Take profits quickly (1.2:1 RR)\n"
            "⏱️ Max hold time: 15 minutes\n"
            "� Quick position sizing\n\n"
            "IMPORTANT SCALPING TIPS:\n"
            "1️⃣ Enter/Exit precisely\n"
            "2️⃣ Book profits quickly\n"
            "3️⃣ Cut losses immediately\n"
            "4️⃣ No averaging/holding\n\n"
            "_Ultra-fast signals incoming! Stay extremely alert!_"
        )
        
        # Start signal generation
        signal_engine.start_signal_generation()
        
        logger.info("Quick profit signal system activated")
        return signal_engine
        
    except Exception as e:
        logger.error(f"Failed to start signal generation: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting Live FnO Signal Generation")
    print("=" * 50)
    print("System will:")
    print("1. Monitor NIFTY and BANKNIFTY options")
    print("2. Generate signals based on technical analysis")
    print("3. Broadcast signals to Telegram")
    print("\nSignals will be sent to:")
    print(f"Chat ID: {TELEGRAM_CHAT_ID}")
    print("\nPress Ctrl+C to stop")
    print("=" * 50)
    
    engine = start_live_signals()
    
    try:
        # Keep main thread alive
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        if engine:
            engine.stop_signal_generation()
        print("\n\n✅ Signal generation stopped")