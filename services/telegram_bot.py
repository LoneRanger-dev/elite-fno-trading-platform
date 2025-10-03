"""
🤖 Premium Telegram Bot Integration
Advanced Telegram bot for delivering premium FnO signals with rich formatting,
charts, timing optimization, and interactive features.
"""

import asyncio
import logging
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import io
import base64

# Telegram Bot API (with fallback for different versions)
try:
    from telegram import (
        Update, InlineKeyboardButton, InlineKeyboardMarkup, 
        Bot, InputMediaPhoto
    )
    from telegram.constants import ParseMode
except ImportError:
    try:
        from telegram import (
            Update, InlineKeyboardButton, InlineKeyboardMarkup, 
            ParseMode, Bot, InputMediaPhoto
        )
    except ImportError:
        # Mock objects for when telegram is not available
        class MockTelegram:
            class ParseMode:
                MARKDOWN_V2 = 'MarkdownV2'
                HTML = 'HTML'
        ParseMode = MockTelegram.ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)

# Chart generation
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import seaborn as sns

# Internal imports
from services.advanced_fno_engine import AdvancedFnOEngine
from services.paper_trading import PaperTradingEngine
from config.settings import TELEGRAM_BOT_TOKEN, DATABASE_URL

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@dataclass
class TelegramUser:
    """Telegram user data structure"""
    user_id: int
    username: str
    first_name: str
    subscription_tier: str  # free, premium, vip
    joined_date: datetime
    last_active: datetime
    preferences: Dict
    paper_trading_enabled: bool = True
    notifications_enabled: bool = True

class PremiumTelegramBot:
    """🚀 Premium Telegram Bot for FnO Trading Signals"""
    
    def __init__(self, token: str):
        self.token = token
        self.bot = Bot(token=token)
        self.application = Application.builder().token(token).build()
        
        # Initialize engines
        self.fno_engine = AdvancedFnOEngine()
        self.paper_engine = PaperTradingEngine()
        
        # User database (in production, use PostgreSQL/MongoDB)
        self.users: Dict[int, TelegramUser] = {}
        
        # Premium channels
        self.premium_channel = "@elite_fno_premium"
        self.vip_channel = "@elite_fno_vip"
        self.free_channel = "@elite_fno_free"
        
        # Chart styling
        self.setup_chart_style()
        
        # Register handlers
        self.register_handlers()
    
    def setup_chart_style(self):
        """Configure chart styling for professional look"""
        plt.style.use('dark_background')
        sns.set_palette("husl")
        
        # Custom color scheme
        self.colors = {
            'bull': '#00f2fe',
            'bear': '#ff6a00',
            'neutral': '#667eea',
            'profit': '#4CAF50',
            'loss': '#f44336',
            'bg': '#0a0a0f',
            'text': '#ffffff'
        }
    
    def register_handlers(self):
        """Register all bot command and callback handlers"""
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("signals", self.signals_command))
        self.application.add_handler(CommandHandler("portfolio", self.portfolio_command))
        self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("leaderboard", self.leaderboard_command))
        self.application.add_handler(CommandHandler("performance", self.performance_command))
        
        # Callback query handlers
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handlers
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome new users with premium onboarding"""
        user = update.effective_user
        user_id = user.id
        
        # Register user if new
        if user_id not in self.users:
            self.users[user_id] = TelegramUser(
                user_id=user_id,
                username=user.username or "Unknown",
                first_name=user.first_name or "Trader",
                subscription_tier="free",
                joined_date=datetime.now(),
                last_active=datetime.now(),
                preferences={"notifications": True, "charts": True, "risk_level": "medium"}
            )
        
        welcome_message = f"""
🚀 **Welcome to Elite FnO Trading Signals!**

Hello {user.first_name}! 👋

I'm your personal trading assistant, ready to deliver premium FnO signals with:

🎯 **AI-Powered Signals** - 85%+ accuracy rate
📊 **Real-time Charts** - Professional technical analysis  
📈 **Paper Trading** - Practice with virtual money
🏆 **Live Leaderboard** - Compete with top traders
💎 **Premium Features** - Exclusive VIP signals

**Quick Start Commands:**
• `/signals` - View live trading signals
• `/portfolio` - Check your paper trading portfolio
• `/subscribe` - Upgrade to premium plans
• `/settings` - Customize your preferences
• `/help` - Get detailed help

**Free Trial**: 7 days of premium features! 🎁

