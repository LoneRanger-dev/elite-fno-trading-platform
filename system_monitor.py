"""
System monitoring and health checks
"""
import logging
import time
from datetime import datetime, timedelta
import psutil
import json
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.metrics_file = self.log_dir / "system_metrics.json"
        self.signal_log_file = self.log_dir / "signal_metrics.json"
        self.start_time = datetime.now()
        self.signal_count = 0
        self.error_count = 0
        self.last_signal_time = None
        self.signal_history = []
        
    def log_signal(self, signal: Dict):
        """Log trading signal metrics"""
        self.signal_count += 1
        self.last_signal_time = datetime.now()
        
        signal_metric = {
            "timestamp": self.last_signal_time.isoformat(),
            "signal_type": signal.get("signal_type"),
            "instrument": signal.get("instrument"),
            "confidence": signal.get("confidence")
        }
        self.signal_history.append(signal_metric)
        
        # Keep only last 100 signals
        if len(self.signal_history) > 100:
            self.signal_history.pop(0)
            
        self.save_signal_metrics()
        
    def log_error(self, error: str):
        """Log system error"""
        self.error_count += 1
        logger.error(f"System error: {error}")
        
    def get_system_metrics(self) -> Dict:
        """Get current system metrics"""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600,
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "signal_count": self.signal_count,
            "error_count": self.error_count,
            "last_signal": self.last_signal_time.isoformat() if self.last_signal_time else None,
            "signal_rate": self.calculate_signal_rate()
        }
        
    def calculate_signal_rate(self) -> float:
        """Calculate signals per hour"""
        if not self.signal_count:
            return 0.0
        hours = (datetime.now() - self.start_time).total_seconds() / 3600
        return self.signal_count / hours if hours > 0 else 0
        
    def save_system_metrics(self):
        """Save current system metrics to file"""
        metrics = self.get_system_metrics()
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save system metrics: {e}")
            
    def save_signal_metrics(self):
        """Save signal history to file"""
        try:
            with open(self.signal_log_file, 'w') as f:
                json.dump(self.signal_history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save signal metrics: {e}")
            
    def get_health_status(self) -> Dict:
        """Get system health status"""
        metrics = self.get_system_metrics()
        
        # Define health checks
        checks = {
            "cpu_health": metrics["cpu_percent"] < 80,
            "memory_health": metrics["memory_percent"] < 80,
            "signal_generation": bool(self.last_signal_time and 
                datetime.now() - self.last_signal_time < timedelta(hours=1)),
            "error_rate": self.error_count < 10
        }
        
        return {
            "status": "healthy" if all(checks.values()) else "warning",
            "checks": checks,
            "metrics": metrics
        }
        
    def start_monitoring(self):
        """Start periodic monitoring"""
        while True:
            try:
                self.save_system_metrics()
                time.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Monitoring error: {e}", exc_info=True)