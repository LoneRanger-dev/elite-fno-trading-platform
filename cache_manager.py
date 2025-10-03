"""
Cache Manager
Handles caching and persistence of market data and signals
"""

import sqlite3
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from contextlib import contextmanager
import os
import threading
import queue

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, db_path: str = "data/cache.db"):
        self.db_path = db_path
        self.memory_cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = time.time()
        self.cache_lock = threading.Lock()
        self.write_queue = queue.Queue()
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_db()
        
        # Start background writer thread
        self.writer_thread = threading.Thread(target=self._background_writer)
        self.writer_thread.daemon = True
        self.writer_thread.start()
        
    def _init_db(self):
        """Initialize SQLite database with required tables"""
        with self._get_db() as conn:
            cursor = conn.cursor()
            
            # Market data cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_data_cache (
                    key TEXT PRIMARY KEY,
                    data TEXT,
                    timestamp INTEGER,
                    expiry INTEGER
                )
            """)
            
            # Signal cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signal_cache (
                    signal_id TEXT PRIMARY KEY,
                    signal_data TEXT,
                    timestamp INTEGER,
                    status TEXT
                )
            """)
            
            # Create indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data_cache(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_signal_timestamp ON signal_cache(timestamp)")
            
            conn.commit()
            
    @contextmanager
    def _get_db(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            yield conn
        finally:
            if conn:
                conn.close()
                
    def _background_writer(self):
        """Background thread for asynchronous database writes"""
        while True:
            try:
                # Get next write operation from queue
                operation = self.write_queue.get()
                if operation is None:
                    break
                    
                table, key, data = operation
                
                with self._get_db() as conn:
                    cursor = conn.cursor()
                    timestamp = int(time.time())
                    
                    if table == 'market_data_cache':
                        cursor.execute("""
                            INSERT OR REPLACE INTO market_data_cache 
                            (key, data, timestamp, expiry) VALUES (?, ?, ?, ?)
                        """, (key, json.dumps(data), timestamp, timestamp + self.cache_ttl))
                    elif table == 'signal_cache':
                        cursor.execute("""
                            INSERT OR REPLACE INTO signal_cache 
                            (signal_id, signal_data, timestamp, status) VALUES (?, ?, ?, ?)
                        """, (key, json.dumps(data), timestamp, data.get('status', 'ACTIVE')))
                        
                    conn.commit()
                    
            except Exception as e:
                logger.error(f"Background writer error: {e}")
                time.sleep(1)
                
    def cache_market_data(self, key: str, data: Any):
        """Cache market data both in memory and database"""
        try:
            timestamp = time.time()
            
            # Update memory cache
            with self.cache_lock:
                self.memory_cache[key] = {
                    'data': data,
                    'timestamp': timestamp,
                    'expiry': timestamp + self.cache_ttl
                }
            
            # Queue database write
            self.write_queue.put(('market_data_cache', key, data))
            
        except Exception as e:
            logger.error(f"Error caching market data: {e}")
            
    def get_market_data(self, key: str) -> Optional[Any]:
        """Get market data from cache"""
        try:
            # Check memory cache first
            with self.cache_lock:
                if key in self.memory_cache:
                    cache_entry = self.memory_cache[key]
                    if time.time() < cache_entry['expiry']:
                        return cache_entry['data']
                    else:
                        del self.memory_cache[key]
            
            # Check database cache
            with self._get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT data, expiry FROM market_data_cache 
                    WHERE key = ? AND expiry > ?
                """, (key, int(time.time())))
                
                row = cursor.fetchone()
                if row:
                    data = json.loads(row[0])
                    # Update memory cache
                    with self.cache_lock:
                        self.memory_cache[key] = {
                            'data': data,
                            'timestamp': time.time(),
                            'expiry': row[1]
                        }
                    return data
                    
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving market data: {e}")
            return None
            
    def cache_signal(self, signal: Dict):
        """Cache signal data"""
        try:
            signal_id = signal['id']
            
            # Queue database write
            self.write_queue.put(('signal_cache', signal_id, signal))
            
        except Exception as e:
            logger.error(f"Error caching signal: {e}")
            
    def get_signal(self, signal_id: str) -> Optional[Dict]:
        """Get signal from cache"""
        try:
            with self._get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT signal_data FROM signal_cache 
                    WHERE signal_id = ?
                """, (signal_id,))
                
                row = cursor.fetchone()
                return json.loads(row[0]) if row else None
                
        except Exception as e:
            logger.error(f"Error retrieving signal: {e}")
            return None
            
    def get_recent_signals(self, limit: int = 100) -> List[Dict]:
        """Get recent signals from cache"""
        try:
            with self._get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT signal_data FROM signal_cache 
                    ORDER BY timestamp DESC LIMIT ?
                """, (limit,))
                
                return [json.loads(row[0]) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error retrieving recent signals: {e}")
            return []
            
    def cleanup(self):
        """Clean up expired cache entries"""
        try:
            current_time = int(time.time())
            
            # Clean memory cache
            with self.cache_lock:
                expired_keys = [k for k, v in self.memory_cache.items() 
                              if current_time > v['expiry']]
                for k in expired_keys:
                    del self.memory_cache[k]
            
            # Clean database cache
            with self._get_db() as conn:
                cursor = conn.cursor()
                
                # Clean market data cache
                cursor.execute("""
                    DELETE FROM market_data_cache 
                    WHERE expiry < ?
                """, (current_time,))
                
                # Clean old signals (keep last 7 days)
                week_ago = current_time - (7 * 24 * 3600)
                cursor.execute("""
                    DELETE FROM signal_cache 
                    WHERE timestamp < ?
                """, (week_ago,))
                
                conn.commit()
                
            self.last_cleanup = current_time
            
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
            
    def periodic_cleanup(self):
        """Perform periodic cleanup if needed"""
        if time.time() - self.last_cleanup > self.cleanup_interval:
            self.cleanup()