"""
Trading Bot Web Dashboard
Flask web application for monitoring signals, performance, and controlling the bot
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
from datetime import datetime, timedelta
import threading
import asyncio
from typing import Dict, List, Any

# Local imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config, logger
from bot.signal_manager import SignalManager
from bot.market_data import MarketDataManager
from bot.telegram_bot import TelegramBot

app = Flask(__name__)
app.config['SECRET_KEY'] = config.FLASK_SECRET_KEY
app.config['DEBUG'] = config.FLASK_DEBUG

# Enable CORS for API access
CORS(app, origins=["*"])

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize managers
signal_manager = SignalManager()
market_data_manager = MarketDataManager()
telegram_bot = TelegramBot()

# Global bot status
bot_status = {
    'running': False,
    'last_signal': None,
    'signals_today': 0,
    'uptime': datetime.now().isoformat()
}

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        # Get today's stats
        today_stats = signal_manager.get_daily_stats()
        
        # Get recent signals
        recent_signals = signal_manager.get_signals(limit=10)
        
        # Get performance summary
        performance = signal_manager.get_performance_summary(days=30)
        
        # Get current market data
        market_data = {}
        for instrument in config.INSTRUMENTS:
            data = market_data_manager.get_live_data(instrument)
            if data:
                market_data[instrument] = {
                    'price': data.get('current_price', 0),
                    'change': data.get('change_percent', 0)
                }
        
        return render_template('dashboard.html',
                             stats=today_stats,
                             signals=recent_signals,
                             performance=performance,
                             market_data=market_data,
                             bot_status=bot_status)
        
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/signals')
def signals_page():
    """Signals history page"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = 20
        offset = (page - 1) * limit
        
        signals = signal_manager.get_signals(limit=limit)
        
        return render_template('signals.html',
                             signals=signals,
                             page=page)
        
    except Exception as e:
        logger.error(f"Error loading signals page: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/performance')
def performance_page():
    """Performance analytics page"""
    try:
        # Get performance data for different periods
        performance_7d = signal_manager.get_performance_summary(days=7)
        performance_30d = signal_manager.get_performance_summary(days=30)
        performance_90d = signal_manager.get_performance_summary(days=90)
        
        return render_template('performance.html',
                             perf_7d=performance_7d,
                             perf_30d=performance_30d,
                             perf_90d=performance_90d)
        
    except Exception as e:
        logger.error(f"Error loading performance page: {str(e)}")
        return render_template('error.html', error=str(e))

@app.route('/settings')
def settings_page():
    """Settings and configuration page"""
    try:
        config_status = config.validate_config()
        
        return render_template('settings.html',
                             config_status=config_status)
        
    except Exception as e:
        logger.error(f"Error loading settings page: {str(e)}")
        return render_template('error.html', error=str(e))

# API Routes
@app.route('/api/status')
def api_status():
    """Get bot status"""
    return jsonify(bot_status)

@app.route('/api/signals')
def api_signals():
    """Get signals via API"""
    try:
        limit = request.args.get('limit', 50, type=int)
        status = request.args.get('status', None)
        
        signals = signal_manager.get_signals(limit=limit, status=status)
        
        return jsonify({
            'success': True,
            'signals': signals,
            'count': len(signals)
        })
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market-data')
def api_market_data():
    """Get current market data"""
    try:
        market_data = {}
        
        for instrument in config.INSTRUMENTS:
            data = market_data_manager.get_live_data(instrument)
            if data:
                market_data[instrument] = {
                    'current_price': data.get('current_price', 0),
                    'change': data.get('change', 0),
                    'change_percent': data.get('change_percent', 0),
                    'volume': data.get('volume', 0),
                    'timestamp': data.get('timestamp', '')
                }
        
        return jsonify({
            'success': True,
            'data': market_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Market data API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/performance')
def api_performance():
    """Get performance data"""
    try:
        days = request.args.get('days', 30, type=int)
        performance = signal_manager.get_performance_summary(days=days)
        
        return jsonify({
            'success': True,
            'performance': performance
        })
        
    except Exception as e:
        logger.error(f"Performance API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/send-test-message', methods=['POST'])
def api_send_test_message():
    """Send test message to Telegram"""
    try:
        async def send_test():
            success = await telegram_bot.send_message(
                f"🧪 Test message from web dashboard - {datetime.now().strftime('%H:%M:%S')}"
            )
            return success
        
        success = asyncio.run(send_test())
        
        return jsonify({
            'success': success,
            'message': 'Test message sent' if success else 'Failed to send message'
        })
        
    except Exception as e:
        logger.error(f"Test message API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bot/start', methods=['POST'])
def api_start_bot():
    """Start the trading bot"""
    try:
        # This would integrate with the main bot
        bot_status['running'] = True
        bot_status['uptime'] = datetime.now().isoformat()
        
        # Emit status update to connected clients
        socketio.emit('bot_status', bot_status)
        
        return jsonify({
            'success': True,
            'message': 'Bot started successfully'
        })
        
    except Exception as e:
        logger.error(f"Start bot API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bot/stop', methods=['POST'])
def api_stop_bot():
    """Stop the trading bot"""
    try:
        bot_status['running'] = False
        
        # Emit status update to connected clients
        socketio.emit('bot_status', bot_status)
        
        return jsonify({
            'success': True,
            'message': 'Bot stopped successfully'
        })
        
    except Exception as e:
        logger.error(f"Stop bot API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected to WebSocket')
    emit('bot_status', bot_status)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected from WebSocket')

@socketio.on('request_update')
def handle_request_update():
    """Handle client request for updates"""
    try:
        # Send current market data
        market_data = {}
        for instrument in config.INSTRUMENTS:
            data = market_data_manager.get_live_data(instrument)
            if data:
                market_data[instrument] = {
                    'price': data.get('current_price', 0),
                    'change': data.get('change_percent', 0)
                }
        
        emit('market_update', market_data)
        
        # Send recent signals
        recent_signals = signal_manager.get_signals(limit=5)
        emit('signals_update', recent_signals)
        
    except Exception as e:
        logger.error(f"WebSocket update error: {str(e)}")
        emit('error', {'message': str(e)})

def broadcast_new_signal(signal_data):
    """Broadcast new signal to all connected clients"""
    try:
        socketio.emit('new_signal', signal_data)
        bot_status['last_signal'] = signal_data.get('timestamp')
        bot_status['signals_today'] += 1
        socketio.emit('bot_status', bot_status)
        
    except Exception as e:
        logger.error(f"Error broadcasting signal: {str(e)}")

def start_background_tasks():
    """Start background tasks for real-time updates"""
    def market_data_updater():
        while True:
            try:
                if bot_status['running']:
                    # Update market data every 30 seconds
                    market_data = {}
                    for instrument in config.INSTRUMENTS:
                        data = market_data_manager.get_live_data(instrument)
                        if data:
                            market_data[instrument] = {
                                'price': data.get('current_price', 0),
                                'change': data.get('change_percent', 0)
                            }
                    
                    socketio.emit('market_update', market_data)
                
                socketio.sleep(30)  # Wait 30 seconds
                
            except Exception as e:
                logger.error(f"Market data updater error: {str(e)}")
                socketio.sleep(60)
    
    # Start background thread
    background_thread = threading.Thread(target=market_data_updater, daemon=True)
    background_thread.start()

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error="Page not found", 
                         error_code=404), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', 
                         error="Internal server error", 
                         error_code=500), 500

if __name__ == '__main__':
    logger.info("Starting Trading Bot Web Dashboard...")
    
    # Start background tasks
    start_background_tasks()
    
    # Run the Flask app with SocketIO
    socketio.run(app, 
                host=config.FLASK_HOST, 
                port=config.FLASK_PORT,
                debug=config.FLASK_DEBUG,
                allow_unsafe_werkzeug=True)