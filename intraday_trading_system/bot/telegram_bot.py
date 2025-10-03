"""
Telegram Bot Integration
Handles sending messages, signals, news, and analysis to Telegram channel
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

# Local imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config, logger

class TelegramBot:
    """Telegram bot for sending trading signals and updates"""
    
    def __init__(self):
        self.logger = logger
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.channel_id = config.TELEGRAM_CHANNEL_ID
        
        if not self.bot_token:
            raise ValueError("Telegram bot token not configured")
        
        self.bot = Bot(token=self.bot_token)
        self.logger.info("Telegram bot initialized")
    
    async def send_message(self, message: str, chat_id: Optional[str] = None, parse_mode: str = ParseMode.HTML) -> bool:
        """Send a message to Telegram"""
        try:
            target_chat = chat_id or self.chat_id
            await self.bot.send_message(
                chat_id=target_chat,
                text=message,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
            return True
        except TelegramError as e:
            self.logger.error(f"Telegram error: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return False
    
    async def send_to_channel(self, message: str) -> bool:
        """Send message to Telegram channel"""
        if self.channel_id:
            return await self.send_message(message, self.channel_id)
        return await self.send_message(message)
    
    async def send_trading_signal(self, signal) -> bool:
        """Send trading signal with rich formatting"""
        try:
            # Calculate risk and reward percentages
            risk_pct = ((signal.entry_price - signal.stop_loss) / signal.entry_price) * 100
            reward_pct = ((signal.target_price - signal.entry_price) / signal.entry_price) * 100
            
            # Format confidence as percentage
            confidence_pct = int(signal.confidence)
            
            # Choose emoji based on signal type
            signal_emoji = "🟢" if signal.signal_type == "BUY" else "🔴"
            
            message = f"""
{signal_emoji} <b>LIVE TRADING SIGNAL</b> {signal_emoji}

⏰ <b>Time:</b> {signal.timestamp}
📊 <b>Instrument:</b> {signal.instrument}
📍 <b>Signal:</b> {signal.signal_type}

💰 <b>Entry Price:</b> ₹{signal.entry_price:.2f}
🎯 <b>Target:</b> ₹{signal.target_price:.2f} (+{reward_pct:.1f}%)
🛑 <b>Stop Loss:</b> ₹{signal.stop_loss:.2f} (-{risk_pct:.1f}%)

📈 <b>Risk:Reward:</b> 1:{signal.risk_reward_ratio:.1f}
🔍 <b>Setup:</b> {signal.setup_description}
📊 <b>Confidence:</b> {confidence_pct}%

📉 <b>Technical Indicators:</b>
"""
            
            # Add technical indicators
            for indicator, value in signal.technical_indicators.items():
                if isinstance(value, (int, float)):
                    message += f"  • <b>{indicator.upper()}:</b> {value:.2f}\n"
                else:
                    message += f"  • <b>{indicator.upper()}:</b> {value}\n"
            
            message += "\n⚡ <i>Trade at your own risk. Follow proper position sizing.</i>"
            
            return await self.send_to_channel(message)
            
        except Exception as e:
            self.logger.error(f"Error sending trading signal: {str(e)}")
            return False
    
    async def send_morning_news(self, news_data: List[Dict]) -> bool:
        """Send morning news alert"""
        try:
            message = f"""
🌅 <b>MORNING NEWS ALERT</b> 🌅
📅 {datetime.now().strftime('%d %B %Y')}

📰 <b>Top Market Moving News:</b>

"""
            
            for i, news in enumerate(news_data[:5], 1):
                impact_emoji = self._get_impact_emoji(news.get('impact', 'neutral'))
                message += f"""
{i}. {impact_emoji} <b>{news['title']}</b>
   📝 {news['summary']}
   🔗 <a href="{news['url']}">Read More</a>

"""
            
            message += "📊 <i>Stay informed, trade smart!</i>"
            
            return await self.send_to_channel(message)
            
        except Exception as e:
            self.logger.error(f"Error sending morning news: {str(e)}")
            return False
    
    async def send_pre_market_analysis(self, analysis: Dict) -> bool:
        """Send pre-market analysis"""
        try:
            sentiment_emoji = self._get_sentiment_emoji(analysis.get('sentiment', 'neutral'))
            
            message = f"""
📊 <b>PRE-MARKET ANALYSIS</b> 📊
🕰️ {datetime.now().strftime('%d %B %Y - %H:%M')}

🌍 <b>Global Markets:</b>
  • US Markets: {analysis.get('us_markets', 'N/A')}
  • Asian Markets: {analysis.get('asian_markets', 'N/A')}
  • European Markets: {analysis.get('european_markets', 'N/A')}

🇮🇳 <b>Indian Futures:</b>
  • Nifty Futures: {analysis.get('nifty_futures', 'N/A')}
  • Bank Nifty: {analysis.get('bank_nifty_futures', 'N/A')}

{sentiment_emoji} <b>Market Sentiment:</b> {analysis.get('sentiment', 'Neutral')}

📈 <b>Key Levels:</b>
  • Support: {analysis.get('support_level', 'N/A')}
  • Resistance: {analysis.get('resistance_level', 'N/A')}

🎯 <b>Trading Outlook:</b>
{analysis.get('outlook', 'Market analysis in progress...')}

💡 <i>Trade with the trend, manage your risk!</i>
"""
            
            return await self.send_to_channel(message)
            
        except Exception as e:
            self.logger.error(f"Error sending pre-market analysis: {str(e)}")
            return False
    
    async def send_post_market_analysis(self, analysis: Dict) -> bool:
        """Send post-market analysis"""
        try:
            message = f"""
