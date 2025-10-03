"""
Advanced trading strategies with multi-timeframe analysis
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import talib

class Timeframe(Enum):
    M1 = "1min"
    M5 = "5min"
    M15 = "15min"
    M30 = "30min"
    H1 = "1hour"
    H4 = "4hour"
    D1 = "1day"

@dataclass
class AdvancedStrategyParams:
    # Price action parameters
    atr_period: int = 14
    breakout_period: int = 20
    
    # Momentum parameters
    rsi_period: int = 14
    rsi_overbought: float = 70
    rsi_oversold: float = 30
    
    # Trend parameters
    ema_short: int = 9
    ema_medium: int = 21
    ema_long: int = 50
    
    # Volume parameters
    volume_ma_period: int = 20
    volume_breakout_mult: float = 1.5
    
    # Option specific
    iv_percentile_period: int = 20
    delta_threshold: float = 0.30
    gamma_threshold: float = 0.10

class AdvancedTradingStrategies:
    def __init__(self, params: Optional[AdvancedStrategyParams] = None):
        self.params = params or AdvancedStrategyParams()
        self.data_buffers = {}  # {(instrument, timeframe): DataFrame}
        
    def update_data(self, instrument: str, timeframe: Timeframe, data: Dict):
        """Update market data for specific timeframe"""
        key = (instrument, timeframe)
        if key not in self.data_buffers:
            self.data_buffers[key] = []
            
        self.data_buffers[key].append({
            'timestamp': pd.Timestamp.now(),
            'open': data.get('open', data.get('last_price', 0)),
            'high': data.get('high', data.get('last_price', 0)),
            'low': data.get('low', data.get('last_price', 0)),
            'close': data.get('last_price', 0),
            'volume': data.get('volume', 0),
            'oi': data.get('oi', 0)
        })
        
        # Keep buffer size manageable
        max_size = max(
            self.params.breakout_period,
            self.params.ema_long,
            self.params.iv_percentile_period
        ) * 3
        
        if len(self.data_buffers[key]) > max_size:
            self.data_buffers[key] = self.data_buffers[key][-max_size:]
            
    def get_dataframe(self, instrument: str, timeframe: Timeframe) -> pd.DataFrame:
        """Get data as DataFrame for analysis"""
        key = (instrument, timeframe)
        if key not in self.data_buffers:
            return pd.DataFrame()
            
        df = pd.DataFrame(self.data_buffers[key])
        df.set_index('timestamp', inplace=True)
        return df
        
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        if len(df) < self.params.ema_long:
            return df
            
        # Trend indicators
        df['ema_short'] = talib.EMA(df['close'], timeperiod=self.params.ema_short)
        df['ema_medium'] = talib.EMA(df['close'], timeperiod=self.params.ema_medium)
        df['ema_long'] = talib.EMA(df['close'], timeperiod=self.params.ema_long)
        
        # Momentum indicators
        df['rsi'] = talib.RSI(df['close'], timeperiod=self.params.rsi_period)
        df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(
            df['close'],
            fastperiod=12,
            slowperiod=26,
            signalperiod=9
        )
        
        # Volatility indicators
        df['atr'] = talib.ATR(
            df['high'],
            df['low'],
            df['close'],
            timeperiod=self.params.atr_period
        )
        
        # Volume indicators
        df['volume_ma'] = talib.SMA(df['volume'], timeperiod=self.params.volume_ma_period)
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        # Support/Resistance
        df['pivot'] = (df['high'] + df['low'] + df['close']) / 3
        df['r1'] = 2 * df['pivot'] - df['low']
        df['s1'] = 2 * df['pivot'] - df['high']
        
        return df
        
    def check_multi_timeframe_trend(self, instrument: str) -> Dict:
        """Analyze trend across multiple timeframes"""
        trends = {}
        for tf in [Timeframe.M15, Timeframe.H1, Timeframe.H4]:
            df = self.get_dataframe(instrument, tf)
            if len(df) < self.params.ema_long:
                continue
                
            df = self.calculate_indicators(df)
            
            # Determine trend
            ema_trend = (
                df['ema_short'].iloc[-1] > df['ema_medium'].iloc[-1] and
                df['ema_medium'].iloc[-1] > df['ema_long'].iloc[-1]
            )
            
            trends[tf.value] = {
                'trend': 'bullish' if ema_trend else 'bearish',
                'strength': abs(
                    df['ema_short'].iloc[-1] - df['ema_long'].iloc[-1]
                ) / df['atr'].iloc[-1]
            }
            
        return trends
        
    def analyze_option_opportunity(self, instrument: str, option_data: Dict) -> Optional[Dict]:
        """Analyze options trading opportunity"""
        # Get primary timeframe data
        df = self.get_dataframe(instrument, Timeframe.M15)
        if len(df) < self.params.ema_long:
            return None
            
        df = self.calculate_indicators(df)
        
        # Get multi-timeframe trend
        trends = self.check_multi_timeframe_trend(instrument)
        trend_alignment = all(
            t['trend'] == trends[Timeframe.H1.value]['trend']
            for t in trends.values()
        )
        
        # Check momentum
        momentum_signal = (
            df['rsi'].iloc[-1] < self.params.rsi_oversold and
            df['macd_hist'].iloc[-1] > df['macd_hist'].iloc[-2]
        ) or (
            df['rsi'].iloc[-1] > self.params.rsi_overbought and
            df['macd_hist'].iloc[-1] < df['macd_hist'].iloc[-2]
        )
        
        # Check volume
        volume_confirmed = df['volume_ratio'].iloc[-1] > self.params.volume_breakout_mult
        
        if trend_alignment and momentum_signal and volume_confirmed:
            signal_type = (
                'BULLISH' if trends[Timeframe.H1.value]['trend'] == 'bullish'
                else 'BEARISH'
            )
            
            return {
                'signal': f'{signal_type}_MULTI_TF',
                'trend_alignment': trends,
                'momentum': {
                    'rsi': df['rsi'].iloc[-1],
                    'macd_hist': df['macd_hist'].iloc[-1]
                },
                'volume_confirmation': df['volume_ratio'].iloc[-1],
                'support_resistance': {
                    'r1': df['r1'].iloc[-1],
                    's1': df['s1'].iloc[-1]
                },
                'strength': min(
                    100,
                    float(
                        trends[Timeframe.H1.value]['strength'] * 
                        df['volume_ratio'].iloc[-1]
                    )
                )
            }
            
        return None
        
    def get_position_size(self, capital: float, risk_per_trade: float, 
                         atr: float, option_price: float) -> int:
        """Calculate position size based on risk parameters"""
        risk_amount = capital * (risk_per_trade / 100)
        stop_size = atr * 1.5  # Using 1.5 ATR for stop loss
        
        # Calculate lot size
        contract_value = option_price * 50  # Assuming NIFTY lot size of 50
        max_lots = risk_amount / (stop_size * 50)
        
        return max(1, int(max_lots))