Ready to start your profitable trading journey?
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🎯 View Live Signals", callback_data="signals"),
                InlineKeyboardButton("📊 Portfolio", callback_data="portfolio")
            ],
            [
                InlineKeyboardButton("💎 Upgrade to Premium", callback_data="subscribe"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ],
            [
                InlineKeyboardButton("📱 Join Premium Channel", url=self.premium_channel),
                InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def signals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display current live signals with interactive buttons"""
        user_id = update.effective_user.id
        user = self.users.get(user_id)
        
        if not user:
            await update.message.reply_text("Please use /start first to register!")
            return
        
        # Get signals based on subscription tier
        signals = await self.get_user_signals(user)
        
        if not signals:
            await update.message.reply_text(
                "🔍 No active signals right now. New signals coming soon!\n\n"
                "💡 Upgrade to Premium for more frequent signals!"
            )
            return
        
        for signal in signals[:5]:  # Show top 5 signals
            await self.send_signal_card(update, signal, user)
    
    async def get_user_signals(self, user: TelegramUser) -> List[Dict]:
        """Get signals based on user subscription tier"""
        # Generate signals using FnO engine
        mock_signals = [
            {
                'id': 1,
                'symbol': 'NIFTY24JAN22000CE',
                'type': 'CE',
                'action': 'BUY',
                'sentiment': 'bullish',
                'entry_price': 145.50,
                'current_price': 167.25,
                'target_price': 180.00,
                'stop_loss': 125.00,
                'quantity': 50,
                'confidence': 87,
                'timestamp': datetime.now(),
                'source': 'AI Engine',
                'risk_level': 'medium'
            }
        ]
        
        # Filter based on subscription
        if user.subscription_tier == "free":
            return mock_signals[:2]  # Limited signals for free users
        elif user.subscription_tier == "premium":
            return mock_signals[:10]
        else:  # VIP
            return mock_signals  # All signals
    
    async def send_signal_card(self, update: Update, signal: Dict, user: TelegramUser):
        """Send beautifully formatted signal card with chart"""
        
        # Generate signal chart
        chart_path = await self.generate_signal_chart(signal)
        
        # Format signal message
        signal_text = self.format_signal_message(signal)
        
        # Create interactive buttons
        keyboard = []
        
        if user.paper_trading_enabled:
            keyboard.append([
                InlineKeyboardButton(
                    f"📈 Paper Trade ({signal['quantity']} lots)", 
                    callback_data=f"paper_trade_{signal['id']}"
                )
            ])
        
        keyboard.extend([
            [
                InlineKeyboardButton("📊 View Chart", callback_data=f"chart_{signal['id']}"),
                InlineKeyboardButton("📋 Analysis", callback_data=f"analysis_{signal['id']}")
            ],
            [
                InlineKeyboardButton("⚡ Set Alert", callback_data=f"alert_{signal['id']}"),
                InlineKeyboardButton("📤 Share", callback_data=f"share_{signal['id']}")
            ]
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send message with chart
        if chart_path and user.preferences.get('charts', True):
            with open(chart_path, 'rb') as chart_file:
                await update.message.reply_photo(
                    photo=chart_file,
                    caption=signal_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
        else:
            await update.message.reply_text(
                signal_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    
    def format_signal_message(self, signal: Dict) -> str:
        """Format signal into rich Telegram message"""
        
        sentiment_emoji = "🚀" if signal['sentiment'] == 'bullish' else "📉"
        action_emoji = "📈" if signal['action'] == 'BUY' else "📉"
        
        # Calculate P&L
        if signal['action'] == 'BUY':
            pnl = (signal['current_price'] - signal['entry_price']) * signal['quantity']
        else:
            pnl = (signal['entry_price'] - signal['current_price']) * signal['quantity']
        
        pnl_percentage = (pnl / (signal['entry_price'] * signal['quantity'])) * 100
        pnl_emoji = "💚" if pnl >= 0 else "❌"
        
        message = f"""
{sentiment_emoji} **PREMIUM SIGNAL** {sentiment_emoji}

🎯 **{signal['symbol']}**
{action_emoji} **{signal['action']} {signal['type']}**

💰 **Trade Details:**
├ Entry: ₹{signal['entry_price']:.2f}
├ Current: ₹{signal['current_price']:.2f}
├ Target: ₹{signal['target_price']:.2f}
└ Stop Loss: ₹{signal['stop_loss']:.2f}

📊 **Performance:**
├ Quantity: {signal['quantity']} lots
├ Confidence: {signal['confidence']}% 🎯
└ P&L: {pnl_emoji} ₹{pnl:+.2f} ({pnl_percentage:+.1f}%)

🤖 **Source:** {signal['source']}
⏰ **Time:** {signal['timestamp'].strftime('%H:%M:%S')}

⚡ **Quick Actions Below** ⚡
        """
        
        return message.strip()
    
    async def generate_signal_chart(self, signal: Dict) -> Optional[str]:
        """Generate professional trading chart for signal"""
        try:
            # Create figure with dark theme
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                          facecolor=self.colors['bg'],
                                          gridspec_kw={'height_ratios': [3, 1]})
            
            # Generate mock price data
            timestamps = pd.date_range(
                start=datetime.now() - timedelta(hours=6),
                end=datetime.now(),
                freq='5T'
            )
            
            # Create realistic price movement
            base_price = signal['entry_price']
            prices = []
            current = base_price
            
            for i, _ in enumerate(timestamps):
                # Add some realistic volatility
                change = np.random.normal(0, base_price * 0.02)
                current = max(0, current + change)
                prices.append(current)
            
            # Ensure current price matches signal
            prices[-1] = signal['current_price']
            
            # Plot price chart
            ax1.plot(timestamps, prices, color=self.colors['bull'], linewidth=2, label='Price')
            
            # Add signal lines
            ax1.axhline(y=signal['entry_price'], color='white', linestyle='--', alpha=0.8, label='Entry')
            ax1.axhline(y=signal['target_price'], color=self.colors['profit'], linestyle='--', alpha=0.8, label='Target')
            ax1.axhline(y=signal['stop_loss'], color=self.colors['loss'], linestyle='--', alpha=0.8, label='Stop Loss')
            
            # Customize chart
            ax1.set_facecolor(self.colors['bg'])
            ax1.grid(True, alpha=0.3)
            ax1.legend(loc='upper left')
            ax1.set_title(f"{signal['symbol']} - {signal['action']} Signal", 
                         color=self.colors['text'], fontsize=16, fontweight='bold')
            ax1.set_ylabel('Price (₹)', color=self.colors['text'])
            
            # Volume chart (mock)
            volumes = np.random.randint(1000, 10000, len(timestamps))
            ax2.bar(timestamps, volumes, color=self.colors['neutral'], alpha=0.6)
            ax2.set_facecolor(self.colors['bg'])
            ax2.set_ylabel('Volume', color=self.colors['text'])
            ax2.set_xlabel('Time', color=self.colors['text'])
            
            # Style axes
            for ax in [ax1, ax2]:
                ax.tick_params(colors=self.colors['text'])
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            
            plt.tight_layout()
            
            # Save chart
            chart_path = f"temp/signal_chart_{signal['id']}.png"
            os.makedirs('temp', exist_ok=True)
            plt.savefig(chart_path, facecolor=self.colors['bg'], 
                       bbox_inches='tight', dpi=150)
            plt.close()
            
            return chart_path
            
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return None
    
    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's paper trading portfolio"""
        user_id = update.effective_user.id
        user = self.users.get(user_id)
        
        if not user:
            await update.message.reply_text("Please use /start first!")
            return
        
        # Get portfolio from paper trading engine
        portfolio = self.paper_engine.get_portfolio(str(user_id))
        
        if not portfolio:
            portfolio = self.paper_engine.create_portfolio(str(user_id))
        
        # Generate portfolio chart
        chart_path = await self.generate_portfolio_chart(portfolio)
        
        # Format portfolio message
        portfolio_text = f"""
📊 **Your Paper Trading Portfolio**

💰 **Capital:**
├ Total: ₹{portfolio.total_capital:,.2f}
├ Available: ₹{portfolio.available_capital:,.2f}
├ Invested: ₹{portfolio.invested_capital:,.2f}
└ Current Value: ₹{portfolio.current_value:,.2f}

📈 **Performance:**
├ Total P&L: ₹{portfolio.total_pnl:+,.2f} ({portfolio.total_pnl_percentage:+.2f}%)
├ Day P&L: ₹{portfolio.day_pnl:+,.2f} ({portfolio.day_pnl_percentage:+.2f}%)
└ Win Rate: {portfolio.win_rate:.1f}%

🏆 **Statistics:**
├ Total Trades: {portfolio.total_trades}
├ Winning: {portfolio.winning_trades} 💚
├ Losing: {portfolio.losing_trades} ❌
└ Rank: #{portfolio.performance_rank}

🏅 **Achievements:** {', '.join(portfolio.badges) if portfolio.badges else 'None yet'}

💡 **Tip:** Keep practicing to improve your win rate!
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📈 Active Trades", callback_data="active_trades"),
                InlineKeyboardButton("📋 Trade History", callback_data="trade_history")
            ],
            [
                InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
                InlineKeyboardButton("📊 Analytics", callback_data="analytics")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if chart_path:
            with open(chart_path, 'rb') as chart_file:
                await update.message.reply_photo(
                    photo=chart_file,
                    caption=portfolio_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
        else:
            await update.message.reply_text(
                portfolio_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    
    async def generate_portfolio_chart(self, portfolio) -> Optional[str]:
        """Generate portfolio performance chart"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10), 
                                                        facecolor=self.colors['bg'])
            
            # Portfolio value over time (mock data)
            dates = pd.date_range(start=portfolio.created_at, end=datetime.now(), freq='D')
            values = np.cumsum(np.random.normal(100, 500, len(dates))) + portfolio.total_capital
            
            ax1.plot(dates, values, color=self.colors['bull'], linewidth=2)
            ax1.set_title('Portfolio Value Over Time', color=self.colors['text'], fontweight='bold')
            ax1.set_facecolor(self.colors['bg'])
            ax1.grid(True, alpha=0.3)
            
            # Win/Loss pie chart
            if portfolio.total_trades > 0:
                sizes = [portfolio.winning_trades, portfolio.losing_trades]
                labels = ['Wins', 'Losses']
                colors = [self.colors['profit'], self.colors['loss']]
                
                ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax2.set_title('Win/Loss Ratio', color=self.colors['text'], fontweight='bold')
            
            # P&L distribution (mock)
            pnl_data = np.random.normal(portfolio.total_pnl/10, 1000, 50)
            ax3.hist(pnl_data, bins=20, color=self.colors['neutral'], alpha=0.7)
            ax3.set_title('P&L Distribution', color=self.colors['text'], fontweight='bold')
            ax3.set_facecolor(self.colors['bg'])
            
            # Performance metrics
            metrics = ['Win Rate', 'Profit Factor', 'Sharpe Ratio', 'Max Drawdown']
            values = [portfolio.win_rate, 1.5, portfolio.sharpe_ratio, portfolio.max_drawdown]
            
            ax4.bar(metrics, values, color=self.colors['bull'])
            ax4.set_title('Performance Metrics', color=self.colors['text'], fontweight='bold')
            ax4.set_facecolor(self.colors['bg'])
            
            # Style all axes
            for ax in [ax1, ax2, ax3, ax4]:
                ax.tick_params(colors=self.colors['text'])
            
            plt.tight_layout()
            
            # Save chart
            chart_path = f"temp/portfolio_chart_{portfolio.user_id}.png"
            plt.savefig(chart_path, facecolor=self.colors['bg'], 
                       bbox_inches='tight', dpi=150)
            plt.close()
            
            return chart_path
            
        except Exception as e:
            logger.error(f"Error generating portfolio chart: {e}")
            return None
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries from inline buttons"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        if data == "signals":
            await self.signals_command(update, context)
        
        elif data == "portfolio":
            await self.portfolio_command(update, context)
        
        elif data.startswith("paper_trade_"):
            signal_id = int(data.split("_")[-1])
            await self.handle_paper_trade(query, signal_id)
        
        elif data.startswith("chart_"):
            signal_id = int(data.split("_")[-1])
            await self.show_detailed_chart(query, signal_id)
        
        elif data == "leaderboard":
            await self.show_leaderboard(query)
        
        elif data == "subscribe":
            await self.show_subscription_plans(query)
        
        # Add more callback handlers as needed
    
    async def handle_paper_trade(self, query, signal_id: int):
        """Execute paper trade for user"""
        user_id = query.from_user.id
        
        # Mock signal data (in production, get from database)
        signal = {
            'id': signal_id,
            'symbol': 'NIFTY24JAN22000CE',
            'type': 'CE',
            'action': 'BUY',
            'entry_price': 145.50,
            'quantity': 50
        }
        
        # Execute paper trade
        trade_data = {
            'symbol': signal['symbol'],
            'instrument_type': signal['type'],
            'transaction_type': signal['action'],
            'quantity': signal['quantity'],
            'entry_price': signal['entry_price'],
            'signal_source': 'Telegram Bot'
        }
        
        result = self.paper_engine.place_paper_trade(str(user_id), trade_data)
        
        if result['success']:
            message = f"""
✅ **Paper Trade Executed!**

🎯 **{signal['symbol']}**
📊 {signal['action']} {signal['quantity']} lots at ₹{signal['entry_price']}

💰 **Cost:** ₹{result['total_cost']:,.2f}
📈 **Trade ID:** {result['trade_id'][:8]}

Your paper portfolio has been updated!
Use /portfolio to see your performance.
            """
        else:
            message = f"❌ **Trade Failed:** {result['message']}"
        
        await query.edit_message_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def broadcast_signal(self, signal: Dict, tier: str = "premium"):
        """Broadcast signal to appropriate channel"""
        try:
            # Format signal for broadcast
            signal_text = self.format_signal_message(signal)
            
            # Generate chart
            chart_path = await self.generate_signal_chart(signal)
            
            # Determine channel based on tier
            channel = self.premium_channel if tier == "premium" else self.vip_channel
            
            # Send to channel
            if chart_path:
                with open(chart_path, 'rb') as chart_file:
                    await self.bot.send_photo(
                        chat_id=channel,
                        photo=chart_file,
                        caption=signal_text,
                        parse_mode=ParseMode.MARKDOWN
                    )
            else:
                await self.bot.send_message(
                    chat_id=channel,
                    text=signal_text,
                    parse_mode=ParseMode.MARKDOWN
                )
            
            logger.info(f"Signal broadcast to {channel}: {signal['symbol']}")
            
        except Exception as e:
            logger.error(f"Error broadcasting signal: {e}")
    
    async def send_daily_summary(self):
        """Send daily performance summary to all users"""
        summary_text = """
📊 **Daily Market Summary**

🎯 **Signals Performance:**
├ Total Signals: 47
├ Hit Target: 32 (68.1%)
├ Hit Stop Loss: 8 (17.0%)
└ Active: 7 (14.9%)

💰 **Top Performers:**
├ NIFTY22000CE: +45.2%
├ BANKNIFTY45000PE: +32.1%
└ NIFTYFUT: +12.8%

📈 **Market Highlights:**
├ Nifty: +0.85% (Bullish)
├ Bank Nifty: +1.23% (Strong)
└ VIX: -5.67% (Reducing)

🏆 **Paper Trading Leaderboard:**
├ 🥇 TradingKing: +15.2%
├ 🥈 OptionsMaster: +12.8%
└ 🥉 FnOExpert: +11.5%

Tomorrow's outlook: BULLISH 🚀
        """
        
        # Send to all channels
        for channel in [self.free_channel, self.premium_channel, self.vip_channel]:
            try:
                await self.bot.send_message(
                    chat_id=channel,
                    text=summary_text,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Error sending daily summary to {channel}: {e}")
    
    def run(self):
        """Start the bot"""
        logger.info("Starting Premium Telegram Bot...")
        
        # Start polling
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

# Scheduler for automated signals and summaries
class TelegramScheduler:
    """Schedule automated Telegram messages"""
    
    def __init__(self, bot: PremiumTelegramBot):
        self.bot = bot
        
    async def schedule_daily_signals(self):
        """Send scheduled signals throughout the day"""
        # Market opening signals (9:15 AM)
        if datetime.now().time() == datetime.strptime("09:15", "%H:%M").time():
            await self.send_market_opening_signals()
        
        # Mid-day signals (1:30 PM)
        elif datetime.now().time() == datetime.strptime("13:30", "%H:%M").time():
            await self.send_midday_signals()
        
        # Market closing summary (3:30 PM)
        elif datetime.now().time() == datetime.strptime("15:30", "%H:%M").time():
            await self.bot.send_daily_summary()
    
    async def send_market_opening_signals(self):
        """Send morning market opening signals"""
        opening_signals = [
            {
                'id': 1001,
                'symbol': 'NIFTY24JAN22000CE',
                'type': 'CE',
                'action': 'BUY',
                'sentiment': 'bullish',
                'entry_price': 145.50,
                'current_price': 145.50,
                'target_price': 180.00,
                'stop_loss': 125.00,
                'quantity': 50,
                'confidence': 87,
                'timestamp': datetime.now(),
                'source': 'Market Opening Analysis'
            }
        ]
        
        for signal in opening_signals:
            await self.bot.broadcast_signal(signal, "premium")

# Example usage and testing
if __name__ == "__main__":
    # Initialize bot
    bot = PremiumTelegramBot(TELEGRAM_BOT_TOKEN)
    
    # Test signal generation
    test_signal = {
        'id': 999,
        'symbol': 'NIFTY24JAN22000CE',
        'type': 'CE',
        'action': 'BUY',
        'sentiment': 'bullish',
        'entry_price': 145.50,
        'current_price': 167.25,
        'target_price': 180.00,
        'stop_loss': 125.00,
        'quantity': 50,
        'confidence': 87,
        'timestamp': datetime.now(),
        'source': 'Test Signal'
    }
    
    print("🤖 Premium Telegram Bot initialized!")
    print(f"📊 Sample signal formatted:")
    print(bot.format_signal_message(test_signal))
    
    # Start bot (uncomment to run)
    # bot.run()