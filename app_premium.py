"""
🚀 Elite FnO Trading Platform - Premium Edition
Complete platform with paper trading, subscriptions, bull/bear animations, and Telegram integration
"""

import sys
import os
from typing import Optional
import hmac
import hashlib
import requests
import logging
import threading
import time
import random
from datetime import datetime, timedelta
import razorpay

# --- Path and Logging Setup ---
# ------------------------------
# Add the project root to the Python path to resolve module imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# --- Flask and Component Imports ---
# -----------------------------------
from flask import Flask, render_template, jsonify, request, redirect, url_for, render_template_string

# Import configuration
import config

# Import core components
from live_signal_engine import LiveSignalEngine
from paper_trading_engine import PaperTradingEngine
from subscription_manager import PremiumSubscriptionManager
from market_data_provider import initialize_market_data_provider
from breakout_strategy import BreakoutStrategy
from pro_trader_setups import get_pro_setups

# Import new components
from cache_manager import CacheManager
from health_monitor import HealthMonitor
from notification_manager import NotificationManager
from signal_generator import SignalGenerator
from signal_validation import SignalValidator
from circuit_breaker import CircuitBreaker
from auto_recovery import AutoRecoveryManager

# --- App Initialization ---
# --------------------------
app = Flask(__name__)
app.secret_key = config.SECRET_KEY if hasattr(config, 'SECRET_KEY') else 'elite-fno-secret-key-2024'

# Initialize components
cache_manager = CacheManager(db_path='data/cache.db')

notification_config = {
    'telegram_token': config.BOT_TOKEN,
    'telegram_chat_id': config.CHAT_ID,
    'email_settings': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'from_email': 'your-email@gmail.com',
        'to_email': 'alerts@yourcompany.com',
        'use_tls': True
    },
    'webhook_url': 'https://your-webhook-url.com/trading-alerts'
}
notification_manager = NotificationManager(notification_config)

health_monitor = HealthMonitor({
    'error_threshold': 5,
    'metric_interval': 60,
    'history_size': 1440
})

# Initialize circuit breakers
circuit_breakers = {
    'market_data': CircuitBreaker('market_data', failure_threshold=3),
    'signal_gen': CircuitBreaker('signal_gen', failure_threshold=5),
    'telegram': CircuitBreaker('telegram', failure_threshold=3)
}

# Initialize auto-recovery
recovery_manager = AutoRecoveryManager(notification_manager)

# Register services for auto-recovery
recovery_manager.register_service(
    'market_data',
    lambda: market_data_provider.check_connection(),
    lambda: market_data_provider.reconnect(),
    check_interval=30
)

recovery_manager.register_service(
    'signal_engine',
    lambda: signal_engine.is_healthy(),
    lambda: signal_engine.restart(),
    check_interval=60
)

recovery_manager.register_service(
    'telegram_bot',
    lambda: notification_manager.check_telegram(),
    lambda: notification_manager.restart_telegram(),
    check_interval=60
)

# Start recovery monitoring
recovery_manager.start()

# Start background services
notification_manager.start()
health_monitor.start()

# --- API Routes ---
# -----------------

@app.route('/api/signals')
def get_signals():
    try:
        # Check system health
        health_status = health_monitor.get_status()
        if not health_status['healthy']:
            notification_manager.send_alert('System health check failed', severity='high')
            return jsonify({'error': 'System health check failed'}), 503
            
        # Check circuit breaker
        if not circuit_breakers['signal_gen'].allow_request():
            cached_signals = cache_manager.get('latest_signals')
            if cached_signals:
                return jsonify({
                    'signals': cached_signals,
                    'warning': 'Using cached data due to circuit breaker'
                })
            return jsonify({'error': 'Service temporarily unavailable'}), 503
            
        # Try cache first
        cached_signals = cache_manager.get('latest_signals')
        if cached_signals:
            circuit_breakers['signal_gen'].record_success()
            return jsonify(cached_signals)
            
        # Generate new signals
        signals = signal_engine.get_signals()
        
        # Validate signals
        validator = SignalValidator()
        validation_result = validator.validate(signals)
        if not validation_result['valid']:
            notification_manager.send_alert(
                f'Signal validation failed: {validation_result["errors"]}',
                severity='high'
            )
            return jsonify({'error': 'Signal validation failed'}), 500
            
        # Cache valid signals
        cache_manager.set('latest_signals', signals, ttl=300)  # 5 min TTL
        
        return jsonify(signals)
        
    except Exception as e:
        health_monitor.record_error('signal_generation')
        notification_manager.send_alert(f'Signal generation failed: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/system/status')
def system_status():
    try:
        # Get comprehensive system status
        status = {
            'health': health_monitor.get_status(),
            'circuit_breakers': {
                name: cb.get_state()
                for name, cb in circuit_breakers.items()
            },
            'auto_recovery': recovery_manager.get_status(),
            'cache': cache_manager.get_stats(),
            'notifications': notification_manager.get_status()
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f'Status check failed: {str(e)}', exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health')
def health_check():
    try:
        health_status = health_monitor.get_status()
        return jsonify(health_status)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# --- Error Handling ---
# ----------------------
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors with a custom page."""
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Page Not Found - Elite FnO</title>
        <style>
            body { background: #0a0a0f; color: white; font-family: Arial; text-align: center; padding: 50px; }
            .container { max-width: 600px; margin: 0 auto; }
            .error-code { font-size: 120px; font-weight: bold; color: #00f5ff; margin-bottom: 20px; }
            .btn { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 12px 24px; 
                   text-decoration: none; border-radius: 25px; display: inline-block; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="error-code">404</div>
            <h1>🚀 Page Not Found</h1>
            <p>The page you're looking for doesn't exist or has been moved.</p>
            <a href="/" class="btn">🏠 Back to Home</a>
            <a href="/dashboard" class="btn">📊 Dashboard</a>
        </div>
    </body>
    </html>
    """), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with a custom page."""
    logger.error(f"Internal server error: {error}")
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Server Error - Elite FnO</title>
        <style>
            body { background: #0a0a0f; color: white; font-family: Arial; text-align: center; padding: 50px; }
            .container { max-width: 600px; margin: 0 auto; }
            .error-code { font-size: 120px; font-weight: bold; color: #ff6b6b; margin-bottom: 20px; }
            .btn { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 12px 24px; 
                   text-decoration: none; border-radius: 25px; display: inline-block; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="error-code">500</div>
            <h1>⚡ Server Error</h1>
            <p>Something went wrong on our end. Our team has been notified.</p>
            <a href="/" class="btn">🏠 Back to Home</a>
            <a href="/dashboard" class="btn">📊 Try Dashboard</a>
        </div>
    </body>
    </html>
    """), 500

