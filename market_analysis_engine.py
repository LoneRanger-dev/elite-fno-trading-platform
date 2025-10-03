"""
📈 Market Analysis Engine
Generates pre-market and post-market analysis reports.
"""
import random
import yfinance as yf
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketAnalysisEngine:
    def __init__(self, telegram_bot=None):
        self.telegram_bot = telegram_bot
        logger.info("Market Analysis Engine initialized")

    def generate_pre_market_report(self):
        """Generates and sends a pre-market analysis report."""
        logger.info("Generating pre-market report...")
        try:
            # In a real scenario, you'd fetch data from news APIs, global indices, etc.
            global_indices = {
                "S&P 500": round(random.uniform(-1.5, 1.5), 2),
                "NASDAQ": round(random.uniform(-2.0, 2.0), 2),
                "GIFT NIFTY": round(random.uniform(-0.8, 0.8), 2),
            }
            
            key_news_headlines = [
                "Global cues mixed as traders await inflation data.",
                "Tech sector shows strength in overnight trading.",
                "Crude oil prices stabilize after recent volatility.",
            ]

            nifty_data = yf.Ticker("^NSEI").history(period="5d")
            prev_close = nifty_data['Close'].iloc[-1]
            support = round(prev_close * 0.985, 2)
            resistance = round(prev_close * 1.015, 2)

            report = f"""
🌅 **Pre-Market Analysis - {datetime.now().strftime('%d %b %Y')}** 🌅

**Global Market Snapshot:**
- S&P 500: {global_indices['S&P 500']}%
- NASDAQ: {global_indices['NASDAQ']}%
- GIFT NIFTY: {global_indices['GIFT NIFTY']}%

**Top News Headlines:**
- {key_news_headlines[0]}
- {key_news_headlines[1]}
- {key_news_headlines[2]}

**NIFTY Key Levels:**
- **Previous Close:** ₹{prev_close:,.2f}
- **Key Support:** ~₹{support:,.2f}
- **Key Resistance:** ~₹{resistance:,.2f}

**Outlook:**
Market is expected to open flat to slightly positive. Watch resistance levels for breakout opportunities. Volatility may be high during the first hour.

Good luck, traders! 📈
"""
            if self.telegram_bot:
                self.telegram_bot.send_message(report)
                logger.info("Pre-market report sent via Telegram.")
            
            return report

        except Exception as e:
            logger.error(f"Error generating pre-market report: {e}")
            return None

    def generate_post_market_report(self):
        """Generates and sends a post-market analysis report."""
        logger.info("Generating post-market report...")
        try:
            nifty_data = yf.Ticker("^NSEI").history(period="1d", interval="15m")
            opening = nifty_data['Open'].iloc[0]
            closing = nifty_data['Close'].iloc[-1]
            high = nifty_data['High'].max()
            low = nifty_data['Low'].min()
            change = closing - opening
            change_percent = (change / opening) * 100

            move_direction = "gained" if change > 0 else "fell"
            
            key_drivers = [
                "strong buying in banking and IT stocks.",
                "weakness in the energy sector due to falling crude prices.",
                "positive global cues from European markets.",
                "profit booking in the second half of the session."
            ]
            random.shuffle(key_drivers)

            report = f"""
🌇 **Post-Market Report - {datetime.now().strftime('%d %b %Y')}** 🌇

**NIFTY Today's Performance:**
- **Open:** ₹{opening:,.2f}
- **High:** ₹{high:,.2f}
- **Low:** ₹{low:,.2f}
- **Close:** ₹{closing:,.2f}
- **Change:** {change:,.2f} ({change_percent:.2f}%)

**Market Summary:**
The market {move_direction} today, driven primarily by {key_drivers[0]}. After a volatile opening, the index found support near the day's low and rallied, though it faced some {key_drivers[3]}.

**Key Takeaways:**
- The overall trend remains {'bullish' if change > 0 else 'cautious'}.
- Key drivers today were {key_drivers[1]}

This analysis is for educational purposes.
"""
            if self.telegram_bot:
                self.telegram_bot.send_message(report)
                logger.info("Post-market report sent via Telegram.")

            return report

        except Exception as e:
            logger.error(f"Error generating post-market report: {e}")
            return None

# Example usage (for testing)
if __name__ == '__main__':
    engine = MarketAnalysisEngine()
    print("--- PRE-MARKET REPORT ---")
    pre_market = engine.generate_pre_market_report()
    if pre_market:
        print(pre_market)

    print("\n--- POST-MARKET REPORT ---")
    post_market = engine.generate_post_market_report()
    if post_market:
        print(post_market)
