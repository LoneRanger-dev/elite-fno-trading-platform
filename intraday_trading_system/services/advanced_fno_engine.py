"""
Advanced FnO Signal Engine
Professional-grade options trading signals with OI analysis, technical indicators, and pattern recognition
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Any, Optional, Tuple
import logging
from kiteconnect import KiteConnect
from config.settings import config
import json
import time

logger = logging.getLogger(__name__)

class AdvancedFnOSignalEngine:
    """Advanced FnO signal engine with professional-grade analysis"""
    
    def __init__(self):
        self.kite = None
        self.tz = pytz.timezone('Asia/Kolkata')
        self.initialize_kite()
        
        # Trading parameters
        self.min_confidence = 70  # Minimum confidence for signal generation
        self.max_daily_signals = 8
        self.signals_today = 0
        
        # Technical indicator parameters
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.bb_period = 20
        self.bb_std = 2
        
        # Options parameters
        self.min_oi_change = 15  # Minimum OI change percentage
        self.min_volume = 1000   # Minimum volume for liquidity
        
        # Instruments for FnO trading
        self.fno_instruments = [
            'NIFTY', 'BANKNIFTY', 'MIDCPNIFTY',
            'RELIANCE', 'TCS', 'HDFCBANK', 'ICICIBANK', 'INFY',
            'ITC', 'KOTAKBANK', 'LT', 'SBIN', 'BAJFINANCE'
        ]
        
    def initialize_kite(self):
        """Initialize Kite Connect API"""
        try:
            self.kite = KiteConnect(api_key=config.KITE_API_KEY)
            self.kite.set_access_token(config.KITE_ACCESS_TOKEN)
            logger.info("✅ Kite Connect initialized for FnO signals")
        except Exception as e:
            logger.error(f"❌ Kite initialization failed: {e}")
            self.kite = None
    
    def is_market_open(self) -> bool:
        """Check if market is open for FnO trading"""
        now = datetime.now(self.tz)
        
        # Check if weekend
        if now.weekday() >= 5:
            return False
            
        # Check market hours (9:15 AM to 3:30 PM)
        market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_start <= now <= market_end
    
    def get_option_chain(self, symbol: str, expiry: str = None) -> Dict[str, Any]:
        """Get complete option chain data"""
        try:
            if not self.kite:
                return {}
                
            # Get instruments for the symbol
            instruments = self.kite.instruments('NFO')
            
            if not expiry:
                # Get nearest expiry
                today = datetime.now().date()
                expiries = []
                
                for inst in instruments:
                    if (inst['name'] == symbol and 
                        inst['instrument_type'] in ['CE', 'PE'] and
                        inst['expiry'].date() >= today):
                        expiries.append(inst['expiry'].date())
                
                if expiries:
                    expiry = min(expiries)
            
            option_chain = {
                'symbol': symbol,
                'expiry': expiry,
                'ce_data': {},
                'pe_data': {},
                'underlying_price': 0
            }
            
            # Get underlying price
            if symbol in ['NIFTY', 'BANKNIFTY']:
                underlying_symbol = f'NSE:{symbol}'
            else:
                underlying_symbol = f'NSE:{symbol}'
                
            try:
                ltp_data = self.kite.ltp(underlying_symbol)
                option_chain['underlying_price'] = ltp_data[underlying_symbol]['last_price']
            except:
                pass
            
            # Process option data
            for inst in instruments:
                if (inst['name'] == symbol and 
                    inst['expiry'].date() == expiry and
                    inst['instrument_type'] in ['CE', 'PE']):
                    
                    strike = inst['strike']
                    option_type = inst['instrument_type']
                    
                    try:
                        # Get live data
                        token = inst['instrument_token']
                        quote = self.kite.quote(f'NFO:{inst["tradingsymbol"]}')
                        
                        option_data = {
                            'strike': strike,
                            'ltp': quote[f'NFO:{inst["tradingsymbol"]}']['last_price'],
                            'volume': quote[f'NFO:{inst["tradingsymbol"]}']['volume'],
                            'oi': quote[f'NFO:{inst["tradingsymbol"]}']['oi'],
                            'bid': quote[f'NFO:{inst["tradingsymbol"]}']['depth']['buy'][0]['price'] if quote[f'NFO:{inst["tradingsymbol"]}']['depth']['buy'] else 0,
                            'ask': quote[f'NFO:{inst["tradingsymbol"]}']['depth']['sell'][0]['price'] if quote[f'NFO:{inst["tradingsymbol"]}']['depth']['sell'] else 0,
                            'tradingsymbol': inst['tradingsymbol'],
                            'token': token
                        }
                        
                        if option_type == 'CE':
                            option_chain['ce_data'][strike] = option_data
                        else:
                            option_chain['pe_data'][strike] = option_data
                            
                    except Exception as e:
                        continue
            
            return option_chain
            
        except Exception as e:
            logger.error(f"Error getting option chain for {symbol}: {e}")
            return {}
    
    def analyze_oi_data(self, option_chain: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Open Interest data for CE/PE signals"""
        try:
            underlying_price = option_chain.get('underlying_price', 0)
            ce_data = option_chain.get('ce_data', {})
            pe_data = option_chain.get('pe_data', {})
            
            analysis = {
                'max_oi_ce': {'strike': 0, 'oi': 0, 'price': 0},
                'max_oi_pe': {'strike': 0, 'oi': 0, 'price': 0},
                'atm_ce': {'strike': 0, 'oi': 0, 'price': 0},
                'atm_pe': {'strike': 0, 'oi': 0, 'price': 0},
                'pcr': 0,  # Put-Call Ratio
                'oi_analysis': 'neutral',
                'support_levels': [],
                'resistance_levels': []
            }
            
            if not ce_data or not pe_data or not underlying_price:
                return analysis
            
            # Find ATM options
            atm_strike = round(underlying_price / 50) * 50  # Round to nearest 50
            
            # Get ATM data
            if atm_strike in ce_data:
                analysis['atm_ce'] = {
                    'strike': atm_strike,
                    'oi': ce_data[atm_strike]['oi'],
                    'price': ce_data[atm_strike]['ltp']
                }
            
            if atm_strike in pe_data:
                analysis['atm_pe'] = {
                    'strike': atm_strike,
                    'oi': pe_data[atm_strike]['oi'],
                    'price': pe_data[atm_strike]['ltp']
                }
            
            # Find max OI strikes
            max_ce_oi = 0
            max_pe_oi = 0
            
            for strike, data in ce_data.items():
                if data['oi'] > max_ce_oi:
                    max_ce_oi = data['oi']
                    analysis['max_oi_ce'] = {
                        'strike': strike,
                        'oi': data['oi'],
                        'price': data['ltp']
                    }
            
            for strike, data in pe_data.items():
                if data['oi'] > max_pe_oi:
                    max_pe_oi = data['oi']
                    analysis['max_oi_pe'] = {
                        'strike': strike,
                        'oi': data['oi'],
                        'price': data['ltp']
                    }
            
            # Calculate PCR
            total_pe_oi = sum(data['oi'] for data in pe_data.values())
            total_ce_oi = sum(data['oi'] for data in ce_data.values())
            
            if total_ce_oi > 0:
                analysis['pcr'] = total_pe_oi / total_ce_oi
            
            # OI Analysis
            if analysis['pcr'] > 1.2:
                analysis['oi_analysis'] = 'bullish'  # More puts, bullish
            elif analysis['pcr'] < 0.8:
                analysis['oi_analysis'] = 'bearish'  # More calls, bearish
            else:
                analysis['oi_analysis'] = 'neutral'
            
            # Support/Resistance levels from high OI strikes
            strikes_with_oi = []
            for strike, data in {**ce_data, **pe_data}.items():
                strikes_with_oi.append((strike, data['oi']))
            
            # Sort by OI and get top strikes
            strikes_with_oi.sort(key=lambda x: x[1], reverse=True)
            top_strikes = [strike for strike, oi in strikes_with_oi[:5]]
            
            # Classify as support/resistance based on current price
            for strike in top_strikes:
                if strike < underlying_price:
                    analysis['support_levels'].append(strike)
                elif strike > underlying_price:
                    analysis['resistance_levels'].append(strike)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing OI data: {e}")
            return {}
    
    def get_technical_analysis(self, symbol: str, timeframe: str = '5minute') -> Dict[str, Any]:
        """Get comprehensive technical analysis"""
        try:
            if not self.kite:
                return {}
            
            # Get historical data
            from_date = datetime.now() - timedelta(days=10)
            to_date = datetime.now()
            
            # Get instrument token
            instruments = self.kite.instruments('NSE')
            instrument_token = None
            
            for inst in instruments:
                if inst['tradingsymbol'] == symbol:
                    instrument_token = inst['instrument_token']
                    break
            
            if not instrument_token:
                return {}
            
            # Get historical data
            data = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=timeframe
            )
            
            if not data:
                return {}
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Calculate technical indicators
            df.ta.rsi(append=True, length=self.rsi_period)
            df.ta.macd(append=True, fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal)
            df.ta.bbands(append=True, length=self.bb_period, std=self.bb_std)
            df.ta.ema(append=True, length=20)
            df.ta.sma(append=True, length=50)
            df.ta.vwap(append=True)
            df.ta.atr(append=True, length=14)
            df.ta.adx(append=True, length=14)
            
            # Get latest values
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            analysis = {
                'symbol': symbol,
                'current_price': float(latest['close']),
                'change': float(latest['close'] - prev['close']),
                'change_percent': float((latest['close'] - prev['close']) / prev['close'] * 100),
                'volume': int(latest['volume']),
                'indicators': {
                    'rsi': float(latest.get(f'RSI_{self.rsi_period}', 50)),
                    'macd': float(latest.get(f'MACD_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}', 0)),
                    'macd_signal': float(latest.get(f'MACDs_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}', 0)),
                    'bb_upper': float(latest.get(f'BBU_{self.bb_period}_{self.bb_std}', 0)),
                    'bb_middle': float(latest.get(f'BBM_{self.bb_period}_{self.bb_std}', 0)),
                    'bb_lower': float(latest.get(f'BBL_{self.bb_period}_{self.bb_std}', 0)),
                    'ema_20': float(latest.get('EMA_20', 0)),
                    'sma_50': float(latest.get('SMA_50', 0)),
                    'vwap': float(latest.get('VWAP', 0)),
                    'atr': float(latest.get('ATRr_14', 0)),
                    'adx': float(latest.get('ADX_14', 0))
                },
                'patterns': self.detect_patterns(df),
                'trend': self.determine_trend(df),
                'signals': self.generate_technical_signals(df)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error getting technical analysis for {symbol}: {e}")
            return {}
    
    def detect_patterns(self, df: pd.DataFrame) -> List[str]:
        """Detect chart patterns"""
        patterns = []
        
        try:
            if len(df) < 20:
                return patterns
            
            # Get recent data
            recent = df.tail(20)
            closes = recent['close'].values
            highs = recent['high'].values
            lows = recent['low'].values
            
            # Pattern detection logic
            current_price = closes[-1]
            
            # Ascending Triangle
            if self.is_ascending_triangle(highs, lows):
                patterns.append('ascending_triangle')
            
            # Descending Triangle
            if self.is_descending_triangle(highs, lows):
                patterns.append('descending_triangle')
            
            # Bull Flag
            if self.is_bull_flag(closes, highs, lows):
                patterns.append('bull_flag')
            
            # Bear Flag
            if self.is_bear_flag(closes, highs, lows):
                patterns.append('bear_flag')
            
            # Breakout
            if self.is_breakout(df):
                patterns.append('breakout')
            
            # Support/Resistance Break
            support_resistance = self.find_support_resistance(closes)
            if support_resistance:
                if current_price > support_resistance['resistance'] * 1.002:
                    patterns.append('resistance_break')
                elif current_price < support_resistance['support'] * 0.998:
                    patterns.append('support_break')
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
        
        return patterns
    
    def is_ascending_triangle(self, highs: np.ndarray, lows: np.ndarray) -> bool:
        """Detect ascending triangle pattern"""
        try:
            # Ascending triangle: resistance level stays same, support is rising
            resistance_levels = highs[-10:]
            support_levels = lows[-10:]
            
            # Check if resistance is flat
            resistance_flat = np.std(resistance_levels) < np.mean(resistance_levels) * 0.02
            
            # Check if support is rising
            support_trend = np.polyfit(range(len(support_levels)), support_levels, 1)[0]
            support_rising = support_trend > 0
            
            return resistance_flat and support_rising
        except:
            return False
    
    def is_descending_triangle(self, highs: np.ndarray, lows: np.ndarray) -> bool:
        """Detect descending triangle pattern"""
        try:
            # Descending triangle: support level stays same, resistance is falling
            resistance_levels = highs[-10:]
            support_levels = lows[-10:]
            
            # Check if support is flat
            support_flat = np.std(support_levels) < np.mean(support_levels) * 0.02
            
            # Check if resistance is falling
            resistance_trend = np.polyfit(range(len(resistance_levels)), resistance_levels, 1)[0]
            resistance_falling = resistance_trend < 0
            
            return support_flat and resistance_falling
        except:
            return False
    
    def is_bull_flag(self, closes: np.ndarray, highs: np.ndarray, lows: np.ndarray) -> bool:
        """Detect bull flag pattern"""
        try:
            # Bull flag: strong upward move followed by sideways/slight downward consolidation
            if len(closes) < 15:
                return False
            
            # Check for initial strong move up
            early_prices = closes[:5]
            middle_prices = closes[5:10]
            recent_prices = closes[10:]
            
            # Strong initial upward move
            initial_move = (middle_prices[-1] - early_prices[0]) / early_prices[0]
            
            # Consolidation or slight pullback
            consolidation_slope = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
            
            return initial_move > 0.02 and -0.001 <= consolidation_slope <= 0.001
        except:
            return False
    
    def is_bear_flag(self, closes: np.ndarray, highs: np.ndarray, lows: np.ndarray) -> bool:
        """Detect bear flag pattern"""
        try:
            # Bear flag: strong downward move followed by sideways/slight upward consolidation
            if len(closes) < 15:
                return False
            
            # Check for initial strong move down
            early_prices = closes[:5]
            middle_prices = closes[5:10]
            recent_prices = closes[10:]
            
            # Strong initial downward move
            initial_move = (middle_prices[-1] - early_prices[0]) / early_prices[0]
            
            # Consolidation or slight bounce
            consolidation_slope = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]
            
            return initial_move < -0.02 and -0.001 <= consolidation_slope <= 0.001
        except:
            return False
    
    def is_breakout(self, df: pd.DataFrame) -> bool:
        """Detect breakout from consolidation"""
        try:
            if len(df) < 20:
                return False
            
            recent = df.tail(20)
            consolidation_period = recent.iloc[:-3]  # Exclude last 3 candles
            breakout_candles = recent.tail(3)
            
            # Check if price was consolidating
            consolidation_range = consolidation_period['high'].max() - consolidation_period['low'].min()
            avg_price = consolidation_period['close'].mean()
            range_percent = consolidation_range / avg_price
            
            # Consolidation should be tight (less than 3% range)
            if range_percent > 0.03:
                return False
            
            # Check for breakout (price moving beyond consolidation range with volume)
            current_price = breakout_candles['close'].iloc[-1]
            consolidation_high = consolidation_period['high'].max()
            consolidation_low = consolidation_period['low'].min()
            
            # Volume confirmation
            avg_volume = consolidation_period['volume'].mean()
            breakout_volume = breakout_candles['volume'].iloc[-1]
            
            volume_spike = breakout_volume > avg_volume * 1.2
            
            price_breakout = (current_price > consolidation_high * 1.005 or 
                            current_price < consolidation_low * 0.995)
            
            return price_breakout and volume_spike
        except:
            return False
    
    def find_support_resistance(self, closes: np.ndarray) -> Dict[str, float]:
        """Find key support and resistance levels"""
        try:
            if len(closes) < 10:
                return {}
            
            # Use pivot points method
            highs = []
            lows = []
            
            for i in range(2, len(closes) - 2):
                # Local high
                if closes[i] > closes[i-1] and closes[i] > closes[i+1] and closes[i] > closes[i-2] and closes[i] > closes[i+2]:
                    highs.append(closes[i])
                
                # Local low
                if closes[i] < closes[i-1] and closes[i] < closes[i+1] and closes[i] < closes[i-2] and closes[i] < closes[i+2]:
                    lows.append(closes[i])
            
            if not highs or not lows:
                return {}
            
            # Find most relevant levels
            resistance = np.median(highs) if highs else closes[-1] * 1.02
            support = np.median(lows) if lows else closes[-1] * 0.98
            
            return {
                'support': support,
                'resistance': resistance
            }
            
        except:
            return {}
    
    def determine_trend(self, df: pd.DataFrame) -> str:
        """Determine overall trend"""
        try:
            if len(df) < 10:
                return 'neutral'
            
            recent = df.tail(10)
            closes = recent['close'].values
            
            # Linear regression to determine trend
            slope = np.polyfit(range(len(closes)), closes, 1)[0]
            
            # Normalize slope by price
            normalized_slope = slope / closes[0]
            
            if normalized_slope > 0.001:
                return 'bullish'
            elif normalized_slope < -0.001:
                return 'bearish'
            else:
                return 'neutral'
                
        except:
            return 'neutral'
    
    def generate_technical_signals(self, df: pd.DataFrame) -> List[str]:
        """Generate technical signals"""
        signals = []
        
        try:
            if len(df) < 20:
                return signals
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # RSI signals
            rsi = latest.get(f'RSI_{self.rsi_period}', 50)
            if rsi < 30:
                signals.append('rsi_oversold')
            elif rsi > 70:
                signals.append('rsi_overbought')
            
            # MACD signals
            macd = latest.get(f'MACD_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}', 0)
            macd_signal = latest.get(f'MACDs_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}', 0)
            prev_macd = prev.get(f'MACD_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}', 0)
            prev_macd_signal = prev.get(f'MACDs_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}', 0)
            
            # MACD crossover
            if macd > macd_signal and prev_macd <= prev_macd_signal:
                signals.append('macd_bullish_crossover')
            elif macd < macd_signal and prev_macd >= prev_macd_signal:
                signals.append('macd_bearish_crossover')
            
            # Bollinger Bands signals
            price = latest['close']
            bb_upper = latest.get(f'BBU_{self.bb_period}_{self.bb_std}', 0)
            bb_lower = latest.get(f'BBL_{self.bb_period}_{self.bb_std}', 0)
            
            if price > bb_upper:
                signals.append('bb_squeeze_up')
            elif price < bb_lower:
                signals.append('bb_squeeze_down')
            
            # EMA signals
            ema_20 = latest.get('EMA_20', 0)
            if price > ema_20 and prev['close'] <= prev.get('EMA_20', 0):
                signals.append('ema_bullish_crossover')
            elif price < ema_20 and prev['close'] >= prev.get('EMA_20', 0):
                signals.append('ema_bearish_crossover')
            
            # VWAP signals
            vwap = latest.get('VWAP', 0)
            if price > vwap:
                signals.append('above_vwap')
            else:
                signals.append('below_vwap')
            
        except Exception as e:
            logger.error(f"Error generating technical signals: {e}")
        
        return signals
    
    def generate_fno_signals(self) -> List[Dict[str, Any]]:
        """Generate professional FnO trading signals"""
        signals = []
        
        try:
            if not self.is_market_open():
                logger.info("Market is closed, no signals generated")
                return signals
            
            if self.signals_today >= self.max_daily_signals:
                logger.info("Daily signal limit reached")
                return signals
            
            for symbol in self.fno_instruments:
                try:
                    # Get technical analysis
                    technical = self.get_technical_analysis(symbol)
                    if not technical:
                        continue
                    
                    # Get option chain
                    option_chain = self.get_option_chain(symbol)
                    if not option_chain:
                        continue
                    
                    # Analyze OI data
                    oi_analysis = self.analyze_oi_data(option_chain)
                    if not oi_analysis:
                        continue
                    
                    # Generate signal based on combined analysis
                    signal = self.evaluate_signal_conditions(technical, oi_analysis, option_chain)
                    
                    if signal and signal['confidence'] >= self.min_confidence:
                        signals.append(signal)
                        self.signals_today += 1
                        
                        if len(signals) >= 3:  # Limit to 3 signals per scan
                            break
                            
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    continue
            
            # Sort by confidence
            signals.sort(key=lambda x: x['confidence'], reverse=True)
            return signals[:3]  # Return top 3 signals
            
        except Exception as e:
            logger.error(f"Error generating FnO signals: {e}")
            return []
    
    def evaluate_signal_conditions(self, technical: Dict, oi_analysis: Dict, option_chain: Dict) -> Optional[Dict[str, Any]]:
        """Evaluate all conditions and generate signal"""
        try:
            symbol = technical['symbol']
            current_price = technical['current_price']
            indicators = technical['indicators']
            patterns = technical['patterns']
            technical_signals = technical['signals']
            
            signal = {
                'id': f"{symbol}_{int(time.time())}",
                'symbol': symbol,
                'timestamp': datetime.now(self.tz).isoformat(),
                'underlying_price': current_price,
                'signal_type': None,
                'option_type': None,  # CE or PE
                'strike': 0,
                'entry_price': 0,
                'target': 0,
                'stop_loss': 0,
                'confidence': 0,
                'reasoning': [],
                'technical_score': 0,
                'oi_score': 0,
                'pattern_score': 0,
                'risk_reward': 0,
                'expected_move': 0,
                'time_decay_risk': 'low',
                'liquidity_score': 0
            }
            
            # Technical scoring
            tech_score = 0
            reasoning = []
            
            # RSI analysis
            rsi = indicators['rsi']
            if rsi < 30:
                tech_score += 15
                reasoning.append(f"RSI oversold at {rsi:.1f}")
            elif rsi > 70:
                tech_score -= 15
                reasoning.append(f"RSI overbought at {rsi:.1f}")
            
            # MACD analysis
            if 'macd_bullish_crossover' in technical_signals:
                tech_score += 20
                reasoning.append("MACD bullish crossover")
            elif 'macd_bearish_crossover' in technical_signals:
                tech_score -= 20
                reasoning.append("MACD bearish crossover")
            
            # EMA analysis
            if 'ema_bullish_crossover' in technical_signals:
                tech_score += 15
                reasoning.append("Price above EMA20")
            elif 'ema_bearish_crossover' in technical_signals:
                tech_score -= 15
                reasoning.append("Price below EMA20")
            
            # VWAP analysis
            if 'above_vwap' in technical_signals:
                tech_score += 10
                reasoning.append("Price above VWAP")
            else:
                tech_score -= 10
                reasoning.append("Price below VWAP")
            
            # Pattern analysis
            pattern_score = 0
            if 'breakout' in patterns:
                pattern_score += 25
                reasoning.append("Breakout pattern detected")
            if 'bull_flag' in patterns:
                pattern_score += 20
                reasoning.append("Bull flag pattern")
            elif 'bear_flag' in patterns:
                pattern_score -= 20
                reasoning.append("Bear flag pattern")
            if 'ascending_triangle' in patterns:
                pattern_score += 15
                reasoning.append("Ascending triangle")
            elif 'descending_triangle' in patterns:
                pattern_score -= 15
                reasoning.append("Descending triangle")
            
            # OI analysis
            oi_score = 0
            pcr = oi_analysis.get('pcr', 1)
            oi_trend = oi_analysis.get('oi_analysis', 'neutral')
            
            if oi_trend == 'bullish':
                oi_score += 20
                reasoning.append(f"Bullish OI setup (PCR: {pcr:.2f})")
            elif oi_trend == 'bearish':
                oi_score -= 20
                reasoning.append(f"Bearish OI setup (PCR: {pcr:.2f})")
            
            # Determine signal direction
            total_score = tech_score + pattern_score + oi_score
            
            if total_score >= 40:
                signal['signal_type'] = 'BUY'
                signal['option_type'] = 'CE'
            elif total_score <= -40:
                signal['signal_type'] = 'BUY'
                signal['option_type'] = 'PE'
            else:
                return None  # No clear direction
            
            # Select strike and calculate entry/targets
            atm_strike = round(current_price / 50) * 50
            
            if signal['option_type'] == 'CE':
                # For bullish signals, prefer slightly OTM
                target_strike = atm_strike + 50 if signal['signal_type'] == 'BUY' else atm_strike
                if target_strike in option_chain.get('ce_data', {}):
                    option_data = option_chain['ce_data'][target_strike]
                    signal['strike'] = target_strike
                    signal['entry_price'] = option_data['ltp']
                    signal['target'] = option_data['ltp'] * 1.3  # 30% target
                    signal['stop_loss'] = option_data['ltp'] * 0.7  # 30% SL
                    signal['liquidity_score'] = min(option_data['volume'] / 1000, 100)
            else:
                # For bearish signals, prefer slightly OTM
                target_strike = atm_strike - 50 if signal['signal_type'] == 'BUY' else atm_strike
                if target_strike in option_chain.get('pe_data', {}):
                    option_data = option_chain['pe_data'][target_strike]
                    signal['strike'] = target_strike
                    signal['entry_price'] = option_data['ltp']
                    signal['target'] = option_data['ltp'] * 1.3  # 30% target
                    signal['stop_loss'] = option_data['ltp'] * 0.7  # 30% SL
                    signal['liquidity_score'] = min(option_data['volume'] / 1000, 100)
            
            if signal['entry_price'] == 0:
                return None  # No valid option data
            
            # Calculate confidence
            signal['technical_score'] = tech_score
            signal['oi_score'] = oi_score
            signal['pattern_score'] = pattern_score
            signal['confidence'] = min(max(total_score + 50, 0), 100)  # Normalize to 0-100
            signal['reasoning'] = reasoning
            
            # Risk-reward ratio
            if signal['entry_price'] > 0:
                profit_potential = abs(signal['target'] - signal['entry_price'])
                loss_potential = abs(signal['entry_price'] - signal['stop_loss'])
                signal['risk_reward'] = profit_potential / loss_potential if loss_potential > 0 else 0
            
            # Time decay assessment
            days_to_expiry = (option_chain.get('expiry') - datetime.now().date()).days if option_chain.get('expiry') else 7
            if days_to_expiry <= 7:
                signal['time_decay_risk'] = 'high'
                signal['confidence'] *= 0.9  # Reduce confidence for expiry risk
            elif days_to_expiry <= 14:
                signal['time_decay_risk'] = 'medium'
                signal['confidence'] *= 0.95
            else:
                signal['time_decay_risk'] = 'low'
            
            # Final validation
            if (signal['confidence'] >= self.min_confidence and 
                signal['liquidity_score'] >= 20 and 
                signal['risk_reward'] >= 1.5):
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error evaluating signal conditions: {e}")
            return None

# Global instance
advanced_fno_engine = AdvancedFnOSignalEngine()