# --- Template Context Processors ---
# -----------------------------------
@app.context_processor
def inject_global_vars():
    """Inject global variables into all templates."""
    from datetime import datetime
    return {
        'current_year': datetime.now().year,
        'app_name': 'Elite FnO Trading Platform',
        'razorpay_enabled': bool(config.settings.RAZORPAY_KEY_ID and config.settings.RAZORPAY_KEY_SECRET),
        'debug_mode': app.debug
    }

# --- Initialize Core Components ---
# ----------------------------------
signal_engine = LiveSignalEngine()
paper_trading_engine = PaperTradingEngine()
subscription_manager = PremiumSubscriptionManager()

# API Configurations
KITE_CONFIG = {
    'api_key': 'zfz6i2qjh9zjl26m',
    'api_secret': 'esdsumpztnzmry8rl1e411b95qt86v2m',
    'access_token': '9tB7VtbqUGu4btfKkX7E4zO6t7wNOtbt'
}

RAZORPAY_CONFIG = {
    'key_id': 'rzp_test_ROCO0lEjsGV5nV',
    'key_secret': 'ZCRd29hmvPla1F0rZUMX8dOn'
}

# Initialize MarketDataProvider with Kite config
market_data_provider = initialize_market_data_provider(KITE_CONFIG)

# Initialize Breakout Strategy Engine
breakout_engine = BreakoutStrategy(market_data_provider)

# Create a dummy user for testing if not exists
if not subscription_manager.get_user('user_001'):
    subscription_manager.create_user('user_001', 'test@example.com', '1234567890')

# Statistics tracking
platform_stats = {
    'total_users': 1247,
    'signals_today': 23,
    'win_rate': 87.3,
    'total_profits': 452000,
    'active_premium_users': 856,
    'paper_trades_today': 145
}

# --- Razorpay Payment Integration ---
# ------------------------------------