📉 <b>POST-MARKET ANALYSIS</b> 📉
🕕 {datetime.now().strftime('%d %B %Y - %H:%M')}

📊 <b>Market Performance:</b>
  • Nifty: {analysis.get('nifty_change', 'N/A')}
  • Bank Nifty: {analysis.get('bank_nifty_change', 'N/A')}
  • Fin Nifty: {analysis.get('fin_nifty_change', 'N/A')}

🚀 <b>Top Gainers:</b>
"""
            
            for gainer in analysis.get('top_gainers', [])[:3]:
                message += f"  • {gainer.get('symbol', 'N/A')}: +{gainer.get('change', 'N/A')}%\n"
            
            message += "\n📉 <b>Top Losers:</b>\n"
            
            for loser in analysis.get('top_losers', [])[:3]:
                message += f"  • {loser.get('symbol', 'N/A')}: {loser.get('change', 'N/A')}%\n"
            
            message += f"""

🔍 <b>Why the market moved:</b>
{analysis.get('market_reason', 'Multiple factors influenced today\'s market movement.')}

🏢 <b>Sector Performance:</b>
  • Best: {analysis.get('best_sector', 'N/A')}
  • Worst: {analysis.get('worst_sector', 'N/A')}

📋 <b>Key Takeaways for Tomorrow:</b>
{analysis.get('tomorrow_outlook', 'Monitor global cues and domestic developments.')}

📈 <i>Review, learn, and prepare for tomorrow!</i>
"""
            
            return await self.send_to_channel(message)
            
        except Exception as e:
            self.logger.error(f"Error sending post-market analysis: {str(e)}")
            return False
    
    async def send_evening_news(self, news_data: List[Dict]) -> bool:
        """Send evening news alert"""
        try:
            message = f"""
🌙 <b>EVENING NEWS ALERT</b> 🌙
📅 {datetime.now().strftime('%d %B %Y')}

📰 <b>News Impacting Tomorrow's Market:</b>

"""
            
            for i, news in enumerate(news_data[:5], 1):
                impact_emoji = self._get_impact_emoji(news.get('impact', 'neutral'))
                message += f"""
{i}. {impact_emoji} <b>{news['title']}</b>
   📝 {news['summary']}
   📊 Impact: {news.get('impact', 'Neutral')}
   🔗 <a href="{news['url']}">Read More</a>

"""
            
            message += "🌟 <i>Stay prepared for tomorrow's opportunities!</i>"
            
            return await self.send_to_channel(message)
            
        except Exception as e:
            self.logger.error(f"Error sending evening news: {str(e)}")
            return False
    
    async def send_startup_message(self) -> bool:
        """Send bot startup message"""
        message = f"""
🚀 <b>TRADING BOT STARTED</b> 🚀

✅ System initialized successfully
📅 Date: {datetime.now().strftime('%d %B %Y')}
🕐 Time: {datetime.now().strftime('%H:%M:%S IST')}

📊 <b>Today's Schedule:</b>
  • 06:30 - Morning News Alert
  • 08:30 - Pre-Market Analysis  
  • 09:15-15:30 - Live Trading Signals
  • 15:30 - Post-Market Analysis
  • 18:30 - Evening News Alert

💪 <b>Ready to deliver premium signals!</b>
        """
        
        return await self.send_to_channel(message)
    
    async def send_shutdown_message(self) -> bool:
        """Send bot shutdown message"""
        message = f"""
🛑 <b>TRADING BOT STOPPED</b>

📅 Shutdown: {datetime.now().strftime('%d %B %Y - %H:%M:%S IST')}
        
✅ All systems safely terminated
💤 Bot is now offline

🔄 <i>Will resume when restarted</i>
        """
        
        return await self.send_to_channel(message)
    
    async def send_error_alert(self, error_message: str) -> bool:
        """Send error alert to admin"""
        message = f"""
⚠️ <b>SYSTEM ERROR ALERT</b> ⚠️

🕐 Time: {datetime.now().strftime('%H:%M:%S IST')}
❌ Error: {error_message}

🔧 <i>Please check system logs</i>
        """
        
        return await self.send_message(message)  # Send to admin chat
    
    def _get_impact_emoji(self, impact: str) -> str:
        """Get emoji for news impact"""
        impact_lower = impact.lower()
        if 'bullish' in impact_lower or 'positive' in impact_lower:
            return "🟢"
        elif 'bearish' in impact_lower or 'negative' in impact_lower:
            return "🔴"
        else:
            return "🟡"
    
    def _get_sentiment_emoji(self, sentiment: str) -> str:
        """Get emoji for market sentiment"""
        sentiment_lower = sentiment.lower()
        if 'bullish' in sentiment_lower:
            return "📈"
        elif 'bearish' in sentiment_lower:
            return "📉"
        else:
            return "➡️"
    
    async def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        try:
            test_message = "🔧 Bot connection test - " + datetime.now().strftime('%H:%M:%S')
            return await self.send_message(test_message)
        except Exception as e:
            self.logger.error(f"Telegram connection test failed: {str(e)}")
            return False

# Test function
async def test_telegram_bot():
    """Test telegram bot functionality"""
    bot = TelegramBot()
    success = await bot.test_connection()
    print(f"Telegram bot test: {'✅ Success' if success else '❌ Failed'}")

if __name__ == "__main__":
    asyncio.run(test_telegram_bot())