"""
Technical Analysis Engine
Implements RSI, MACD, Bollinger Bands, VWAP and other technical indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

# Local imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config, logger

class TechnicalAnalyzer:
    """Technical analysis for trading signals"""
    
    def __init__(self):
        self.logger = logger
        self.config = config
        self.ta_params = config.TA_PARAMS
        self.logger.info("Technical Analyzer initialized")
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main analysis function that returns trading signals"""
        try:
            hist_data = market_data.get('historical_data')
            if hist_data is None or hist_data.empty:
                return self._no_signal_result("No historical data available")
            
            # Calculate all technical indicators
            indicators = self._calculate_all_indicators(hist_data)
            
            # Generate trading signal
            signal = self._generate_signal(market_data, indicators)
            
            return signal
            
        except Exception as e:
            self.logger.error(f"Error in technical analysis: {str(e)}")
            return self._no_signal_result(f"Analysis error: {str(e)}")
    
    def _calculate_all_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate all technical indicators"""
        indicators = {}
        
        try:
            # RSI
            indicators['rsi'] = self._calculate_rsi(data['Close'], self.ta_params['rsi_period'])
            
            # MACD
            macd_data = self._calculate_macd(
                data['Close'], 
                self.ta_params['macd_fast'],
                self.ta_params['macd_slow'],
                self.ta_params['macd_signal']
            )
            indicators.update(macd_data)
            
            # Bollinger Bands
            bb_data = self._calculate_bollinger_bands(
                data['Close'],
                self.ta_params['bb_period'],
                self.ta_params['bb_std']
            )
            indicators.update(bb_data)
            
            # VWAP
            indicators['vwap'] = self._calculate_vwap(data)
            
            # Moving Averages
            indicators['sma_20'] = data['Close'].rolling(window=20).mean().iloc[-1]
            indicators['ema_20'] = data['Close'].ewm(span=20).mean().iloc[-1]
            
            # Volume indicators
            indicators['volume_avg'] = data['Volume'].rolling(window=20).mean().iloc[-1]
            indicators['volume_current'] = data['Volume'].iloc[-1]
            indicators['volume_surge'] = indicators['volume_current'] / indicators['volume_avg'] if indicators['volume_avg'] > 0 else 1
            
            # Price action
            indicators['current_price'] = data['Close'].iloc[-1]
            indicators['high_20'] = data['High'].rolling(window=20).max().iloc[-1]
            indicators['low_20'] = data['Low'].rolling(window=20).min().iloc[-1]
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {str(e)}")
            return {}
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)"""
        try:
            prices = pd.to_numeric(prices, errors='coerce').dropna()
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except:
            return 50.0  # Neutral RSI
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        try:
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            histogram = macd_line - signal_line
            
            return {
                'macd': macd_line.iloc[-1],
                'macd_signal': signal_line.iloc[-1],
                'macd_histogram': histogram.iloc[-1]
            }
        except:
            return {'macd': 0.0, 'macd_signal': 0.0, 'macd_histogram': 0.0}
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            return {
                'bb_upper': upper_band.iloc[-1],
                'bb_middle': sma.iloc[-1],
                'bb_lower': lower_band.iloc[-1]
            }
        except:
            current_price = prices.iloc[-1]
            return {
                'bb_upper': current_price * 1.02,
                'bb_middle': current_price,
                'bb_lower': current_price * 0.98
            }
    
    def _calculate_vwap(self, data: pd.DataFrame) -> float:
        """Calculate VWAP (Volume Weighted Average Price)"""
        try:
            typical_price = (data['High'] + data['Low'] + data['Close']) / 3
            vwap = (typical_price * data['Volume']).cumsum() / data['Volume'].cumsum()
            return vwap.iloc[-1]
        except:
            return data['Close'].iloc[-1]  # Fallback to current price
    
    def _generate_signal(self, market_data: Dict[str, Any], indicators: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signal based on technical indicators"""
        try:
            current_price = indicators.get('current_price', market_data.get('current_price', 0))
            rsi = indicators.get('rsi', 50)
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            bb_upper = indicators.get('bb_upper', current_price * 1.02)
            bb_lower = indicators.get('bb_lower', current_price * 0.98)
            vwap = indicators.get('vwap', current_price)
            volume_surge = indicators.get('volume_surge', 1)
            
            # Initialize signal components
            signal_strength = 0
            signal_type = "HOLD"
            setup_reasons = []
            confidence = 0
            
            # RSI Signals
            if rsi < self.ta_params['rsi_oversold']:
                signal_strength += 3
                setup_reasons.append("RSI Oversold")
            elif rsi > self.ta_params['rsi_overbought']:
                signal_strength -= 3
                setup_reasons.append("RSI Overbought")
            
            # MACD Signals
            if macd > macd_signal and macd > 0:
                signal_strength += 2
                setup_reasons.append("MACD Bullish")
            elif macd < macd_signal and macd < 0:
                signal_strength -= 2
                setup_reasons.append("MACD Bearish")
            
            # Bollinger Bands Signals
            if current_price <= bb_lower:
                signal_strength += 2
                setup_reasons.append("BB Support")
            elif current_price >= bb_upper:
                signal_strength -= 2
                setup_reasons.append("BB Resistance")
            
            # VWAP Signals
            if current_price > vwap:
                signal_strength += 1
                setup_reasons.append("Above VWAP")
            else:
                signal_strength -= 1
                setup_reasons.append("Below VWAP")
            
            # Volume confirmation
            if volume_surge > self.ta_params['volume_threshold']:
                signal_strength += 1
                setup_reasons.append("Volume Surge")
            
            # Determine signal type and confidence
            if signal_strength >= 4:
                signal_type = "BUY"
                confidence = min(100, 60 + signal_strength * 5)
            elif signal_strength <= -4:
                signal_type = "SELL"
                confidence = min(100, 60 + abs(signal_strength) * 5)
            else:
                return self._no_signal_result("Insufficient signal strength")
            
            # Calculate entry, target, and stop loss
            entry_price = current_price
            
            if signal_type == "BUY":
                target_price = entry_price * (1 + 0.02)  # 2% target
                stop_loss = entry_price * (1 - 0.015)    # 1.5% stop loss
            else:  # SELL
                target_price = entry_price * (1 - 0.02)  # 2% target
                stop_loss = entry_price * (1 + 0.015)    # 1.5% stop loss
            
            # Calculate risk-reward ratio
            risk = abs(entry_price - stop_loss)
            reward = abs(target_price - entry_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0
            
            # Check minimum confidence threshold
            if confidence < self.config.MIN_CONFIDENCE_THRESHOLD:
                return self._no_signal_result(f"Confidence {confidence:.1f}% below threshold")
            
            # Check minimum risk-reward ratio
            if risk_reward_ratio < self.config.RISK_REWARD_RATIO:
                return self._no_signal_result(f"R:R {risk_reward_ratio:.1f} below minimum")
            
            return {
                'signal_type': signal_type,
                'entry_price': entry_price,
                'target_price': target_price,
                'stop_loss': stop_loss,
                'confidence': confidence,
                'setup_description': " + ".join(setup_reasons),
                'risk_reward_ratio': risk_reward_ratio,
                'indicators': {
                    'RSI': rsi,
                    'MACD': macd,
                    'VWAP': vwap,
                    'Volume Surge': f"{volume_surge:.1f}x"
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating signal: {str(e)}")
            return self._no_signal_result(f"Signal generation error: {str(e)}")
    
    def _no_signal_result(self, reason: str) -> Dict[str, Any]:
        """Return no signal result"""
        return {
            'signal_type': 'NONE',
            'confidence': 0,
            'reason': reason,
            'entry_price': 0,
            'target_price': 0,
            'stop_loss': 0,
            'setup_description': 'No signal',
            'risk_reward_ratio': 0,
            'indicators': {}
        }
    
    def get_support_resistance(self, data: pd.DataFrame, lookback: int = 20) -> Tuple[float, float]:
        """Calculate support and resistance levels"""
        try:
            recent_highs = data['High'].rolling(window=lookback).max()
            recent_lows = data['Low'].rolling(window=lookback).min()
            
            resistance = recent_highs.iloc[-1]
            support = recent_lows.iloc[-1]
            
            return support, resistance
            
        except Exception as e:
            self.logger.error(f"Error calculating support/resistance: {str(e)}")
            current_price = data['Close'].iloc[-1]
            return current_price * 0.98, current_price * 1.02
    
    def test_analysis(self, instrument: str = "NIFTY") -> Dict[str, Any]:
        """Test technical analysis with sample data"""
        try:
            # Create sample data for testing
            dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
            np.random.seed(42)
            
            # Generate realistic price data
            base_price = 20000
            price_changes = np.random.normal(0, 0.02, 100)
            prices = [base_price]
            
            for change in price_changes:
                new_price = prices[-1] * (1 + change)
                prices.append(new_price)
            
            prices = prices[1:]  # Remove initial price
            
            # Create DataFrame
            sample_data = pd.DataFrame({
                'Open': prices,
                'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
                'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
                'Close': prices,
                'Volume': [np.random.randint(1000000, 5000000) for _ in prices]
            }, index=dates)
            
            # Test analysis
            market_data = {
                'symbol': instrument,
                'current_price': prices[-1],
                'historical_data': sample_data
            }
            
            result = self.analyze(market_data)
            return result
            
        except Exception as e:
            self.logger.error(f"Error in test analysis: {str(e)}")
            return self._no_signal_result(f"Test error: {str(e)}")

# Test function
def test_technical_analysis():
    """Test technical analysis functionality"""
    analyzer = TechnicalAnalyzer()
    
    print("Testing technical analysis...")
    result = analyzer.test_analysis()
    
    print(f"Signal Type: {result.get('signal_type', 'NONE')}")
    print(f"Confidence: {result.get('confidence', 0):.1f}%")
    print(f"Setup: {result.get('setup_description', 'N/A')}")
    
    if result.get('signal_type') != 'NONE':
        print(f"Entry: ₹{result.get('entry_price', 0):.2f}")
        print(f"Target: ₹{result.get('target_price', 0):.2f}")
        print(f"Stop Loss: ₹{result.get('stop_loss', 0):.2f}")
        print(f"R:R Ratio: 1:{result.get('risk_reward_ratio', 0):.1f}")

if __name__ == "__main__":
    test_technical_analysis()