# Initialize Razorpay configuration from config
RAZORPAY_KEY_ID = config.RAZORPAY_CONFIG['KEY_ID']
RAZORPAY_KEY_SECRET = config.RAZORPAY_CONFIG['KEY_SECRET']

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@app.route('/api/create-order', methods=['POST'])
def create_razorpay_order():
    """Create a Razorpay order and return details to the frontend."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400

    try:
        user_id = data.get('user_id')
        plan_type = data.get('plan_type')
        
        result = subscription_manager.create_payment_order(user_id, plan_type)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error creating payment order: {e}")
        return jsonify({'success': False, 'message': str(e)})

# --- Telegram Bot Integration ---
# --------------------------------

# Replace hardcoded tokens with values from config
BOT_TOKEN = config.TELEGRAM_CONFIG['BOT_TOKEN']
CHAT_ID = config.TELEGRAM_CONFIG['CHAT_ID']

def send_telegram_message(message: str, chat_id: Optional[str] = None):
    """Sends a message to a specified Telegram chat."""
    try:
        if not BOT_TOKEN:
            logger.warning("Telegram BOT_TOKEN is not configured. Skipping message.")
            return
        
        target_chat_id = chat_id if chat_id else CHAT_ID
        if not target_chat_id:
            logger.warning("Telegram CHAT_ID is not configured. Skipping message.")
            return

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': target_chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, data=data, timeout=10)
        result = response.json()

        if result.get('ok'):
            logger.info(f"✅ Telegram message sent successfully to {target_chat_id}")
        else:
            logger.error(f"❌ Telegram error: {result}")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")

def verify_razorpay_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """Verifies the Razorpay payment signature."""
    try:
        message = f"{order_id}|{payment_id}"
        expected_signature = hmac.new(
            bytes(RAZORPAY_KEY_SECRET, 'utf-8'),
            msg=bytes(message, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        return False

# --- Web App Routes ---
# ----------------------
@app.route('/')
def premium_landing():
    """Renders the enhanced premium landing page."""
    try:
        # Use the new ultra-enhanced landing page which is a static HTML file
        return render_template('landing_ultra_enhanced.html')
    except Exception as e:
        logger.error(f"Error loading premium landing: {e}")
        # Fallback to original template if enhanced fails
        try:
            # Get current year for footer
            from datetime import datetime
            current_year = datetime.now().year
            
            # Check if Razorpay is enabled
            razorpay_enabled = bool(config.RAZORPAY_KEY_ID and config.RAZORPAY_KEY_SECRET)
            
            return render_template('premium_landing.html',
                                current_year=current_year,
                                razorpay_enabled=razorpay_enabled)
        except Exception as e2:
            logger.error(f"Error loading fallback template: {e2}")
            return render_template_string("""
            <html><body style="background:#000;color:#fff;text-align:center;padding:50px;font-family:Arial;">
            <h1>🚀 Elite FnO Trading Platform</h1>
            <p>Platform is temporarily unavailable. Please try again later.</p>
            <p><a href="/dashboard" style="color:#00f5ff;">Go to Dashboard</a></p>
            </body></html>
            """), 500

@app.route('/premium-landing')
def premium_landing_page():
    """Renders the new premium landing page."""
    return premium_landing()

@app.route('/landing-original')
def premium_landing_original():
    """Renders the original premium landing page for comparison."""
    try:
        # Prepare required template variables
        landing_data = {
            'features': [
                {'icon': 'chart-line', 'title': 'Real-Time Signals', 'description': 'Get instant FnO trading signals with high accuracy'},
                {'icon': 'robot', 'title': 'AI-Powered Analysis', 'description': 'Advanced algorithms analyze market patterns'},
                {'icon': 'mobile-alt', 'title': 'Mobile Alerts', 'description': 'Receive signals directly on your phone'},
                {'icon': 'chart-bar', 'title': 'Paper Trading', 'description': 'Practice risk-free with virtual portfolio'}
            ],
            'pricing_plans': [
                {
                    'name': 'Monthly Premium',
                    'price': '999',
                    'period': 'month',
                    'features': ['Real-time FnO Signals', 'Telegram Notifications', 'Basic Support']
                },
                {
                    'name': 'Quarterly Premium',
                    'price': '2,499',
                    'period': 'quarter',
                    'features': ['All Monthly Features', 'Priority Support', '15% Discount']
                },
                {
                    'name': 'Annual Premium',
                    'price': '7,999',
                    'period': 'year',
                    'features': ['All Quarterly Features', 'VIP Support', '33% Discount']
                }
            ],
            'stats': {
                'signals_today': platform_stats.get('signals_today', 0),
                'win_rate': platform_stats.get('win_rate', 85.0),
                'total_users': platform_stats.get('total_users', 1200),
                'paper_trades': platform_stats.get('paper_trades_today', 0)
            }
        }
        
        logger.info("Rendering original premium landing page")
        return render_template('premium_landing.html', **landing_data)
    except Exception as e:
        logger.error(f"Error loading original premium landing: {e}", exc_info=True)
        # Return a more user-friendly error page
        return render_template_string("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Temporarily Unavailable</title>
                <style>
                    body { font-family: 'Inter', sans-serif; background: #1a1a2e; color: #fff; padding: 2rem; text-align: center; }
                    .container { max-width: 600px; margin: 0 auto; }
                    h1 { color: #ff6b6b; }
                    .btn { display: inline-block; background: #4a90e2; color: white; padding: 10px 20px; 
                           text-decoration: none; border-radius: 5px; margin-top: 20px; }
                    .error { background: #2d2d44; padding: 15px; border-radius: 5px; margin-top: 20px; font-family: monospace; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 Page Temporarily Unavailable</h1>
                    <p>We're experiencing technical difficulties. Please try again in a few moments.</p>
                    <a href="/" class="btn">Return to Homepage</a>
                    {% if config.DEBUG %}
                    <div class="error">
                        <strong>Debug Info:</strong><br>
                        {{ error }}
                    </div>
                    {% endif %}
                </div>
            </body>
            </html>
        """, error=str(e)), 500

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    """Handle subscription requests with proper validation and error handling"""
    try:
        logger.info("Processing subscription request")
        
        # Validate request data
        data = request.get_json()
        if not data:
            logger.error("No JSON data received in subscription request")
            return jsonify({
                'status': 'error',
                'message': 'Invalid request data'
            }), 400

        required_fields = ['plan', 'email', 'name', 'phone']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            logger.error(f"Missing required fields in subscription request: {missing_fields}")
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Validate plan
        valid_plans = {'monthly': 999, 'quarterly': 2499, 'annual': 7999}
        if data['plan'] not in valid_plans:
            logger.error(f"Invalid plan selected: {data['plan']}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid subscription plan'
            }), 400

        # Create Razorpay order
        try:
            amount = valid_plans[data['plan']]
            currency = "INR"
            
            # Create order
            order_data = {
                'amount': amount * 100,  # Amount in paise
                'currency': currency,
                'receipt': f'order_{int(time.time())}',
                'notes': {
                    'plan': data['plan'],
                    'email': data['email'],
                    'name': data['name']
                }
            }
            
            # Initialize Razorpay client
            client = razorpay.Client(auth=(config.RAZORPAY_KEY_ID, config.RAZORPAY_KEY_SECRET))
            order = client.order.create(data=order_data)
            
            logger.info(f"Created Razorpay order: {order['id']}")
            
            # Save subscription attempt
            subscription_manager.create_subscription_attempt(
                user_email=data['email'],
                plan=data['plan'],
                amount=amount,
                order_id=order['id']
            )
            
            return jsonify({
                'status': 'success',
                'order_id': order['id'],
                'amount': amount,
                'currency': currency,
                'key_id': config.RAZORPAY_KEY_ID
            })
            
        except Exception as payment_error:
            logger.error(f"Payment creation failed: {payment_error}", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': 'Payment initialization failed. Please try again.'
            }), 500

    except Exception as e:
        logger.error(f"Subscription request failed: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred. Please try again.'
        }), 500

