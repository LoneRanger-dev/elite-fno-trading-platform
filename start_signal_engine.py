"""
Start Signal Engine
Initializes and runs the live signal generation engine
"""

import logging
import time
from live_signal_engine import LiveSignalEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Initialize signal engine
        logger.info("Initializing LiveSignalEngine...")
        engine = LiveSignalEngine()
        
        # Send test signal to verify setup
        from live_signal_engine import TradingSignal
        from datetime import datetime
        
        test_signal = TradingSignal(
            id="TEST_001",
            timestamp=datetime.now(),
            instrument="NIFTY",
            option_symbol="NIFTY 24500 CE",
            signal_type="TEST_SIGNAL",
            strike_price=24500,
            option_entry_price=150.0,
            option_target_price=180.0,
            option_stop_loss=135.0,
            confidence=95.0,
            setup_description="Test signal to verify system setup",
            technical_indicators={"RSI": 65, "MACD": "Bullish"},
            risk_reward_ratio=2.0,
            expiry_date="25-OCT-2025",
            lot_size=50
        )
        
        logger.info("Sending test signal...")
        engine.send_signal_notification(test_signal)
        logger.info("Test signal sent successfully")
        
        # Keep the engine running
        logger.info("Signal engine started successfully")
        while True:
            # Add your signal generation logic here
            time.sleep(60)  # Check for signals every minute
            
    except KeyboardInterrupt:
        logger.info("Signal engine stopped by user")
    except Exception as e:
        logger.error(f"Signal engine error: {e}", exc_info=True)

if __name__ == "__main__":
    main()