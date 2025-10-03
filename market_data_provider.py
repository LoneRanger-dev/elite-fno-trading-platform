"""
Market Data Provider
This module is responsible for fetching market data from various sources.
Primarily uses Zerodha Kite API for real-time market data.
"""
import yfinance as yf
from typing import Dict, List
from kiteconnect import KiteConnect
import pandas as pd
import logging
import requests
import time
from datetime import datetime, timedelta
from config.settings import KITE_API_KEY, KITE_API_SECRET, KITE_ACCESS_TOKEN

# Configure logging
logger = logging.getLogger(__name__)

class MarketDataProvider:
    def __init__(self, use_kite=True):
        self.indices = {
            "NIFTY 50": {"kite": "NSE:NIFTY 50", "yf": "^NSEI", "nse": "NIFTY"},
            "NIFTY BANK": {"kite": "NSE:NIFTY BANK", "yf": "^NSEBANK", "nse": "BANKNIFTY"},
            "SENSEX": {"kite": "BSE:SENSEX", "yf": "^BSESN", "nse": "SENSEX"}
        }
        self.cache = {}
        self.cache_ttl = 5  # Cache TTL in seconds
        self.instrument_tokens = {
            "NSE:NIFTY 50": 256265,
            "NSE:NIFTY BANK": 260105,
            "BSE:SENSEX": 265
        }
        self.data_sources = ["kite", "yf", "nse"]
        self.source_failures = {source: 0 for source in self.data_sources}
        self.max_failures = 3  # Switch source after 3 consecutive failures
        
        self.kite = None
        if use_kite:
            try:
                self.kite = KiteConnect(api_key=KITE_API_KEY)
                self.kite.set_access_token(KITE_ACCESS_TOKEN)
                logger.info("Successfully initialized Kite Connect")
                print("KiteConnect initialized.")
            except Exception as e:
                print(f"Could not initialize KiteConnect: {e}")

    def get_market_pulse(self) -> Dict[str, Dict]:
        """
        Fetches live market data from multiple sources with automatic failover.
        """
        for source in self.data_sources:
            try:
                if source == "kite" and self.source_failures["kite"] < self.max_failures:
                    data = self._get_market_pulse_kite()
                    if data:
                        self.source_failures["kite"] = 0
                        return data
                    self.source_failures["kite"] += 1
                
                elif source == "yf" and self.source_failures["yf"] < self.max_failures:
                    data = self._get_market_pulse_yf()
                    if data:
                        self.source_failures["yf"] = 0
                        return data
                    self.source_failures["yf"] += 1
                
                elif source == "nse" and self.source_failures["nse"] < self.max_failures:
                    data = self._get_market_pulse_nse()
                    if data:
                        self.source_failures["nse"] = 0
                        return data
                    self.source_failures["nse"] += 1
                    
            except Exception as e:
                logger.error(f"Error fetching data from {source}: {e}")
                self.source_failures[source] += 1
                
        return self._get_empty_pulse_data("All data sources failed")

        try:
            quotes = self.kite.quote(list(self.instrument_tokens.values()))
            
            if not quotes:
                return self._get_empty_pulse_data("Kite API returned no data for quotes.")

            data = {}
            for instrument, token in self.instrument_tokens.items():
                quote = quotes.get(str(token))
                if quote:
                    last_price = quote['last_price']
                    prev_close = quote['ohlc']['close']
                    
                    change = last_price - prev_close
                    change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
                    
                    # The instrument name from Kite might be slightly different, so we find the key by value
                    index_name = next((name for name, inst in self.indices.items() if inst == instrument), None)
                    if index_name:
                        data[index_name] = {
                            'value': round(last_price, 2),
                            'change': round(change, 2),
                            'change_percent': round(change_percent, 2)
                        }
                else:
                    index_name = next((name for name, inst in self.indices.items() if inst == instrument), None)
                    if index_name:
                         data[index_name] = self._get_empty_pulse_data(f"No quote data for {index_name}")['data'][index_name]


            return {'success': True, 'data': data}

        except Exception as e:
            return self._get_empty_pulse_data(f"Kite API Error: {e}")

    def get_instrument_token(self, tradingsymbol, exchange='NSE'):
        """
        Retrieves the instrument token for a given trading symbol.
        Note: This is a simplified version. A robust implementation would
              fetch and cache the full instrument list from Kite.
        """
        # This is a sample mapping. For a real app, you'd fetch this from Kite's instrument dump.
        # For now, we'll add a few common ones.
        instrument_map = {
            "RELIANCE": 738561,
            "HDFCBANK": 341249,
            "INFY": 408065,
            "ICICIBANK": 3450627,
            "TCS": 2953217,
            "KOTAKBANK": 492033,
            "HINDUNILVR": 356865,
            "ITC": 424961,
            "BAJFINANCE": 81153,
            "SBIN": 779521,
        }
        token = instrument_map.get(tradingsymbol.upper())
        if not token:
            print(f"Warning: Instrument token not found for {tradingsymbol}. Using a placeholder. Please update instrument map.")
            # Fallback for symbols not in our map
            try:
                # This is not a real Kite API call, but simulates searching
                search_result = self.kite.instruments(exchange=exchange)
                for inst in search_result:
                    if inst['tradingsymbol'] == tradingsymbol.upper():
                        return inst['instrument_token']
            except Exception as e:
                print(f"Could not dynamically find instrument token for {tradingsymbol}: {e}")
        return token

    def get_historical_data_kite(self, tradingsymbol, interval='day', period=30):
        """
        Fetches historical data for a given instrument using Kite API.
        """
        if not self.kite or not self.kite.access_token:
            print("Kite API not available for historical data.")
            return None

        instrument_token = self.get_instrument_token(tradingsymbol)
        if not instrument_token:
            return None

        from_date = (pd.Timestamp.now() - pd.DateOffset(days=period)).strftime('%Y-%m-%d')
        to_date = pd.Timestamp.now().strftime('%Y-%m-%d')

        try:
            records = self.kite.historical_data(instrument_token, from_date, to_date, interval)
            df = pd.DataFrame(records)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                return df
            return None
        except Exception as e:
            print(f"Error fetching historical data for {tradingsymbol} from Kite: {e}")
            return None

    def get_market_pulse_yfinance(self) -> Dict[str, Dict]:
        """
        Fetches live market data for major indices using yfinance.
        """
        data = {}
        tickers = " ".join(self.indices.values())
        
        try:
            # Use download for more efficient fetching of multiple tickers
            hist = yf.download(tickers=tickers, period="2d", progress=False)
            if hist.empty:
                return self._get_empty_pulse_data("yfinance download returned no data.")

            for name, ticker_symbol in self.indices.items():
                # Check if data for the ticker is present
                if ticker_symbol in hist['Close']:
                    ticker_hist = hist.loc[:, (slice(None), ticker_symbol)]
                    if len(ticker_hist) >= 2:
                        last_close = ticker_hist['Close', ticker_symbol].iloc[-1]
                        prev_close = ticker_hist['Close', ticker_symbol].iloc[-2]
                        
                        change = last_close - prev_close
                        change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
                        
                        data[name] = {
                            'value': round(last_close, 2),
                            'change': round(change, 2),
                            'change_percent': round(change_percent, 2)
                        }
                    else:
                        data[name] = self._get_empty_pulse_data(f"Not enough history for {name}")['data']
                else:
                    data[name] = self._get_empty_pulse_data(f"No data for {name}")['data']

            return {'success': True, 'data': data}

        except Exception as e:
            return self._get_empty_pulse_data(str(e))

    def _get_empty_pulse_data(self, error_message: str):
        """Returns a default structure for when data fetching fails."""
        print(f"Market Pulse Error: {error_message}")
        return {
            'success': False,
            'message': error_message,
            'data': {
                name: {
                    'value': 0,
                    'change': 0,
                    'change_percent': 0
                } for name in self.indices
            }
        }

    def get_kite_login_url(self):
        """Generates and returns the Kite login URL."""
        if self.kite:
            return self.kite.login_url()
        return None

# Singleton instance - will be initialized from the main app
market_data_provider = None

def initialize_market_data_provider(kite_config=None):
    """Factory function to initialize the singleton."""
    global market_data_provider
    if market_data_provider is None:
        market_data_provider = MarketDataProvider(kite_config)
    return market_data_provider