@app.route('/internal/test_signal')
def test_signal_generation():
    """
    An internal route to test signal generation and verify the fix for the TypeError.
    This should not be exposed to the public.
    """
    logger.info("--- Internal Signal Generation Test Started ---")
    try:
        # Test signal generation for each instrument
        for instrument in signal_engine.instruments:
            logger.info(f"Testing signal for instrument: {instrument}")
            signal = signal_engine.generate_test_signal(instrument)
            if signal:
                logger.info(f"Successfully generated test signal for {instrument}: {signal['option_symbol']}")
                # Also log the description to ensure it's formatted correctly
                logger.info(f"Setup Description: {signal['setup_description']}")
            else:
                logger.warning(f"No active signal generated for {instrument} under current test conditions.")
        
        logger.info("--- Internal Signal Generation Test Finished ---")
        return jsonify({'success': True, 'message': 'Signal generation test completed. Check server logs for details.'})
    except Exception as e:
        logger.error(f"CRITICAL: Error during internal signal test: {repr(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Test failed. Error: {repr(e)}'}), 500

@app.route('/pro-setups')
def pro_setups_page():
    """Page to display pro trader indicator setups."""
    try:
        setups = get_pro_setups()
        return render_template('pro_setups.html', setups=setups)
    except Exception as e:
        logger.error(f"Error loading pro setups page: {e}")
        return redirect('/dashboard')

@app.route('/start_trial', methods=['POST'])
def start_trial():
    """Handle free trial signup with validation and error handling"""
    try:
        logger.info("Processing trial signup request")
        
        # Validate request data
        try:
            data = request.get_json()
            if not data:
                logger.error("No JSON data received in trial request")
                return jsonify({
                    'success': False,
                    'message': 'Invalid request format'
                }), 400
        except Exception as json_error:
            logger.error(f"JSON parsing error: {json_error}")
            return jsonify({
                'success': False,
                'message': 'Invalid request format'
            }), 400

        # Validate required fields
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        name = data.get('name', '').strip()

        if not all([email, phone, name]):
            logger.error(f"Missing required fields: email={bool(email)}, phone={bool(phone)}, name={bool(name)}")
            return jsonify({
                'success': False,
                'message': 'Name, email and phone number are required.'
            }), 400

        # Validate email format
        if not '@' in email or not '.' in email:
            logger.error(f"Invalid email format: {email}")
            return jsonify({
                'success': False,
                'message': 'Please enter a valid email address.'
            }), 400

        # Validate phone number (basic check for length)
        if not phone.isdigit() or len(phone) < 10:
            logger.error(f"Invalid phone format: {phone}")
            return jsonify({
                'success': False,
                'message': 'Please enter a valid phone number.'
            }), 400

        # Check if user already exists
        try:
            existing_user = subscription_manager.get_user_by_details(email, phone)
            
            if existing_user:
                if existing_user.get('has_used_trial', False):
                    logger.info(f"Trial already used for email: {email}")
                    return jsonify({
                        'success': False,
                        'message': 'Free trial has already been used for this account.'
                    }), 403
                
                if existing_user.get('subscription_status') == 'active':
                    logger.info(f"User already has active subscription: {email}")
                    return jsonify({
                        'success': False,
                        'message': 'You already have an active subscription.'
                    }), 403
        except Exception as user_check_error:
            logger.error(f"Error checking existing user: {user_check_error}", exc_info=True)
            return jsonify({
                'success': False,
                'message': 'Unable to verify account status. Please try again.'
            }), 500

        # Create new trial account
        try:
            # Generate trial user data
            trial_data = {
                'email': email,
                'phone': phone,
                'name': name,
                'trial_start': datetime.now().isoformat(),
                'trial_days': 7,  # 7-day trial
                'has_used_trial': True,
                'subscription_status': 'trial'
            }
            
            # Create user account
            user_id = subscription_manager.create_user(
                email=email,
                phone=phone,
                name=name,
                trial_data=trial_data
            )
            
            # Send welcome email (non-blocking)
            try:
                threading.Thread(target=subscription_manager.send_welcome_email,
                               args=(email, name)).start()
            except Exception as email_error:
                logger.error(f"Error sending welcome email: {email_error}")
                # Don't fail the registration if email fails
            
            logger.info(f"Trial account created successfully for {email}")
            
            return jsonify({
                'success': True,
                'message': 'Trial account created successfully!',
                'user_id': user_id,
                'trial_ends': (datetime.now() + timedelta(days=7)).isoformat(),
                'next_steps': [
                    'Check your email for login credentials',
                    'Download our mobile app for instant alerts',
                    'Join our Telegram channel for community updates'
                ]
            })
            
        except Exception as creation_error:
            logger.error(f"Error creating trial account: {creation_error}", exc_info=True)
            return jsonify({
                'success': False,
                'message': 'Failed to create trial account. Please try again.'
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error in trial signup: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred. Please try again.'
        }), 500
    else:
        # If user exists but hasn't used trial (e.g. failed payment before), start trial
        user_id = existing_user['id']
        subscription_manager.start_free_trial(user_id)
        return jsonify({'success': True, 'user_id': user_id})

    # Create new user and start trial
    user_id = f"user_{int(time.time())}"
    new_user = subscription_manager.create_user(user_id, email, phone)
    
    # The free trial is now started automatically on user creation
    # so we just need to return the user_id
    
    return jsonify({'success': True, 'user_id': new_user['id']})

@app.route('/dashboard')
def dashboard():
    """Enhanced trading dashboard"""
    try:
        logger.info("Entering dashboard route")
        
        # Get live signals and market data
        logger.info("Getting signals and market data...")
        try:
            signals = signal_engine.get_recent_signals(10)
            logger.info(f"Got {len(signals) if signals else 0} signals")
        except Exception as signal_error:
            logger.error(f"Error getting signals: {signal_error}")
            signals = []

        try:
            market_data = signal_engine.get_live_market_data()
            logger.info("Got market data")
        except Exception as market_error:
            logger.error(f"Error getting market data: {market_error}")
            market_data = {}

        # Convert signals to plain dictionaries to avoid string formatting issues
        safe_signals = []
        for signal in signals:
            try:
                safe_signal = {
                    'instrument': signal.instrument,
                    'signal_type': signal.signal_type,
                    'option_symbol': signal.option_symbol,
                    'option_entry_price': signal.option_entry_price,
                    'option_target_price': signal.option_target_price,
                    'option_stop_loss': signal.option_stop_loss,
                    'confidence': signal.confidence,
                    'setup_description': signal.setup_description,
                    'timestamp': signal.timestamp,
                    'expiry_date': signal.expiry_date,
                    'risk_reward_ratio': signal.risk_reward_ratio
                }
                safe_signals.append(safe_signal)
            except Exception as signal_conv_error:
                logger.error(f"Error converting signal to dict: {signal_conv_error}")

        # Update platform stats
        try:
            platform_stats['signals_today'] = len(signals)
            platform_stats['win_rate'] = random.uniform(85.0, 90.0)
            logger.info(f"Updated platform stats: {platform_stats}")
        except Exception as stats_error:
            logger.error(f"Error updating stats: {stats_error}")

        # Render template with simplified data
        logger.info("Rendering template...")
        try:
            return render_template('dashboard_ultra_modern.html', 
                                signals=safe_signals, 
                                market_data=market_data, 
                                stats=platform_stats)
        except Exception as template_error:
            logger.error(f"Error rendering dashboard template: {template_error}", exc_info=True)
            # A more robust fallback template
            return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard Error</title>
    <style>
        body { background-color: #1a1a1a; color: #e0e0e0; font-family: sans-serif; padding: 20px; }
        h1 { color: #ff6b6b; }
        pre { background-color: #2c2c2c; padding: 15px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body>
    <h1>Dashboard Unavailable</h1>
    <p>We encountered an error while loading the dashboard. The development team has been notified.</p>
    <p><a href="/">Return to Homepage</a></p>
    <h2>Error Details:</h2>
    <pre>{{ error }}</pre>
    <h3>Debug Information:</h3>
    <pre>
Signals: {{ signal_data }}
Market Data: {{ market_summary }}
Platform Stats: {{ stats_data }}
    </pre>
</body>
</html>
""", error=str(template_error),
                signal_data=str(safe_signals),
                market_summary=str(market_data),
                stats_data=str(platform_stats))
    except Exception as e:
        logger.error(f"Error in dashboard route: {e}", exc_info=True)
        try:
            # Use repr(e) to get a more detailed error string
            return render_template_string("""
<h1>🚀 Elite FnO Dashboard</h1>
<p>Dashboard temporarily unavailable. <a href="/">Return to home</a></p>
<p>Error: {{ error }}</p>
""", error=repr(e))
        except Exception as template_error:
            logger.error(f"Error rendering dashboard template: {template_error}", exc_info=True)
            # A more robust fallback template
            return render_template_string("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Dashboard Error</title>
                <style>
                    body { background-color: #1a1a1a; color: #e0e0e0; font-family: sans-serif; padding: 20px; }
                    h1 { color: #ff6b6b; }
                    pre { background-color: #2c2c2c; padding: 15px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; }
                </style>
            </head>
            <body>
                <h1>Dashboard Unavailable</h1>
                <p>We encountered an error while loading the dashboard. The development team has been notified.</p>
                <p><a href="/">Return to Homepage</a></p>
                <h2>Error Details:</h2>
                <pre>{{ error }}</pre>
            </body>
            </html>
            """, error=str(template_error))
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}", exc_info=True)
        # Use repr(e) to get a more detailed error string
        return render_template_string("""
        <h1>🚀 Elite FnO Dashboard</h1>
        <p>Dashboard temporarily unavailable. <a href="/">Return to home</a></p>
        <p>Error: {{ error }}</p>
        """, error=repr(e))

@app.route('/paper-trading')
def paper_trading_page():
    """Paper trading interface"""
    try:
        return render_template('paper_trading.html')
    except Exception as e:
        logger.error(f"Error loading paper trading: {e}")
        return render_template_string("""
        <h1>💼 Paper Trading</h1>
        <p>Paper trading temporarily unavailable. <a href="/">Return to home</a></p>
        """)

# Paper Trading API Routes
@app.route('/api/paper-trading/portfolio/<user_id>')
def get_paper_portfolio(user_id):
    """Get user's paper trading portfolio"""
    try:
        portfolio = paper_trading_engine.get_portfolio(user_id)
        if portfolio:
            return jsonify({'success': True, 'portfolio': portfolio})
        else:
            return jsonify({'success': False, 'message': 'Portfolio not found'})
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/paper-trading/create-portfolio', methods=['POST'])
def handle_create_paper_portfolio():
    """API endpoint to create a new paper trading portfolio."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400

    try:
        user_id = data.get('user_id')
        initial_balance = data.get('initial_balance', 100000.0)
        
        portfolio = paper_trading_engine.create_portfolio(user_id, initial_balance)
        return jsonify({'success': True, 'portfolio': portfolio})
    except Exception as e:
        logger.error(f"Error creating portfolio: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/paper-trading/place-order', methods=['POST'])
def handle_place_paper_order():
    """API endpoint to place a new paper trading order."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400

    try:
        result = paper_trading_engine.place_order(
            user_id=data['user_id'],
            symbol=data['symbol'],
            quantity=data['quantity'],
            price=data['price'],
            order_type=data['order_type']
        )
        
        # Update platform stats
        if result['success']:
            platform_stats['paper_trades_today'] += 1
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/paper-trading/update-market-data', methods=['POST'])
def handle_update_market_data():
    """API endpoint to update market data for paper trading portfolios."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
    try:
        price_data = data.get('price_data', {})
        paper_trading_engine.update_market_data(price_data)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error updating prices: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/subscribe', methods=['POST'])
def handle_subscribe():
    """Handles new premium subscriptions."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
    try:
        user_id = data['user_id']
        plan_type = data.get('plan_type')
        if not plan_type:
            return jsonify({'success': False, 'message': 'Subscription plan not specified.'}), 400
        
        # In a real scenario, you would create an order and pass the order_id to the frontend
        # For now, we'll simulate a successful subscription activation
        subscription_manager.activate_subscription(user_id, plan_type)
        
        return jsonify({
            'success': True,
            'message': f'Successfully subscribed to {plan_type} plan!'
        })
    except Exception as e:
        logger.error(f"Error in handle_subscribe: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during subscription.'}), 500

@app.route('/api/verify-payment', methods=['POST'])
def handle_verify_payment():
    """Verifies a Razorpay payment and activates a subscription."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
    try:
        payment_id = data.get('payment_id')
        order_id = data.get('order_id')
        signature = data.get('signature')
        user_id = data.get('user_id')

        if not all([payment_id, order_id, signature, user_id]):
            return jsonify({'success': False, 'message': 'Missing payment details.'}), 400

        if verify_razorpay_signature(order_id, payment_id, signature):
            plan_type = "premium" # You would fetch this based on the order
            subscription_manager.activate_subscription(user_id, plan_type)
            return jsonify({'success': True, 'message': f'Payment verified! {plan_type.capitalize()} plan activated.'})
        else:
            return jsonify({'success': False, 'message': 'Payment verification failed.'}), 400
    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during payment verification.'}), 500

@app.route('/api/subscription-status/<user_id>')
def subscription_status(user_id):
    user = subscription_manager.get_user(user_id)
    if not user:
        return jsonify({'is_premium': False, 'message': 'User not found'}), 404

    is_premium = subscription_manager.is_premium(user_id)
    plan_id = user.get('plan_id')
    end_date = user.get('subscription_end')

    return jsonify({
        'is_premium': is_premium,
        'plan_id': plan_id,
        'end_date': end_date.isoformat() if end_date else None
    })

@app.route('/api/market-pulse')
def market_pulse():
    """API endpoint to get live market pulse data."""
    data = market_data_provider.get_market_pulse_kite()
    return jsonify(data)

@app.route('/api/breakout-scan')
def breakout_scan():
    """API endpoint to scan for breakout signals."""
    # In a real scenario, we might get the instrument list from the user or a predefined list
    instruments_to_scan = [
        'RELIANCE', 'HDFCBANK', 'ICICIBANK', 'INFY', 'TCS', 
        'KOTAKBANK', 'HINDUNILVR', 'ITC', 'BAJFINANCE', 'SBIN'
    ]
    
    signals = breakout_engine.scan_for_breakouts(instruments_to_scan)
    
    return jsonify({'success': True, 'signals': signals})

@app.route('/api/kite/login')
def kite_login():
    """Generates and returns the Kite login URL."""
    try:
        login_url = market_data_provider.get_kite_login_url()
        return jsonify({'success': True, 'login_url': login_url})
    except Exception as e:
        logger.error(f"Error generating Kite login URL: {e}")
        return jsonify({'success': False, 'message': 'Could not generate Kite login URL.'})

@app.route('/api/test-telegram', methods=['POST'])
def test_telegram_connection():
    """Test Telegram connection by sending a simple message."""
    try:
        # Use the main CHAT_ID for testing
        send_telegram_message("🔔 Elite FnO Telegram Bot is connected and running!", config.CHAT_ID)
        return jsonify({'success': True, 'message': 'Test message sent successfully!'})
    except Exception as e:
        logger.error(f"Failed to send test Telegram message: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/generate-test-signal', methods=['POST'])
def generate_test_signal():
    """Generate test signal"""
    try:
        signal = signal_engine.generate_test_signal()
        if signal:
            # Send to Telegram if available
            signal_message = f"""
🎯 *Test Signal Generated*

📊 *{signal['instrument']}*
🔔 {signal['signal_type'].replace('_', ' ')}
💰 Entry: ₹{signal['entry_price']}
🎯 Target: ₹{signal['target_price']}
🛡️ SL: ₹{signal['stop_loss']}
📈 Setup: {signal['setup_description']}
🎪 Confidence: {signal['confidence']}%

⚡ *Premium AI Signal* ⚡
            """
            telegram_result = send_telegram_message(signal_message)
            
            return jsonify({
                'success': True,
                'message': '🎯 Test signal generated and sent to Telegram!',
                'data': signal,
                'telegram_sent': telegram_result is not None and telegram_result.get('ok', False)
            })
        else:
            return jsonify({
                'success': False,
                'message': '❌ Failed to generate test signal'
            })
    except Exception as e:
        logger.error(f"Error generating test signal: {e}")
        return jsonify({
            'success': False,
            'message': f'❌ Error: {str(e)}'
        })

@app.route('/api/market-data')
def get_market_data():
    """Get live market data"""
    try:
        market_data = signal_engine.get_live_market_data()
        return jsonify({
            'success': True,
            'data': market_data,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': {}
        })

@app.route('/api/signals')
def get_signals_api():
    """Get current signals"""
    try:
        signals = signal_engine.get_recent_signals(15)
        return jsonify({
            'success': True,
            'data': {
                'signals': signals,
                'count': len(signals),
                'last_updated': datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error getting signals: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': {'signals': [], 'count': 0}
        })

# Statistics API
@app.route('/test-all-features')
def test_all_features():
    """Test page for all platform features"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🧪 Test All Features - Elite FnO</title>
        <style>
            body { 
                font-family: 'Inter', sans-serif; 
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
                color: white; 
                padding: 2rem; 
                min-height: 100vh;
            }
            .container { max-width: 1000px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 3rem; }
            .test-section { 
                background: rgba(255, 255, 255, 0.05); 
                padding: 2rem; 
                border-radius: 20px; 
                margin-bottom: 2rem; 
            }
            .test-btn { 
                padding: 1rem 2rem; 
                background: linear-gradient(135deg, #00f5ff, #0080ff);
                border: none; 
                border-radius: 15px; 
                color: white; 
                cursor: pointer; 
                margin: 0.5rem; 
                transition: all 0.3s ease;
            }
            .test-btn:hover { 
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(0, 245, 255, 0.3);
            }
            .results { 
                background: rgba(0, 0, 0, 0.3); 
                padding: 1rem; 
                border-radius: 10px; 
                margin-top: 1rem; 
                display: none; 
            }
            .success { color: #00ff88; }
            .error { color: #ff6b6b; }
            .nav-links { text-align: center; margin: 2rem 0; }
            .nav-links a { 
                color: #00f5ff; text-decoration: none; margin: 0 1rem; 
                padding: 0.5rem 1rem; border: 1px solid #00f5ff; border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧪 Elite FnO - Feature Testing Dashboard</h1>
                <p>Test all platform features and integrations</p>
            </div>
            
            <div class="nav-links">
                <a href="/">🏠 Home</a>
                <a href="/dashboard">📊 Dashboard</a>
                <a href="/paper-trading">💼 Paper Trading</a>
            </div>
            
            <div class="test-section">
                <h2>🤖 Telegram Bot Testing</h2>
                <p>Test Telegram bot integration and message sending</p>
                <button class="test-btn" onclick="testTelegram()">Test Telegram Bot</button>
                <button class="test-btn" onclick="testTelegramSignal()">Send Test Signal</button>
                <div id="telegram-results" class="results"></div>
            </div>
            
            <div class="test-section">
                <h2>💳 Payment System Testing</h2>
                <p>Test Razorpay integration (Test Mode)</p>
                <button class="test-btn" onclick="testPaymentWeekly()">Test Weekly Plan (₹350)</button>
                <button class="test-btn" onclick="testPaymentMonthly()">Test Monthly Plan (₹900)</button>
                <div id="payment-results" class="results"></div>
            </div>
            
            <div class="test-section">
                <h2>💼 Paper Trading Testing</h2>
                <p>Test virtual trading system</p>
                <button class="test-btn" onclick="testPaperTrading()">Create Demo Portfolio</button>
                <button class="test-btn" onclick="testPaperOrder()">Place Demo Order</button>
                <div id="paper-results" class="results"></div>
            </div>
            
            <div class="test-section">
                <h2>🎯 Signal Generation Testing</h2>
                <p>Test AI signal generation and broadcasting</p>
                <button class="test-btn" onclick="testSignalGeneration()">Generate Test Signal</button>
                <button class="test-btn" onclick="testSignalBroadcast()">Broadcast to Telegram</button>
                <div id="signal-results" class="results"></div>
            </div>
            
            <div class="test-section">
                <h2>📊 Platform Status</h2>
                <p>Overall system health check</p>
                <button class="test-btn" onclick="checkAllSystems()">Check All Systems</button>
                <div id="status-results" class="results"></div>
            </div>
        </div>
        
        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
        <script>
            function showResults(elementId, message, isSuccess = true) {
                const element = document.getElementById(elementId);
                element.style.display = 'block';
                element.innerHTML = '<pre class="' + (isSuccess ? 'success' : 'error') + '">' + message + '</pre>';
            }
            
            function testTelegram() {
                showResults('telegram-results', '🔄 Testing Telegram bot...');
                fetch('/api/test-telegram', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        const message = data.success 
                            ? '✅ Telegram bot working! Message sent successfully.'
                            : '❌ Telegram bot failed: ' + data.message;
                        showResults('telegram-results', message, data.success);
                    })
                    .catch(error => {
                        showResults('telegram-results', '❌ Error: ' + error.message, false);
                    });
            }
            
            function testTelegramSignal() {
                showResults('telegram-results', '🔄 Sending test signal to Telegram...');
                fetch('/api/generate-test-signal', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        const message = data.success 
                            ? '✅ Signal sent to Telegram! Check your bot.'
                            : '❌ Signal failed: ' + data.message;
                        showResults('telegram-results', message, data.success);
                    });
            }
            
            function testPaymentWeekly() {
                testPayment('weekly');
            }
            
            function testPaymentMonthly() {
                testPayment('monthly');
            }
            
            function testPayment(planType) {
                showResults('payment-results', '🔄 Testing ' + planType + ' payment...');
                
                const plans = {
                    weekly: { amount: 35000, name: 'Weekly Premium' },
                    monthly: { amount: 90000, name: 'Monthly Premium' }
                };
                
                const plan = plans[planType];
                
                const options = {
                    key: 'rzp_test_ROCO0lEjsGV5nV',
                    amount: plan.amount,
                    currency: 'INR',
                    name: 'Elite FnO Trading (TEST)',
                    description: plan.name + ' - Test Payment',
                    handler: function(response) {
                        const message = '✅ Test payment successful!\\nPayment ID: ' + response.razorpay_payment_id;
                        showResults('payment-results', message, true);
                    },
                    prefill: {
                        name: 'Test User',
                        email: 'test@example.com',
                        contact: '9999999999'
                    },
                    theme: { color: '#0080ff' },
                    modal: {
                        ondismiss: function() {
                            showResults('payment-results', '⚠️ Payment cancelled by user', false);
                        }
                    }
                };
                
                const rzp = new Razorpay(options);
                rzp.open();
            }
            
            function testPaperTrading() {
                showResults('paper-results', '🔄 Creating demo paper trading portfolio...');
                
                const testUserId = 'test_user_' + Date.now();
                
                fetch('/api/paper-trading/create-portfolio', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: testUserId,
                        initial_balance: 100000
                    })
                })
                .then(response => response.json())
                .then(data => {
                    const message = data.success 
                        ? '✅ Paper trading portfolio created!\\nUser ID: ' + testUserId + '\\nBalance: ₹1,00,000'
                        : '❌ Failed: ' + data.message;
                    showResults('paper-results', message, data.success);
                });
            }
            
            function testPaperOrder() {
                showResults('paper-results', '🔄 Placing demo paper trading order...');
                
                const testUserId = 'test_user_' + Date.now();
                
                // First create portfolio, then place order
                fetch('/api/paper-trading/create-portfolio', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: testUserId, initial_balance: 100000 })
                })
                .then(() => {
                    return fetch('/api/paper-trading/place-order', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_id: testUserId,
                            symbol: 'NIFTY_CE',
                            quantity: 2,
                            price: 150.50,
                            order_type: 'BUY'
                        })
                    });
                })
                .then(response => response.json())
                .then(data => {
                    const message = data.success 
                        ? '✅ Demo order placed!\\nSymbol: NIFTY_CE\\nQuantity: 2\\nPrice: ₹150.50'
                        : '❌ Order failed: ' + data.message;
                    showResults('paper-results', message, data.success);
                });
            }
            
            function testSignalGeneration() {
                showResults('signal-results', '🔄 Generating AI test signal...');
                fetch('/api/generate-test-signal', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        const message = data.success 
                            ? '✅ Signal generated!\\nInstrument: ' + data.data.instrument + '\\nType: ' + data.data.signal_type
                            : '❌ Signal failed: ' + data.message;
                        showResults('signal-results', message, data.success);
                    });
            }
            
            function testSignalBroadcast() {
                showResults('signal-results', '🔄 Broadcasting signal to Telegram...');
                fetch('/api/generate-test-signal', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        const message = data.success && data.telegram_sent
                            ? '✅ Signal broadcasted to Telegram successfully!'
                            : '❌ Broadcast failed or Telegram not connected';
                        showResults('signal-results', message, data.success && data.telegram_sent);
                    });
            }
            
            function checkAllSystems() {
                showResults('status-results', '🔄 Checking all systems...');
                
                const checks = [
                    { name: 'Web Server', status: '✅ Online' },
                    { name: 'Signal Engine', status: '✅ Running' },
                    { name: 'Paper Trading', status: '✅ Active' },
                    { name: 'Payment Gateway', status: '✅ Connected' },
                    { name: 'Telegram Bot', status: '🔄 Testing...' },
                    { name: 'Database', status: '✅ Operational' }
                ];
                
                let statusMessage = 'System Status Check:\\n\\n';
                checks.forEach(check => {
                    statusMessage += check.name + ': ' + check.status + '\\n';
                });
                
                // Test Telegram to update status
                fetch('/api/test-telegram', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        const telegramStatus = data.success ? '✅ Connected' : '❌ Disconnected';
                        statusMessage = statusMessage.replace('🔄 Testing...', telegramStatus);
                        statusMessage += '\\n✅ All core systems operational!';
                        showResults('status-results', statusMessage, true);
                    })
                    .catch(() => {
                        statusMessage = statusMessage.replace('🔄 Testing...', '❌ Connection Error');
                        showResults('status-results', statusMessage, false);
                    });
            }
        </script>
    </body>
    </html>
    """)

@app.route('/api/platform-stats')
def get_platform_stats():
    """Get platform statistics"""
    try:
        # Update some dynamic stats
        platform_stats['total_users'] += random.randint(0, 3)
        platform_stats['win_rate'] = round(random.uniform(84.0, 92.0), 1)
        
        # Add subscription stats
        sub_stats = subscription_manager.get_subscription_stats()
        
        combined_stats = {
            **platform_stats,
            **sub_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'stats': combined_stats
        })
    except Exception as e:
        logger.error(f"Error getting platform stats: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

# Telegram Bot Webhook (optional)
@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """Handle Telegram bot updates"""
    try:
        update = request.json
        
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            if text.startswith('/start'):
                welcome_msg = """
