"""
Enhanced Web Application with Premium Features
Premium subscription management, user authentication, and payment integration
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
from datetime import datetime, timedelta
import threading
import asyncio
from typing import Dict, List, Any, Optional
from functools import wraps
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config, logger
from bot.signal_manager import SignalManager
from bot.market_data import MarketDataManager
from bot.telegram_bot import TelegramBot
from models.user import UserManager, UserRole, SubscriptionStatus
from services.premium_signals import PremiumSignalManager
from services.payment import PaymentManager
from services.multi_broker import enhanced_trading_system
from services.scheduler import initialize_scheduler, scheduled_alert_system

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.FLASK_SECRET_KEY
app.config['DEBUG'] = config.FLASK_DEBUG

# Enable CORS
CORS(app, origins=["*"])

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize managers
signal_manager = SignalManager()
market_data_manager = MarketDataManager()
telegram_bot = TelegramBot()

# Initialize premium features
user_manager = UserManager(
    db_path=os.path.join(config.DATA_DIR, 'users.db'),
    secret_key=config.FLASK_SECRET_KEY
)
premium_signal_manager = PremiumSignalManager(user_manager)

# Initialize payment system (you'll need to add these to your .env file)
RAZORPAY_KEY = os.getenv('RAZORPAY_KEY_ID', 'your_razorpay_key')
RAZORPAY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', 'your_razorpay_secret')
payment_manager = PaymentManager(RAZORPAY_KEY, RAZORPAY_SECRET, user_manager)

# Global bot status
bot_status = {
    'running': False,
    'last_signal': None,
    'signals_today': 0,
    'uptime': datetime.now().isoformat()
}

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def premium_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user_id = session['user_id']
        if not user_manager.has_premium_access(user_id):
            flash('Premium subscription required for this feature.', 'warning')
            return redirect(url_for('subscribe'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = user_manager.get_user_by_id(session['user_id'])
        if not user or user.role != UserRole.ADMIN:
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        result = user_manager.authenticate_user(username, password)
        
        if result['success']:
            session['user_id'] = result['user']['id']
            session['username'] = result['user']['username']
            session['role'] = result['user']['role']
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result['message'], 'error')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        result = user_manager.create_user(username, email, phone, password)
        
        if result['success']:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(result['message'], 'error')
    
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

# Main Routes
@app.route('/')
def index():
    """Main landing page"""
    user_id = session.get('user_id')
    
    # Get recent signals (limited for non-premium users)
    recent_signals = signal_manager.get_recent_signals(limit=5)
    signal_data = premium_signal_manager.filter_signals_for_user(recent_signals, user_id)
    
    # Get market data
    market_data = market_data_manager.get_market_overview()
    
    # Get subscription benefits
    benefits = premium_signal_manager.get_subscription_benefits()
    
    return render_template('index.html', 
                         signal_data=signal_data,
                         market_data=market_data,
                         benefits=benefits,
                         user_id=user_id)

@app.route('/dashboard')
@login_required
def dashboard():
    """Enhanced premium dashboard with modern UI"""
    try:
        user_id = session['user_id']
        user = user_manager.get_user_by_id(user_id)
        subscription_status = user.subscription_status.value if user.subscription_status else 'free'
        
        # Get market status and data
        market_open = enhanced_trading_system.is_market_open()
        market_scan = enhanced_trading_system.run_market_scan()
        
        # Get trading statistics
        stats = {
            'signals_today': len(market_scan.get('breakouts', [])),
            'accuracy': 87,
            'active_positions': 3,
            'profit_today': 2.8
        }
        
        # Get market indicators
        indicators = {
            'nifty_value': 19850,
            'nifty_trend': 'bullish',
            'banknifty_value': 44750,
            'banknifty_trend': 'bullish',
            'rsi_value': 55.2,
            'macd_value': 15.8,
            'macd_signal': 'positive'
        }
        
        # Get latest signal for premium users
        latest_signal = None
        if subscription_status == 'active' and market_scan.get('breakouts'):
            latest_signal = market_scan['breakouts'][0]
            latest_signal['time'] = datetime.now().strftime('%I:%M %p')
        
        # Get market news
        market_news = enhanced_trading_system.get_market_news()
        
        return render_template('dashboard_modern.html', 
                             user=user, 
                             stats=stats,
                             indicators=indicators,
                             latest_signal=latest_signal,
                             market_news=market_news,
                             market_open=market_open,
                             subscription_status=subscription_status,
                             **stats, **indicators)
                             
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        flash('Error loading dashboard', 'danger')
        return redirect(url_for('index'))

@app.route('/signals')
@login_required
def signals():
    """Enhanced live signals page"""
    try:
        user_id = session.get('user_id')
        
        # Check premium access
        if not user_manager.has_premium_access(user_id):
            flash('Premium subscription required for live signals', 'warning')
            return redirect(url_for('subscribe'))
        
        # Get market scan with enhanced analysis
        market_scan = enhanced_trading_system.run_market_scan()
        signals = market_scan.get('breakouts', [])
        
        # Get signal history
        signal_history = signal_manager.get_recent_signals(limit=20)
        
        return render_template('signals.html', 
                             signals=signals,
                             signal_history=signal_history,
                             market_status=market_scan.get('status'),
                             market_open=enhanced_trading_system.is_market_open())
                             
    except Exception as e:
        logger.error(f"Signals error: {e}")
        flash('Error loading signals', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('signals.html',
                         signal_data=signal_data,
                         access_message=access_message,
                         user_id=user_id)

@app.route('/subscribe')
def subscribe():
    """Subscription plans page"""
    plans = user_manager.get_subscription_plans()
    benefits = premium_signal_manager.get_subscription_benefits()
    
    user_id = session.get('user_id')
    user = user_manager.get_user_by_id(user_id) if user_id else None
    
    return render_template('subscription/plans.html',
                         plans=plans,
                         benefits=benefits,
                         user=user)

@app.route('/payment/<int:plan_id>')
@login_required
def payment(plan_id):
    """Payment page for subscription"""
    user_id = session['user_id']
    
    # Create payment order
    order_result = payment_manager.create_subscription_order(user_id, plan_id)
    
    if not order_result['success']:
        flash(order_result['message'], 'error')
        return redirect(url_for('subscribe'))
    
    return render_template('subscription/payment.html',
                         order=order_result,
                         razorpay_key=RAZORPAY_KEY)

@app.route('/account')
@login_required
def account():
    """User account management"""
    user_id = session['user_id']
    user = user_manager.get_user_by_id(user_id)
    
    # Get payment history
    payment_history = payment_manager.get_payment_history(user_id)
    
    # Get subscription status
    access_info = premium_signal_manager.can_access_premium_signals(user_id)
    
    return render_template('account/profile.html',
                         user=user,
                         payment_history=payment_history,
                         access_info=access_info)

# Admin Routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    # Get user statistics
    user_stats = user_manager.get_user_stats()
    
    # Get revenue statistics
    revenue_stats = payment_manager.get_revenue_stats()
    
    # Get system status
    system_stats = {
        'signals_today': len(signal_manager.get_signals_by_date(datetime.now().date())),
        'bot_uptime': bot_status['uptime'],
        'bot_running': bot_status['running']
    }
    
    return render_template('admin/dashboard.html',
                         user_stats=user_stats,
                         revenue_stats=revenue_stats,
                         system_stats=system_stats)

@app.route('/admin/users')
@admin_required
def admin_users():
    """Admin user management"""
    # This would be implemented to show all users
    return render_template('admin/users.html')

# API Routes
@app.route('/api/signals')
def api_signals():
    """API endpoint for signals (with premium filtering)"""
    user_id = session.get('user_id')
    
    limit = int(request.args.get('limit', 20))
    recent_signals = signal_manager.get_recent_signals(limit=limit)
    
    # Filter signals based on user subscription
    signal_data = premium_signal_manager.filter_signals_for_user(recent_signals, user_id)
    
    return jsonify(signal_data)

@app.route('/api/payment/success', methods=['POST'])
def payment_success():
    """Handle successful payment"""
    payment_data = request.json
    
    result = payment_manager.process_successful_payment(payment_data)
    
    if result['success']:
        # Update session if it's the current user
        if session.get('user_id') == result['user_id']:
            session['role'] = 'premium'
        
        # Send real-time update
        socketio.emit('subscription_activated', {
            'user_id': result['user_id'],
            'plan_id': result['plan_id']
        })
    
    return jsonify(result)

@app.route('/api/payment/webhook', methods=['POST'])
def payment_webhook():
    """Handle Razorpay webhooks"""
    webhook_signature = request.headers.get('X-Razorpay-Signature')
    webhook_body = request.get_data(as_text=True)
    
    result = payment_manager.handle_webhook(webhook_body, webhook_signature)
    
    return jsonify(result)

@app.route('/api/subscription/cancel', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel user subscription"""
    user_id = session['user_id']
    
    result = payment_manager.cancel_subscription(user_id)
    
    return jsonify(result)

