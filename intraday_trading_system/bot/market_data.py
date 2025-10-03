"""
Market Data Manager
Handles fetching live market data from Zerodha Kite Connect and yfinance
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio
import requests

# Local imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config, logger

class MarketDataManager:
    """Manages market data from multiple sources"""
    
    def __init__(self):
        self.logger = logger
        self.config = config
        
        # Kite Connect setup (if available)
        self.kite = None
        if config.KITE_API_KEY and config.KITE_ACCESS_TOKEN:
            try:
                # Note: kiteconnect import handled in production
                self.logger.info("Kite Connect configured")
            except ImportError:
                self.logger.warning("kiteconnect not available, using yfinance only")
        
        # Symbol mapping for yfinance
        self.symbol_mapping = {
            'NIFTY': '^NSEI',
            'BANKNIFTY': '^NSEBANK'
        }
        
        self.logger.info("Market Data Manager initialized")
    
    def get_live_data(self, instrument: str) -> Optional[Dict[str, Any]]:
        """Get live market data for an instrument"""
        try:
            # Try Kite Connect first (if available)
            if self.kite:
                return self._get_kite_data(instrument)
            else:
                # Fallback to yfinance
                return self._get_yfinance_data(instrument)
                
        except Exception as e:
            self.logger.error(f"Error fetching data for {instrument}: {str(e)}")
            return None
    
    def _get_yfinance_data(self, instrument: str) -> Optional[Dict[str, Any]]:
        """Get data from yfinance"""
        try:
            symbol = self.symbol_mapping.get(instrument, instrument)
            ticker = yf.Ticker(symbol)
            
            # Get historical data for technical analysis
            hist = ticker.history(period="5d", interval="1m")
            if hist.empty:
                return None
            
            # Get current price info
            info = ticker.info
            current_price = hist['Close'].iloc[-1]
            
            data = {
                'symbol': instrument,
                'current_price': current_price,
                'open': hist['Open'].iloc[-1],
                'high': hist['High'].iloc[-1],
                'low': hist['Low'].iloc[-1],
                'volume': hist['Volume'].iloc[-1],
                'previous_close': info.get('previousClose', hist['Close'].iloc[-2]),
                'change': current_price - info.get('previousClose', hist['Close'].iloc[-2]),
                'change_percent': ((current_price - info.get('previousClose', hist['Close'].iloc[-2])) / info.get('previousClose', hist['Close'].iloc[-2])) * 100,
                'historical_data': hist,
                'timestamp': datetime.now().isoformat()
            }
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching yfinance data for {instrument}: {str(e)}")
            return None
    
    def _get_kite_data(self, instrument: str) -> Optional[Dict[str, Any]]:
        """Get data from Kite Connect (placeholder for production)"""
        # This would be implemented with actual Kite Connect API
        self.logger.info(f"Kite data fetch for {instrument} (placeholder)")
        return None
    
    async def get_pre_market_analysis(self) -> Dict[str, Any]:
        """Get pre-market analysis data"""
        try:
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'sentiment': 'Neutral',
                'nifty_futures': 'Loading...',
                'bank_nifty_futures': 'Loading...',
                'support_level': 'Calculating...',
                'resistance_level': 'Calculating...',
                'us_markets': await self._get_us_markets_summary(),
                'asian_markets': await self._get_asian_markets_summary(),
                'european_markets': await self._get_european_markets_summary(),
                'outlook': 'Market analysis in progress. Monitor global cues and domestic developments.'
            }
            
            # Get Nifty futures data
            nifty_data = self.get_live_data('NIFTY')
            if nifty_data:
                change_pct = nifty_data.get('change_percent', 0)
                analysis['nifty_futures'] = f"{nifty_data.get('current_price', 'N/A')} ({change_pct:+.2f}%)"
                
                # Determine sentiment based on change
                if change_pct > 0.5:
                    analysis['sentiment'] = 'Bullish'
                elif change_pct < -0.5:
                    analysis['sentiment'] = 'Bearish'
                
                # Calculate support and resistance (simple method)
                hist = nifty_data.get('historical_data')
                if hist is not None and not hist.empty:
                    recent_high = hist['High'].rolling(20).max().iloc[-1]
                    recent_low = hist['Low'].rolling(20).min().iloc[-1]
                    analysis['resistance_level'] = f"{recent_high:.2f}"
                    analysis['support_level'] = f"{recent_low:.2f}"
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in pre-market analysis: {str(e)}")
            return {'error': str(e)}
    
    async def get_post_market_analysis(self) -> Dict[str, Any]:
        """Get post-market analysis data"""
        try:
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'nifty_change': 'Loading...',
                'bank_nifty_change': 'Loading...',
                'fin_nifty_change': 'Loading...',
                'top_gainers': [],
                'top_losers': [],
                'market_reason': 'Market movements influenced by multiple domestic and global factors.',
                'best_sector': 'Analysis in progress',
                'worst_sector': 'Analysis in progress',
                'tomorrow_outlook': 'Monitor global cues, domestic developments, and technical levels.'
            }
            
            # Get index performance
            for instrument in ['NIFTY', 'BANKNIFTY']:
                data = self.get_live_data(instrument)
                if data:
                    change_pct = data.get('change_percent', 0)
                    change_text = f"{data.get('current_price', 'N/A')} ({change_pct:+.2f}%)"
                    
                    if instrument == 'NIFTY':
                        analysis['nifty_change'] = change_text
                    elif instrument == 'BANKNIFTY':
                        analysis['bank_nifty_change'] = change_text
            
            # Add sample gainers/losers (in production, fetch from actual data)
            analysis['top_gainers'] = [
                {'symbol': 'RELIANCE', 'change': '2.5'},
                {'symbol': 'TCS', 'change': '1.8'},
                {'symbol': 'HDFC', 'change': '1.2'}
            ]
            
            analysis['top_losers'] = [
                {'symbol': 'ZOMATO', 'change': '-3.2'},
                {'symbol': 'PAYTM', 'change': '-2.8'},
                {'symbol': 'NYKAA', 'change': '-1.9'}
            ]
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in post-market analysis: {str(e)}")
            return {'error': str(e)}
    
    async def _get_us_markets_summary(self) -> str:
        """Get US markets summary"""
        try:
            # Fetch major US indices
            indices = ['^GSPC', '^DJI', '^IXIC']  # S&P 500, Dow Jones, NASDAQ
            summary_parts = []
            
            for index in indices:
                ticker = yf.Ticker(index)
                hist = ticker.history(period="2d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    previous = hist['Close'].iloc[-2]
                    change_pct = ((current - previous) / previous) * 100
                    
                    name = {'^GSPC': 'S&P 500', '^DJI': 'Dow', '^IXIC': 'NASDAQ'}[index]
                    summary_parts.append(f"{name} {change_pct:+.1f}%")
            
            return ", ".join(summary_parts) if summary_parts else "Data unavailable"
            
        except Exception as e:
            return "Error fetching US data"
    
    async def _get_asian_markets_summary(self) -> str:
        """Get Asian markets summary"""
        try:
            # Major Asian indices
            indices = ['^N225', '^HSI', '000001.SS']  # Nikkei, Hang Seng, Shanghai
            summary_parts = []
            
            for index in indices:
                ticker = yf.Ticker(index)
                hist = ticker.history(period="2d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    previous = hist['Close'].iloc[-2]
                    change_pct = ((current - previous) / previous) * 100
                    
                    name = {'^N225': 'Nikkei', '^HSI': 'Hang Seng', '000001.SS': 'Shanghai'}[index]
                    summary_parts.append(f"{name} {change_pct:+.1f}%")
            
            return ", ".join(summary_parts) if summary_parts else "Data unavailable"
            
        except Exception as e:
            return "Error fetching Asian data"
    
    async def _get_european_markets_summary(self) -> str:
        """Get European markets summary"""
        try:
            # Major European indices
            indices = ['^FTSE', '^GDAXI', '^FCHI']  # FTSE 100, DAX, CAC 40
            summary_parts = []
            
            for index in indices:
                ticker = yf.Ticker(index)
                hist = ticker.history(period="2d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    previous = hist['Close'].iloc[-2]
                    change_pct = ((current - previous) / previous) * 100
                    
                    name = {'^FTSE': 'FTSE', '^GDAXI': 'DAX', '^FCHI': 'CAC'}[index]
                    summary_parts.append(f"{name} {change_pct:+.1f}%")
            
            return ", ".join(summary_parts) if summary_parts else "Data unavailable"
            
        except Exception as e:
            return "Error fetching European data"
    
    def get_historical_data(self, instrument: str, period: str = "1mo", interval: str = "1d") -> Optional[pd.DataFrame]:
        """Get historical data for technical analysis"""
        try:
            symbol = self.symbol_mapping.get(instrument, instrument)
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            return hist if not hist.empty else None
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data for {instrument}: {str(e)}")
            return None
    
    def test_connection(self) -> bool:
        """Test market data connection"""
        try:
            test_data = self.get_live_data('NIFTY')
            return test_data is not None
        except Exception as e:
            self.logger.error(f"Market data connection test failed: {str(e)}")
            return False

# Test function
def test_market_data():
    """Test market data functionality"""
    manager = MarketDataManager()
    
    print("Testing market data connection...")
    success = manager.test_connection()
    print(f"Market data test: {'✅ Success' if success else '❌ Failed'}")
    
    if success:
        data = manager.get_live_data('NIFTY')
        if data:
            print(f"NIFTY data: {data.get('current_price', 'N/A')} ({data.get('change_percent', 0):+.2f}%)")
        else:
            print("Failed to retrieve NIFTY data.")

if __name__ == "__main__":
    test_market_data()