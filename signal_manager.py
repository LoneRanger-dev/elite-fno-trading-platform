"""
Signal Manager
Coordinates signal generation, validation, and distribution
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
from queue import Queue
import threading
import time

logger = logging.getLogger(__name__)

class SignalManager:
    def __init__(self, signal_engine):
        self.engine = signal_engine
        self.signal_queue = Queue()
        self.active_signals = {}
        self.signal_history = []
        self.last_cleanup = datetime.now()
        
        # Signal processing settings
        self.max_active_signals = 5
        self.signal_ttl = 3600  # 1 hour
        self.min_confidence = 75
        self.max_signals_per_instrument = 2
        
        # Initialize worker thread
        self.is_running = False
        self.worker_thread = threading.Thread(target=self._process_signals)
        self.worker_thread.daemon = True
        
    def start(self):
        """Start the signal manager"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread.start()
            logger.info("Signal manager started")
            
    def stop(self):
        """Stop the signal manager"""
        self.is_running = False
        if self.worker_thread.is_alive():
            self.worker_thread.join()
        logger.info("Signal manager stopped")
            
    def add_signal(self, signal: Dict):
        """Add a new signal to the processing queue"""
        try:
            # Basic validation
            if not self._validate_signal_format(signal):
                logger.warning(f"Invalid signal format: {signal}")
                return
                
            # Add to queue
            self.signal_queue.put(signal)
            logger.debug(f"Signal added to queue: {signal['id']}")
            
        except Exception as e:
            logger.error(f"Error adding signal: {e}")
            
    def get_active_signals(self) -> List[Dict]:
        """Get list of currently active signals"""
        try:
            # Clean expired signals first
            self._cleanup_expired_signals()
            
            return list(self.active_signals.values())
            
        except Exception as e:
            logger.error(f"Error getting active signals: {e}")
            return []
            
    def get_signal_history(self, limit: int = 50) -> List[Dict]:
        """Get recent signal history"""
        try:
            return self.signal_history[-limit:]
        except Exception as e:
            logger.error(f"Error getting signal history: {e}")
            return []
            
    def _process_signals(self):
        """Main signal processing loop"""
        while self.is_running:
            try:
                # Clean expired signals periodically
                if (datetime.now() - self.last_cleanup).seconds > 300:  # Every 5 minutes
                    self._cleanup_expired_signals()
                    
                # Get next signal from queue
                if self.signal_queue.empty():
                    time.sleep(1)
                    continue
                    
                signal = self.signal_queue.get()
                
                # Skip if we have too many active signals
                if len(self.active_signals) >= self.max_active_signals:
                    logger.warning("Maximum active signals reached, skipping")
                    continue
                    
                # Validate signal
                validation_result = self.engine.validator.validate_signal(signal)
                if not validation_result.is_valid:
                    logger.info(f"Signal validation failed: {validation_result.messages}")
                    continue
                    
                # Check confidence threshold
                if validation_result.confidence < self.min_confidence:
                    logger.info(f"Signal confidence too low: {validation_result.confidence}")
                    continue
                    
                # Check instrument limits
                instrument = signal['instrument']
                active_for_instrument = sum(1 for s in self.active_signals.values() 
                                         if s['instrument'] == instrument)
                if active_for_instrument >= self.max_signals_per_instrument:
                    logger.info(f"Maximum signals reached for {instrument}")
                    continue
                    
                # Add validation results to signal
                signal['validation'] = {
                    'confidence': validation_result.confidence,
                    'indicators': validation_result.indicators,
                    'messages': validation_result.messages
                }
                
                # Add to active signals
                signal['added_time'] = datetime.now()
                signal['expiry_time'] = datetime.now() + timedelta(seconds=self.signal_ttl)
                self.active_signals[signal['id']] = signal
                
                # Add to history
                self.signal_history.append(signal)
                if len(self.signal_history) > 1000:  # Keep last 1000 signals
                    self.signal_history = self.signal_history[-1000:]
                    
                # Notify subscribers
                self._notify_signal(signal)
                
                logger.info(f"Signal processed successfully: {signal['id']}")
                
            except Exception as e:
                logger.error(f"Error processing signals: {e}")
                time.sleep(1)
                
    def _cleanup_expired_signals(self):
        """Remove expired signals"""
        try:
            now = datetime.now()
            expired = []
            
            for signal_id, signal in self.active_signals.items():
                if now > signal['expiry_time']:
                    expired.append(signal_id)
                    
            for signal_id in expired:
                signal = self.active_signals.pop(signal_id)
                signal['status'] = 'EXPIRED'
                logger.info(f"Signal expired: {signal_id}")
                
            self.last_cleanup = now
            
        except Exception as e:
            logger.error(f"Error cleaning up signals: {e}")
            
    def _validate_signal_format(self, signal: Dict) -> bool:
        """Validate signal has required fields"""
        required_fields = ['id', 'instrument', 'signal_type', 'timestamp']
        return all(field in signal for field in required_fields)
        
    def _notify_signal(self, signal: Dict):
        """Notify subscribers of new signal"""
        try:
            # Telegram notification
            if hasattr(self.engine, 'telegram'):
                message = self._format_signal_message(signal)
                self.engine.telegram.send_message(message)
                
            # Update dashboard
            if hasattr(self.engine, 'dashboard'):
                self.engine.dashboard.update_signals(self.get_active_signals())
                
            # Paper trading system
            if hasattr(self.engine, 'paper_trader'):
                self.engine.paper_trader.process_signal(signal)
                
        except Exception as e:
            logger.error(f"Error notifying signal: {e}")
            
    def _format_signal_message(self, signal: Dict) -> str:
        """Format signal for Telegram notification"""
        try:
            return f"""🔔 *New Trading Signal*
            
*Instrument:* {signal['instrument']}
*Type:* {signal['signal_type']}
*Entry:* {signal.get('option_entry_price', 'N/A')}
*Target:* {signal.get('option_target_price', 'N/A')}
*Stop Loss:* {signal.get('option_stop_loss', 'N/A')}
*Confidence:* {signal['validation']['confidence']}%
*Setup:* {signal.get('setup_description', 'N/A')}

*Technical Indicators:*
{self._format_indicators(signal['validation']['indicators'])}

*Risk/Reward:* {signal.get('risk_reward_ratio', 'N/A')}
*Lot Size:* {signal.get('lot_size', 1)}
*Expiry:* {signal.get('expiry_date', 'N/A')}

⚠️ *Trade at your own risk*
            """
        except Exception as e:
            logger.error(f"Error formatting signal message: {e}")
            return str(signal)
            
    def _format_indicators(self, indicators: Dict) -> str:
        """Format technical indicators for message"""
        try:
            lines = []
            for name, value in indicators.items():
                if isinstance(value, (int, float)):
                    lines.append(f"• {name.upper()}: {value:.2f}")
                else:
                    lines.append(f"• {name.upper()}: {value}")
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error formatting indicators: {e}")
            return "N/A"