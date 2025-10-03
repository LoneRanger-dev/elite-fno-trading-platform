"""
Generate real-time market test signal
"""

import yfinance as yf
from datetime import datetime, timedelta
from telegram_bot import TelegramBot, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_live_nifty_data():
    """Get real-time NIFTY data"""
    try:
        nifty = yf.Ticker("^NSEI")
        live_data = nifty.history(period="1d", interval="1m")
        
        if not live_data.empty:
            current = live_data.iloc[-1]
            prev_close = live_data.iloc[-2]['Close'] if len(live_data) > 1 else current['Close']
            
            return {
                'ltp': round(float(current['Close']), 2),
                'high': round(float(current['High']), 2),
                'low': round(float(current['Low']), 2),
                'volume': int(current['Volume']),
                'change': round(float(current['Close'] - prev_close), 2),
                'change_percent': round(((float(current['Close'] - prev_close) / prev_close) * 100), 2)
            }
    except Exception as e:
        logger.error(f"Error fetching NIFTY data: {e}")
    return None

def send_live_test_signal():
    """Send a test signal based on current market data"""
    try:
        # Get live NIFTY data
        market_data = get_live_nifty_data()
        if not market_data:
            print("❌ Could not fetch live market data")
            return
            
        # Initialize Telegram bot
        telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        
        # Calculate levels
        spot_price = market_data['ltp']
        atm_strike = round(spot_price / 50) * 50
        
        # Determine signal type based on current momentum
        if market_data['change_percent'] > 0:
            signal_type = "CE"
            entry_price = round(market_data['change'] * 1.2, 2)  # Simulated option premium
            trend_desc = "bullish momentum"
            signal_reason = "Bullish breakout with volume confirmation"
        else:
            signal_type = "PE"
            entry_price = round(abs(market_data['change']) * 1.2, 2)  # Simulated option premium
            trend_desc = "bearish momentum"
            signal_reason = "Bearish breakdown with volume confirmation"

        # Create detailed signal message
        signal_msg = f"""
🎯 *LIVE MARKET TEST SIGNAL ({signal_type}) - DO NOT TRADE*

*NIFTY {signal_type} SETUP ({datetime.now().strftime('%H:%M:%S')}):*
Current Spot: {spot_price}
Strike: NIFTY {atm_strike} {signal_type}
Movement: {market_data['change_percent']}% ({market_data['change']})

*ENTRY PARAMETERS:*
Entry Price: ₹{entry_price}
Target 1: ₹{round(entry_price * 1.15, 2)} (+15%)
Target 2: ₹{round(entry_price * 1.25, 2)} (+25%)
Stop Loss: ₹{round(entry_price * 0.85, 2)} (-15%)
Lot Size: 50

*REAL-TIME TECHNICAL SETUP:*
• Current {trend_desc}
• Day's High: {market_data['high']}
• Day's Low: {market_data['low']}
• Volume Analysis: {market_data['volume']:,} 

*KEY LEVELS:*
🔵 Support 1: {atm_strike-50}
🔵 Support 2: {atm_strike-100}
🔴 Resistance 1: {atm_strike+50}
🔴 Resistance 2: {atm_strike+100}

*Signal Reasoning:*
{signal_reason}

*Risk Management (Per Lot):*
• Max Risk: ₹{round(entry_price * 0.15 * 50, 2)}
• Potential Profit: ₹{round(entry_price * 0.25 * 50, 2)}
• Risk:Reward = 1:1.67

⚠️ This is a TEST signal based on LIVE market data
⏰ Generated at {datetime.now().strftime('%H:%M:%S')}
"""
        
        # Send signal
        telegram_bot.send_message(signal_msg)
        print("✅ Live market test signal sent successfully!")
        
    except Exception as e:
        logger.error(f"Error sending live test signal: {e}")
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("\n🔄 Generating Live Market Test Signal...")
    print("=" * 50)
    send_live_test_signal()
    print("=" * 50)
    print("\nCheck your Telegram for the live market test signal!")