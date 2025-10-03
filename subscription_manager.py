"""
💎 Premium Subscription System
Weekly ₹350 and Monthly ₹900 plans with Razorpay integration
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import uuid
import requests
import hmac
import hashlib

logger = logging.getLogger(__name__)

class PremiumSubscriptionManager:
    def __init__(self):
        self.data_file = "subscription_data.json"
        self.users = {}
        self.plans = {
            'weekly': {
                'name': '⚡ Weekly Premium',
                'price': 350,
                'currency': 'INR',
                'duration_days': 7,
                'features': [
                    '🎯 Premium AI Signals (15-20 daily)',
                    '📊 Advanced Technical Analysis',
                    '🚀 Real-time Alerts via Telegram',
                    '💼 Paper Trading with Live Data',
                    '📈 Market Sentiment Analysis',
                    '🎪 Bull/Bear Animations & Effects',
                    '⚡ Priority Customer Support'
                ],
                'badge': '⚡',
                'color': '#00f5ff'
            },
            'monthly': {
                'name': '👑 Monthly Premium',
                'price': 900,
                'currency': 'INR',
                'duration_days': 30,
                'features': [
                    '🎯 Premium AI Signals (20-25 daily)',
                    '📊 Advanced Technical Analysis',
                    '🚀 Real-time Alerts via Telegram',
                    '💼 Paper Trading with Live Data',
                    '📈 Market Sentiment Analysis',
                    '🎪 Bull/Bear Animations & Effects',
                    '🤖 AI Portfolio Optimization',
                    '📱 Mobile App Access',
                    '💎 VIP Trading Room Access',
                    '🏆 Leaderboard Rankings',
                    '⚡ Priority Customer Support',
                    '🎁 Bonus: Weekly Market Reports'
                ],
                'badge': '👑',
                'color': '#ffd700'
            },
            'trial': {
                'name': '🚀 2-Day Free Trial',
                'price': 0,
                'currency': 'INR',
                'duration_days': 2,
                'features': [
                    '🎯 Premium AI Signals (15-20 daily)',
                    '📊 Advanced Technical Analysis',
                    '🚀 Real-time Alerts via Telegram',
                    '💼 Paper Trading with Live Data',
                    '📈 Market Sentiment Analysis',
                    '🎪 Bull/Bear Animations & Effects',
                    '⚡ Priority Customer Support'
                ],
                'badge': '🚀',
                'color': '#4caf50'
            }
        }
        
        # Payment gateway configuration
        self.razorpay_key_id = "rzp_test_ROCO0lEjsGV5nV"
        self.razorpay_key_secret = "ZCRd29hmvPla1F0rZUMX8dOn"
        
        self.load_data()

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Retrieve a user by their ID."""
        return self.users.get(user_id)

    def get_user_by_details(self, email: str, phone: str) -> Optional[Dict]:
        """Find a user by email or phone."""
        for user in self.users.values():
            if user.get('email') == email or user.get('phone') == phone:
                return user
        return None
    
    def load_data(self):
        """Load subscription data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
            else:
                self.users = {}
        except Exception as e:
            logger.error(f"Error loading subscription data: {e}")
            self.users = {}
    
    def save_data(self):
        """Save subscription data to file"""
        try:
            data = {
                'users': self.users,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving subscription data: {e}")
    
    def create_user(self, user_id: str, email: str, telegram_id: str = None) -> Dict:
        """Create a new user account"""
        user = {
            'user_id': user_id,
            'email': email,
            'telegram_id': telegram_id,
            'subscription': 'free', # Will be updated by trial
            'subscription_start': None,
            'subscription_end': None,
            'has_used_trial': False, # New flag
            'payment_history': [],
            'features_used': {
                'signals_today': 0,
                'paper_trades': 0,
                'last_reset': datetime.now().date().isoformat()
            },
            'created_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat()
        }
        
        self.users[user_id] = user
        self.start_free_trial(user_id) # Start trial on creation
        self.save_data()
        
        logger.info(f"Created user account and started free trial: {user_id}")
        return user
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user subscription details"""
        return self.users.get(user_id)
    
    def is_premium(self, user_id: str) -> bool:
        """Check if user has active premium subscription (including trial)"""
        user = self.get_user(user_id)
        if not user or user['subscription'] == 'free':
            return False
        
        if user['subscription_end']:
            end_date = datetime.fromisoformat(user['subscription_end'])
            return datetime.now() < end_date
        
        return False

    def get_all_premium_user_ids(self) -> List[str]:
        """Returns a list of user_ids for all active premium (including trial) subscribers."""
        return [
            uid for uid, user in self.users.items() 
            if self.is_premium(uid) and user.get('telegram_id')
        ]
    
    def get_user_plan(self, user_id: str) -> Dict:
        """Get user's current plan details"""
        user = self.get_user(user_id)
        if not user:
            return {'plan': 'free', 'features': [], 'days_left': 0}
        
        if self.is_premium(user_id):
            plan_type = user['subscription']
            plan = self.plans[plan_type]
            
            end_date = datetime.fromisoformat(user['subscription_end'])
            days_left = (end_date - datetime.now()).days
            
            return {
                'plan': plan_type,
                'name': plan['name'],
                'features': plan['features'],
                'days_left': max(0, days_left),
                'badge': plan['badge'],
                'color': plan['color']
            }
        else:
            return {
                'plan': 'free',
                'name': '🆓 Free Plan',
                'features': [
                    '🎯 Basic Signals (3-5 daily)',
                    '📊 Basic Market Data',
                    '💼 Limited Paper Trading',
                    '📧 Email Support'
                ],
                'days_left': 0,
                'badge': '🆓',
                'color': '#666666'
            }
    
    def start_free_trial(self, user_id: str) -> Dict:
        """Starts a 2-day free trial for the user."""
        user = self.get_user(user_id)
        if not user:
            return {'success': False, 'message': 'User not found.'}
        
        if user.get('has_used_trial', False):
            return {'success': False, 'message': 'Free trial has already been used.'}

        plan = self.plans['trial']
        start_date = datetime.now()
        end_date = start_date + timedelta(days=plan['duration_days'])

        user['subscription'] = 'trial'
        user['subscription_start'] = start_date.isoformat()
        user['subscription_end'] = end_date.isoformat()
        user['has_used_trial'] = True
        
        self.save_data()
        
        logger.info(f"Started 2-day free trial for user {user_id}")
        return {
            'success': True, 
            'message': '🚀 2-Day Free Trial activated!',
            'subscription_end': end_date.isoformat()
        }

    def create_payment_order(self, user_id: str, plan_type: str) -> Dict:
        """Create Razorpay payment order"""
        if plan_type not in self.plans:
            return {'success': False, 'message': 'Invalid plan type'}
        
        plan = self.plans[plan_type]
        amount = plan['price'] * 100  # Convert to paise
        
        # Generate order ID
        order_id = f"order_{user_id}_{plan_type}_{int(datetime.now().timestamp())}"
        
        # In a real implementation, you would call Razorpay API here
        # For demo purposes, we'll simulate the order creation
        
        payment_order = {
            'order_id': order_id,
            'amount': amount,
            'currency': plan['currency'],
            'plan_type': plan_type,
            'user_id': user_id,
            'status': 'created',
            'created_at': datetime.now().isoformat(),
            'razorpay_key': self.razorpay_key_id
        }
        
        logger.info(f"Created payment order: {order_id} for user {user_id}")
        return {
            'success': True,
            'order': payment_order
        }
    
    def process_payment(self, user_id: str, plan_type: str, payment_id: str, 
                       order_id: str, signature: str) -> Dict:
        """Process successful payment and activate subscription"""
        user = self.get_user(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        plan = self.plans[plan_type]
        
        # In a real implementation, verify payment signature here
        # For demo, we'll assume payment is successful
        
        # Calculate subscription dates
        start_date = datetime.now()
        end_date = start_date + timedelta(days=plan['duration_days'])
        
        # Update user subscription
        user['subscription'] = plan_type
        user['subscription_start'] = start_date.isoformat()
        user['subscription_end'] = end_date.isoformat()
        
        # Add to payment history
        payment_record = {
            'payment_id': payment_id,
            'order_id': order_id,
            'plan_type': plan_type,
            'amount': plan['price'],
            'currency': plan['currency'],
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        
        user['payment_history'].append(payment_record)
        self.save_data()
        
        logger.info(f"Activated {plan_type} subscription for user {user_id}")
        
        return {
            'success': True,
            'message': f'✅ {plan["name"]} activated successfully!',
            'subscription_end': end_date.isoformat(),
            'features': plan['features']
        }
    
    def check_feature_limit(self, user_id: str, feature: str) -> Dict:
        """Check if user can use a feature based on their plan"""
        user = self.get_user(user_id)
        if not user:
            return {'allowed': False, 'message': 'User not found'}
        
        # Reset daily counters if needed
        today = datetime.now().date().isoformat()
        if user['features_used']['last_reset'] != today:
            user['features_used']['signals_today'] = 0
            user['features_used']['paper_trades'] = 0
            user['features_used']['last_reset'] = today
            self.save_data()
        
        is_premium_user = self.is_premium(user_id)
        
        if feature == 'signals':
            if is_premium_user:
                return {'allowed': True, 'limit': 25, 'used': user['features_used']['signals_today']}
            else:
                if user['features_used']['signals_today'] >= 5:
                    return {'allowed': False, 'message': 'Daily signal limit reached. Upgrade to premium!'}
                return {'allowed': True, 'limit': 5, 'used': user['features_used']['signals_today']}
        
        elif feature == 'paper_trading':
            if is_premium_user:
                return {'allowed': True, 'limit': 'unlimited'}
            else:
                if user['features_used']['paper_trades'] >= 10:
                    return {'allowed': False, 'message': 'Daily paper trading limit reached. Upgrade to premium!'}
                return {'allowed': True, 'limit': 10, 'used': user['features_used']['paper_trades']}
        
        elif feature == 'telegram_alerts':
            if is_premium_user:
                return {'allowed': True}
            else:
                return {'allowed': False, 'message': 'Telegram alerts are premium feature. Upgrade now!'}
        
        elif feature == 'advanced_analysis':
            if is_premium_user:
                return {'allowed': True}
            else:
                return {'allowed': False, 'message': 'Advanced analysis requires premium subscription.'}
        
        return {'allowed': True}
    
    def use_feature(self, user_id: str, feature: str):
        """Track feature usage"""
        user = self.get_user(user_id)
        if user:
            if feature == 'signals':
                user['features_used']['signals_today'] += 1
            elif feature == 'paper_trading':
                user['features_used']['paper_trades'] += 1
            
            self.save_data()
    
    def get_subscription_stats(self) -> Dict:
        """Get subscription statistics"""
        total_users = len(self.users)
        premium_users = sum(1 for user in self.users.values() if self.is_premium(user['user_id']))
        free_users = total_users - premium_users
        
        # Calculate revenue
        total_revenue = 0
        monthly_revenue = 0
        current_month = datetime.now().month
        
        for user in self.users.values():
            for payment in user['payment_history']:
                if payment['status'] == 'success':
                    total_revenue += payment['amount']
                    payment_date = datetime.fromisoformat(payment['timestamp'])
                    if payment_date.month == current_month:
                        monthly_revenue += payment['amount']
        
        return {
            'total_users': total_users,
            'premium_users': premium_users,
            'free_users': free_users,
            'conversion_rate': (premium_users / total_users * 100) if total_users > 0 else 0,
            'total_revenue': total_revenue,
            'monthly_revenue': monthly_revenue
        }

# Global subscription manager instance
subscription_manager = PremiumSubscriptionManager()

# Create demo users
demo_users = [
    ('user_001', 'trader1@example.com', '123456789'),
    ('user_002', 'trader2@example.com', '987654321'),
    ('user_003', 'trader3@example.com', '456789123')
]

for user_id, email, telegram_id in demo_users:
    if user_id not in subscription_manager.users:
        subscription_manager.create_user(user_id, email, telegram_id)