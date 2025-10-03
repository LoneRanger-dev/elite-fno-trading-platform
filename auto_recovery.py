"""Auto-recovery manager for handling service failures."""

import time
import logging
import threading
from typing import Dict, Any, Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AutoRecoveryManager:
    """
    Manages automatic recovery of failed services and components.
    
    Features:
    - Periodic health checks
    - Automatic restart attempts
    - Failure tracking and backoff
    - Recovery status notifications
    """
    
    def __init__(self, notification_manager=None):
        """
        Initialize recovery manager.
        
        Args:
            notification_manager: Optional NotificationManager instance
        """
        self.notification_manager = notification_manager
        self.services: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        self._stop_event = threading.Event()
        self._monitor_thread = None
        
    def register_service(self, name: str, health_check: Callable[[], bool],
                        recovery_action: Callable[[], None],
                        check_interval: int = 60,
                        max_retries: int = 3,
                        backoff_factor: float = 2.0) -> None:
        """
        Register a service for monitoring.
        
        Args:
            name: Service identifier
            health_check: Function that returns True if service is healthy
            recovery_action: Function to call to attempt recovery
            check_interval: Seconds between health checks
            max_retries: Maximum recovery attempts before giving up
            backoff_factor: Multiplier for successive retry delays
        """
        with self.lock:
            self.services[name] = {
                'health_check': health_check,
                'recovery_action': recovery_action,
                'check_interval': check_interval,
                'max_retries': max_retries,
                'backoff_factor': backoff_factor,
                'last_check': None,
                'last_failure': None,
                'retry_count': 0,
                'status': 'unknown'
            }
            logger.info(f'Registered service {name} for auto-recovery')
            
    def start(self) -> None:
        """Start monitoring registered services."""
        if self._monitor_thread is not None:
            return
            
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_services,
            daemon=True
        )
        self._monitor_thread.start()
        logger.info('Auto-recovery monitoring started')
        
    def stop(self) -> None:
        """Stop monitoring services."""
        if self._monitor_thread is None:
            return
            
        self._stop_event.set()
        self._monitor_thread.join()
        self._monitor_thread = None
        logger.info('Auto-recovery monitoring stopped')
        
    def _monitor_services(self) -> None:
        """Main monitoring loop."""
        while not self._stop_event.is_set():
            try:
                self._check_all_services()
            except Exception as e:
                logger.error(
                    f'Error in recovery monitoring loop: {str(e)}',
                    exc_info=True
                )
            time.sleep(1)  # Prevent tight loop
            
    def _check_all_services(self) -> None:
        """Check health of all registered services."""
        current_time = datetime.now()
        
        with self.lock:
            for name, service in self.services.items():
                # Check if it's time for next health check
                if (service['last_check'] is not None and
                    (current_time - service['last_check']).total_seconds() 
                    < service['check_interval']):
                    continue
                    
                service['last_check'] = current_time
                
                try:
                    is_healthy = service['health_check']()
                except Exception as e:
                    logger.error(
                        f'Health check failed for {name}: {str(e)}',
                        exc_info=True
                    )
                    is_healthy = False
                    
                if is_healthy:
                    if service['status'] != 'healthy':
                        self._handle_recovery(name)
                else:
                    self._handle_failure(name, current_time)
                    
    def _handle_failure(self, name: str, current_time: datetime) -> None:
        """Handle service failure detection."""
        service = self.services[name]
        service['last_failure'] = current_time
        service['status'] = 'failed'
        
        if service['retry_count'] >= service['max_retries']:
            logger.error(
                f'Service {name} has failed {service["retry_count"]} times, '
                'giving up auto-recovery'
            )
            if self.notification_manager:
                self.notification_manager.send_alert(
                    f'Service {name} auto-recovery failed after '
                    f'{service["retry_count"]} attempts',
                    severity='critical'
                )
            return
            
        # Calculate backoff delay
        delay = service['check_interval'] * (
            service['backoff_factor'] ** service['retry_count']
        )
        
        logger.warning(
            f'Service {name} failed, attempting recovery in {delay:.1f} seconds'
        )
        
        if self.notification_manager:
            self.notification_manager.send_alert(
                f'Service {name} failed, attempting recovery',
                severity='high'
            )
            
        # Start recovery thread
        threading.Thread(
            target=self._delayed_recovery,
            args=(name, delay),
            daemon=True
        ).start()
        
    def _delayed_recovery(self, name: str, delay: float) -> None:
        """Attempt recovery after delay."""
        time.sleep(delay)
        
        with self.lock:
            service = self.services[name]
            service['retry_count'] += 1
            
            try:
                service['recovery_action']()
                logger.info(f'Recovery action completed for {name}')
            except Exception as e:
                logger.error(
                    f'Recovery action failed for {name}: {str(e)}',
                    exc_info=True
                )
                
    def _handle_recovery(self, name: str) -> None:
        """Handle successful service recovery."""
        service = self.services[name]
        old_status = service['status']
        service['status'] = 'healthy'
        service['retry_count'] = 0
        
        if old_status == 'failed':
            logger.info(f'Service {name} has recovered')
            if self.notification_manager:
                self.notification_manager.send_alert(
                    f'Service {name} has recovered successfully',
                    severity='info'
                )
                
    def get_status(self) -> Dict[str, Dict[str, Any]]:
        """Get current status of all services."""
        with self.lock:
            return {
                name: {
                    'status': service['status'],
                    'last_check': service['last_check'].isoformat() 
                        if service['last_check'] else None,
                    'last_failure': service['last_failure'].isoformat() 
                        if service['last_failure'] else None,
                    'retry_count': service['retry_count']
                }
                for name, service in self.services.items()
            }