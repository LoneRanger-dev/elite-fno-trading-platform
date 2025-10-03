"""
Dashboard backend for real-time trading signal monitoring
"""
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardManager:
    def __init__(self, signal_engine=None):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app)
        self.signal_engine = signal_engine
        self.signals_today = []
        self.last_update = datetime.now()
        
        # Register routes
        self.register_routes()
        
        # Start background tasks
        self.start_background_tasks()
        
    def register_routes(self):
        @self.app.route('/dashboard')
        def dashboard():
            return render_template('trading_dashboard.html')
            
        @self.socketio.on('connect', namespace='/ws/dashboard')
        def handle_connect():
            logger.info("Client connected to dashboard")
            self.send_initial_data()
            
    def send_initial_data(self):
        """Send initial dashboard data to new connections"""
        data = self.get_dashboard_data()
        emit('message', json.dumps(data), namespace='/ws/dashboard')
        
    def get_dashboard_data(self) -> Dict:
        """Get current dashboard data"""
        # Get paper trading metrics
        if self.signal_engine:
            paper_metrics = self.signal_engine.paper_trader.get_performance_metrics()
        else:
            paper_metrics = {}
            
        return {
            'stats': self.get_stats(),
            'system_health': self.get_system_health(),
            'performance_data': self.get_performance_data(),
            'strategy_data': self.get_strategy_data(),
            'recent_signals': self.get_recent_signals(),
            'paper_trading': paper_metrics,
            'system_active': True
        }
        
    def get_stats(self) -> Dict:
        """Calculate current trading statistics"""
        if not self.signals_today:
            return {
                'signals_today': 0,
                'success_rate': 0,
                'avg_profit': 0
            }
            
        success_count = sum(1 for s in self.signals_today if s['status'] == 'SUCCESS')
        total_profit = sum(s['profit'] for s in self.signals_today if s['status'] == 'SUCCESS')
        
        return {
            'signals_today': len(self.signals_today),
            'success_rate': round(success_count / len(self.signals_today) * 100, 2),
            'avg_profit': round(total_profit / max(success_count, 1), 2)
        }
        
    def get_system_health(self) -> Dict:
        """Get current system health status"""
        if not self.signal_engine:
            return {'status': 'Unknown'}
            
        return self.signal_engine.monitor.get_health_status()
        
    def get_performance_data(self) -> Dict:
        """Get signal performance data for charts"""
        if not self.signals_today:
            return {
                'labels': [],
                'data': []
            }
            
        signals = sorted(self.signals_today, key=lambda x: x['timestamp'])
        return {
            'labels': [s['timestamp'].strftime('%H:%M') for s in signals],
            'data': [s.get('profit', 0) for s in signals]
        }
        
    def get_strategy_data(self) -> Dict:
        """Get strategy distribution data"""
        if not self.signals_today:
            return {
                'labels': [],
                'data': []
            }
            
        strategy_counts = {}
        for signal in self.signals_today:
            strategy = signal['signal_type']
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            
        return {
            'labels': list(strategy_counts.keys()),
            'data': list(strategy_counts.values())
        }
        
    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """Get most recent signals"""
        return sorted(
            self.signals_today,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]
        
    def add_signal(self, signal: Dict):
        """Add new signal and update dashboard"""
        self.signals_today.append(signal)
        
        # Remove signals older than 24 hours
        cutoff = datetime.now() - timedelta(days=1)
        self.signals_today = [
            s for s in self.signals_today
            if s['timestamp'] > cutoff
        ]
        
        # Update dashboard
        self.broadcast_update()
        
    def broadcast_update(self):
        """Send dashboard update to all connected clients"""
        if datetime.now() - self.last_update < timedelta(seconds=1):
            return  # Throttle updates
            
        data = self.get_dashboard_data()
        self.socketio.emit(
            'message',
            json.dumps(data),
            namespace='/ws/dashboard'
        )
        self.last_update = datetime.now()
        
    def start_background_tasks(self):
        """Start background monitoring tasks"""
        def update_loop():
            while True:
                try:
                    self.broadcast_update()
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error in update loop: {e}", exc_info=True)
                    
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        
    def run(self, host: str = '0.0.0.0', port: int = 5000):
        """Run the dashboard server"""
        self.socketio.run(self.app, host=host, port=port)