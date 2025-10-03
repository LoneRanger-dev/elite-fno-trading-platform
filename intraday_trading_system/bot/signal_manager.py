"""
Signal Manager
Manages trading signals, stores them in database, and tracks performance
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import asdict

# Local imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config, logger

class SignalManager:
    """Manages trading signals and performance tracking"""
    
    def __init__(self):
        self.logger = logger
        self.config = config
        self.db_path = os.path.join(config.DATA_DIR, 'trading_signals.db')
        self._init_database()
        self.logger.info("Signal Manager initialized")
    
    def _init_database(self):
        """Initialize SQLite database for signal storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create signals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    instrument TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    target_price REAL NOT NULL,
                    stop_loss REAL NOT NULL,
                    confidence REAL NOT NULL,
                    setup_description TEXT,
                    technical_indicators TEXT,
                    risk_reward_ratio REAL NOT NULL,
                    status TEXT DEFAULT 'ACTIVE',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create performance tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signal_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_id INTEGER NOT NULL,
                    exit_price REAL,
                    exit_time TEXT,
                    pnl_points REAL,
                    pnl_percent REAL,
                    outcome TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (signal_id) REFERENCES signals (id)
                )
            ''')
            
            # Create daily stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE NOT NULL,
                    total_signals INTEGER DEFAULT 0,
                    winning_signals INTEGER DEFAULT 0,
                    losing_signals INTEGER DEFAULT 0,
                    total_pnl REAL DEFAULT 0,
                    win_rate REAL DEFAULT 0,
                    avg_win REAL DEFAULT 0,
                    avg_loss REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
    
    def save_signal(self, signal) -> Optional[int]:
        """Save a trading signal to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert technical indicators to JSON string
            indicators_json = json.dumps(signal.technical_indicators)
            
            cursor.execute('''
                INSERT INTO signals (
                    timestamp, instrument, signal_type, entry_price,
                    target_price, stop_loss, confidence, setup_description,
                    technical_indicators, risk_reward_ratio
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.timestamp,
                signal.instrument,
                signal.signal_type,
                signal.entry_price,
                signal.target_price,
                signal.stop_loss,
                signal.confidence,
                signal.setup_description,
                indicators_json,
                signal.risk_reward_ratio
            ))
            
            signal_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info(f"Signal saved with ID: {signal_id}")
            return signal_id
            
        except Exception as e:
            self.logger.error(f"Error saving signal: {str(e)}")
            return None
    
    def get_signals(self, limit: int = 50, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get trading signals from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT * FROM signals'
            params = []
            
            if status:
                query += ' WHERE status = ?'
                params.append(status)
            
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            columns = [description[0] for description in cursor.description]
            signals = []
            
            for row in rows:
                signal = dict(zip(columns, row))
                # Parse technical indicators JSON
                if signal['technical_indicators']:
                    signal['technical_indicators'] = json.loads(signal['technical_indicators'])
                signals.append(signal)
            
            conn.close()
            return signals
            
        except Exception as e:
            self.logger.error(f"Error getting signals: {str(e)}")
            return []
    
    def update_signal_status(self, signal_id: int, status: str, notes: Optional[str] = None) -> bool:
        """Update signal status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE signals 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (status, signal_id))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Signal {signal_id} status updated to {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating signal status: {str(e)}")
            return False
    
    def record_signal_performance(self, signal_id: int, exit_price: float, 
                                 outcome: str, notes: Optional[str] = None) -> bool:
        """Record signal performance when closed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get signal details
            cursor.execute('SELECT * FROM signals WHERE id = ?', (signal_id,))
            signal = cursor.fetchone()
            
            if not signal:
                self.logger.error(f"Signal {signal_id} not found")
                return False
            
            # Calculate P&L
            entry_price = signal[4]  # entry_price column
            signal_type = signal[3]  # signal_type column
            
            if signal_type == 'BUY':
                pnl_points = exit_price - entry_price
            else:  # SELL
                pnl_points = entry_price - exit_price
            
            pnl_percent = (pnl_points / entry_price) * 100
            
            # Record performance
            cursor.execute('''
                INSERT INTO signal_performance (
                    signal_id, exit_price, exit_time, pnl_points,
                    pnl_percent, outcome, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal_id,
                exit_price,
                datetime.now().isoformat(),
                pnl_points,
                pnl_percent,
                outcome,
                notes
            ))
            
            # Update signal status
            cursor.execute('''
                UPDATE signals 
                SET status = 'CLOSED', updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (signal_id,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Performance recorded for signal {signal_id}: {outcome}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording performance: {str(e)}")
            return False
    
    def get_daily_stats(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get daily trading statistics"""
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get signals for the date
            cursor.execute('''
                SELECT s.*, p.pnl_percent, p.outcome
                FROM signals s
                LEFT JOIN signal_performance p ON s.id = p.signal_id
                WHERE DATE(s.created_at) = ?
            ''', (date,))
            
            signals = cursor.fetchall()
            
            stats = {
                'date': date,
                'total_signals': len(signals),
                'winning_signals': 0,
                'losing_signals': 0,
                'total_pnl': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'best_signal': None,
                'worst_signal': None
            }
            
            if signals:
                wins = []
                losses = []
                pnl_values = []
                
                for signal in signals:
                    pnl_percent = signal[-2]  # pnl_percent from performance table
                    outcome = signal[-1]      # outcome from performance table
                    
                    if pnl_percent is not None:
                        pnl_values.append(pnl_percent)
                        
                        if outcome == 'WIN':
                            wins.append(pnl_percent)
                            stats['winning_signals'] += 1
                        elif outcome == 'LOSS':
                            losses.append(pnl_percent)
                            stats['losing_signals'] += 1
                
                if pnl_values:
                    stats['total_pnl'] = sum(pnl_values)
                    stats['best_signal'] = max(pnl_values)
                    stats['worst_signal'] = min(pnl_values)
                
                if wins:
                    stats['avg_win'] = sum(wins) / len(wins)
                
                if losses:
                    stats['avg_loss'] = sum(losses) / len(losses)
                
                total_closed = stats['winning_signals'] + stats['losing_signals']
                if total_closed > 0:
                    stats['win_rate'] = (stats['winning_signals'] / total_closed) * 100
            
            conn.close()
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting daily stats: {str(e)}")
            return {'error': str(e)}
    
    def get_performance_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get performance summary for specified number of days"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_signals,
                    COUNT(CASE WHEN p.outcome = 'WIN' THEN 1 END) as wins,
                    COUNT(CASE WHEN p.outcome = 'LOSS' THEN 1 END) as losses,
                    AVG(CASE WHEN p.outcome = 'WIN' THEN p.pnl_percent END) as avg_win,
                    AVG(CASE WHEN p.outcome = 'LOSS' THEN p.pnl_percent END) as avg_loss,
                    SUM(p.pnl_percent) as total_pnl,
                    MAX(p.pnl_percent) as best_trade,
                    MIN(p.pnl_percent) as worst_trade
                FROM signals s
                LEFT JOIN signal_performance p ON s.id = p.signal_id
                WHERE DATE(s.created_at) >= ?
            ''', (start_date,))
            
            result = cursor.fetchone()
            
            summary = {
                'period_days': days,
                'total_signals': result[0] or 0,
                'winning_trades': result[1] or 0,
                'losing_trades': result[2] or 0,
                'win_rate': ((result[1] or 0) / max(1, (result[1] or 0) + (result[2] or 0))) * 100,
                'avg_win': result[3] or 0,
                'avg_loss': result[4] or 0,
                'total_pnl': result[5] or 0,
                'best_trade': result[6] or 0,
                'worst_trade': result[7] or 0,
                'profit_factor': abs((result[3] or 0) / (result[4] or -1)) if result[4] and result[4] < 0 else 0
            }
            
            conn.close()
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {str(e)}")
            return {'error': str(e)}
    
    def cleanup_old_signals(self, days: int = 90) -> int:
        """Clean up signals older than specified days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM signal_performance 
                WHERE signal_id IN (
                    SELECT id FROM signals WHERE DATE(created_at) < ?
                )
            ''', (cutoff_date,))
            
            cursor.execute('''
                DELETE FROM signals WHERE DATE(created_at) < ?
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            self.logger.info(f"Cleaned up {deleted_count} old signals")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up signals: {str(e)}")
            return 0
    
    def test_database(self) -> bool:
        """Test database connectivity and operations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM signals')
            count = cursor.fetchone()[0]
            conn.close()
            
            self.logger.info(f"Database test successful: {count} signals in database")
            return True
            
        except Exception as e:
            self.logger.error(f"Database test failed: {str(e)}")
            return False

# Test function
def test_signal_manager():
    """Test signal manager functionality"""
    manager = SignalManager()
    
    print("Testing signal manager...")
    success = manager.test_database()
    print(f"Database test: {'✅ Success' if success else '❌ Failed'}")
    
    # Get recent signals
    signals = manager.get_signals(limit=5)
    print(f"Recent signals: {len(signals)}")
    
    # Get daily stats
    stats = manager.get_daily_stats()
    print(f"Today's stats: {stats.get('total_signals', 0)} signals")

if __name__ == "__main__":
    test_signal_manager()