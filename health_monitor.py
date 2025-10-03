"""
System Health Monitor
Monitors system health and implements auto-recovery mechanisms
"""

import psutil
import time
import threading
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from dataclasses import dataclass, asdict
import subprocess

logger = logging.getLogger(__name__)

@dataclass
class HealthMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    connection_status: Dict[str, bool]
    api_latencies: Dict[str, float]
    error_count: Dict[str, int]
    last_signal_time: datetime
    active_signals: int
    system_uptime: float
    component_status: Dict[str, str]

class HealthMonitor:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.metrics_history = []
        self.error_threshold = self.config.get('error_threshold', 5)
        self.metric_interval = self.config.get('metric_interval', 60)  # 1 minute
        self.history_size = self.config.get('history_size', 1440)  # 24 hours
        
        # Component health status
        self.component_status = {
            'market_data': 'unknown',
            'signal_generator': 'unknown',
            'telegram_bot': 'unknown',
            'paper_trading': 'unknown',
            'cache_system': 'unknown'
        }
        
        # Error counters
        self.error_counts = {component: 0 for component in self.component_status}
        
        # Initialize monitoring
        self.is_running = False
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        
        # Recovery actions
        self.recovery_actions = {
            'market_data': self._recover_market_data,
            'signal_generator': self._recover_signal_generator,
            'telegram_bot': self._recover_telegram_bot,
            'paper_trading': self._recover_paper_trading,
            'cache_system': self._recover_cache_system
        }
        
        # Notification settings
        self.notification_channels = {
            'telegram': self._notify_telegram,
            'email': self._notify_email,
            'webhook': self._notify_webhook
        }
        
    def start(self):
        """Start health monitoring"""
        if not self.is_running:
            self.is_running = True
            self.monitor_thread.start()
            logger.info("Health monitoring started")
            
    def stop(self):
        """Stop health monitoring"""
        self.is_running = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join()
        logger.info("Health monitoring stopped")
            
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Collect health metrics
                metrics = self._collect_metrics()
                
                # Store metrics history
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.history_size:
                    self.metrics_history = self.metrics_history[-self.history_size:]
                    
                # Check for issues
                self._check_health(metrics)
                
                # Wait for next interval
                time.sleep(self.metric_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Wait before retrying
                
    def _collect_metrics(self) -> HealthMetrics:
        """Collect current system health metrics"""
        try:
            # System metrics
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # API connection status
            connection_status = {
                'kite': self._check_kite_connection(),
                'telegram': self._check_telegram_connection(),
                'cache': self._check_cache_connection()
            }
            
            # API latencies
            api_latencies = {
                'kite': self._measure_api_latency('kite'),
                'telegram': self._measure_api_latency('telegram')
            }
            
            # Component status
            status = self._check_component_status()
            
            return HealthMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                connection_status=connection_status,
                api_latencies=api_latencies,
                error_count=dict(self.error_counts),
                last_signal_time=self._get_last_signal_time(),
                active_signals=self._count_active_signals(),
                system_uptime=time.time() - psutil.boot_time(),
                component_status=status
            )
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return None
            
    def _check_health(self, metrics: HealthMetrics):
        """Check health metrics and trigger recovery if needed"""
        try:
            if not metrics:
                return
                
            # Check system resources
            if metrics.cpu_usage > 80:
                self._notify_high_resource_usage('CPU', metrics.cpu_usage)
            if metrics.memory_usage > 80:
                self._notify_high_resource_usage('Memory', metrics.memory_usage)
            if metrics.disk_usage > 80:
                self._notify_high_resource_usage('Disk', metrics.disk_usage)
                
            # Check component status
            for component, status in metrics.component_status.items():
                if status == 'error':
                    self.error_counts[component] += 1
                    if self.error_counts[component] >= self.error_threshold:
                        self._trigger_recovery(component)
                else:
                    self.error_counts[component] = 0
                    
            # Check API connections
            for api, connected in metrics.connection_status.items():
                if not connected:
                    logger.warning(f"{api} connection lost")
                    self._notify_connection_issue(api)
                    
            # Check signal generation
            if datetime.now() - metrics.last_signal_time > timedelta(hours=1):
                logger.warning("No signals generated in last hour")
                self._notify_signal_issue()
                
        except Exception as e:
            logger.error(f"Error checking health: {e}")
            
    def _trigger_recovery(self, component: str):
        """Trigger recovery action for component"""
        try:
            logger.info(f"Triggering recovery for {component}")
            
            # Get recovery action
            recovery_action = self.recovery_actions.get(component)
            if recovery_action:
                # Execute recovery
                success = recovery_action()
                
                # Reset error count on success
                if success:
                    self.error_counts[component] = 0
                    self.component_status[component] = 'healthy'
                    logger.info(f"Recovery successful for {component}")
                else:
                    logger.error(f"Recovery failed for {component}")
                    self._notify_recovery_failure(component)
            else:
                logger.warning(f"No recovery action defined for {component}")
                
        except Exception as e:
            logger.error(f"Error in recovery: {e}")
            
    def _recover_market_data(self) -> bool:
        """Recover market data component"""
        try:
            # Attempt to reconnect to Kite
            from market_data_provider import MarketDataProvider
            provider = MarketDataProvider(use_kite=True)
            
            # Test connection
            test_data = provider.get_market_pulse()
            return bool(test_data)
            
        except Exception as e:
            logger.error(f"Market data recovery failed: {e}")
            return False
            
    def _recover_signal_generator(self) -> bool:
        """Recover signal generator component"""
        try:
            # Restart signal generation
            from signal_generator import SignalGenerator
            generator = SignalGenerator()
            
            # Test generation
            test_signal = generator.generate_signals({'test': True}, {})
            return bool(test_signal)
            
        except Exception as e:
            logger.error(f"Signal generator recovery failed: {e}")
            return False
            
    def _recover_telegram_bot(self) -> bool:
        """Recover Telegram bot component"""
        try:
            # Reinitialize bot
            from telegram_bot import TelegramBot
            bot = TelegramBot()
            
            # Test message
            return bot.send_message("Health check test")
            
        except Exception as e:
            logger.error(f"Telegram bot recovery failed: {e}")
            return False
            
    def _recover_paper_trading(self) -> bool:
        """Recover paper trading component"""
        try:
            # Reinitialize paper trading
            from paper_trading_engine import PaperTradingEngine
            engine = PaperTradingEngine()
            
            # Verify data loaded
            return engine.load_data()
            
        except Exception as e:
            logger.error(f"Paper trading recovery failed: {e}")
            return False
            
    def _recover_cache_system(self) -> bool:
        """Recover cache system component"""
        try:
            # Reinitialize cache
            from cache_manager import CacheManager
            cache = CacheManager()
            
            # Test cache operations
            cache.cache_market_data("test", {"test": True})
            test_data = cache.get_market_data("test")
            return test_data is not None
            
        except Exception as e:
            logger.error(f"Cache system recovery failed: {e}")
            return False
            
    def _notify_high_resource_usage(self, resource: str, usage: float):
        """Notify about high resource usage"""
        message = f"High {resource} usage: {usage:.1f}%"
        self._send_notification('warning', message)
            
    def _notify_connection_issue(self, api: str):
        """Notify about API connection issues"""
        message = f"Connection lost to {api}"
        self._send_notification('error', message)
            
    def _notify_signal_issue(self):
        """Notify about signal generation issues"""
        message = "No signals generated in last hour"
        self._send_notification('warning', message)
            
    def _notify_recovery_failure(self, component: str):
        """Notify about recovery failure"""
        message = f"Recovery failed for {component}"
        self._send_notification('error', message)
            
    def _send_notification(self, level: str, message: str):
        """Send notification through all available channels"""
        for channel, notify_func in self.notification_channels.items():
            try:
                notify_func(level, message)
            except Exception as e:
                logger.error(f"Notification failed for {channel}: {e}")
                
    def _notify_telegram(self, level: str, message: str):
        """Send Telegram notification"""
        try:
            if hasattr(self, 'telegram_bot'):
                self.telegram_bot.send_message(f"[{level.upper()}] {message}")
        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")
            
    def _notify_email(self, level: str, message: str):
        """Send email notification"""
        # Implement email notification
        pass
            
    def _notify_webhook(self, level: str, message: str):
        """Send webhook notification"""
        # Implement webhook notification
        pass
            
    def get_health_status(self) -> Dict:
        """Get current health status"""
        if self.metrics_history:
            latest = self.metrics_history[-1]
            return {
                'status': 'healthy' if all(s == 'healthy' for s in latest.component_status.values()) else 'issues',
                'metrics': asdict(latest),
                'timestamp': datetime.now().isoformat()
            }
        return {'status': 'unknown'}