"""
Enhanced Scheduled Alert System
Implements 4 daily alerts: 6:30 AM news, 8:30 AM pre-market, 3:30 PM post-market, 6:30 PM evening news
"""

import schedule
import time
import datetime
import pytz
from typing import Dict, Any, List
import logging
from services.multi_broker import enhanced_trading_system
from models.user import UserManager
import asyncio
import threading

logger = logging.getLogger(__name__)

class ScheduledAlertSystem:
    """Manages all scheduled alerts and notifications"""
    
    def __init__(self, telegram_token: str, premium_chat_id: str):
        self.telegram_token = telegram_token
        self.premium_chat_id = premium_chat_id
        self.user_manager = UserManager()
        self.tz = pytz.timezone('Asia/Kolkata')
        self.is_running = False
        self.scheduler_thread = None
        
        # Setup all scheduled jobs
        self.setup_schedule()
    
    def setup_schedule(self):
        """Setup all scheduled jobs"""
        # 6:30 AM - Morning news alert
        schedule.every().day.at("06:30").do(self.send_morning_news)
        
        # 8:30 AM - Pre-market analysis
        schedule.every().day.at("08:30").do(self.send_premarket_analysis)
        
        # 9:15 AM - Market open alert
        schedule.every().day.at("09:15").do(self.send_market_open_alert)
        
        # 12:00 PM - Mid-day market update
        schedule.every().day.at("12:00").do(self.send_midday_update)
        
        # 3:30 PM - Post-market analysis
        schedule.every().day.at("15:30").do(self.send_postmarket_analysis)
        
        # 6:30 PM - Evening news and tomorrow's outlook
        schedule.every().day.at("18:30").do(self.send_evening_news)
        
        # Every 15 minutes during market hours - live signals
        schedule.every(15).minutes.do(self.send_live_signals)
        
        logger.info("✅ Scheduled alerts configured")
    
    def start_scheduler(self):
        """Start the scheduler in a separate thread"""
        if self.is_running:
            return
            
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("🚀 Scheduled alert system started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("⏹️ Scheduled alert system stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def send_morning_news(self):
        """6:30 AM - Send morning market news"""
        try:
            now = datetime.datetime.now(self.tz)
            if now.weekday() >= 5:  # Skip weekends
                return
                
            logger.info("📰 Sending morning news alert...")
            
            # Get market news
            news = enhanced_trading_system.get_market_news()
            
            # Create message
            message = f"""🌅 **GOOD MORNING! Market News Alert**
📅 {now.strftime('%d %B %Y, %A')}

📰 **Top 5 Market-Moving News:**

"""
            
            for i, item in enumerate(news[:5], 1):
                message += f"{i}. [{item['title']}]({item['url']})\n   📊 Source: {item['source']}\n\n"
            
            message += """
⏰ **Today's Schedule:**
• 8:30 AM - Pre-market Analysis
• 9:15 AM - Market Open Alert  
• 12:00 PM - Mid-day Update
• 3:30 PM - Post-market Analysis
• 6:30 PM - Evening Outlook

🎯 **Premium subscribers get live trading signals during market hours!**
"""
            
            # Send to premium subscribers
            self._send_to_premium_subscribers(message)
            
        except Exception as e:
            logger.error(f"Error sending morning news: {e}")
    
    def send_premarket_analysis(self):
        """8:30 AM - Send pre-market analysis"""
        try:
            now = datetime.datetime.now(self.tz)
            if now.weekday() >= 5:  # Skip weekends
                return
                
            logger.info("📈 Sending pre-market analysis...")
            
            message = f"""📈 **PRE-MARKET ANALYSIS**
📅 {now.strftime('%d %B %Y')} | ⏰ 8:30 AM

🎯 **Key Levels to Watch:**
• **NIFTY**: Support 19800, Resistance 20200
• **BANK NIFTY**: Support 44500, Resistance 45200

📊 **Pre-Market Movers:**
• Top Gainers: TCS, INFY, HDFCBANK
• Top Losers: RELIANCE, ICICIBANK

🌍 **Global Cues:**
• US Markets: Mixed closing
• Asian Markets: Positive start
• SGX Nifty: +50 points

⚡ **Trading Strategy:**
• Buy on dips near support levels
• Book profits near resistance
• Watch for breakout above key levels

🚨 **Market opens in 45 minutes!**
"""
            
            self._send_to_premium_subscribers(message)
            
        except Exception as e:
            logger.error(f"Error sending pre-market analysis: {e}")
    
    def send_market_open_alert(self):
        """9:15 AM - Market open alert"""
        try:
            now = datetime.datetime.now(self.tz)
            if not enhanced_trading_system.is_market_open(now):
                return
                
            logger.info("🔔 Sending market open alert...")
            
            message = f"""🔔 **MARKET IS NOW OPEN!**
📅 {now.strftime('%d %B %Y')} | ⏰ 9:15 AM

📊 **Opening Bell Analysis:**
• Market Status: ✅ OPEN
• Trading Session: 9:15 AM - 3:30 PM

🎯 **Live Signal Mode ACTIVATED**
Premium subscribers will now receive:
• Real-time breakout alerts
• CE/PE signals with OI analysis  
• Technical indicator updates
• Volume spike notifications

⚡ **Stay Alert for Live Signals!**
"""
            
            self._send_to_premium_subscribers(message)
            
        except Exception as e:
            logger.error(f"Error sending market open alert: {e}")
    
    def send_midday_update(self):
        """12:00 PM - Mid-day market update"""
        try:
            now = datetime.datetime.now(self.tz)
            if not enhanced_trading_system.is_market_open(now):
                return
                
            logger.info("📊 Sending mid-day update...")
            
            # Get current market scan
            scan_result = enhanced_trading_system.run_market_scan()
            
            message = f"""📊 **MID-DAY MARKET UPDATE**
📅 {now.strftime('%d %B %Y')} | ⏰ 12:00 PM

📈 **Market Performance:**
• Session: 50% Complete
• Time Remaining: 3.5 hours

🎯 **Active Breakouts:**
"""
            
            if scan_result.get('breakouts'):
                for breakout in scan_result['breakouts'][:3]:
                    message += f"• **{breakout['symbol']}**: {breakout['signal']} ({breakout['confidence']}% confidence)\n"
            else:
                message += "• No major breakouts detected\n"
            
            message += """
⚡ **Afternoon Strategy:**
• Monitor for post-lunch momentum
• Watch for 2:30 PM institutional activity
• Prepare for closing hour volatility

🔥 **Premium signals continue until 3:30 PM!**
"""
            
            self._send_to_premium_subscribers(message)
            
        except Exception as e:
            logger.error(f"Error sending mid-day update: {e}")
    
    def send_postmarket_analysis(self):
        """3:30 PM - Post-market analysis"""
        try:
            now = datetime.datetime.now(self.tz)
            if now.weekday() >= 5:  # Skip weekends
                return
                
            logger.info("📊 Sending post-market analysis...")
            
            message = f"""📊 **POST-MARKET ANALYSIS**
📅 {now.strftime('%d %B %Y')} | ⏰ 3:30 PM

🔔 **MARKET CLOSED**

📈 **Today's Performance:**
• Session Summary: Market closed
• Key Movers: Analysis in progress
• Volume: Normal/High/Low

🎯 **Key Highlights:**
• Breakout stocks delivered signals
• Premium subscribers received live alerts
• Technical levels held/broken

📊 **Tomorrow's Outlook:**
• Key levels to watch
• Sectoral focus areas
• Global cues impact

⏰ **Next Update: 6:30 PM Evening News**
"""
            
            self._send_to_premium_subscribers(message)
            
        except Exception as e:
            logger.error(f"Error sending post-market analysis: {e}")
    
    def send_evening_news(self):
        """6:30 PM - Evening news and tomorrow's outlook"""
        try:
            now = datetime.datetime.now(self.tz)
            if now.weekday() >= 5:  # Skip weekends for tomorrow outlook
                return
                
            logger.info("📰 Sending evening news...")
            
            # Get latest news
            news = enhanced_trading_system.get_market_news()
            
            tomorrow = now + datetime.timedelta(days=1)
            
            message = f"""📰 **EVENING MARKET WRAP**
📅 {now.strftime('%d %B %Y')} | ⏰ 6:30 PM

📊 **Today's Market Summary:**
• Trading session completed
• Signals delivered to premium subscribers
• Market analysis updated

📰 **Top 5 News for Tomorrow:**

"""
            
            for i, item in enumerate(news[:5], 1):
                message += f"{i}. [{item['title']}]({item['url']})\n   📊 {item['source']}\n\n"
            
            message += f"""
🌅 **Tomorrow's Schedule ({tomorrow.strftime('%d %B %Y')}):**
• 6:30 AM - Morning News Alert
• 8:30 AM - Pre-market Analysis
• 9:15 AM - Live Signal Mode
• 12:00 PM - Mid-day Update
• 3:30 PM - Post-market Analysis

😴 **Good Night! See you tomorrow for more premium signals!**
"""
            
            self._send_to_premium_subscribers(message)
            
        except Exception as e:
            logger.error(f"Error sending evening news: {e}")
    
    def send_live_signals(self):
        """Send live trading signals during market hours"""
        try:
            now = datetime.datetime.now(self.tz)
            
            # Only send during market hours (9:15 AM - 3:30 PM)
            if not enhanced_trading_system.is_market_open(now):
                return
                
            # Skip if not on 15-minute intervals
            if now.minute % 15 != 0:
                return
                
            logger.info("⚡ Scanning for live signals...")
            
            # Get market scan
            scan_result = enhanced_trading_system.run_market_scan()
            
            if scan_result.get('status') != 'success':
                return
                
            breakouts = scan_result.get('breakouts', [])
            
            if breakouts:
                message = f"""⚡ **LIVE SIGNAL ALERT**
📅 {now.strftime('%d %B %Y')} | ⏰ {now.strftime('%I:%M %p')}

🎯 **Active Breakouts Detected:**

"""
                
                for breakout in breakouts[:3]:  # Top 3 signals
                    confidence_emoji = "🔥" if breakout['confidence'] >= 70 else "⚡"
                    
                    message += f"""{confidence_emoji} **{breakout['symbol']}**
   📊 Signal: **{breakout['signal']}**
   🎯 Confidence: **{breakout['confidence']}%**
   💰 Price: ₹{breakout['price']:.2f}
   📈 RSI: {breakout['rsi']:.1f}

"""
                
                message += """
🚨 **For Premium Subscribers Only**
⏰ Next scan in 15 minutes
"""
                
                self._send_to_premium_subscribers(message)
                
        except Exception as e:
            logger.error(f"Error sending live signals: {e}")
    
    def _send_to_premium_subscribers(self, message: str):
        """Send message to all premium subscribers"""
        try:
            # Get all premium users
            premium_users = self.user_manager.get_premium_users()
            
            # Send to main premium channel
            enhanced_trading_system.send_telegram_signal(
                self.telegram_token,
                self.premium_chat_id,
                message
            )
            
            # Also send to individual premium users if they have telegram IDs
            for user in premium_users:
                user_telegram_id = user.get('telegram_id')
                if user_telegram_id:
                    enhanced_trading_system.send_telegram_signal(
                        self.telegram_token,
                        user_telegram_id,
                        message
                    )
                    
            logger.info(f"📤 Alert sent to {len(premium_users)} premium subscribers")
            
        except Exception as e:
            logger.error(f"Error sending to premium subscribers: {e}")
    
    def send_custom_alert(self, title: str, content: str, alert_type: str = "custom"):
        """Send custom alert to premium subscribers"""
        try:
            now = datetime.datetime.now(self.tz)
            
            message = f"""🔔 **{title.upper()}**
📅 {now.strftime('%d %B %Y')} | ⏰ {now.strftime('%I:%M %p')}

{content}

🎯 **Premium Alert System**
"""
            
            self._send_to_premium_subscribers(message)
            logger.info(f"Custom alert sent: {title}")
            
        except Exception as e:
            logger.error(f"Error sending custom alert: {e}")

# Global scheduler instance
scheduled_alert_system = None

def initialize_scheduler(telegram_token: str, premium_chat_id: str):
    """Initialize the global scheduler"""
    global scheduled_alert_system
    scheduled_alert_system = ScheduledAlertSystem(telegram_token, premium_chat_id)
    return scheduled_alert_system