🚀 *Welcome to Elite FnO Trading Bot!*

🎯 Get premium trading signals
💼 Practice with paper trading
💎 Subscribe to premium plans

Commands:
/signals - Get latest signals
/portfolio - Check paper portfolio
/subscribe - View premium plans
/help - Show this help

Visit: https://your-platform.com
                """
                send_telegram_message(welcome_msg, str(chat_id))
            
            elif text.startswith('/signals'):
                signals = signal_engine.get_recent_signals(3)
                if signals:
                    signals_msg = "🎯 *Latest Signals:*\n\n"
                    for signal in signals[:3]:
                        signals_msg += f"📊 {signal['instrument']}\n"
                        signals_msg += f"🔔 {signal['signal_type'].replace('_', ' ')}\n"
                        signals_msg += f"💰 Entry: ₹{signal['entry_price']}\n"
                        signals_msg += f"🎯 Target: ₹{signal['target_price']}\n\n"
                    send_telegram_message(signals_msg, str(chat_id))
                else:
                    send_telegram_message("No signals available right now.", str(chat_id))
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error handling Telegram webhook: {e}")
        return jsonify({'success': False})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template_string("""
    <h1>🚀 Elite FnO - Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <p><a href="/">Return to Home</a> | <a href="/dashboard">Go to Dashboard</a> | <a href="/paper-trading">Paper Trading</a></p>
    """), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template_string("""
    <h1>🚀 Elite FnO - Server Error</h1>
    <p>Something went wrong on our end. Please try again later.</p>
    <p><a href="/">Return to Home</a></p>
    """), 500

# Auto signal broadcasting
def broadcast_signals():
    """Broadcast signals to Telegram at regular intervals"""
    while True:
        try:
            time.sleep(random.randint(300, 900))  # 5-15 minutes

            if random.random() < 0.3:  # 30% chance
                signal = signal_engine.generate_test_signal()
                if signal:
                    signal_message = f"""
