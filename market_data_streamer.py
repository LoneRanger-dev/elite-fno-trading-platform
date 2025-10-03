"""
Real-time market data streamer using KiteTicker
"""
from kiteconnect import KiteTicker
from typing import Dict, List, Callable
import logging
import json
from config import kite_api_key, kite_access_token

logger = logging.getLogger(__name__)

class MarketDataStreamer:
    def __init__(self):
        self.kws = None
        self.callbacks = []
        self.subscribed_tokens = set()
        
    def on_connect(self, ws, response):
        logger.info("Successfully connected to market data stream")
        if self.subscribed_tokens:
            self.kws.subscribe(list(self.subscribed_tokens))
            self.kws.set_mode(self.kws.MODE_FULL, list(self.subscribed_tokens))
            
    def on_close(self, ws, code, reason):
        logger.warning(f"Market data connection closed: {reason}")
        
    def on_error(self, ws, code, reason):
        logger.error(f"Market data error: {reason}")
        
    def on_message(self, ws, data):
        """Handle incoming market data"""
        try:
            for callback in self.callbacks:
                callback(data)
        except Exception as e:
            logger.error(f"Error processing market data: {e}", exc_info=True)
            
    def on_order_update(self, ws, data):
        """Handle order updates"""
        logger.info(f"Order update: {json.dumps(data, indent=2)}")
            
    def start(self):
        """Start market data stream"""
        try:
            self.kws = KiteTicker(kite_api_key, kite_access_token)
            
            # Set callbacks
            self.kws.on_connect = self.on_connect
            self.kws.on_close = self.on_close
            self.kws.on_error = self.on_error
            self.kws.on_message = self.on_message
            self.kws.on_order_update = self.on_order_update
            
            # Connect
            self.kws.connect(threaded=True)
            logger.info("Market data streamer started")
            
        except Exception as e:
            logger.error(f"Failed to start market data stream: {e}", exc_info=True)
            raise
            
    def stop(self):
        """Stop market data stream"""
        if self.kws:
            self.kws.close()
            logger.info("Market data streamer stopped")
            
    def subscribe(self, instrument_tokens: List[int]):
        """Subscribe to market data for given instruments"""
        try:
            self.subscribed_tokens.update(instrument_tokens)
            if self.kws and self.kws.is_connected():
                self.kws.subscribe(instrument_tokens)
                self.kws.set_mode(self.kws.MODE_FULL, instrument_tokens)
                logger.info(f"Subscribed to instruments: {instrument_tokens}")
        except Exception as e:
            logger.error(f"Subscription failed: {e}", exc_info=True)
            
    def add_callback(self, callback: Callable):
        """Add callback for market data updates"""
        self.callbacks.append(callback)