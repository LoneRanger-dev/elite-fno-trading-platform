"""
Advanced Signal Generator
Processes market data to generate accurate trading signals
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SignalGenerator:
    def __init__(self):
        self.lookback_periods = {
            'short': 20,
            'medium': 50,
            'long': 200
        }
        self.volatility_window = 20
        self.momentum_window = 14
        self.volume_ma_period = 20
        
    def generate_signals(self, data: Dict, market_context: Dict) -> List[Dict]:
        """
        Generate trading signals based on market data and context
        """
        try:
            signals = []
            
            # Convert data to DataFrame for easier analysis
            df = pd.DataFrame(data)
            
            # Calculate core technical indicators
            indicators = self.calculate_indicators(df)
            
            # Check various signal conditions
            trend_signals = self.analyze_trends(df, indicators)
            reversal_signals = self.analyze_reversals(df, indicators)
            breakout_signals = self.analyze_breakouts(df, indicators)
            
            # Combine all potential signals
            potential_signals = trend_signals + reversal_signals + breakout_signals
            
            # Filter and rank signals
            filtered_signals = self.filter_signals(potential_signals, market_context)
            ranked_signals = self.rank_signals(filtered_signals)
            
            return ranked_signals
            
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return []
            
    def calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate key technical indicators"""
        try:
            indicators = {}
            
            # Moving averages
            for period, days in self.lookback_periods.items():
                indicators[f'ma_{period}'] = df['close'].rolling(window=days).mean()
                
            # Volatility
            indicators['atr'] = self.calculate_atr(df)
            indicators['bollinger_bands'] = self.calculate_bollinger_bands(df)
            
            # Momentum
            indicators['rsi'] = self.calculate_rsi(df['close'])
            indicators['macd'] = self.calculate_macd(df['close'])
            
            # Volume analysis
            indicators['volume_ma'] = df['volume'].rolling(window=self.volume_ma_period).mean()
            indicators['obv'] = self.calculate_obv(df)
            
            # Support/Resistance
            indicators['support_resistance'] = self.identify_support_resistance(df)
            
            return indicators
            
        except Exception as e:
            logger.error(f"Indicator calculation error: {e}")
            return {}
            
    def analyze_trends(self, df: pd.DataFrame, indicators: Dict) -> List[Dict]:
        """Analyze price trends for signal generation"""
        try:
            signals = []
            
            # Check moving average alignments
            ma_short = indicators['ma_short']
            ma_medium = indicators['ma_medium']
            ma_long = indicators['ma_long']
            
            # Bullish trend conditions
            if (ma_short.iloc[-1] > ma_medium.iloc[-1] > ma_long.iloc[-1] and
                ma_short.iloc[-2] <= ma_medium.iloc[-2]):
                signals.append({
                    'type': 'TREND_LONG',
                    'strength': 0.8,
                    'reason': 'Golden cross with proper MA alignment'
                })
                
            # Bearish trend conditions
            elif (ma_short.iloc[-1] < ma_medium.iloc[-1] < ma_long.iloc[-1] and
                  ma_short.iloc[-2] >= ma_medium.iloc[-2]):
                signals.append({
                    'type': 'TREND_SHORT',
                    'strength': 0.8,
                    'reason': 'Death cross with proper MA alignment'
                })
                
            return signals
            
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            return []
            
    def analyze_reversals(self, df: pd.DataFrame, indicators: Dict) -> List[Dict]:
        """Identify potential reversal signals"""
        try:
            signals = []
            
            # RSI reversals
            rsi = indicators['rsi']
            if rsi.iloc[-1] < 30 and rsi.iloc[-2] >= 30:
                signals.append({
                    'type': 'REVERSAL_LONG',
                    'strength': 0.7,
                    'reason': 'RSI oversold with bullish divergence'
                })
            elif rsi.iloc[-1] > 70 and rsi.iloc[-2] <= 70:
                signals.append({
                    'type': 'REVERSAL_SHORT',
                    'strength': 0.7,
                    'reason': 'RSI overbought with bearish divergence'
                })
                
            # Check for candlestick patterns
            if self.check_reversal_patterns(df):
                pattern_type = self.identify_pattern_type(df)
                signals.append({
                    'type': f'REVERSAL_{pattern_type}',
                    'strength': 0.6,
                    'reason': f'Reversal pattern: {pattern_type}'
                })
                
            return signals
            
        except Exception as e:
            logger.error(f"Reversal analysis error: {e}")
            return []
            
    def analyze_breakouts(self, df: pd.DataFrame, indicators: Dict) -> List[Dict]:
        """Identify breakout opportunities"""
        try:
            signals = []
            
            # Bollinger Band breakouts
            bb = indicators['bollinger_bands']
            if df['close'].iloc[-1] > bb['upper'].iloc[-1]:
                signals.append({
                    'type': 'BREAKOUT_LONG',
                    'strength': 0.75,
                    'reason': 'Bullish BB breakout with volume confirmation'
                })
            elif df['close'].iloc[-1] < bb['lower'].iloc[-1]:
                signals.append({
                    'type': 'BREAKOUT_SHORT',
                    'strength': 0.75,
                    'reason': 'Bearish BB breakout with volume confirmation'
                })
                
            # Support/Resistance breakouts
            sr_levels = indicators['support_resistance']
            for level in sr_levels:
                if self.confirm_breakout(df, level):
                    signals.append({
                        'type': 'BREAKOUT_LONG',
                        'strength': 0.8,
                        'reason': f'Breakout from key level: {level}'
                    })
                    
            return signals
            
        except Exception as e:
            logger.error(f"Breakout analysis error: {e}")
            return []
            
    def filter_signals(self, signals: List[Dict], context: Dict) -> List[Dict]:
        """Filter signals based on market context and conditions"""
        try:
            filtered = []
            
            for signal in signals:
                # Check market conditions
                if context.get('market_condition', '') == 'HIGH_VOLATILITY' and signal['strength'] < 0.8:
                    continue
                    
                # Check trading session
                if not self.is_valid_trading_session():
                    continue
                    
                # Verify signal hasn't been repeated recently
                if self.is_signal_repeated(signal):
                    continue
                    
                # Add market context to signal
                signal['market_context'] = context
                filtered.append(signal)
                
            return filtered
            
        except Exception as e:
            logger.error(f"Signal filtering error: {e}")
            return []
            
    def rank_signals(self, signals: List[Dict]) -> List[Dict]:
        """Rank and prioritize signals"""
        try:
            # Calculate composite score for each signal
            for signal in signals:
                score = signal['strength']
                
                # Adjust based on market context
                if signal['market_context']['trend_strength'] > 0.7:
                    score *= 1.2
                    
                # Adjust based on volume confirmation
                if signal.get('volume_confirmed', False):
                    score *= 1.1
                    
                signal['final_score'] = score
                
            # Sort by final score
            ranked = sorted(signals, key=lambda x: x['final_score'], reverse=True)
            
            return ranked
            
        except Exception as e:
            logger.error(f"Signal ranking error: {e}")
            return signals  # Return original list if ranking fails
            
    def is_valid_trading_session(self) -> bool:
        """Check if current time is within valid trading hours"""
        now = datetime.now()
        
        # Trading hours: 9:15 AM to 3:30 PM IST
        market_open = now.replace(hour=9, minute=15, second=0)
        market_close = now.replace(hour=15, minute=30, second=0)
        
        return market_open <= now <= market_close
        
    def is_signal_repeated(self, signal: Dict) -> bool:
        """Check if similar signal was generated recently"""
        # Implementation depends on signal history tracking
        return False  # Placeholder
        
    def calculate_atr(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Average True Range"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=self.volatility_window).mean()
        
    def calculate_bollinger_bands(self, df: pd.DataFrame) -> Dict:
        """Calculate Bollinger Bands"""
        ma = df['close'].rolling(window=20).mean()
        std = df['close'].rolling(window=20).std()
        
        return {
            'middle': ma,
            'upper': ma + (2 * std),
            'lower': ma - (2 * std)
        }
        
    def calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=self.momentum_window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.momentum_window).mean()
        
        rs = gain / loss
        return 100 - (100 / (1 + rs))
        
    def calculate_macd(self, prices: pd.Series) -> Dict:
        """Calculate MACD indicator"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        
        return {
            'macd': macd,
            'signal': signal,
            'histogram': macd - signal
        }
        
    def calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        """Calculate On Balance Volume"""
        obv = pd.Series(index=df.index, dtype=float)
        obv.iloc[0] = 0
        
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + df['volume'].iloc[i]
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - df['volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
                
        return obv
        
    def identify_support_resistance(self, df: pd.DataFrame) -> List[float]:
        """Identify key support and resistance levels"""
        try:
            levels = []
            
            # Use pivot points
            high = df['high'].iloc[-1]
            low = df['low'].iloc[-1]
            close = df['close'].iloc[-1]
            
            pivot = (high + low + close) / 3
            
            r1 = (2 * pivot) - low
            r2 = pivot + (high - low)
            s1 = (2 * pivot) - high
            s2 = pivot - (high - low)
            
            levels.extend([s2, s1, pivot, r1, r2])
            
            # Add recent swing highs/lows
            swings = self.find_swing_points(df)
            levels.extend(swings)
            
            return sorted(list(set(levels)))
            
        except Exception as e:
            logger.error(f"Support/Resistance calculation error: {e}")
            return []
            
    def find_swing_points(self, df: pd.DataFrame, window: int = 5) -> List[float]:
        """Identify swing high and low points"""
        try:
            swing_points = []
            
            for i in range(window, len(df) - window):
                # Check for swing high
                if all(df['high'].iloc[i] > df['high'].iloc[i-j] for j in range(1, window+1)) and \
                   all(df['high'].iloc[i] > df['high'].iloc[i+j] for j in range(1, window+1)):
                    swing_points.append(df['high'].iloc[i])
                    
                # Check for swing low
                if all(df['low'].iloc[i] < df['low'].iloc[i-j] for j in range(1, window+1)) and \
                   all(df['low'].iloc[i] < df['low'].iloc[i+j] for j in range(1, window+1)):
                    swing_points.append(df['low'].iloc[i])
                    
            return swing_points
            
        except Exception as e:
            logger.error(f"Swing point detection error: {e}")
            return []
            
    def check_reversal_patterns(self, df: pd.DataFrame) -> bool:
        """Check for candlestick reversal patterns"""
        try:
            # Basic implementation - can be expanded
            return self.is_hammer(df) or self.is_engulfing(df)
        except Exception as e:
            logger.error(f"Pattern check error: {e}")
            return False
            
    def is_hammer(self, df: pd.DataFrame) -> bool:
        """Check for hammer candlestick pattern"""
        try:
            last_candle = df.iloc[-1]
            body = abs(last_candle['open'] - last_candle['close'])
            upper_shadow = last_candle['high'] - max(last_candle['open'], last_candle['close'])
            lower_shadow = min(last_candle['open'], last_candle['close']) - last_candle['low']
            
            # Hammer criteria
            return (lower_shadow > (2 * body) and upper_shadow < (0.1 * body))
            
        except Exception as e:
            logger.error(f"Hammer pattern check error: {e}")
            return False
            
    def is_engulfing(self, df: pd.DataFrame) -> bool:
        """Check for engulfing pattern"""
        try:
            current = df.iloc[-1]
            previous = df.iloc[-2]
            
            # Bullish engulfing
            if (current['close'] > current['open'] and  # Current is bullish
                previous['close'] < previous['open'] and  # Previous is bearish
                current['open'] < previous['close'] and  # Current opens below previous close
                current['close'] > previous['open']):  # Current closes above previous open
                return True
                
            # Bearish engulfing
            if (current['close'] < current['open'] and  # Current is bearish
                previous['close'] > previous['open'] and  # Previous is bullish
                current['open'] > previous['close'] and  # Current opens above previous close
                current['close'] < previous['open']):  # Current closes below previous open
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Engulfing pattern check error: {e}")
            return False
            
    def identify_pattern_type(self, df: pd.DataFrame) -> str:
        """Identify the type of reversal pattern"""
        try:
            if self.is_hammer(df):
                return 'HAMMER'
            elif self.is_engulfing(df):
                return 'ENGULFING'
            else:
                return 'UNKNOWN'
        except Exception as e:
            logger.error(f"Pattern identification error: {e}")
            return 'UNKNOWN'
            
    def confirm_breakout(self, df: pd.DataFrame, level: float) -> bool:
        """Confirm if a breakout is valid"""
        try:
            close = df['close'].iloc[-1]
            volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].rolling(window=20).mean().iloc[-1]
            
            # Price has broken the level
            price_breakout = abs(close - level) / level > 0.002  # 0.2% minimum movement
            
            # Volume confirmation
            volume_confirmation = volume > (1.5 * avg_volume)
            
            # Momentum confirmation
            momentum = self.calculate_rsi(df['close']).iloc[-1]
            momentum_confirmation = momentum > 60 if close > level else momentum < 40
            
            return price_breakout and volume_confirmation and momentum_confirmation
            
        except Exception as e:
            logger.error(f"Breakout confirmation error: {e}")
            return False