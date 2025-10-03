"""
Advanced FnO Signal Engine
Professional options trading signals with OI analysis, CE/PE selection, and technical patterns
"""

import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional, Tuple
from kiteconnect import KiteConnect
import pandas_ta as ta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SignalType(Enum):
    BUY_CE = "BUY_CE"
    BUY_PE = "BUY_PE"
    SELL_CE = "SELL_CE"
    SELL_PE = "SELL_PE"

class ConfidenceLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"

@dataclass
class FnOSignal:
    """Professional FnO Signal Structure"""
    symbol: str
    instrument_type: str  # CE/PE
    strike_price: float
    entry_price: float
    target_price: float
    stop_loss: float
    signal_type: SignalType
    confidence: int
    confidence_level: ConfidenceLevel
    expiry_date: str
    reasoning: str
    technical_setup: str
    oi_analysis: Dict[str, Any]
    risk_reward: float
    quantity: int
    timestamp: datetime
    chart_pattern: str
    market_sentiment: str
    vwap_analysis: str
    volume_profile: str
    time_decay_impact: str

class ProfessionalFnOEngine:
    """Advanced FnO Signal Generation Engine"""
    
    def __init__(self, api_key: str, access_token: str):
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
        self.api_key = api_key
        self.access_token = access_token
        
        # Trading parameters
        self.min_confidence = 75
        self.max_signals_per_day = 8
        self.risk_reward_ratio = 2.0
        self.signals_generated_today = 0
        
        # Instruments focus
        self.primary_instruments = ['NIFTY', 'BANKNIFTY']
        self.stock_instruments = ['RELIANCE', 'HDFC', 'ICICIBANK', 'INFY', 'TCS']
        
        logger.info("🚀 Professional FnO Signal Engine initialized")
    
    def get_option_chain(self, instrument: str) -> Dict[str, Any]:
        """Get complete option chain with OI analysis"""
        try:
            # Get instrument token
            instruments = self.kite.instruments('NFO')
            base_instrument = None
            
            for inst in instruments:
                if inst['name'] == instrument and inst['instrument_type'] == 'FUT':
                    base_instrument = inst
                    break
            
            if not base_instrument:
                return {}
            
            # Get current month options
            options = [inst for inst in instruments 
                      if inst['name'] == instrument 
                      and inst['instrument_type'] in ['CE', 'PE']
                      and inst['expiry'] == base_instrument['expiry']]
            
            # Get LTP and OI data
            option_tokens = [str(opt['instrument_token']) for opt in options[:50]]  # Limit to avoid rate limits
            
            if option_tokens:
                ltp_data = self.kite.ltp([f"NFO:{opt['tradingsymbol']}" for opt in options[:50]])
                ohlc_data = self.kite.ohlc([f"NFO:{opt['tradingsymbol']}" for opt in options[:50]])
                
                # Combine data
                option_chain = []
                for opt in options[:50]:
                    key = f"NFO:{opt['tradingsymbol']}"
                    if key in ltp_data and key in ohlc_data:
                        option_chain.append({
                            'symbol': opt['tradingsymbol'],
                            'strike': opt['strike'],
                            'option_type': opt['instrument_type'],
                            'ltp': ltp_data[key]['last_price'],
                            'oi': ohlc_data[key]['oi'],
                            'volume': ohlc_data[key]['volume'],
                            'expiry': opt['expiry']
                        })
                
                return {
                    'instrument': instrument,
                    'spot_price': self.get_spot_price(instrument),
                    'options': option_chain,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting option chain for {instrument}: {e}")
            return {}
    
    def get_spot_price(self, instrument: str) -> float:
        """Get current spot price"""
        try:
            if instrument in ['NIFTY', 'BANKNIFTY']:
                # Index prices
                quote = self.kite.ltp([f"NSE:{instrument} 50" if instrument == 'NIFTY' else f"NSE:{instrument}"])
                key = list(quote.keys())[0]
                return quote[key]['last_price']
            else:
                # Stock prices
                quote = self.kite.ltp([f"NSE:{instrument}"])
                key = list(quote.keys())[0]
                return quote[key]['last_price']
        except Exception as e:
            logger.warning(f"Error getting spot price for {instrument}: {e}")
            return 0.0
    
    def analyze_open_interest(self, option_chain: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced Open Interest Analysis"""
        try:
            options = option_chain.get('options', [])
            spot_price = option_chain.get('spot_price', 0)
            
            if not options or not spot_price:
                return {}
            
            # Separate CE and PE options
            ce_options = [opt for opt in options if opt['option_type'] == 'CE']
            pe_options = [opt for opt in options if opt['option_type'] == 'PE']
            
            # Find ATM, ITM, OTM levels
            atm_strike = self.find_nearest_strike(spot_price, [opt['strike'] for opt in options])
            
            # OI Analysis
            total_ce_oi = sum(opt['oi'] for opt in ce_options)
            total_pe_oi = sum(opt['oi'] for opt in pe_options)
            
            # Find max OI strikes
            max_ce_oi = max(ce_options, key=lambda x: x['oi']) if ce_options else None
            max_pe_oi = max(pe_options, key=lambda x: x['oi']) if pe_options else None
            
            # Calculate Put-Call Ratio
            pcr = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
            
            # Support and Resistance from OI
            support_level = max_pe_oi['strike'] if max_pe_oi else spot_price
            resistance_level = max_ce_oi['strike'] if max_ce_oi else spot_price
            
            return {
                'total_ce_oi': total_ce_oi,
                'total_pe_oi': total_pe_oi,
                'put_call_ratio': pcr,
                'atm_strike': atm_strike,
                'max_ce_oi_strike': max_ce_oi['strike'] if max_ce_oi else None,
                'max_pe_oi_strike': max_pe_oi['strike'] if max_pe_oi else None,
                'support_level': support_level,
                'resistance_level': resistance_level,
                'sentiment': self.get_oi_sentiment(pcr),
                'strength': 'Strong' if abs(pcr - 1) > 0.3 else 'Moderate'
            }
            
        except Exception as e:
            logger.error(f"OI Analysis error: {e}")
            return {}
    
    def find_nearest_strike(self, spot_price: float, strikes: List[float]) -> float:
        """Find nearest strike to spot price"""
        return min(strikes, key=lambda x: abs(x - spot_price))
    
    def get_oi_sentiment(self, pcr: float) -> str:
        """Determine market sentiment from PCR"""
        if pcr > 1.3:
            return "Bullish"
        elif pcr < 0.7:
            return "Bearish"
        else:
            return "Neutral"
    
    def get_historical_data(self, instrument_token: int, days: int = 10) -> pd.DataFrame:
        """Get historical data for technical analysis"""
        try:
            from_date = datetime.now() - timedelta(days=days)
            to_date = datetime.now()
            
            data = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval='5minute'
            )
            
            if data:
                df = pd.DataFrame(data)
                df['datetime'] = pd.to_datetime(df['date'])
                df.set_index('datetime', inplace=True)
                return df
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            
        return pd.DataFrame()
    
    def technical_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive Technical Analysis"""
        if df.empty:
            return {}
        
        try:
            # Add technical indicators
            df.ta.rsi(append=True, length=14)
            df.ta.macd(append=True)
            df.ta.bbands(append=True)
            df.ta.ema(append=True, length=20)
            df.ta.sma(append=True, length=50)
            df.ta.vwap(append=True)
            df.ta.adx(append=True)
            df.ta.stoch(append=True)
            
            # Get latest values
            latest = df.iloc[-1]
            
            indicators = {
                'rsi': float(latest.get('RSI_14', 50)),
                'macd': float(latest.get('MACD_12_26_9', 0)),
                'macd_signal': float(latest.get('MACDs_12_26_9', 0)),
                'bb_upper': float(latest.get('BBU_5_2.0', 0)),
                'bb_lower': float(latest.get('BBL_5_2.0', 0)),
                'ema_20': float(latest.get('EMA_20', 0)),
                'sma_50': float(latest.get('SMA_50', 0)),
                'vwap': float(latest.get('VWAP_D', 0)),
                'adx': float(latest.get('ADX_14', 0)),
                'stoch_k': float(latest.get('STOCHk_14_3_3', 0)),
                'volume': float(latest.get('volume', 0)),
                'close': float(latest.get('close', 0))
            }
            
            # Pattern recognition
            pattern = self.identify_chart_pattern(df)
            
            # Signal strength
            strength = self.calculate_signal_strength(indicators)
            
            return {
                'indicators': indicators,
                'pattern': pattern,
                'strength': strength,
                'trend': self.determine_trend(indicators),
                'volatility': self.calculate_volatility(df)
            }
            
        except Exception as e:
            logger.error(f"Technical analysis error: {e}")
            return {}
    
    def identify_chart_pattern(self, df: pd.DataFrame) -> str:
        """Identify chart patterns"""
        try:
            if len(df) < 20:
                return "Insufficient Data"
            
            # Simple pattern recognition
            recent_highs = df['high'].tail(10)
            recent_lows = df['low'].tail(10)
            
            # Ascending triangle
            if recent_lows.min() > recent_lows.iloc[0] and recent_highs.std() < recent_lows.std():
                return "Ascending Triangle"
            
            # Descending triangle
            elif recent_highs.max() < recent_highs.iloc[0] and recent_lows.std() < recent_highs.std():
                return "Descending Triangle"
            
            # Breakout
            elif df['close'].iloc[-1] > df['high'].tail(10).max() * 0.98:
                return "Upward Breakout"
            
            elif df['close'].iloc[-1] < df['low'].tail(10).min() * 1.02:
                return "Downward Breakout"
            
            else:
                return "Consolidation"
                
        except Exception as e:
            logger.error(f"Pattern recognition error: {e}")
            return "Unknown"
    
    def calculate_signal_strength(self, indicators: Dict[str, Any]) -> int:
        """Calculate overall signal strength (0-100)"""
        try:
            strength = 0
            
            # RSI analysis
            rsi = indicators.get('rsi', 50)
            if rsi < 30:
                strength += 20  # Oversold
            elif rsi > 70:
                strength += 20  # Overbought
            elif 40 <= rsi <= 60:
                strength += 10  # Neutral
            
            # MACD analysis
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            if macd > macd_signal:
                strength += 15  # Bullish crossover
            elif macd < macd_signal:
                strength += 15  # Bearish crossover
            
            # EMA vs SMA
            ema_20 = indicators.get('ema_20', 0)
            sma_50 = indicators.get('sma_50', 0)
            if ema_20 > sma_50:
                strength += 15  # Bullish trend
            elif ema_20 < sma_50:
                strength += 15  # Bearish trend
            
            # VWAP analysis
            close = indicators.get('close', 0)
            vwap = indicators.get('vwap', 0)
            if abs(close - vwap) / vwap < 0.005:  # Close to VWAP
                strength += 10
            
            # ADX for trend strength
            adx = indicators.get('adx', 0)
            if adx > 25:
                strength += 15  # Strong trend
            
            # Volume confirmation
            volume = indicators.get('volume', 0)
            if volume > 0:  # Has volume data
                strength += 10
            
            return min(strength, 100)
            
        except Exception as e:
            logger.error(f"Signal strength calculation error: {e}")
            return 50
    
    def determine_trend(self, indicators: Dict[str, Any]) -> str:
        """Determine overall trend direction"""
        try:
            bullish_signals = 0
            bearish_signals = 0
            
            # RSI
            rsi = indicators.get('rsi', 50)
            if rsi > 50:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            # MACD
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            if macd > macd_signal:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            # EMA vs SMA
            ema_20 = indicators.get('ema_20', 0)
            sma_50 = indicators.get('sma_50', 0)
            if ema_20 > sma_50:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            if bullish_signals > bearish_signals:
                return "Bullish"
            elif bearish_signals > bullish_signals:
                return "Bearish"
            else:
                return "Sideways"
                
        except Exception as e:
            logger.error(f"Trend determination error: {e}")
            return "Unknown"
    
    def calculate_volatility(self, df: pd.DataFrame) -> str:
        """Calculate volatility level"""
        try:
            if len(df) < 10:
                return "Unknown"
            
            returns = df['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # Annualized
            
            if volatility > 0.3:
                return "High"
            elif volatility > 0.15:
                return "Medium"
            else:
                return "Low"
                
        except Exception as e:
            logger.error(f"Volatility calculation error: {e}")
            return "Unknown"
    
    def generate_fno_signal(self, instrument: str) -> Optional[FnOSignal]:
        """Generate professional FnO signal"""
        try:
            logger.info(f"🔍 Analyzing {instrument} for FnO signals...")
            
            # Get option chain
            option_chain = self.get_option_chain(instrument)
            if not option_chain:
                return None
            
            # OI Analysis
            oi_analysis = self.analyze_open_interest(option_chain)
            if not oi_analysis:
                return None
            
            # Get spot price and technical data
            spot_price = option_chain['spot_price']
            
            # For technical analysis, we need instrument token
            instruments = self.kite.instruments('NSE')
            instrument_token = None
            for inst in instruments:
                if inst['tradingsymbol'] == f"{instrument}50" or inst['tradingsymbol'] == instrument:
                    instrument_token = inst['instrument_token']
                    break
            
            if not instrument_token:
                logger.warning(f"No instrument token found for {instrument}")
                return None
            
            # Technical analysis
            df = self.get_historical_data(instrument_token)
            technical_data = self.technical_analysis(df)
            
            if not technical_data:
                return None
            
            # Generate signal based on analysis
            signal = self.create_signal_from_analysis(
                instrument, spot_price, option_chain, oi_analysis, technical_data
            )
            
            if signal and signal.confidence >= self.min_confidence:
                logger.info(f"✅ Generated {signal.confidence}% confidence {signal.signal_type.value} signal for {instrument}")
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating FnO signal for {instrument}: {e}")
            return None
    
    def create_signal_from_analysis(
        self, 
        instrument: str, 
        spot_price: float, 
        option_chain: Dict[str, Any], 
        oi_analysis: Dict[str, Any], 
        technical_data: Dict[str, Any]
    ) -> Optional[FnOSignal]:
        """Create signal from comprehensive analysis"""
        try:
            indicators = technical_data.get('indicators', {})
            pattern = technical_data.get('pattern', 'Unknown')
            trend = technical_data.get('trend', 'Unknown')
            strength = technical_data.get('strength', 0)
            
            # Determine signal type based on analysis
            signal_type, confidence = self.determine_signal_type(oi_analysis, indicators, trend, strength)
            
            if not signal_type or confidence < self.min_confidence:
                return None
            
            # Select optimal strike
            optimal_strike = self.select_optimal_strike(
                spot_price, option_chain['options'], signal_type, oi_analysis
            )
            
            if not optimal_strike:
                return None
            
            # Calculate entry, target, and stop loss
            entry_price = optimal_strike['ltp']
            target_price, stop_loss = self.calculate_targets(
                entry_price, signal_type, indicators, confidence
            )
            
            # Risk-reward validation
            risk = abs(entry_price - stop_loss)
            reward = abs(target_price - entry_price)
            risk_reward = reward / risk if risk > 0 else 0
            
            if risk_reward < self.risk_reward_ratio:
                logger.info(f"Signal rejected due to poor risk-reward: {risk_reward:.2f}")
                return None
            
            # Create professional signal
            signal = FnOSignal(
                symbol=optimal_strike['symbol'],
                instrument_type=optimal_strike['option_type'],
                strike_price=optimal_strike['strike'],
                entry_price=entry_price,
                target_price=target_price,
                stop_loss=stop_loss,
                signal_type=signal_type,
                confidence=confidence,
                confidence_level=self.get_confidence_level(confidence),
                expiry_date=optimal_strike['expiry'].strftime('%d-%b-%Y'),
                reasoning=self.generate_reasoning(oi_analysis, indicators, pattern, trend),
                technical_setup=f"{pattern} | {trend} Trend | Strength: {strength}%",
                oi_analysis=oi_analysis,
                risk_reward=risk_reward,
                quantity=self.calculate_quantity(entry_price, risk),
                timestamp=datetime.now(),
                chart_pattern=pattern,
                market_sentiment=oi_analysis.get('sentiment', 'Neutral'),
                vwap_analysis=f"Price vs VWAP: {self.get_vwap_analysis(indicators)}",
                volume_profile="Above Average" if indicators.get('volume', 0) > 0 else "Below Average",
                time_decay_impact=self.get_time_decay_impact(optimal_strike['expiry'])
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Error creating signal from analysis: {e}")
            return None
    
    def determine_signal_type(
        self, 
        oi_analysis: Dict[str, Any], 
        indicators: Dict[str, Any], 
        trend: str, 
        strength: int
    ) -> Tuple[Optional[SignalType], int]:
        """Determine signal type and confidence"""
        try:
            confidence = 0
            signal_type = None
            
            # OI-based signals
            pcr = oi_analysis.get('put_call_ratio', 1.0)
            oi_sentiment = oi_analysis.get('sentiment', 'Neutral')
            
            # Technical signals
            rsi = indicators.get('rsi', 50)
            macd = indicators.get('macd', 0)
            macd_signal = indicators.get('macd_signal', 0)
            
            # Bullish signals
            if (oi_sentiment == 'Bullish' and trend == 'Bullish' and 
                rsi < 70 and macd > macd_signal):
                signal_type = SignalType.BUY_CE
                confidence = min(85 + strength // 5, 95)
            
            # Bearish signals
            elif (oi_sentiment == 'Bearish' and trend == 'Bearish' and 
                  rsi > 30 and macd < macd_signal):
                signal_type = SignalType.BUY_PE
                confidence = min(85 + strength // 5, 95)
            
            # Mean reversion signals
            elif rsi > 80 and trend != 'Bullish':
                signal_type = SignalType.BUY_PE
                confidence = min(75 + strength // 8, 85)
            
            elif rsi < 20 and trend != 'Bearish':
                signal_type = SignalType.BUY_CE
                confidence = min(75 + strength // 8, 85)
            
            return signal_type, confidence
            
        except Exception as e:
            logger.error(f"Error determining signal type: {e}")
            return None, 0
    
    def select_optimal_strike(
        self, 
        spot_price: float, 
        options: List[Dict], 
        signal_type: SignalType, 
        oi_analysis: Dict[str, Any]
    ) -> Optional[Dict]:
        """Select optimal strike based on signal type"""
        try:
            # Filter options by type
            if signal_type in [SignalType.BUY_CE, SignalType.SELL_CE]:
                filtered_options = [opt for opt in options if opt['option_type'] == 'CE']
            else:
                filtered_options = [opt for opt in options if opt['option_type'] == 'PE']
            
            if not filtered_options:
                return None
            
            # For buy signals, prefer slightly OTM options
            if signal_type in [SignalType.BUY_CE, SignalType.BUY_PE]:
                if signal_type == SignalType.BUY_CE:
                    # For CE, find strikes above spot
                    candidates = [opt for opt in filtered_options if opt['strike'] >= spot_price]
                    candidates = sorted(candidates, key=lambda x: x['strike'])[:3]  # Top 3 OTM
                else:
                    # For PE, find strikes below spot
                    candidates = [opt for opt in filtered_options if opt['strike'] <= spot_price]
                    candidates = sorted(candidates, key=lambda x: x['strike'], reverse=True)[:3]  # Top 3 OTM
            
            if not candidates:
                # Fallback to nearest ATM
                candidates = sorted(filtered_options, key=lambda x: abs(x['strike'] - spot_price))[:3]
            
            # Select based on liquidity and OI
            best_option = max(candidates, key=lambda x: x['oi'] * x['volume'] if x['volume'] > 0 else x['oi'])
            
            return best_option
            
        except Exception as e:
            logger.error(f"Error selecting optimal strike: {e}")
            return None
    
    def calculate_targets(
        self, 
        entry_price: float, 
        signal_type: SignalType, 
        indicators: Dict[str, Any], 
        confidence: int
    ) -> Tuple[float, float]:
        """Calculate target and stop loss prices"""
        try:
            # Base percentages based on confidence
            if confidence >= 90:
                target_pct = 0.25  # 25% target
                sl_pct = 0.10      # 10% stop loss
            elif confidence >= 80:
                target_pct = 0.20  # 20% target
                sl_pct = 0.12      # 12% stop loss
            else:
                target_pct = 0.15  # 15% target
                sl_pct = 0.15      # 15% stop loss
            
            # Adjust based on volatility
            volatility = indicators.get('adx', 25)
            if volatility > 30:  # High volatility
                target_pct *= 1.2
                sl_pct *= 1.1
            
            # Calculate prices
            if signal_type in [SignalType.BUY_CE, SignalType.BUY_PE]:
                target_price = entry_price * (1 + target_pct)
                stop_loss = entry_price * (1 - sl_pct)
            else:  # SELL signals
                target_price = entry_price * (1 - target_pct)
                stop_loss = entry_price * (1 + sl_pct)
            
            return round(target_price, 2), round(stop_loss, 2)
            
        except Exception as e:
            logger.error(f"Error calculating targets: {e}")
            return entry_price * 1.15, entry_price * 0.85
    
    def calculate_quantity(self, entry_price: float, risk_amount: float) -> int:
        """Calculate optimal quantity based on risk management"""
        try:
            # Risk per trade (example: ₹500 per trade)
            max_risk_per_trade = 500
            
            # Calculate quantity
            if risk_amount > 0:
                quantity = int(max_risk_per_trade / risk_amount)
                return max(1, min(quantity, 10))  # Between 1-10 lots
            
            return 1
            
        except Exception as e:
            logger.error(f"Error calculating quantity: {e}")
            return 1
    
    def get_confidence_level(self, confidence: int) -> ConfidenceLevel:
        """Convert confidence percentage to level"""
        if confidence >= 90:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 80:
            return ConfidenceLevel.HIGH
        elif confidence >= 70:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def generate_reasoning(
        self, 
        oi_analysis: Dict[str, Any], 
        indicators: Dict[str, Any], 
        pattern: str, 
        trend: str
    ) -> str:
        """Generate human-readable reasoning"""
        try:
            reasoning_parts = []
            
            # OI reasoning
            pcr = oi_analysis.get('put_call_ratio', 1.0)
            sentiment = oi_analysis.get('sentiment', 'Neutral')
            reasoning_parts.append(f"OI shows {sentiment.lower()} sentiment (PCR: {pcr:.2f})")
            
            # Technical reasoning
            rsi = indicators.get('rsi', 50)
            if rsi > 70:
                reasoning_parts.append("RSI indicates overbought conditions")
            elif rsi < 30:
                reasoning_parts.append("RSI indicates oversold conditions")
            else:
                reasoning_parts.append(f"RSI at {rsi:.1f} shows balanced momentum")
            
            # Pattern reasoning
            if pattern != 'Unknown':
                reasoning_parts.append(f"Chart shows {pattern.lower()} formation")
            
            # Trend reasoning
            reasoning_parts.append(f"Overall trend is {trend.lower()}")
            
            return " | ".join(reasoning_parts)
            
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            return "Technical and OI analysis confluence"
    
    def get_vwap_analysis(self, indicators: Dict[str, Any]) -> str:
        """Get VWAP analysis description"""
        try:
            close = indicators.get('close', 0)
            vwap = indicators.get('vwap', 0)
            
            if vwap == 0:
                return "VWAP data unavailable"
            
            diff_pct = ((close - vwap) / vwap) * 100
            
            if diff_pct > 1:
                return f"Above VWAP by {diff_pct:.1f}% (Bullish)"
            elif diff_pct < -1:
                return f"Below VWAP by {abs(diff_pct):.1f}% (Bearish)"
            else:
                return f"Near VWAP ({diff_pct:+.1f}%)"
                
        except Exception as e:
            logger.error(f"VWAP analysis error: {e}")
            return "VWAP analysis unavailable"
    
    def get_time_decay_impact(self, expiry_date: datetime) -> str:
        """Assess time decay impact"""
        try:
            days_to_expiry = (expiry_date - datetime.now()).days
            
            if days_to_expiry <= 7:
                return "High (Weekly expiry - Fast decay)"
            elif days_to_expiry <= 30:
                return "Medium (Monthly expiry)"
            else:
                return "Low (Far expiry)"
                
        except Exception as e:
            logger.error(f"Time decay analysis error: {e}")
            return "Unknown"
    
    def scan_all_instruments(self) -> List[FnOSignal]:
        """Scan all instruments for signals"""
        signals = []
        
        try:
            # Scan primary instruments (indices)
            for instrument in self.primary_instruments:
                if self.signals_generated_today >= self.max_signals_per_day:
                    break
                    
                signal = self.generate_fno_signal(instrument)
                if signal:
                    signals.append(signal)
                    self.signals_generated_today += 1
                    logger.info(f"🎯 Added {signal.signal_type.value} signal for {instrument}")
            
            # Scan stock instruments if we have capacity
            if self.signals_generated_today < self.max_signals_per_day:
                for instrument in self.stock_instruments[:3]:  # Limit to 3 stocks
                    if self.signals_generated_today >= self.max_signals_per_day:
                        break
                        
                    signal = self.generate_fno_signal(instrument)
                    if signal:
                        signals.append(signal)
                        self.signals_generated_today += 1
                        logger.info(f"🎯 Added {signal.signal_type.value} signal for {instrument}")
            
            logger.info(f"📊 Generated {len(signals)} professional FnO signals")
            return signals
            
        except Exception as e:
            logger.error(f"Error scanning instruments: {e}")
            return signals

# Global instance
professional_fno_engine = None

def initialize_fno_engine(api_key: str, access_token: str) -> ProfessionalFnOEngine:
    """Initialize the global FnO engine"""
    global professional_fno_engine
    professional_fno_engine = ProfessionalFnOEngine(api_key, access_token)
    return professional_fno_engine