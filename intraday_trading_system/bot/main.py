"""
Main Trading Bot - Core Orchestrator
Handles scheduling, signal generation, and coordination between all modules
"""

import asyncio
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass

# Local imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config, logger
from bot.market_data import MarketDataManager
from bot.technical_analysis import TechnicalAnalyzer
from bot.telegram_bot import TelegramBot
from bot.news_fetcher import NewsFetcher
from bot.signal_manager import SignalManager

@dataclass
class TradingSignal:
    """Trading signal data structure"""
    timestamp: str
    instrument: str
    signal_type: str  # BUY/SELL
    entry_price: float
    target_price: float
    stop_loss: float
    confidence: float
    setup_description: str
    technical_indicators: Dict[str, Any]
    risk_reward_ratio: float

class TradingBot:
    """Main trading bot orchestrator"""
    
    def __init__(self):
        self.logger = logger
        self.config = config
        self.is_running = False
        self.signals_sent_today = 0
        self.last_signal_time = None
        
        # Initialize modules
        self.market_data = MarketDataManager()
        self.technical_analyzer = TechnicalAnalyzer()
        self.telegram_bot = TelegramBot()
        self.news_fetcher = NewsFetcher()
        self.signal_manager = SignalManager()
        
        self.logger.info("Trading Bot initialized successfully")
    
    def start(self):
        """Start the trading bot"""
        self.logger.info("Starting Intraday Trading Bot...")
        
        # Validate configuration
        validation_result = self.config.validate_config()
        if validation_result['errors']:
            self.logger.error(f"Configuration errors: {validation_result['errors']}")
            return False
        
        self.is_running = True
        
        # Setup scheduled tasks
        self._setup_schedule()
        
        # Send startup message
        asyncio.run(self.telegram_bot.send_startup_message())
        
        # Start background monitoring
        monitoring_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        monitoring_thread.start()
        
        # Start real-time signal monitoring during market hours
        signal_thread = threading.Thread(target=self._monitor_signals, daemon=True)
        signal_thread.start()
        
        self.logger.info("✅ Trading Bot started successfully!")
        return True
    
    def stop(self):
        """Stop the trading bot"""
        self.logger.info("🛑 Stopping Trading Bot...")
        self.is_running = False
        asyncio.run(self.telegram_bot.send_shutdown_message())
        self.logger.info("✅ Trading Bot stopped")
    
    def _setup_schedule(self):
        """Setup scheduled tasks"""
        # Morning news at 6:30 AM
        schedule.every().day.at(self.config.MORNING_NEWS_TIME).do(
            lambda: asyncio.run(self.send_morning_news())
        )
        
        # Pre-market analysis at 8:30 AM
        schedule.every().day.at(self.config.PRE_MARKET_TIME).do(
            lambda: asyncio.run(self.send_pre_market_analysis())
        )
        
        # Post-market analysis at 3:30 PM
        schedule.every().day.at(self.config.MARKET_CLOSE_TIME).do(
            lambda: asyncio.run(self.send_post_market_analysis())
        )
        
        # Evening news at 6:30 PM
        schedule.every().day.at(self.config.EVENING_NEWS_TIME).do(
            lambda: asyncio.run(self.send_evening_news())
        )
        
        # Reset daily counters at midnight
        schedule.every().day.at("00:00").do(self._reset_daily_counters)
        
        self.logger.info("📅 Scheduled tasks configured")
    
    def _run_scheduler(self):
        """Run the scheduler in background"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _monitor_signals(self):
        """Monitor for trading signals during market hours"""
        while self.is_running:
            try:
                if self.config.is_market_open() and self.config.is_trading_day():
                    if self._can_send_signal():
                        signals = self._generate_signals()
                        for signal in signals:
                            asyncio.run(self.telegram_bot.send_trading_signal(signal))
                            self.signals_sent_today += 1
                            self.last_signal_time = datetime.now()
                            
                            # Save signal to database
                            self.signal_manager.save_signal(signal)
                            
                            self.logger.info(f"Signal sent: {signal.instrument} - {signal.signal_type}")
                
                time.sleep(60)  # Check every minute during market hours
                
            except Exception as e:
                self.logger.error(f"Error in signal monitoring: {str(e)}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _can_send_signal(self) -> bool:
        """Check if we can send a new signal"""
        # Check daily limit
        if self.signals_sent_today >= self.config.MAX_SIGNALS_PER_DAY:
            return False
        
        # Check time interval
        if self.last_signal_time:
            time_since_last = (datetime.now() - self.last_signal_time).total_seconds()
            if time_since_last < self.config.MIN_SIGNAL_INTERVAL:
                return False
        
        return True
    
    def _generate_signals(self) -> List[TradingSignal]:
        """Generate trading signals"""
        signals = []
        
        try:
            for instrument in self.config.INSTRUMENTS:
                # Get market data
                market_data = self.market_data.get_live_data(instrument)
                if not market_data:
                    continue
                
                # Perform technical analysis
                analysis = self.technical_analyzer.analyze(market_data)
                
                # Check if signal meets criteria
                if analysis['confidence'] >= self.config.MIN_CONFIDENCE_THRESHOLD:
                    signal = TradingSignal(
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        instrument=instrument,
                        signal_type=analysis['signal_type'],
                        entry_price=analysis['entry_price'],
                        target_price=analysis['target_price'],
                        stop_loss=analysis['stop_loss'],
                        confidence=analysis['confidence'],
                        setup_description=analysis['setup_description'],
                        technical_indicators=analysis['indicators'],
                        risk_reward_ratio=analysis['risk_reward_ratio']
                    )
                    signals.append(signal)
                    
        except Exception as e:
            self.logger.error(f"Error generating signals: {str(e)}")
        
        return signals
    
    async def send_morning_news(self):
        """Send morning news alert"""
        try:
            self.logger.info("📰 Sending morning news...")
            news = await self.news_fetcher.get_morning_news()
            await self.telegram_bot.send_morning_news(news)
            self.logger.info("✅ Morning news sent")
        except Exception as e:
            self.logger.error(f"Error sending morning news: {str(e)}")
    
    async def send_pre_market_analysis(self):
        """Send pre-market analysis"""
        try:
            self.logger.info("Sending pre-market analysis...")
            analysis = await self.market_data.get_pre_market_analysis()
            await self.telegram_bot.send_pre_market_analysis(analysis)
            self.logger.info("✅ Pre-market analysis sent")
        except Exception as e:
            self.logger.error(f"Error sending pre-market analysis: {str(e)}")
    
    async def send_post_market_analysis(self):
        """Send post-market analysis"""
        try:
            self.logger.info("📉 Sending post-market analysis...")
            analysis = await self.market_data.get_post_market_analysis()
            await self.telegram_bot.send_post_market_analysis(analysis)
            self.logger.info("✅ Post-market analysis sent")
        except Exception as e:
            self.logger.error(f"Error sending post-market analysis: {str(e)}")
    
    async def send_evening_news(self):
        """Send evening news alert"""
        try:
            self.logger.info("🌙 Sending evening news...")
            news = await self.news_fetcher.get_evening_news()
            await self.telegram_bot.send_evening_news(news)
            self.logger.info("✅ Evening news sent")
        except Exception as e:
            self.logger.error(f"Error sending evening news: {str(e)}")
    
    def _reset_daily_counters(self):
        """Reset daily counters at midnight"""
        self.signals_sent_today = 0
        self.last_signal_time = None
        self.logger.info("🔄 Daily counters reset")
    
    def get_status(self) -> Dict[str, Any]:
        """Get bot status"""
        return {
            'running': self.is_running,
            'signals_sent_today': self.signals_sent_today,
            'last_signal_time': self.last_signal_time.isoformat() if self.last_signal_time else None,
            'market_open': self.config.is_market_open(),
            'trading_day': self.config.is_trading_day(),
            'uptime': datetime.now().isoformat()
        }

def main():
    """Main entry point"""
    bot = TradingBot()
    
    try:
        # Start the bot
        if bot.start():
            # Keep running
            while bot.is_running:
                time.sleep(10)
        else:
            logger.error("Failed to start bot")
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        bot.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        bot.stop()

if __name__ == "__main__":
    main()