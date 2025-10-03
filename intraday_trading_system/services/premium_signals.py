"""
Premium Signal Manager
Handles premium signal filtering and access control
"""

import datetime
from typing import List, Dict, Any, Optional
from models.user import UserManager, UserRole, SubscriptionStatus

class PremiumSignalManager:
    """Manages premium signal access and filtering"""
    
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager
        self.market_start_time = datetime.time(9, 15)  # 9:15 AM
        self.market_end_time = datetime.time(15, 30)   # 3:30 PM
    
    def is_market_hours(self) -> bool:
        """Check if current time is within market hours (9:15 AM - 3:30 PM)"""
        now = datetime.datetime.now().time()
        return self.market_start_time <= now <= self.market_end_time
    
    def is_trading_day(self) -> bool:
        """Check if today is a trading day (Monday-Friday)"""
        return datetime.datetime.now().weekday() < 5
    
    def can_access_premium_signals(self, user_id: Optional[int]) -> Dict[str, Any]:
        """Check if user can access premium signals with detailed response"""
        if not user_id:
            return {
                'access': False,
                'reason': 'login_required',
                'message': 'Please login to access premium signals',
                'action': 'redirect_login'
            }
        
        user = self.user_manager.get_user_by_id(user_id)
        if not user:
            return {
                'access': False,
                'reason': 'user_not_found',
                'message': 'User account not found',
                'action': 'redirect_login'
            }
        
        # Admin always has access
        if user.role == UserRole.ADMIN:
            return {
                'access': True,
                'reason': 'admin_access',
                'message': 'Admin access granted'
            }
        
        # Check subscription status
        if user.subscription_status != SubscriptionStatus.ACTIVE:
            return {
                'access': False,
                'reason': 'subscription_inactive',
                'message': 'Premium subscription required for live signals',
                'action': 'upgrade_subscription',
                'subscription_status': user.subscription_status.value
            }
        
        # Check subscription expiry
        if user.subscription_end and user.subscription_end < datetime.datetime.now():
            # Update expired subscription
            self.user_manager.update_subscription_status(user.id, SubscriptionStatus.EXPIRED)
            return {
                'access': False,
                'reason': 'subscription_expired',
                'message': 'Your subscription has expired. Please renew to continue receiving signals',
                'action': 'renew_subscription',
                'expired_date': user.subscription_end.isoformat()
            }
        
        # Check market hours for live signals
        if not self.is_trading_day():
            return {
                'access': True,
                'reason': 'non_trading_day',
                'message': 'Markets are closed today. Historical signals available.',
                'live_signals': False
            }
        
        if not self.is_market_hours():
            return {
                'access': True,
                'reason': 'outside_market_hours',
                'message': 'Live signals available during market hours (9:15 AM - 3:30 PM)',
                'live_signals': False,
                'next_market_open': self._get_next_market_open()
            }
        
        return {
            'access': True,
            'reason': 'premium_active',
            'message': 'Premium access granted - Live signals active',
            'live_signals': True
        }
    
    def _get_next_market_open(self) -> str:
        """Get next market opening time"""
        now = datetime.datetime.now()
        
        # If it's a weekday before 9:15 AM, next opening is today
        if now.weekday() < 5 and now.time() < self.market_start_time:
            next_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        else:
            # Find next weekday
            days_ahead = 1
            while (now + datetime.timedelta(days=days_ahead)).weekday() >= 5:
                days_ahead += 1
            next_open = (now + datetime.timedelta(days=days_ahead)).replace(
                hour=9, minute=15, second=0, microsecond=0
            )
        
        return next_open.isoformat()
    
    def filter_signals_for_user(self, signals: List[Dict], user_id: Optional[int]) -> Dict[str, Any]:
        """Filter signals based on user subscription status"""
        access_check = self.can_access_premium_signals(user_id)
        
        if not access_check['access']:
            # Return sample/demo signals for free users
            demo_signals = self._get_demo_signals(signals)
            return {
                'signals': demo_signals,
                'access_info': access_check,
                'is_premium': False,
                'total_signals': len(signals),
                'available_signals': len(demo_signals)
            }
        
        # Premium user gets all signals
        return {
            'signals': signals,
            'access_info': access_check,
            'is_premium': True,
            'total_signals': len(signals),
            'available_signals': len(signals)
        }
    
    def _get_demo_signals(self, signals: List[Dict], limit: int = 2) -> List[Dict[str, Any]]:
        """Get demo/sample signals for free users with limited information"""
        demo_signals = []
        
        for i, signal in enumerate(signals[:limit]):
            demo_signal = {
                'id': signal.get('id', i+1),
                'timestamp': signal.get('timestamp', datetime.datetime.now().isoformat()),
                'instrument': signal.get('instrument', 'NIFTY'),
                'signal_type': signal.get('signal_type', 'BUY'),
                'entry_price': 'Premium Only',
                'target_price': 'Premium Only',
                'stop_loss': 'Premium Only',
                'confidence': 'Premium Only',
                'is_demo': True,
                'message': 'Upgrade to Premium to see full signal details'
            }
            demo_signals.append(demo_signal)
        
        return demo_signals
    
    def get_signal_access_message(self, user_id: Optional[int]) -> Dict[str, Any]:
        """Get user-specific message about signal access"""
        access_check = self.can_access_premium_signals(user_id)
        
        messages = {
            'login_required': {
                'title': 'Login Required',
                'message': 'Please login to access trading signals',
                'button_text': 'Login Now',
                'button_action': 'login'
            },
            'subscription_inactive': {
                'title': 'Premium Subscription Required',
                'message': 'Upgrade to Premium to receive live intraday trading signals during market hours (9:15 AM - 3:30 PM)',
                'button_text': 'Upgrade to Premium',
                'button_action': 'subscribe'
            },
            'subscription_expired': {
                'title': 'Subscription Expired',
                'message': 'Your premium subscription has expired. Renew now to continue receiving live trading signals.',
                'button_text': 'Renew Subscription',
                'button_action': 'renew'
            },
            'non_trading_day': {
                'title': 'Markets Closed',
                'message': 'Markets are closed today. Check back on the next trading day for live signals.',
                'button_text': 'View Historical Signals',
                'button_action': 'history'
            },
            'outside_market_hours': {
                'title': 'Outside Market Hours',
                'message': 'Live signals are available during market hours (9:15 AM - 3:30 PM IST).',
                'button_text': 'Set Alert',
                'button_action': 'alert'
            },
            'premium_active': {
                'title': 'Live Signals Active',
                'message': 'Premium subscription active. Receiving live intraday signals during market hours.',
                'button_text': 'View Signals',
                'button_action': 'signals'
            }
        }
        
        return messages.get(access_check['reason'], {
            'title': 'Unknown Status',
            'message': 'Unable to determine signal access status',
            'button_text': 'Contact Support',
            'button_action': 'support'
        })
    
    def log_signal_access_attempt(self, user_id: Optional[int], signal_id: int, granted: bool):
        """Log signal access attempts for analytics"""
        # This could be extended to log to database for analytics
        timestamp = datetime.datetime.now().isoformat()
        print(f"[{timestamp}] Signal Access: User {user_id} -> Signal {signal_id} -> {'GRANTED' if granted else 'DENIED'}")
    
    def get_subscription_benefits(self) -> List[Dict[str, Any]]:
        """Get list of premium subscription benefits"""
        return [
            {
                'icon': '📈',
                'title': 'Live Intraday Signals',
                'description': 'Real-time BUY/SELL signals during market hours (9:15 AM - 3:30 PM)'
            },
            {
                'icon': '🎯',
                'title': 'Precise Entry/Exit Points',
                'description': 'Exact entry price, target levels, and stop-loss for every signal'
            },
            {
                'icon': '📱',
                'title': 'Instant Telegram Alerts',
                'description': 'Get signals instantly on your mobile via Telegram notifications'
            },
            {
                'icon': '📊',
                'title': 'Technical Analysis',
                'description': 'Detailed technical analysis with RSI, MACD, Bollinger Bands insights'
            },
            {
                'icon': '⚡',
                'title': 'High Confidence Signals',
                'description': 'Only signals with 70%+ confidence based on multiple indicators'
            },
            {
                'icon': '📈',
                'title': 'Performance Tracking',
                'description': 'Track your trading performance with detailed analytics'
            },
            {
                'icon': '🛡️',
                'title': 'Risk Management',
                'description': 'Built-in risk management with optimal position sizing'
            },
            {
                'icon': '🎁',
                'title': 'Premium Support',
                'description': 'Priority customer support and direct access to trading team'
            }
        ]