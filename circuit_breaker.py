"""Circuit breaker implementation for API and service protection."""

import time
import logging
import threading
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """
    Implements circuit breaker pattern to prevent cascade failures.
    
    States:
    - CLOSED: Normal operation, requests allowed
    - OPEN: Failure threshold exceeded, requests blocked
    - HALF_OPEN: Testing if service recovered
    """
    
    CLOSED = 'CLOSED'
    OPEN = 'OPEN'
    HALF_OPEN = 'HALF_OPEN'
    
    def __init__(self, name: str, failure_threshold: int = 5,
                 reset_timeout: int = 60, half_open_limit: int = 3):
        """
        Initialize circuit breaker.
        
        Args:
            name: Identifier for this circuit breaker
            failure_threshold: Number of failures before opening circuit
            reset_timeout: Seconds to wait before attempting reset
            half_open_limit: Number of successful requests needed to close circuit
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_limit = half_open_limit
        
        self.state = self.CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time = None
        self.lock = threading.Lock()
        
    def record_failure(self) -> None:
        """Record a failure and potentially open the circuit."""
        with self.lock:
            self.failures += 1
            self.last_failure_time = datetime.now()
            
            if self.state == self.CLOSED and self.failures >= self.failure_threshold:
                logger.warning(
                    f'Circuit {self.name} opened after {self.failures} failures'
                )
                self.state = self.OPEN
                
            elif self.state == self.HALF_OPEN:
                logger.warning(f'Circuit {self.name} reopened after test failure')
                self.state = self.OPEN
                self.failures = self.failure_threshold
                self.successes = 0
                
    def record_success(self) -> None:
        """Record a success and potentially close the circuit."""
        with self.lock:
            if self.state == self.HALF_OPEN:
                self.successes += 1
                if self.successes >= self.half_open_limit:
                    logger.info(
                        f'Circuit {self.name} closed after {self.successes} '
                        'successful tests'
                    )
                    self.state = self.CLOSED
                    self.failures = 0
                    self.successes = 0
                    
            elif self.state == self.CLOSED:
                self.failures = max(0, self.failures - 1)  # Decay failure count
                
    def allow_request(self) -> bool:
        """Check if a request should be allowed through the circuit."""
        with self.lock:
            if self.state == self.CLOSED:
                return True
                
            elif self.state == self.OPEN:
                if self._should_attempt_reset():
                    logger.info(f'Circuit {self.name} entering half-open state')
                    self.state = self.HALF_OPEN
                    self.successes = 0
                    return True
                return False
                
            else:  # HALF_OPEN
                return True
                
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try resetting the circuit."""
        if not self.last_failure_time:
            return True
            
        elapsed = datetime.now() - self.last_failure_time
        return elapsed.total_seconds() >= self.reset_timeout
        
    def get_state(self) -> Dict[str, Any]:
        """Get current state of the circuit breaker."""
        with self.lock:
            return {
                'name': self.name,
                'state': self.state,
                'failures': self.failures,
                'successes': self.successes,
                'last_failure': self.last_failure_time.isoformat() 
                    if self.last_failure_time else None
            }