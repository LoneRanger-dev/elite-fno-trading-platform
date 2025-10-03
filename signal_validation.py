"""
Signal Validation Module
Provides robust validation and confirmation of trading signals
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    is_valid: bool
    confidence: float
    messages: List[str]
    indicators: Dict[str, float]

class SignalValidator:
    def __init__(self):
        # Validation thresholds
        self.min_volume = 100000
        self.min_price_move = 0.5
        self.min_confirmations = 2
        self.min_confidence = 70
        
        # Technical parameters
        self.ma_periods = [20, 50, 200]
        self.rsi_period = 14
        self.macd_params = {'short': 12, 'long': 26, 'signal': 9}
        self.bb_params = {'period': 20, 'stddev': 2}
        
    def validate_signal(self, data: Dict) -> ValidationResult:
        """
        Comprehensive signal validation with multiple confirmations
        """
        messages = []
        confirmations = 0
        confidence_scores = []
        indicators = {}
        
        # Volume check
        volume = data.get('volume', 0)
        if volume > self.min_volume:
            confirmations += 1
            confidence_scores.append(min(100, (volume / self.min_volume) * 50))
            messages.append(f"Volume check passed: {volume:,}")
        else:
            messages.append(f"Low volume: {volume:,}")
            
        # Price movement check
        price_change = abs(data.get('change_percent', 0))
        if price_change > self.min_price_move:
            confirmations += 1
            confidence_scores.append(min(100, (price_change / self.min_price_move) * 50))
            messages.append(f"Price movement significant: {price_change:.2f}%")
        else:
            messages.append(f"Insufficient price movement: {price_change:.2f}%")
            
        # Technical indicator checks
        if tech_indicators := self.check_technical_indicators(data):
            confirmations += tech_indicators.count(True)
            messages.extend(f"Technical check {i+1}: {result}" for i, result in enumerate(tech_indicators))
            
        # Calculate overall confidence
        confidence = (sum(confidence_scores) / len(confidence_scores)) if confidence_scores else 0
        
        # Add market context
        context_score = self.analyze_market_context(data)
        if context_score > 0:
            confidence = (confidence + context_score) / 2
            
        return ValidationResult(
            is_valid=confirmations >= self.min_confirmations and confidence >= self.min_confidence,
            confidence=confidence,
            messages=messages,
            indicators=indicators
        )
        
    def check_technical_indicators(self, data: Dict) -> List[bool]:
        """Check multiple technical indicators for confirmation"""
        results = []
        
        # Moving Average Check
        try:
            ma_results = self.check_moving_averages(data)
            results.append(ma_results[0])
        except Exception as e:
            logger.error(f"MA check failed: {e}")
            
        # RSI Check
        try:
            rsi_results = self.check_rsi(data)
            results.append(rsi_results[0])
        except Exception as e:
            logger.error(f"RSI check failed: {e}")
            
        # MACD Check
        try:
            macd_results = self.check_macd(data)
            results.append(macd_results[0])
        except Exception as e:
            logger.error(f"MACD check failed: {e}")
            
        # Bollinger Bands Check
        try:
            bb_results = self.check_bollinger_bands(data)
            results.append(bb_results[0])
        except Exception as e:
            logger.error(f"BB check failed: {e}")
            
        return results
        
    def check_moving_averages(self, data: Dict) -> Tuple[bool, str]:
        """Check Moving Average crossovers and trends"""
        try:
            prices = data.get('price_series', [])
            if len(prices) < 200:  # Need enough data for 200 MA
                return False, "Insufficient price history"
                
            # Calculate MAs
            ma20 = np.mean(prices[-20:])
            ma50 = np.mean(prices[-50:])
            ma200 = np.mean(prices[-200:])
            
            current_price = prices[-1]
            
            # Look for golden/death crosses
            if ma20 > ma50 > ma200:
                return True, "Bullish MA alignment"
            elif ma20 < ma50 < ma200:
                return True, "Bearish MA alignment"
                
            # Check for bounces off major MAs
            for ma in [ma20, ma50, ma200]:
                if abs(current_price - ma) / ma < 0.001:  # Within 0.1%
                    return True, f"Price at major MA: {ma:.2f}"
                    
            return False, "No significant MA signals"
            
        except Exception as e:
            logger.error(f"MA check error: {e}")
            return False, "MA check failed"
            
    def check_rsi(self, data: Dict) -> Tuple[bool, str]:
        """Check RSI for overbought/oversold conditions"""
        try:
            rsi = data.get('rsi', 50)
            
            if rsi <= 30:
                return True, f"Oversold RSI: {rsi:.1f}"
            elif rsi >= 70:
                return True, f"Overbought RSI: {rsi:.1f}"
                
            # Check for divergence
            if price_rsi_divergence := self.check_divergence(data):
                return True, f"RSI divergence detected: {price_rsi_divergence}"
                
            return False, f"Neutral RSI: {rsi:.1f}"
            
        except Exception as e:
            logger.error(f"RSI check error: {e}")
            return False, "RSI check failed"
            
    def check_macd(self, data: Dict) -> Tuple[bool, str]:
        """Check MACD for signals"""
        try:
            macd = data.get('macd', 0)
            signal = data.get('signal', 0)
            prev_macd = data.get('prev_macd', 0)
            prev_signal = data.get('prev_signal', 0)
            
            # Check for crossovers
            if prev_macd < prev_signal and macd > signal:
                return True, "Bullish MACD crossover"
            elif prev_macd > prev_signal and macd < signal:
                return True, "Bearish MACD crossover"
                
            # Check for histogram trend
            hist = macd - signal
            prev_hist = prev_macd - prev_signal
            
            if abs(hist) > abs(prev_hist):
                return True, "MACD momentum increasing"
                
            return False, "No significant MACD signals"
            
        except Exception as e:
            logger.error(f"MACD check error: {e}")
            return False, "MACD check failed"
            
    def check_bollinger_bands(self, data: Dict) -> Tuple[bool, str]:
        """Check Bollinger Bands for breakouts and squeezes"""
        try:
            price = data.get('close', 0)
            upper = data.get('bb_upper', float('inf'))
            lower = data.get('bb_lower', float('-inf'))
            middle = data.get('bb_middle', price)
            
            # Calculate bandwidth
            bandwidth = (upper - lower) / middle
            
            # Check for breakouts
            if price > upper:
                return True, f"Bullish BB breakout: {price:.2f} > {upper:.2f}"
            elif price < lower:
                return True, f"Bearish BB breakout: {price:.2f} < {lower:.2f}"
                
            # Check for squeeze
            if bandwidth < 0.1:  # Tight bands
                return True, "BB squeeze detected"
                
            return False, "No significant BB signals"
            
        except Exception as e:
            logger.error(f"BB check error: {e}")
            return False, "BB check failed"
            
    def check_divergence(self, data: Dict) -> Optional[str]:
        """Check for price/indicator divergence"""
        try:
            prices = data.get('price_series', [])
            rsi_values = data.get('rsi_series', [])
            
            if len(prices) < 10 or len(rsi_values) < 10:
                return None
                
            # Get recent highs/lows
            price_trend = 1 if prices[-1] > prices[-5] else -1
            rsi_trend = 1 if rsi_values[-1] > rsi_values[-5] else -1
            
            if price_trend != rsi_trend:
                return "Bullish" if rsi_trend > price_trend else "Bearish"
                
            return None
            
        except Exception as e:
            logger.error(f"Divergence check error: {e}")
            return None
            
    def analyze_market_context(self, data: Dict) -> float:
        """Analyze broader market context for signal validation"""
        try:
            context_score = 50  # Start neutral
            
            # Check market breadth
            breadth = data.get('market_breadth', 0)
            context_score += breadth * 10  # -10 to +10
            
            # Check sector performance
            sector_perf = data.get('sector_performance', 0)
            context_score += sector_perf * 5  # -5 to +5
            
            # Check volatility
            vix = data.get('vix', 20)
            if vix > 30:  # High volatility
                context_score -= 10
            elif vix < 15:  # Low volatility
                context_score += 10
                
            # Check trend strength
            adx = data.get('adx', 25)
            if adx > 30:  # Strong trend
                context_score += 15
            elif adx < 20:  # Weak trend
                context_score -= 10
                
            return min(100, max(0, context_score))
            
        except Exception as e:
            logger.error(f"Market context analysis error: {e}")
            return 50  # Return neutral score on error