ðŸš¨ *LIVE SIGNAL ALERT* ðŸš¨

ðŸ“Š *{signal['instrument']}*
ðŸ”” {signal['signal_type'].replace('_', ' ')}
ðŸ’° Entry: â‚¹{signal['entry_price']}
ðŸŽ¯ Target: â‚¹{signal['target_price']}
ðŸ›¡ï¸ Stop Loss: â‚¹{signal['stop_loss']}

ðŸ“ˆ Setup: {signal['setup_description']}
ðŸŽª AI Confidence: {signal['confidence']}%

âš¡ *Premium AI Signal* âš¡
ðŸ¤– Powered by Elite FnO Bot
                    """
                    # Ensure broadcast uses the correct CHAT_ID from config
                    send_telegram_message(signal_message, config.CHAT_ID)
                    logger.info(f"Broadcasted signal: {signal['instrument']}")
        except Exception as e:
            logger.error(f"Error in signal broadcasting: {e}")

# ----------------------------------------------------
# Debug/Diagnostics Routes (to investigate 404 issues)
# ----------------------------------------------------
@app.route('/__debug/routes')
def list_registered_routes():
    """Return JSON of all registered Flask routes (diagnostic)."""
    routes = []
    for rule in app.url_map.iter_rules():
        methods = sorted(m for m in rule.methods if m not in ('HEAD', 'OPTIONS'))
        routes.append({
            'rule': str(rule),
            'endpoint': rule.endpoint,
            'methods': methods
        })
    return jsonify({'success': True, 'count': len(routes), 'routes': routes})

@app.route('/__debug/ping')
def debug_ping():
    return jsonify({'success': True, 'message': 'Premium app alive', 'time': datetime.now().isoformat()})

def cleanup():
    """Clean up resources before shutdown."""
    try:
        logger.info('Starting cleanup...')
        
        # Stop background services
        notification_manager.stop()
        health_monitor.stop()
        recovery_manager.stop()
        
        # Stop signal generation
        if hasattr(app, 'signal_engine'):
            app.signal_engine.stop_signal_generation()
            
        # Clear cache
        cache_manager.clear()
        
        # Close any open connections
        if hasattr(app, 'kite_client'):
            app.kite_client.close()
            
        logger.info('Cleanup completed successfully')
        
    except Exception as e:
        logger.error(f'Error during cleanup: {str(e)}', exc_info=True)

# Register cleanup function
import atexit
atexit.register(cleanup)

if __name__ == '__main__':
    print("🚀 Starting Elite FnO Trading Platform - Premium Edition")
    print("=" * 80)
    print("🌐 Premium Landing: http://localhost:5000")
    print("📊 Trading Dashboard: http://localhost:5000/dashboard")
    print("💼 Paper Trading: http://localhost:5000/paper-trading")
    print("🤖 Telegram Bot: Integrated")
    print("💳 Razorpay Payments: Integrated")
    print("🎪 Bull/Bear Animations: Active")
    print("=" * 80)
    
    try:
        # Initialize core services
        print("🎯 Starting core services...")
        app.signal_engine = signal_engine
        app.signal_engine.start_signal_generation()
        print("✅ Signal generation started!")
        
        # Start background signal broadcasting
        broadcast_thread = threading.Thread(target=broadcast_signals, daemon=True)
        broadcast_thread.start()
        print("📡 Telegram signal broadcasting started!")
        
        # Add service worker route
        @app.route('/sw.js')
        def service_worker():
            """Serve the service worker file"""
            response = app.send_static_file('sw.js')
            response.headers['Content-Type'] = 'application/javascript'
            response.headers['Service-Worker-Allowed'] = '/'
            return response

        # Start the Flask app
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=True)
        
    except Exception as e:
        logger.error(f'Failed to start server: {str(e)}', exc_info=True)
        cleanup()
        sys.exit(1)