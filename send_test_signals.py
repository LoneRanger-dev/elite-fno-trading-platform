"""
Generate detailed CE/PE test signals for validation
"""

from live_signal_engine import LiveSignalEngine
from market_data_provider import initialize_market_data_provider
from telegram_bot import TelegramBot, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_detailed_test_signals():
    """Send detailed CE and PE test signals"""
    try:
        # Initialize components
        telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        
        # Current market simulation
        spot_price = 19850
        atm_strike = round(spot_price / 50) * 50
        expiry = (datetime.now() + timedelta(days=2)).strftime('%d-%b-%Y')
        
        # 1. CALL OPTION (CE) SIGNAL
        ce_signal = f"""
🎯 *TEST SIGNAL (CE) - DO NOT TRADE*

*NIFTY CALL OPTION SETUP:*
Symbol: NIFTY {atm_strike} CE
Current Spot: {spot_price}
Expiry: {expiry}

*ENTRY PARAMETERS:*
Entry Price: ₹155.50
Target 1: ₹170.00 (+9.3%)
Target 2: ₹188.00 (+20.9%)
Stop Loss: ₹140.00 (-10%)
Lot Size: 50

*TECHNICAL SETUP:*
• Strong bullish momentum detected
• Price broke above key resistance
• Volume: 2.3x average (High)
• RSI: 68.5 (Bullish)
• VWAP: Price above VWAP
• PCR: 0.85 (Bullish bias)

*KEY LEVELS:*
🔵 Support 1: {atm_strike-50}
🔵 Support 2: {atm_strike-100}
🔴 Resistance 1: {atm_strike+50}
🔴 Resistance 2: {atm_strike+100}

*Risk Management:*
• Risk per lot: ₹775
• Potential profit: ₹1,625
• Risk:Reward = 1:2.1

⚠️ This is a TEST signal for format validation
"""

        # 2. PUT OPTION (PE) SIGNAL
        pe_signal = f"""
🎯 *TEST SIGNAL (PE) - DO NOT TRADE*

*NIFTY PUT OPTION SETUP:*
Symbol: NIFTY {atm_strike} PE
Current Spot: {spot_price}
Expiry: {expiry}

*ENTRY PARAMETERS:*
Entry Price: ₹142.25
Target 1: ₹156.50 (+10%)
Target 2: ₹170.70 (+20%)
Stop Loss: ₹128.00 (-10%)
Lot Size: 50

*TECHNICAL SETUP:*
• Bearish reversal pattern forming
• Price below key support
• Volume: 1.8x average
• RSI: 32.5 (Bearish)
• VWAP: Price below VWAP
• PCR: 1.25 (Bearish bias)

*KEY LEVELS:*
🔴 Resistance 1: {atm_strike}
🔴 Resistance 2: {atm_strike+50}
🔵 Support 1: {atm_strike-50}
🔵 Support 2: {atm_strike-100}

*Risk Management:*
• Risk per lot: ₹715
• Potential profit: ₹1,425
• Risk:Reward = 1:2

⚠️ This is a TEST signal for format validation
"""
        
        # Send both signals
        print("Sending CE signal...")
        telegram_bot.send_message(ce_signal)
        
        # Wait briefly between signals
        import time
        time.sleep(2)
        
        print("Sending PE signal...")
        telegram_bot.send_message(pe_signal)
        
        print("✅ Test signals sent successfully!")
        
    except Exception as e:
        logger.error(f"Error sending test signals: {e}")
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("\n🔄 Sending Detailed CE/PE Test Signals...")
    print("=" * 50)
    send_detailed_test_signals()
    print("=" * 50)
    print("\nCheck your Telegram for the test signals!")