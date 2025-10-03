"""
🎯 Live Signal Generation Engine
Real-time FnO signal generation with market data integration
"""

import asyncio
import json
import os
import random
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import logging

from pro_trader_setups import ProTraderSetups
from signal_validation import SignalValidator
from signal_generator import SignalGenerator
from signal_manager import SignalManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradingSignal:
    """Trading signal data structure"""
    id: str
    timestamp: datetime
    instrument: str  # e.g., NIFTY
    option_symbol: str # e.g., NIFTY 24500 CE
    signal_type: str  # BUY_CALL, BUY_PUT
    strike_price: float
    option_entry_price: float
    option_target_price: float
    option_stop_loss: float
    confidence: float  # 0-100
    setup_description: str
    technical_indicators: Dict[str, Any]
    risk_reward_ratio: float
    expiry_date: str
    lot_size: int
    status: str = "ACTIVE"

class LiveSignalEngine:
    """Real-time signal generation engine with advanced technical analysis"""
    
    def check_support_resistance(self, symbol, interval="1d", lookback=20):
        """Calculate support and resistance levels and generate signals."""
        try:
            # Get historical data
            data = self.market_data.get_historical_data(symbol, interval)
            if data is None or len(data) < lookback:
                return None
                
            # Find recent highs and lows
            recent_data = data.tail(lookback)
            highs = recent_data['high']
            lows = recent_data['low']
            
            # Calculate support and resistance
            resistance = highs.max()
            support = lows.min()
            
            # Get current price
            current_price = data['close'].iloc[-1]
            
            # Calculate price position
            range_size = resistance - support
            if range_size == 0:
                return None
                
            position = (current_price - support) / range_size
            
            # Generate signals
            if position > 0.95:  # Near resistance
                return {'signal': 'SELL', 'strength': 'strong'}
            elif position < 0.05:  # Near support
                return {'signal': 'BUY', 'strength': 'strong'}
            elif position > 0.8:
                return {'signal': 'SELL', 'strength': 'weak'}
            elif position < 0.2:
                return {'signal': 'BUY', 'strength': 'weak'}
            else:
                return {'signal': 'NEUTRAL', 'strength': 'weak'}
                
        except Exception as e:
            logger.error(f"Error checking support/resistance: {str(e)}")
            return None
            
    def check_bollinger_bands(self, symbol, interval="1d", period=20, num_std=2):
        """Calculate Bollinger Bands and generate signals."""
        try:
            # Get historical data
            data = self.market_data.get_historical_data(symbol, interval)
            if data is None or len(data) < period:
                return None
                
            # Calculate Bollinger Bands
            sma = data['close'].rolling(window=period).mean()
            std = data['close'].rolling(window=period).std()
            upper_band = sma + (std * num_std)
            lower_band = sma - (std * num_std)
            
            # Get current values
            current_price = data['close'].iloc[-1]
            current_upper = upper_band.iloc[-1]
            current_lower = lower_band.iloc[-1]
            current_sma = sma.iloc[-1]
            
            # Generate signals
            if current_price > current_upper:
                return {'signal': 'SELL', 'strength': 'strong'}
            elif current_price < current_lower:
                return {'signal': 'BUY', 'strength': 'strong'}
            else:
                position = (current_price - current_lower) / (current_upper - current_lower)
                if position > 0.8:
                    return {'signal': 'SELL', 'strength': 'weak'}
                elif position < 0.2:
                    return {'signal': 'BUY', 'strength': 'weak'}
                else:
                    return {'signal': 'NEUTRAL', 'strength': 'weak'}
                    
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return None
            
    def check_macd(self, symbol, interval="1d"):
        """Calculate MACD and generate signals."""
        try:
            # Get historical data
            data = self.market_data.get_historical_data(symbol, interval)
            if data is None:
                return None
                
            # Calculate MACD
            exp1 = data['close'].ewm(span=12, adjust=False).mean()
            exp2 = data['close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            
            # Get current values
            current_macd = macd.iloc[-1]
            current_signal = signal.iloc[-1]
            
            # Generate signals
            if current_macd > current_signal:
                strength = 'strong' if current_macd > 0 else 'weak'
                return {'signal': 'BUY', 'strength': strength}
            else:
                strength = 'strong' if current_macd < 0 else 'weak'
                return {'signal': 'SELL', 'strength': strength}
                
        except Exception as e:
            logger.error(f"Error calculating MACD: {str(e)}")
            return None
            
    def check_rsi(self, symbol, period=14, interval="1d"):
        """Calculate RSI and generate signals."""
        try:
            # Get historical data
            data = self.market_data.get_historical_data(symbol, interval)
            if data is None or len(data) < period:
                return None
                
            # Calculate RSI
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            
            # Generate signals
            if current_rsi > 70:
                return {'signal': 'SELL', 'strength': 'strong', 'rsi': current_rsi}
            elif current_rsi < 30:
                return {'signal': 'BUY', 'strength': 'strong', 'rsi': current_rsi}
            else:
                return {'signal': 'NEUTRAL', 'strength': 'weak', 'rsi': current_rsi}
                
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return None
            
    def check_moving_averages(self, symbol, interval="1d", lookback=20):
        """Check moving average signals for a symbol."""
        try:
            # Get historical data
            data = self.market_data.get_historical_data(symbol, interval)
            if data is None or len(data) < lookback:
                return None
                
            # Calculate moving averages
            data['SMA20'] = data['close'].rolling(window=20).mean()
            data['SMA50'] = data['close'].rolling(window=50).mean()
            
            # Get current values
            current_price = data['close'].iloc[-1]
            sma20 = data['SMA20'].iloc[-1]
            sma50 = data['SMA50'].iloc[-1]
            
            # Generate signals
            if current_price > sma20 and sma20 > sma50:
                return {'signal': 'BUY', 'strength': 'strong'}
            elif current_price < sma20 and sma20 < sma50:
                return {'signal': 'SELL', 'strength': 'strong'}
            else:
                return {'signal': 'NEUTRAL', 'strength': 'weak'}
                
        except Exception as e:
            logger.error(f"Error checking moving averages: {str(e)}")
            return None
            
    def __init__(self):
        from market_data_provider import MarketDataProvider
        from market_data_streamer import MarketDataStreamer
        from telegram_bot import TelegramBot
        from config import telegram_bot_token, telegram_chat_id
        
        # Initialize market data components
        self.market_data = MarketDataProvider(use_kite=True)
        self.streamer = MarketDataStreamer()
        self.streamer.add_callback(self.on_market_data)
        
        # Initialize Telegram bot
        self.telegram = TelegramBot(
            token=telegram_bot_token,
            chat_id=telegram_chat_id
        )
        
        # Initialize advanced trading strategies
        from advanced_trading_strategies import (
            AdvancedTradingStrategies, 
            AdvancedStrategyParams,
            Timeframe
        )
        self.strategies = AdvancedTradingStrategies(AdvancedStrategyParams())
        self.timeframes = [
            Timeframe.M15,  # Primary analysis
            Timeframe.H1,   # Trend confirmation
            Timeframe.H4    # Overall market context
        ]
        
        # Initialize system monitor
        from system_monitor import SystemMonitor
        self.monitor = SystemMonitor()
        
        # Initialize risk management system
        from risk_manager import RiskManager, RiskConfig
        self.risk_manager = RiskManager(RiskConfig())
        
        # Initialize paper trading system
        from paper_trading_system import PaperTradingSystem
        self.paper_trader = PaperTradingSystem(initial_capital=100000.0)
        
        # Initialize dashboard
        from dashboard_manager import DashboardManager
        self.dashboard = DashboardManager(self)
        
        # Initialize signal generation state
        self.is_running = False
        self.instruments = ["NIFTY50", "BANKNIFTY", "SENSEX"]  # Default instruments to track
        self.signals = []
        self.last_signal_time = {}
        
        # Initialize signal components
        self.validator = SignalValidator()
        self.generator = SignalGenerator()
        self.signal_manager = SignalManager(self)
        
        # Signal generation settings
        self.min_signal_interval = 300  # 5 minutes between signals
        self.max_active_signals = 5  # Maximum concurrent signals
        self.signal_expiry = 3600  # Signals expire after 1 hour if not triggered
        self.signal_cooldown = 300  # 5 minutes between signals for same instrument
        
        # Signal validation thresholds
        self.min_volume_threshold = 100000  # Minimum volume for valid signal
        self.min_price_move = 0.5  # Minimum price movement percentage
        self.confirmation_required = 2  # Number of indicators needed for confirmation
        
        # Initialize technical indicators
        self.indicators = [
            self.check_moving_averages,
            self.check_rsi,
            self.check_macd,
            self.check_bollinger_bands,
            self.check_support_resistance
        ]
        
        # Start background services
        import threading
        
        # Start monitoring
        self.monitor_thread = threading.Thread(target=self.monitor.start_monitoring, daemon=True)
        self.monitor_thread.start()
        
        # Start dashboard
        self.dashboard_thread = threading.Thread(
            target=self.dashboard.run,
            kwargs={'port': 5500},
            daemon=True
        )
        self.dashboard_thread.start()
        
        # Start position monitoring
        self.position_monitor_thread = threading.Thread(
            target=self.monitor_paper_positions,
            daemon=True
        )
        self.position_monitor_thread.start()
        
        # Start market data stream
        self.streamer.start()
        
    def on_market_data(self, data):
        """Handle incoming market data updates"""
        try:
            # Process the market data
            instrument_token = data['instrument_token']
            last_price = data['last_price']
            volume = data.get('volume', 0)
            
            # Add to data buffer for analysis
            self.update_market_data_buffer(instrument_token, data)
            
            # Run strategy analysis
            self.analyze_market_data(instrument_token)
            
        except Exception as e:
            logger.error(f"Error processing market data: {e}", exc_info=True)
            
    def update_market_data_buffer(self, instrument_token, data):
        """Update market data buffer for analysis"""
        instrument = self.get_instrument_name(instrument_token)
        for timeframe in self.timeframes:
            self.strategies.update_data(instrument, timeframe, data)
        
    def analyze_market_data(self, instrument_token):
        """Analyze market data and generate signals"""
        instrument = self.get_instrument_name(instrument_token)
        
        # Get option chain data for the instrument
        option_data = self.market_data.get_option_chain(instrument)
        
        # Analyze for trading opportunities
        opportunity = self.strategies.analyze_option_opportunity(
            instrument,
            option_data
        )
        
        if opportunity:
            # Check risk management criteria
            can_trade, reason = self.risk_manager.can_take_trade(
                opportunity,
                self.paper_trader.account.current_balance
            )
            
            if can_trade:
                # Calculate position size
                lots = self.risk_manager.calculate_position_size(
                    opportunity,
                    self.paper_trader.account.current_balance
                )
                opportunity['lot_size'] = lots
                
                # Generate and send signal
                self.generate_signal_from_opportunity(opportunity)
            else:
                logger.info(f"Trade rejected by risk management: {reason}")
        
        for signal_data in self.signals:
            # Create trading signal
            signal = TradingSignal(
                id=f"SIGNAL_{int(time.time())}",
                timestamp=datetime.now(),
                instrument=self.get_instrument_name(instrument_token),
                option_symbol=self.get_option_symbol(instrument_token, signal_data),
                signal_type=signal_data['signal'],
                strike_price=self.calculate_strike_price(instrument_token, signal_data),
                option_entry_price=signal_data['price_level'],
                option_target_price=self.calculate_target(signal_data),
                option_stop_loss=self.calculate_stop_loss(signal_data),
                confidence=signal_data['strength'],
                setup_description=self.get_signal_description(signal_data),
                technical_indicators=self.get_technical_indicators(instrument_token),
                risk_reward_ratio=2.0,  # Configurable
                expiry_date=self.get_next_expiry(),
                lot_size=50  # Standard lot size
            )
            
            # Send signal notification
            self.send_signal_notification(signal)
            
    def get_instrument_name(self, instrument_token):
        """Get instrument name from token"""
        # Implementation based on your instrument mapping
        return "NIFTY"  # Placeholder
        
    def get_option_symbol(self, instrument_token, signal_data):
        """Generate option symbol based on signal"""
        strike = self.calculate_strike_price(instrument_token, signal_data)
        option_type = "CE" if "BULLISH" in signal_data['signal'] else "PUT"
        return f"NIFTY {strike} {option_type}"
        
    def calculate_strike_price(self, instrument_token, signal_data):
        """Calculate appropriate strike price"""
        current_price = signal_data['price_level']
        # Round to nearest strike (assuming 50 point intervals for NIFTY)
        return round(current_price / 50) * 50
        
    def calculate_target(self, signal_data):
        """Calculate price target"""
        return signal_data['price_level'] * 1.2  # 20% target
        
    def calculate_stop_loss(self, signal_data):
        """Calculate stop loss"""
        return signal_data['price_level'] * 0.9  # 10% stop loss
        
    def get_signal_description(self, signal_data):
        """Generate human-readable signal description"""
        if "BREAKOUT" in signal_data['signal']:
            return f"{signal_data['signal']} with {signal_data['strength']}% strength"
        return f"{signal_data['signal']} signal detected"
        
    def get_technical_indicators(self, instrument_token):
        """Get current technical indicator values"""
        df = self.strategies.get_dataframe(instrument_token)
        if len(df) > 0:
            return {
                "RSI": df['rsi'].iloc[-1] if 'rsi' in df else None,
                "EMA_Cross": "Bullish" if df['ema_short'].iloc[-1] > df['ema_long'].iloc[-1] else "Bearish"
                if 'ema_short' in df and 'ema_long' in df else None
            }
        return {}
        
    def get_next_expiry(self):
        """Get next expiry date"""
        # Implementation based on your expiry calendar
        today = datetime.now()
        # Assuming monthly expiry
        if today.month == 12:
            next_month = 1
            next_year = today.year + 1
        else:
            next_month = today.month + 1
            next_year = today.year
        return f"{next_month:02d}-{next_year}"
        
        # Initialize ProTrader setups
        self.pro_setups = ProTraderSetups()
        logger.info("LiveSignalEngine initialized successfully")
    
    def send_signal_notification(self, signal: TradingSignal):
        """Send formatted signal notification via Telegram"""
        current_time = datetime.now()
        
        # Prepare signal data
        signal_data = {
            "timestamp": current_time,
            "signal_type": signal.signal_type,
            "instrument": signal.instrument,
            "option_symbol": signal.option_symbol,
            "confidence": signal.confidence,
            "option_entry_price": signal.option_entry_price,
            "option_target_price": signal.option_target_price,
            "option_stop_loss": signal.option_stop_loss,
            "status": "ACTIVE",
            "profit": 0,
            "lot_size": signal.lot_size
        }
        
        # Get risk metrics
        risk_metrics = self.risk_manager.get_risk_metrics()
        
        # Format Telegram message
        message = f"""
🎯 *NEW PREMIUM TRADING SIGNAL*
------------------
📊 *{signal.instrument}* ({signal.option_symbol})
▶️ *Signal*: {signal.signal_type}
💰 *Strike*: {signal.strike_price}
📈 *Entry*: {signal.option_entry_price}
🎯 *Target*: {signal.option_target_price}
🛑 *Stop Loss*: {signal.option_stop_loss}
📦 *Lot Size*: {signal.lot_size}

💡 *Setup*: {signal.setup_description}
⚖️ *Risk/Reward*: {signal.risk_reward_ratio:.2f}
🎲 *Confidence*: {signal.confidence}%

📊 *Risk Analysis*:
• Account Risk: {signal.lot_size * abs(signal.option_entry_price - signal.option_stop_loss):.2f}
• Open Positions: {risk_metrics['open_positions']}
• Daily P&L: ₹{risk_metrics['daily_pnl']:.2f}

⏰ *{current_time.strftime('%I:%M:%S %p')}*
📅 *{current_time.strftime('%d-%b-%Y')}*

💫 _Premium Signal Service_
        """
        
        # Send to Telegram
        try:
            self.telegram.send_message(message, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
        
        # Log in monitoring system
        self.monitor.log_signal(signal_data)
        
        # Update dashboard
        self.dashboard.add_signal(signal_data)
        
        # Execute paper trade
        paper_trade = self.paper_trader.enter_trade(signal_data)
        if paper_trade:
            # Add to risk manager tracking
            self.risk_manager.add_position(paper_trade.trade_id, signal_data)
            logger.info(f"Paper trade entered: {paper_trade.trade_id}")
            
    def monitor_paper_positions(self):
        """Monitor and update paper trading positions"""
        while True:
            try:
                # Get current market data for active positions
                symbols = [
                    trade.option_symbol
                    for trade in self.paper_trader.account.current_positions.values()
                ]
                
                if symbols:
                    market_data = {}
                    for symbol in symbols:
                        # Get real-time price from market data provider
                        price = self.market_data.get_ltp(symbol)
                        if price:
                            market_data[symbol] = {'last_price': price}
                    
                    # Update paper trading positions
                    self.paper_trader.update_positions(market_data)
                    
                    # Get updated metrics
                    metrics = self.paper_trader.get_performance_metrics()
                    logger.debug(f"Paper trading metrics: {metrics}")
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error monitoring positions: {e}", exc_info=True)
                time.sleep(5)  # Wait before retrying
        
        # Get system health
        health = self.monitor.get_health_status()
        
        message = f"""
🎯 *NEW TRADING SIGNAL*
------------------
📊 *{signal.instrument}* ({signal.option_symbol})
▶️ *Signal*: {signal.signal_type}
💰 *Strike*: {signal.strike_price}
📈 *Entry*: {signal.option_entry_price}
🎯 *Target*: {signal.option_target_price}
🛑 *Stop Loss*: {signal.option_stop_loss}
📊 *Risk/Reward*: {signal.risk_reward_ratio:.2f}
🎲 *Confidence*: {signal.confidence}%
📅 *Expiry*: {signal.expiry_date}
📦 *Lot Size*: {signal.lot_size}

💡 *Setup*: {signal.setup_description}

🔄 *System Health*: {'✅' if health['status'] == 'healthy' else '⚠️'}
        """
        try:
            self.telegram.send_message(message, parse_mode="Markdown")
            logger.info(f"Signal notification sent successfully: {signal.id}")
        except Exception as e:
            logger.error(f"Failed to send signal notification: {e}", exc_info=True)
        self.signals = []
        self.market_data = {}
        self.pro_setups = ProTraderSetups()  # Initialize professional setups
        
        # Enhanced strategy parameters
        self.strategy_params = {
            'vwap': {
                'reversal_confirmation_period': 3,
                'volume_threshold': 1.5
            },
            'momentum': {
                'ema_fast': 9,
                'ema_slow': 21,
                'rsi_period': 14,
                'rsi_overbought': 70,
                'rsi_oversold': 30
            },
            'breakout': {
                'volume_surge_threshold': 2.0,
                'consolidation_periods': 3,
                'minimum_consolidation_width': 0.5  # % of price
            },
            'risk_management': {
                'max_risk_per_trade': 1.0,  # % of capital
                'minimum_risk_reward': 1.5,
                'trailing_stop': 0.5  # % of price
            }
        }
        self.is_running = False
        self.signal_thread = None
        self.market_data_provider = market_data_provider
        self.telegram_bot = telegram_bot
        
        # Instruments to monitor
        self.instruments = {
            'NIFTY': {
                'lot_size': 50,
                'atm_range': 500,  # Monitor strikes within ±500 of ATM
                'min_premium': 50,  # Minimum option premium
                'max_premium': 300  # Maximum option premium
            },
            'BANKNIFTY': {
                'lot_size': 25,
                'atm_range': 1000,
                'min_premium': 70,
                'max_premium': 400
            }
        }
        
        # Technical indicators configuration
        self.indicators = {
            'RSI': {'period': 14, 'overbought': 70, 'oversold': 30},
            'MACD': {'fast': 12, 'slow': 26, 'signal': 9},
            'Supertrend': {'period': 10, 'multiplier': 3},
            'Volume': {'avg_period': 20, 'min_ratio': 1.5}
        }
        
        # Signal generation parameters
        self.min_confidence = 75  # Increased minimum confidence
        self.max_signals_per_hour = 4  # Reduced for higher quality
        self.signal_cooldown = 900  # 15 minutes between signals
        self.last_signal_time = {}
        
        # Risk management
        self.max_risk_per_trade = 2.0  # Maximum % of capital to risk
        self.min_risk_reward = 1.5  # Minimum risk-reward ratio
        
        logger.info("Live Signal Engine initialized with advanced configuration")

    def calculate_indicators(self, data: pd.DataFrame) -> dict:
        """Calculate technical indicators for signal generation"""
        indicators = {}
        
        try:
            # RSI Calculation
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=self.indicators['RSI']['period']).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.indicators['RSI']['period']).mean()
            rs = gain / loss
            indicators['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD Calculation
            exp1 = data['close'].ewm(span=self.indicators['MACD']['fast']).mean()
            exp2 = data['close'].ewm(span=self.indicators['MACD']['slow']).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=self.indicators['MACD']['signal']).mean()
            indicators['MACD'] = macd
            indicators['MACD_Signal'] = signal
            
            # Supertrend Calculation
            atr_period = self.indicators['Supertrend']['period']
            factor = self.indicators['Supertrend']['multiplier']
            
            tr1 = data['high'] - data['low']
            tr2 = abs(data['high'] - data['close'].shift())
            tr3 = abs(data['low'] - data['close'].shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=atr_period).mean()
            
            upperband = ((data['high'] + data['low']) / 2) + (factor * atr)
            lowerband = ((data['high'] + data['low']) / 2) - (factor * atr)
            indicators['Supertrend_Upper'] = upperband
            indicators['Supertrend_Lower'] = lowerband
            
            # Volume Analysis
            indicators['Volume_Ratio'] = data['volume'] / data['volume'].rolling(window=self.indicators['Volume']['avg_period']).mean()
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return {}
            
        return indicators

    def analyze_option_chain(self, instrument: str) -> dict:
        """Analyze option chain for potential setups"""
        try:
            # Get current price and option chain
            spot_price = self.market_data_provider.get_ltp(instrument)
            option_chain = self.market_data_provider.get_option_chain(instrument)
            
            # Find ATM strike
            atm_strike = round(spot_price / 50) * 50
            
            # Filter relevant strikes
            config = self.instruments[instrument]
            min_strike = atm_strike - config['atm_range']
            max_strike = atm_strike + config['atm_range']
            
            relevant_options = []
            for option in option_chain:
                if (min_strike <= option['strike'] <= max_strike and 
                    config['min_premium'] <= option['last_price'] <= config['max_premium']):
                    relevant_options.append(option)
            
            return {
                'spot_price': spot_price,
                'atm_strike': atm_strike,
                'options': relevant_options
            }
            
        except Exception as e:
            logger.error(f"Error analyzing option chain: {e}")
            return {}

    def generate_signal(self, instrument: str) -> Optional[TradingSignal]:
        """Generate trading signal based on technical analysis and option chain"""
        try:
            # Get historical data for analysis
            data = self.market_data_provider.get_historical_data(
                instrument, 
                interval='5minute',
                limit=100
            )
            
            if data.empty:
                return None
                
            # Calculate indicators
            indicators = self.calculate_indicators(data)
            if not indicators:
                return None
                
            # Analyze option chain
            option_data = self.analyze_option_chain(instrument)
            if not option_data:
                return None
                
            # Signal generation logic
            signal = None
            rsi = indicators['RSI'].iloc[-1]
            macd = indicators['MACD'].iloc[-1]
            macd_signal = indicators['MACD_Signal'].iloc[-1]
            volume_ratio = indicators['Volume_Ratio'].iloc[-1]
            
            # Bullish setup
            if (rsi < self.indicators['RSI']['oversold'] and 
                macd > macd_signal and
                volume_ratio > self.indicators['Volume']['min_ratio']):
                
                # Find suitable CE option
                for option in option_data['options']:
                    if option['type'] == 'CE':
                        entry = option['last_price']
                        target = entry * 1.5  # 50% target
                        stop_loss = entry * 0.8  # 20% stop loss
                        
                        signal = TradingSignal(
                            id=f"{instrument}_CE_{int(time.time())}",
                            timestamp=datetime.now(),
                            instrument=instrument,
                            option_symbol=f"{instrument}{option['strike']}CE",
                            signal_type="BUY_CALL",
                            strike_price=option['strike'],
                            option_entry_price=entry,
                            option_target_price=target,
                            option_stop_loss=stop_loss,
                            confidence=min(85.0, rsi + volume_ratio * 10),
                            setup_description="Oversold RSI with MACD bullish crossover and high volume",
                            technical_indicators={
                                'RSI': round(rsi, 2),
                                'MACD': 'Bullish Crossover',
                                'Volume': f"{round(volume_ratio, 1)}x average"
                            },
                            risk_reward_ratio=(target - entry) / (entry - stop_loss),
                            expiry_date=option['expiry'],
                            lot_size=self.instruments[instrument]['lot_size']
                        )
                        break
                        
            # Bearish setup
            elif (rsi > self.indicators['RSI']['overbought'] and 
                  macd < macd_signal and
                  volume_ratio > self.indicators['Volume']['min_ratio']):
                  
                # Find suitable PE option
                for option in option_data['options']:
                    if option['type'] == 'PE':
                        entry = option['last_price']
                        target = entry * 1.5
                        stop_loss = entry * 0.8
                        
                        signal = TradingSignal(
                            id=f"{instrument}_PE_{int(time.time())}",
                            timestamp=datetime.now(),
                            instrument=instrument,
                            option_symbol=f"{instrument}{option['strike']}PE",
                            signal_type="BUY_PUT",
                            strike_price=option['strike'],
                            option_entry_price=entry,
                            option_target_price=target,
                            option_stop_loss=stop_loss,
                            confidence=min(85.0, (100 - rsi) + volume_ratio * 10),
                            setup_description="Overbought RSI with MACD bearish crossover and high volume",
                            technical_indicators={
                                'RSI': round(rsi, 2),
                                'MACD': 'Bearish Crossover',
                                'Volume': f"{round(volume_ratio, 1)}x average"
                            },
                            risk_reward_ratio=(target - entry) / (entry - stop_loss),
                            expiry_date=option['expiry'],
                            lot_size=self.instruments[instrument]['lot_size']
                        )
                        break
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return None
            
    def broadcast_signal(self, signal: TradingSignal):
        """Broadcast trading signal to Telegram"""
        try:
            if not self.telegram_bot:
                logger.warning("Telegram bot not configured")
                return
                
            message = (
                "🎯 *FnO Trading Signal*\n\n"
                f"Symbol: `{signal.instrument}`\n"
                f"Option: `{signal.option_symbol}`\n"
                f"Type: `{signal.signal_type}`\n\n"
                f"Entry: `₹{signal.option_entry_price:.2f}`\n"
                f"Target: `₹{signal.option_target_price:.2f}` 🎯\n"
                f"Stop Loss: `₹{signal.option_stop_loss:.2f}` 🛑\n\n"
                f"Lot Size: `{signal.lot_size}`\n"
                f"Risk/Reward: `{signal.risk_reward_ratio:.2f}`\n"
                f"Confidence: `{signal.confidence:.1f}%`\n\n"
                "*Technical Analysis:*\n"
            )
            
            for indicator, value in signal.technical_indicators.items():
                message += f"{indicator}: `{value}`\n"
                
            message += f"\nSetup: _{signal.setup_description}_\n\n"
            message += f"⏰ `{signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}`"
            
            self.telegram_bot.send_message(message)
            logger.info(f"Signal broadcast for {signal.option_symbol}")
            
        except Exception as e:
            logger.error(f"Error broadcasting signal: {e}")

    def start_signal_generation(self):
        """Start the signal generation engine"""
        if self.is_running:
            logger.warning("Signal generation already running")
            return
            
        self.is_running = True
        self.signal_thread = threading.Thread(target=self._signal_generation_loop)
        self.signal_thread.daemon = True
        self.signal_thread.start()
        logger.info("Signal generation started")
        
    def _signal_generation_loop(self):
        """Main signal generation loop"""
        while self.is_running:
            try:
                # Check market hours (9:15 AM to 3:30 PM, Monday to Friday)
                now = datetime.now()
                if (now.weekday() >= 5 or  # Weekend
                    now.hour < 9 or  # Before market
                    (now.hour == 9 and now.minute < 15) or  # Before market
                    now.hour > 15 or  # After market
                    (now.hour == 15 and now.minute > 30)):  # After market
                    time.sleep(60)
                    continue
                
                # Process each instrument
                for instrument in self.instruments:
                    try:
                        # Check signal cooldown
                        last_time = self.last_signal_time.get(instrument)
                        if last_time and (datetime.now() - last_time).seconds < self.signal_cooldown:
                            continue
                            
                        # Generate signal
                        signal = self.generate_signal(instrument)
                        
                        if signal and signal.confidence >= self.min_confidence:
                            # Broadcast signal
                            self.broadcast_signal(signal)
                            self.signals.append(signal)
                            self.last_signal_time[instrument] = datetime.now()
                            
                    except Exception as e:
                        logger.error(f"Error processing {instrument}: {e}")
                        
                # Sleep for 5 minutes before next check
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in signal generation loop: {e}")
                time.sleep(60)  # Wait a minute before retrying
                
    def stop_signal_generation(self):
        """Stop the signal generation engine"""
        self.is_running = False
        if self.signal_thread:
            self.signal_thread.join(timeout=1)
        logger.info("Signal generation stopped")
        
        logger.info("Live Signal Engine initialized")
    
    def start_signal_generation(self):
        """Start the signal generation process"""
        if not self.is_running:
            self.is_running = True
            self.signal_thread = threading.Thread(target=self._signal_generation_loop)
            self.signal_thread.daemon = True
            self.signal_thread.start()
            logger.info("🚀 Signal generation started")
        else:
            logger.info("Signal generation already running")
    
    def stop_signal_generation(self):
        """Stop the signal generation process"""
        self.is_running = False
        if self.signal_thread:
            self.signal_thread.join(timeout=5)
        logger.info("⏹️ Signal generation stopped")
    
    def _signal_generation_loop(self):
        """Main signal generation loop"""
        while self.is_running:
            try:
                # Update market data
                self._update_market_data()
                
                # Generate signals based on market conditions
                self._generate_signals()
                
                # Clean old signals
                self._cleanup_old_signals()
                
                # Sleep for 30 seconds before next iteration
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in signal generation loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _update_market_data(self):
        """Update live market data"""
        try:
            for instrument in self.instruments:
                # Simulate live data (replace with actual API calls)
                if instrument == 'NIFTY':
                    symbol = '^NSEI'
                elif instrument == 'BANKNIFTY':
                    symbol = '^NSEBANK'
                else:
                    symbol = f"{instrument}.NS"
                
                try:
                    # Get live data using yfinance
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d", interval="1m")
                    
                    if not hist.empty:
                        latest = hist.iloc[-1]
                        prev_close = hist.iloc[-2]['Close'] if len(hist) > 1 else latest['Close']
                        
                        self.market_data[instrument] = {
                            'ltp': round(float(latest['Close']), 2),
                            'open': round(float(latest['Open']), 2),
                            'high': round(float(latest['High']), 2),
                            'low': round(float(latest['Low']), 2),
                            'volume': int(latest['Volume']),
                            'change': round(float(latest['Close'] - prev_close), 2),
                            'change_percent': round(((float(latest['Close'] - prev_close) / prev_close) * 100), 2),
                            'timestamp': datetime.now().strftime('%H:%M:%S')
                        }
                    else:
                        # Fallback to simulated data
                        self._generate_simulated_data(instrument)
                        
                except Exception as e:
                    logger.warning(f"Failed to get real data for {instrument}, using simulated: {e}")
                    self._generate_simulated_data(instrument)
                    
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
    
    def _generate_simulated_data(self, instrument: str):
        """Generate simulated market data"""
        base_prices = {'NIFTY': 24800, 'BANKNIFTY': 55000}  # Removed FINNIFTY
        base_price = base_prices.get(instrument, 25000)
        
        # Add some randomness
        change_percent = random.uniform(-2.0, 2.0)
        ltp = base_price * (1 + change_percent / 100)
        
        self.market_data[instrument] = {
            'ltp': round(ltp, 2),
            'open': round(base_price, 2),
            'high': round(ltp * 1.01, 2),
            'low': round(ltp * 0.99, 2),
            'volume': random.randint(100000, 500000),
            'change': round(ltp - base_price, 2),
            'change_percent': round(change_percent, 2),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    
    def _generate_signals(self):
        """Generate trading signals based on professional setups and market analysis"""
        try:
            for instrument in self.instruments:
                # 1. Check cooldown period
                if self._is_in_cooldown(instrument):
                    continue
                
                # 2. Analyze market conditions using pro setups
                conditions = self._check_market_conditions(instrument)
                if not conditions['suitable']:
                    logger.info(f"Skipping {instrument}: {conditions['reason']}")
                    continue
                
                # 3. Get pro trader setups for current conditions
                market_data = self.market_data[instrument]
                df = pd.DataFrame([market_data])
                
                # 4. Get trade setup from pro analysis
                setup = self.pro_setups.get_trade_setup(df)
                
                # 5. Generate signal only for high-confidence setups
                if setup['confidence'] >= self.min_confidence:
                    signal = self._create_signal_from_setup(instrument, setup, conditions)
                    
                    if signal:
                        self.signals.append(signal)
                        self.last_signal_time[instrument] = datetime.now()
                        logger.info(f"🎯 High-quality signal generated: {signal.instrument} {signal.signal_type} (Confidence: {setup['confidence']}%)")
                        
                        # Broadcast signal
                        self.broadcast_signal(signal)
                
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
    
    def _is_in_cooldown(self, instrument: str) -> bool:
        """Check if instrument is in signal cooldown period"""
        if instrument not in self.last_signal_time:
            return False
        
        last_time = self.last_signal_time[instrument]
        now = datetime.now()
        return (now - last_time).total_seconds() < self.signal_cooldown
    
    def _check_market_conditions(self, instrument: str) -> dict:
        """Check if market conditions are suitable for signal generation"""
        if instrument not in self.market_data:
            return {'suitable': False, 'reason': 'No market data available'}
        
        try:
            data = self.market_data[instrument]
            df = pd.DataFrame([data])
            
            # 1. Get market analysis from pro setups
            market_condition = self.pro_setups.analyze_market_condition(df)
            
            # 2. Check volatility conditions
            if market_condition['volatility'] == 'high' and abs(data['change_percent']) > 5.0:
                return {'suitable': False, 'reason': 'Extreme volatility'}
                
            if market_condition['volatility'] == 'low' and abs(data['change_percent']) < 0.1:
                return {'suitable': False, 'reason': 'Insufficient volatility'}
            
            # 3. Check volume conditions
            if market_condition['volume_condition'] == 'low':
                return {'suitable': False, 'reason': 'Low volume'}
            
            # 4. Check recommended setups
            if not market_condition['recommended_setups']:
                return {'suitable': False, 'reason': 'No valid setups found'}
            
            # 5. Market is suitable with specific setups
            return {
                'suitable': True,
                'market_condition': market_condition,
                'trend': market_condition['trend'],
                'volatility': market_condition['volatility'],
                'recommended_setups': market_condition['recommended_setups']
            }
            
        except Exception as e:
            logger.error(f"Error checking market conditions: {e}")
            return {'suitable': False, 'reason': f'Analysis error: {str(e)}'}
    
    def _create_signal_from_setup(self, instrument: str, setup: Dict, conditions: Dict) -> Optional[TradingSignal]:
        """Create a detailed, actionable trading signal based on professional setup analysis."""
        try:
            if instrument not in self.market_data:
                logger.warning(f"No market data for {instrument} to create signal.")
                return None

            data = self.market_data[instrument]
            ltp = data['ltp']
            
            # 1. Determine Signal Direction from Setup
            if setup['status'] == 'bullish_setup':
                signal_type = 'BUY_CALL'
            elif setup['status'] == 'bearish_setup':
                signal_type = 'BUY_PUT'
            else:
                return None
                
            # Use the professional setup's analysis
            entry_zone = setup['entry_zone']
            stop_loss = setup['stop_loss']
            target = setup['target']

            # 2. Select Strike Price
            strike_step = 50 if instrument == 'NIFTY' else 100
            base_strike = round(ltp / strike_step) * strike_step
            strike_price = base_strike
            option_type = "CE" if signal_type == 'BUY_CALL' else "PE"

            # 3. Simulate Option Premium
            simulated_premium = round(random.uniform(70, 150), 2)
            
            # 4. Define Entry, Target, and Stop-Loss
            entry_price = simulated_premium
            target_price = round(entry_price * random.uniform(1.20, 1.50), 2)
            stop_loss = round(entry_price * random.uniform(0.80, 0.90), 2)

            # 5. Calculate Risk-Reward Ratio
            risk = abs(entry_price - stop_loss)
            reward = abs(target_price - entry_price)
            rr_ratio = round(reward / risk, 2) if risk > 0 else 1.0

            # 6. Generate Confidence and Description
            confidence = random.uniform(70, 95)
            setup_desc = self._generate_setup_description(instrument, signal_type)
            
            # 7. Construct the Signal
            expiry = self._get_next_expiry()
            option_symbol = f"{instrument} {int(strike_price)} {option_type}"

            signal = TradingSignal(
                id=f"{instrument}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                instrument=instrument,
                option_symbol=option_symbol,
                signal_type=signal_type,
                strike_price=strike_price,
                option_entry_price=entry_price,
                option_target_price=target_price,
                option_stop_loss=stop_loss,
                confidence=round(confidence, 1),
                setup_description=setup_desc,
                technical_indicators=self._generate_technical_indicators(data),
                risk_reward_ratio=rr_ratio,
                expiry_date=expiry,
                lot_size=self._get_lot_size(instrument),
                status="ACTIVE"
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error creating detailed signal: {e}")
            return None
    
    def _generate_setup_description(self, instrument: str, signal_type: str) -> str:
        """Generate a compelling setup description for the signal."""
        
        market_outlook = "bullish" if "CALL" in signal_type else "bearish"
        
        if instrument not in self.market_data:
            return f"A {market_outlook} signal was generated for {instrument}."

        key_level = round(self.market_data[instrument]['ltp'] * random.uniform(0.995, 1.005), 2)
        
        templates = [
            f"📈 **{instrument} showing strong {market_outlook} momentum.** Breakout above key resistance at {key_level}. Volume confirmation suggests a strong upward move.",
            f"📉 **Potential reversal pattern forming in {instrument}.** Price action indicates a {market_outlook} bias. Watching for a break of the {key_level} level.",
            f"📊 **{instrument} is consolidating near a critical support level.** A {market_outlook} move is anticipated. Entry triggered on high volume.",
            f"🚀 **High-probability {market_outlook} setup for {instrument}.** The current trend is strong, and we're seeing signs of continuation above {key_level}."
        ]
        return random.choice(templates)
    
    def _generate_technical_indicators(self, data: Dict) -> Dict[str, Any]:
        """Generate technical indicators"""
        return {
            'rsi': round(random.uniform(30, 70), 1),
            'macd': round(random.uniform(-50, 50), 2),
            'volume_ratio': round(random.uniform(0.8, 2.5), 2),
            'support': round(data['ltp'] * random.uniform(0.95, 0.98), 2),
            'resistance': round(data['ltp'] * random.uniform(1.02, 1.05), 2),
            'trend': random.choice(['BULLISH', 'BEARISH', 'SIDEWAYS'])
        }
    
    def _get_next_expiry(self) -> str:
        """Get next Thursday expiry"""
        today = datetime.now()
        days_ahead = 3 - today.weekday()  # Thursday is 3
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        next_thursday = today + timedelta(days_ahead)
        return next_thursday.strftime('%d-%b-%Y')
    
    def _get_lot_size(self, instrument: str) -> int:
        """Get lot size for instrument"""
        lot_sizes = {'NIFTY': 50, 'BANKNIFTY': 15}
        return lot_sizes.get(instrument, 50)
    
    def _cleanup_old_signals(self):
        """Remove old signals"""
        now = datetime.now()
        self.signals = [
            signal for signal in self.signals
            if (now - signal.timestamp).total_seconds() < 3600  # Keep for 1 hour
        ]
    
    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """Get recent signals"""
        recent = sorted(self.signals, key=lambda x: x.timestamp, reverse=True)[:limit]
        return [self._signal_to_dict(signal) for signal in recent]
    
    def get_live_market_data(self) -> Dict:
        """Get current market data"""
        return self.market_data.copy()
    
    def generate_test_signal(self) -> None:
        """Generate and broadcast a test signal for validation"""
        try:
            # Current market data for NIFTY
            spot_price = 19750  # Example spot price
            atm_strike = round(spot_price / 50) * 50  # Round to nearest 50
            
            # Create a test signal
            test_signal = TradingSignal(
                id=f"TEST_SIGNAL_{int(time.time())}",
                timestamp=datetime.now(),
                instrument="NIFTY",
                option_symbol=f"NIFTY {atm_strike} CE",
                signal_type="BUY_CALL",
                strike_price=atm_strike,
                option_entry_price=145.50,
                option_target_price=175.00,
                option_stop_loss=130.00,
                confidence=85.5,
                setup_description="🎯 VALIDATION SIGNAL - DO NOT TRADE\n"
                                "Strong momentum breakout setup with volume confirmation. "
                                "Price above VWAP with RSI showing strength.",
                technical_indicators={
                    'RSI': '68.5 (Bullish)',
                    'VWAP': 'Price > VWAP',
                    'Volume': '2.1x average',
                    'Trend': 'Strong Uptrend',
                    'Support': f'{atm_strike-100}',
                    'Resistance': f'{atm_strike+150}'
                },
                risk_reward_ratio=2.0,
                expiry_date=(datetime.now() + timedelta(days=2)).strftime('%d-%b-%Y'),
                lot_size=50,
                status="TEST"
            )
            
            # Broadcast the test signal
            self.broadcast_signal(test_signal)
            logger.info("Test signal generated and broadcast")
            
        except Exception as e:
            logger.error(f"Error generating test signal: {e}")

    def _signal_to_dict(self, signal: TradingSignal) -> Dict:
        """Convert detailed signal to dictionary for API response."""
        return {
            'id': signal.id,
            'timestamp': signal.timestamp.strftime('%H:%M:%S'),
            'instrument': signal.instrument,
            'option_symbol': signal.option_symbol,
            'signal_type': signal.signal_type,
            'strike_price': signal.strike_price,
            'entry_price': signal.option_entry_price, # Use the option entry price
            'target_price': signal.option_target_price,
            'stop_loss': signal.option_stop_loss,
            'confidence': signal.confidence,
            'setup_description': signal.setup_description,
            'technical_indicators': signal.technical_indicators,
            'risk_reward_ratio': signal.risk_reward_ratio,
            'expiry_date': signal.expiry_date,
            'lot_size': signal.lot_size,
            'status': signal.status,
            # The 'premium' field is now represented by 'option_entry_price'
            'premium': signal.option_entry_price 
        }

    def generate_test_signal(self, instrument: str = None) -> Dict:
        """Generate a test signal immediately"""
        if not instrument:
            instrument = random.choice(self.instruments)
        
        # Update market data first
        self._update_market_data()
        
        # Force generate a signal
        signal = self._create_signal(instrument)
        if signal:
            self.signals.append(signal)
            logger.info(f"🧪 Test signal generated: {signal.instrument} {signal.signal_type}")
            return self._signal_to_dict(signal)
        
        return {}

# Global signal engine instance
signal_engine = LiveSignalEngine()