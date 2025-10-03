"""
Trading strategies for options signal generation
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class StrategyParams:
    rsi_period: int = 14
    rsi_overbought: float = 70
    rsi_oversold: float = 30
    ema_short: int = 9
    ema_long: int = 21
    atr_period: int = 14
    breakout_period: int = 20
    volume_ma_period: int = 20

class TradingStrategies:
    def __init__(self, params: Optional[StrategyParams] = None):
        self.params = params or StrategyParams()
        self.data_buffers = {}  # Store market data for analysis
        
    def update_data(self, instrument_token: int, market_data: Dict):
        """Update data buffer for an instrument"""
        if instrument_token not in self.data_buffers:
            self.data_buffers[instrument_token] = []
            
        self.data_buffers[instrument_token].append({
            'timestamp': pd.Timestamp.now(),
            'price': market_data['last_price'],
            'volume': market_data.get('volume', 0),
            'oi': market_data.get('oi', 0)
        })
        
        # Keep only recent data
        if len(self.data_buffers[instrument_token]) > max(
            self.params.breakout_period,
            self.params.rsi_period,
            self.params.ema_long,
            self.params.atr_period
        ) * 2:
            self.data_buffers[instrument_token].pop(0)
            
    def get_dataframe(self, instrument_token: int) -> pd.DataFrame:
        """Convert buffer to DataFrame for analysis"""
        if instrument_token not in self.data_buffers:
            return pd.DataFrame()
            
        df = pd.DataFrame(self.data_buffers[instrument_token])
        df.set_index('timestamp', inplace=True)
        return df
        
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        if len(df) < self.params.ema_long:
            return df
            
        # RSI
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.params.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.params.rsi_period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # EMAs
        df['ema_short'] = df['price'].ewm(span=self.params.ema_short).mean()
        df['ema_long'] = df['price'].ewm(span=self.params.ema_long).mean()
        
        # ATR
        high_low = df['price'].rolling(2).max() - df['price'].rolling(2).min()
        high_close = abs(df['price'].rolling(2).max() - df['price'].shift())
        low_close = abs(df['price'].rolling(2).min() - df['price'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['atr'] = true_range.rolling(self.params.atr_period).mean()
        
        # Volume MA
        df['volume_ma'] = df['volume'].rolling(self.params.volume_ma_period).mean()
        
        return df
        
    def check_breakout_strategy(self, df: pd.DataFrame) -> Optional[Dict]:
        """Check for breakout patterns"""
        if len(df) < self.params.breakout_period:
            return None
            
        current_price = df['price'].iloc[-1]
        prev_high = df['price'].iloc[-self.params.breakout_period:-1].max()
        prev_low = df['price'].iloc[-self.params.breakout_period:-1].min()
        volume_ratio = df['volume'].iloc[-1] / df['volume_ma'].iloc[-1]
        
        # Bullish breakout
        if current_price > prev_high and volume_ratio > 1.5:
            return {
                'signal': 'BULLISH_BREAKOUT',
                'strength': min((current_price - prev_high) / df['atr'].iloc[-1], 100),
                'price_level': prev_high
            }
            
        # Bearish breakout
        if current_price < prev_low and volume_ratio > 1.5:
            return {
                'signal': 'BEARISH_BREAKOUT',
                'strength': min((prev_low - current_price) / df['atr'].iloc[-1], 100),
                'price_level': prev_low
            }
            
        return None
        
    def check_momentum_strategy(self, df: pd.DataFrame) -> Optional[Dict]:
        """Check for momentum signals"""
        if len(df) < self.params.ema_long:
            return None
            
        rsi = df['rsi'].iloc[-1]
        ema_cross = (
            df['ema_short'].iloc[-2] <= df['ema_long'].iloc[-2] and
            df['ema_short'].iloc[-1] > df['ema_long'].iloc[-1]
        )
        
        if rsi < self.params.rsi_oversold and ema_cross:
            return {
                'signal': 'BULLISH_MOMENTUM',
                'strength': 100 - rsi,
                'price_level': df['price'].iloc[-1]
            }
            
        ema_cross_bearish = (
            df['ema_short'].iloc[-2] >= df['ema_long'].iloc[-2] and
            df['ema_short'].iloc[-1] < df['ema_long'].iloc[-1]
        )
        
        if rsi > self.params.rsi_overbought and ema_cross_bearish:
            return {
                'signal': 'BEARISH_MOMENTUM',
                'strength': rsi - 50,
                'price_level': df['price'].iloc[-1]
            }
            
        return None
        
    def analyze(self, instrument_token: int) -> List[Dict]:
        """Analyze market data and return signals"""
        df = self.get_dataframe(instrument_token)
        if len(df) < self.params.ema_long:
            return []
            
        df = self.calculate_indicators(df)
        signals = []
        
        # Check each strategy
        breakout = self.check_breakout_strategy(df)
        if breakout:
            signals.append(breakout)
            
        momentum = self.check_momentum_strategy(df)
        if momentum:
            signals.append(momentum)
            
        return signals