# Enhanced Routes
@app.route('/analysis')
@login_required
def analysis():
    """Market analysis page"""
    try:
        # Get comprehensive market analysis
        market_scan = enhanced_trading_system.run_market_scan()
        news = enhanced_trading_system.get_market_news()
        
        analysis_data = {
            'breakouts': market_scan.get('breakouts', []),
            'news': news,
            'market_status': market_scan.get('status'),
            'alerts': market_scan.get('alerts', {})
        }
        
        return render_template('analysis.html', **analysis_data)
                             
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        flash('Error loading analysis', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/api/bot_command', methods=['POST'])
@login_required
def bot_command():
    """Handle bot command requests"""
    try:
        command = request.json.get('command')
        response = {}
        
        if command == 'market_status':
            market_scan = enhanced_trading_system.run_market_scan()
            response = {
                'status': 'success',
                'message': f"Market Status: {'OPEN' if enhanced_trading_system.is_market_open() else 'CLOSED'}",
                'data': market_scan
            }
        elif command == 'latest_signals':
            market_scan = enhanced_trading_system.run_market_scan()
            signals = market_scan.get('breakouts', [])
            response = {
                'status': 'success',
                'message': f"Found {len(signals)} active signals",
                'data': signals
            }
        elif command == 'news_update':
            news = enhanced_trading_system.get_market_news()
            response = {
                'status': 'success',
                'message': f"Latest {len(news)} news items",
                'data': news
            }
        else:
            response = {
                'status': 'error',
                'message': 'Unknown command'
            }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Bot command error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

# Socket Events
@socketio.on('connect')
def on_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    
    # Send current bot status
    emit('bot_status', bot_status)

@socketio.on('disconnect')
def on_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

# Background task for real-time updates
def background_tasks():
    """Background tasks for real-time updates"""
    while True:
        try:
            # Update market data every 30 seconds
            market_data = market_data_manager.get_market_overview()
            socketio.emit('market_update', market_data)
            
            # Check for new signals
            new_signals = signal_manager.get_recent_signals(limit=1)
            if new_signals and new_signals[0].timestamp > datetime.now() - timedelta(minutes=1):
                socketio.emit('new_signal', {
                    'signal': new_signals[0].__dict__,
                    'timestamp': datetime.now().isoformat()
                })
            
            socketio.sleep(30)
            
        except Exception as e:
            logger.error(f"Background task error: {e}")
            socketio.sleep(60)

# Start background tasks
def start_background_tasks():
    """Start background tasks"""
    socketio.start_background_task(background_tasks)

# Initialize enhanced system
def init_enhanced_system():
    """Initialize enhanced trading system components"""
    try:
        # Initialize scheduler with Telegram credentials
        telegram_token = config.TELEGRAM_BOT_TOKEN
        premium_chat_id = config.TELEGRAM_CHAT_ID
        
        scheduler = initialize_scheduler(telegram_token, premium_chat_id)
        scheduler.start_scheduler()
        
        logger.info("✅ Enhanced trading system initialized")
        return True
        
    except Exception as e:
        logger.error(f"Enhanced system initialization error: {e}")
        return False

if __name__ == '__main__':
    try:
        logger.info("🚀 Starting Enhanced Premium Web Application...")
        
        # Initialize enhanced system
        init_enhanced_system()
        
        # Start background tasks
        start_background_tasks()
        
        # Run the application
        socketio.run(app, 
                    host=config.FLASK_HOST, 
                    port=config.FLASK_PORT, 
                    debug=config.FLASK_DEBUG)
                    
    except Exception as e:
        logger.error(f"Application startup error: {e}")
        raise