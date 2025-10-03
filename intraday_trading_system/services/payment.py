"""
Payment Integration System
Handles Razorpay payment processing for subscriptions
"""

import razorpay
import hashlib
import hmac
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from models.user import UserManager, SubscriptionPlan

class PaymentManager:
    """Manages subscription payments and Razorpay integration"""
    
    def __init__(self, razorpay_key: str, razorpay_secret: str, user_manager: UserManager):
        self.client = razorpay.Client(auth=(razorpay_key, razorpay_secret))
        self.user_manager = user_manager
        self.razorpay_secret = razorpay_secret
    
    def create_subscription_order(self, user_id: int, plan_id: int) -> Dict[str, Any]:
        """Create Razorpay order for subscription payment"""
        try:
            # Get user details
            user = self.user_manager.get_user_by_id(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Get subscription plan
            plans = self.user_manager.get_subscription_plans()
            plan = next((p for p in plans if p.id == plan_id), None)
            if not plan:
                return {'success': False, 'message': 'Subscription plan not found'}
            
            # Create Razorpay order
            order_data = {
                'amount': int(plan.price * 100),  # Amount in paise
                'currency': 'INR',
                'receipt': f'sub_{user_id}_{plan_id}_{int(datetime.now().timestamp())}',
                'notes': {
                    'user_id': user_id,
                    'plan_id': plan_id,
                    'plan_name': plan.name,
                    'user_email': user.email,
                    'user_phone': user.phone
                }
            }
            
            order = self.client.order.create(data=order_data)
            
            return {
                'success': True,
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'plan_name': plan.name,
                'plan_duration': plan.duration_days,
                'user_email': user.email,
                'user_phone': user.phone,
                'user_name': user.username
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Payment order creation failed: {str(e)}'}
    
    def verify_payment_signature(self, payment_data: Dict[str, str]) -> bool:
        """Verify Razorpay payment signature"""
        try:
            # Required fields
            razorpay_order_id = payment_data.get('razorpay_order_id')
            razorpay_payment_id = payment_data.get('razorpay_payment_id')
            razorpay_signature = payment_data.get('razorpay_signature')
            
            if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
                return False
            
            # Create signature
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            expected_signature = hmac.new(
                self.razorpay_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, razorpay_signature)
            
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False
    
    def process_successful_payment(self, payment_data: Dict[str, str]) -> Dict[str, Any]:
        """Process successful payment and activate subscription"""
        try:
            # Verify signature first
            if not self.verify_payment_signature(payment_data):
                return {'success': False, 'message': 'Invalid payment signature'}
            
            razorpay_payment_id = payment_data['razorpay_payment_id']
            razorpay_order_id = payment_data['razorpay_order_id']
            
            # Get payment details from Razorpay
            payment_info = self.client.payment.fetch(razorpay_payment_id)
            order_info = self.client.order.fetch(razorpay_order_id)
            
            if payment_info['status'] != 'captured':
                return {'success': False, 'message': 'Payment not captured'}
            
            # Extract user and plan info from order notes
            user_id = int(order_info['notes']['user_id'])
            plan_id = int(order_info['notes']['plan_id'])
            
            # Record payment in database
            self._record_payment(user_id, plan_id, payment_info)
            
            # Activate subscription
            success = self.user_manager.activate_subscription(user_id, plan_id, razorpay_payment_id)
            
            if success:
                # Send confirmation notification
                self._send_subscription_confirmation(user_id, plan_id)
                
                return {
                    'success': True,
                    'message': 'Subscription activated successfully',
                    'payment_id': razorpay_payment_id,
                    'user_id': user_id,
                    'plan_id': plan_id
                }
            else:
                return {'success': False, 'message': 'Failed to activate subscription'}
                
        except Exception as e:
            return {'success': False, 'message': f'Payment processing error: {str(e)}'}
    
    def _record_payment(self, user_id: int, plan_id: int, payment_info: Dict):
        """Record payment in database"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.user_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO payments (user_id, plan_id, payment_id, amount, status, payment_method)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                plan_id,
                payment_info['id'],
                payment_info['amount'] / 100,  # Convert from paise to rupees
                'completed',
                payment_info.get('method', 'unknown')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error recording payment: {e}")
    
    def _send_subscription_confirmation(self, user_id: int, plan_id: int):
        """Send subscription confirmation via Telegram"""
        try:
            user = self.user_manager.get_user_by_id(user_id)
            plans = self.user_manager.get_subscription_plans()
            plan = next((p for p in plans if p.id == plan_id), None)
            
            if user and plan and user.telegram_chat_id:
                # Import telegram bot here to avoid circular imports
                from bot.telegram_bot import TelegramBot
                from config.settings import config
                
                telegram_bot = TelegramBot(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID)
                
                message = f"""
🎉 <b>SUBSCRIPTION ACTIVATED</b> 🎉

✅ <b>Welcome to Premium!</b>

👤 <b>User:</b> {user.username}
📱 <b>Plan:</b> {plan.name}
💰 <b>Amount:</b> ₹{plan.price}
⏰ <b>Valid Until:</b> {user.subscription_end.strftime('%d %B %Y') if user.subscription_end else 'N/A'}

🚀 <b>Premium Benefits Activated:</b>
• Live intraday signals (9:15 AM - 3:30 PM)
• Real-time Telegram alerts
• Precise entry/exit/stop-loss levels
• Technical analysis insights
• Performance tracking
• Priority customer support

📈 <b>Happy Trading!</b>
                """
                
                # Send to user if they have telegram chat ID
                if user.telegram_chat_id:
                    telegram_bot.send_message(message, user.telegram_chat_id)
                
        except Exception as e:
            print(f"Error sending confirmation: {e}")
    
    def handle_webhook(self, webhook_body: str, webhook_signature: str) -> Dict[str, Any]:
        """Handle Razorpay webhook events"""
        try:
            # Verify webhook signature
            expected_signature = hmac.new(
                self.razorpay_secret.encode(),
                webhook_body.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(expected_signature, webhook_signature):
                return {'success': False, 'message': 'Invalid webhook signature'}
            
            # Parse webhook data
            webhook_data = json.loads(webhook_body)
            event = webhook_data.get('event')
            
            if event == 'payment.captured':
                # Handle successful payment
                payment = webhook_data['payload']['payment']['entity']
                order_id = payment['order_id']
                
                # Get order details
                order_info = self.client.order.fetch(order_id)
                user_id = int(order_info['notes']['user_id'])
                plan_id = int(order_info['notes']['plan_id'])
                
                # Record payment and activate subscription
                self._record_payment(user_id, plan_id, payment)
                self.user_manager.activate_subscription(user_id, plan_id, payment['id'])
                self._send_subscription_confirmation(user_id, plan_id)
                
                return {'success': True, 'message': 'Payment processed'}
            
            elif event == 'payment.failed':
                # Handle failed payment
                payment = webhook_data['payload']['payment']['entity']
                print(f"Payment failed: {payment['id']}")
                return {'success': True, 'message': 'Payment failure recorded'}
            
            return {'success': True, 'message': 'Webhook processed'}
            
        except Exception as e:
            return {'success': False, 'message': f'Webhook error: {str(e)}'}
    
    def get_payment_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Get payment history for user"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.user_manager.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.*, sp.name as plan_name 
                FROM payments p
                JOIN subscription_plans sp ON p.plan_id = sp.id
                WHERE p.user_id = ?
                ORDER BY p.created_at DESC
            ''', (user_id,))
            
            payments = []
            for row in cursor.fetchall():
                payments.append({
                    'id': row[0],
                    'plan_name': row[8],
                    'amount': row[4],
                    'status': row[5],
                    'payment_method': row[6],
                    'created_at': row[7]
                })
            
            conn.close()
            return payments
            
        except Exception as e:
            print(f"Error getting payment history: {e}")
            return []
    
    def cancel_subscription(self, user_id: int) -> Dict[str, Any]:
        """Cancel user subscription"""
        try:
            from models.user import SubscriptionStatus
            
            user = self.user_manager.get_user_by_id(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            # Update subscription status
            self.user_manager.update_subscription_status(user_id, SubscriptionStatus.CANCELLED)
            
            # Send cancellation notification
            if user.telegram_chat_id:
                from bot.telegram_bot import TelegramBot
                from config.settings import config
                
                telegram_bot = TelegramBot(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID)
                
                message = f"""
❌ <b>SUBSCRIPTION CANCELLED</b>

👤 <b>User:</b> {user.username}
📅 <b>Cancelled On:</b> {datetime.now().strftime('%d %B %Y')}

🔔 <b>Important:</b>
• Your subscription has been cancelled
• Premium features will remain active until {user.subscription_end.strftime('%d %B %Y') if user.subscription_end else 'N/A'}
• You can reactivate anytime before expiry

💬 <b>Need Help?</b> Contact our support team.
                """
                
                telegram_bot.send_message(message, user.telegram_chat_id)
            
            return {'success': True, 'message': 'Subscription cancelled successfully'}
            
        except Exception as e:
            return {'success': False, 'message': f'Cancellation error: {str(e)}'}
    
    def get_revenue_stats(self) -> Dict[str, Any]:
        """Get revenue statistics for admin dashboard"""
        try:
            import sqlite3
            conn = sqlite3.connect(self.user_manager.db_path)
            cursor = conn.cursor()
            
            # Total revenue
            cursor.execute('SELECT SUM(amount) FROM payments WHERE status = "completed"')
            total_revenue = cursor.fetchone()[0] or 0
            
            # Monthly revenue
            cursor.execute('''
                SELECT SUM(amount) FROM payments 
                WHERE status = "completed" 
                AND DATE(created_at) >= DATE('now', 'start of month')
            ''')
            monthly_revenue = cursor.fetchone()[0] or 0
            
            # Today's revenue
            cursor.execute('''
                SELECT SUM(amount) FROM payments 
                WHERE status = "completed" 
                AND DATE(created_at) = DATE('now')
            ''')
            daily_revenue = cursor.fetchone()[0] or 0
            
            # Payment method breakdown
            cursor.execute('''
                SELECT payment_method, COUNT(*), SUM(amount) 
                FROM payments 
                WHERE status = "completed" 
                GROUP BY payment_method
            ''')
            payment_methods = {}
            for row in cursor.fetchall():
                payment_methods[row[0]] = {'count': row[1], 'amount': row[2]}
            
            conn.close()
            
            return {
                'total_revenue': total_revenue,
                'monthly_revenue': monthly_revenue,
                'daily_revenue': daily_revenue,
                'payment_methods': payment_methods
            }
            
        except Exception as e:
            print(f"Error getting revenue stats: {e}")
            return {}