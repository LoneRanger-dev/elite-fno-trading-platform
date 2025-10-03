"""
Pro Trader Indicator Setups

This module defines various professional trading setups based on technical indicators.
Each setup will have a description, the indicators used, and a visual representation (chart URL).
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

def get_pro_setups() -> List[Dict]:
    """Returns the list of available pro trader setups"""
    setup_engine = ProTraderSetups()
    return setup_engine.get_pro_setups()

class ProTraderSetups:
    def __init__(self):
        # Initialize standard indicator settings
        self.settings = {
            'vwap': {'period': 'D'},
            'supertrend': {'period': 10, 'multiplier': 3},
            'rsi': {'period': 14, 'overbought': 70, 'oversold': 30},
            'macd': {'fast': 12, 'slow': 26, 'signal': 9},
            'volume': {'ma_period': 20},
            'atr': {'period': 14}
        }

    def get_pro_setups(self) -> List[Dict]:
        """
        Returns enhanced professional trading setups with clear rules and risk management.
        """
        setups = [
            {
                "id": "vwap_momentum",
                "name": "VWAP Momentum Strategy",
                "description": "High-probability setup combining VWAP with price action and volume. "
                             "Buy when price pulls back to VWAP with increased volume and bullish candle pattern.",
                "rules": {
                    "entry_long": [
                        "Price touches or slightly crosses below VWAP",
                        "Volume > 1.5x 20-period average volume",
                        "Current candle closes above VWAP",
                        "Previous 3 candles show bullish momentum"
                    ],
                    "entry_short": [
                        "Price touches or slightly crosses above VWAP",
                        "Volume > 1.5x 20-period average volume",
                        "Current candle closes below VWAP",
                        "Previous 3 candles show bearish momentum"
                    ],
                    "stop_loss": "Below/above the recent swing low/high",
                    "target": "2-3x stop loss distance"
                },
                "indicators": ["VWAP", "Volume MA (20)", "Candlestick Patterns"],
                "timeframe": "5-minute",
                "best_time": "First 2 hours of market",
                "complexity": "Intermediate"
            },
            {
                "id": "supertrend_reversal",
                "name": "SuperTrend Reversal Strategy",
                "description": "High-accuracy reversal setup using SuperTrend with RSI divergence confirmation.",
                "rules": {
                    "entry_long": [
                        "SuperTrend changes from red to green",
                        "RSI shows bullish divergence",
                        "Price above VWAP",
                        "Current candle closes above SuperTrend line"
                    ],
                    "entry_short": [
                        "SuperTrend changes from green to red",
                        "RSI shows bearish divergence",
                        "Price below VWAP",
                        "Current candle closes below SuperTrend line"
                    ],
                    "stop_loss": "Just below/above the SuperTrend line",
                    "target": "Next significant resistance/support level"
                },
                "indicators": ["SuperTrend (10,3)", "RSI (14)", "VWAP"],
                "timeframe": "15-minute",
                "risk_reward": "Minimum 1:2",
                "complexity": "Advanced"
            },
            {
                "id": "volume_breakout",
                "name": "Professional Volume Breakout",
                "description": "Institutional-grade breakout strategy focusing on volume confirmation and price action.",
                "rules": {
                    "entry_long": [
                        "Price breaks above key resistance with volume > 2x average",
                        "No major resistance within 1.5x target distance",
                        "Previous consolidation lasted at least 3 periods",
                        "RSI not overbought"
                    ],
                    "entry_short": [
                        "Price breaks below key support with volume > 2x average",
                        "No major support within 1.5x target distance",
                        "Previous consolidation lasted at least 3 periods",
                        "RSI not oversold"
                    ],
                    "stop_loss": "Below/above the breakout candle's low/high",
                    "target": "1.5x the height of consolidation"
                },
                "indicators": ["Volume Analysis", "Price Action", "RSI (14)"],
                "timeframe": "5-minute and 15-minute",
                "best_time": "High volatility periods",
                "complexity": "Advanced"
            },
            {
                "id": "momentum_pullback",
                "name": "Institutional Momentum Pullback",
                "description": "Professional pullback strategy targeting high-probability continuation trades.",
                "rules": {
                    "entry_long": [
                        "Strong uptrend (higher highs and higher lows)",
                        "Pullback to 21 EMA or key support",
                        "RSI above 40 (showing strength)",
                        "Volume declining during pullback",
                        "Bullish candle pattern at support"
                    ],
                    "entry_short": [
                        "Strong downtrend (lower highs and lower lows)",
                        "Pullback to 21 EMA or key resistance",
                        "RSI below 60 (showing weakness)",
                        "Volume declining during pullback",
                        "Bearish candle pattern at resistance"
                    ],
                    "stop_loss": "Below/above the recent swing low/high",
                    "target": "Previous swing high/low"
                },
                "indicators": ["EMA (21)", "RSI (14)", "Volume", "Price Action"],
                "timeframe": "15-minute",
                "risk_reward": "Minimum 1:2",
                "complexity": "Intermediate"
            },
            {
                "id": "opening_range_breakout",
                "name": "Professional Opening Range Breakout",
                "description": "Institutional-quality opening range breakout strategy for capturing strong trend days.",
                "rules": {
                    "entry_long": [
                        "Price breaks above first 30-min range high",
                        "Volume surge on breakout",
                        "Previous day's trend was up or sideways",
                        "No major resistance within target distance"
                    ],
                    "entry_short": [
                        "Price breaks below first 30-min range low",
                        "Volume surge on breakout",
                        "Previous day's trend was down or sideways",
                        "No major support within target distance"
                    ],
                    "stop_loss": "Middle of opening range",
                    "target": "1.5x opening range height"
                },
                "indicators": ["Opening Range", "Volume", "Previous Day's High/Low"],
                "timeframe": "5-minute for execution",
                "best_time": "Market open",
                "complexity": "Advanced"
            }
        ]
        return setups

    def analyze_market_condition(self, df: pd.DataFrame) -> Dict:
        """
        Analyze current market condition to determine optimal setup.
        """
        try:
            analysis = {
                'trend': None,
                'volatility': None,
                'volume_condition': None,
                'recommended_setups': []
            }
            
            # Analyze trend using EMA
            ema_20 = df['close'].ewm(span=20).mean()
            ema_50 = df['close'].ewm(span=50).mean()
            current_price = df['close'].iloc[-1]
            
            if current_price > ema_20.iloc[-1] > ema_50.iloc[-1]:
                analysis['trend'] = 'strong_uptrend'
            elif current_price < ema_20.iloc[-1] < ema_50.iloc[-1]:
                analysis['trend'] = 'strong_downtrend'
            else:
                analysis['trend'] = 'sideways'
            
            # Analyze volatility using ATR
            atr = self._calculate_atr(df, self.settings['atr']['period'])
            avg_atr = atr.mean()
            current_atr = atr.iloc[-1]
            
            if current_atr > avg_atr * 1.5:
                analysis['volatility'] = 'high'
            elif current_atr < avg_atr * 0.5:
                analysis['volatility'] = 'low'
            else:
                analysis['volatility'] = 'normal'
            
            # Analyze volume
            volume_ma = df['volume'].rolling(window=self.settings['volume']['ma_period']).mean()
            current_volume = df['volume'].iloc[-1]
            
            if current_volume > volume_ma.iloc[-1] * 1.5:
                analysis['volume_condition'] = 'high'
            elif current_volume < volume_ma.iloc[-1] * 0.5:
                analysis['volume_condition'] = 'low'
            else:
                analysis['volume_condition'] = 'normal'
            
            # Recommend setups based on conditions
            if analysis['trend'] == 'strong_uptrend' and analysis['volume_condition'] == 'high':
                analysis['recommended_setups'].append('momentum_pullback')
            
            if analysis['volatility'] == 'high' and analysis['volume_condition'] == 'high':
                analysis['recommended_setups'].append('volume_breakout')
            
            if analysis['trend'] == 'sideways' and analysis['volatility'] == 'low':
                analysis['recommended_setups'].append('opening_range_breakout')
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing market condition: {e}")
            return {'trend': None, 'volatility': None, 'volume_condition': None, 'recommended_setups': []}

    def _calculate_atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Average True Range"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
