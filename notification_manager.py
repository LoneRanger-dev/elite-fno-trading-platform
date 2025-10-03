"""
Notification Manager
Handles notifications with multiple fallback channels
"""

import smtplib
import requests
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import threading
import queue
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, config: Dict):
        self.config = config
        
        # Initialize channels
        self.telegram_enabled = bool(config.get('telegram_token'))
        self.email_enabled = bool(config.get('email_settings'))
        self.webhook_enabled = bool(config.get('webhook_url'))
        
        # Notification queue
        self.queue = queue.Queue()
        self.is_running = False
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self._process_notifications)
        self.worker_thread.daemon = True
        
        # Notification history
        self.history = []
        self.max_history = 1000
        
        # Rate limiting
        self.rate_limits = {
            'telegram': {'count': 0, 'reset_time': time.time(), 'max_per_minute': 30},
            'email': {'count': 0, 'reset_time': time.time(), 'max_per_minute': 10},
            'webhook': {'count': 0, 'reset_time': time.time(), 'max_per_minute': 60}
        }
        
    def start(self):
        """Start notification processing"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread.start()
            logger.info("Notification manager started")
            
    def stop(self):
        """Stop notification processing"""
        self.is_running = False
        if self.worker_thread.is_alive():
            self.worker_thread.join()
            
    def send_notification(self, message: str, level: str = 'info', 
                        channels: List[str] = None):
        """Queue a notification for sending"""
        try:
            notification = {
                'message': message,
                'level': level,
                'channels': channels or ['telegram', 'email', 'webhook'],
                'timestamp': datetime.now().isoformat()
            }
            
            self.queue.put(notification)
            
        except Exception as e:
            logger.error(f"Error queueing notification: {e}")
            
    def _process_notifications(self):
        """Process notification queue"""
        while self.is_running:
            try:
                # Get next notification
                notification = self.queue.get(timeout=1)
                
                success = False
                tried_channels = []
                
                # Try each channel in order
                for channel in notification['channels']:
                    if self._can_send(channel):
                        success = self._send_via_channel(channel, notification)
                        tried_channels.append(channel)
                        if success:
                            break
                            
                # Log result
                self._log_notification(notification, success, tried_channels)
                
                # Store in history
                self._store_notification(notification, success, tried_channels)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing notification: {e}")
                
    def _can_send(self, channel: str) -> bool:
        """Check if we can send via channel (rate limiting)"""
        try:
            limit = self.rate_limits[channel]
            now = time.time()
            
            # Reset counter if minute has passed
            if now - limit['reset_time'] > 60:
                limit['count'] = 0
                limit['reset_time'] = now
                
            # Check if under limit
            return limit['count'] < limit['max_per_minute']
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False
            
    def _send_via_channel(self, channel: str, notification: Dict) -> bool:
        """Send notification via specified channel"""
        try:
            if channel == 'telegram' and self.telegram_enabled:
                success = self._send_telegram(notification)
            elif channel == 'email' and self.email_enabled:
                success = self._send_email(notification)
            elif channel == 'webhook' and self.webhook_enabled:
                success = self._send_webhook(notification)
            else:
                return False
                
            if success:
                self.rate_limits[channel]['count'] += 1
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending via {channel}: {e}")
            return False
            
    def _send_telegram(self, notification: Dict) -> bool:
        """Send notification via Telegram"""
        try:
            token = self.config['telegram_token']
            chat_id = self.config['telegram_chat_id']
            
            formatted_message = self._format_telegram_message(notification)
            
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': formatted_message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=data, timeout=5)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False
            
    def _send_email(self, notification: Dict) -> bool:
        """Send notification via email"""
        try:
            settings = self.config['email_settings']
            
            msg = MIMEMultipart()
            msg['From'] = settings['from_email']
            msg['To'] = settings['to_email']
            msg['Subject'] = f"Trading Alert: {notification['level'].upper()}"
            
            body = self._format_email_message(notification)
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(settings['smtp_server'], settings['smtp_port']) as server:
                if settings.get('use_tls'):
                    server.starttls()
                if settings.get('username'):
                    server.login(settings['username'], settings['password'])
                server.send_message(msg)
                
            return True
            
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return False
            
    def _send_webhook(self, notification: Dict) -> bool:
        """Send notification via webhook"""
        try:
            webhook_url = self.config['webhook_url']
            
            payload = {
                'level': notification['level'],
                'message': notification['message'],
                'timestamp': notification['timestamp']
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Webhook send error: {e}")
            return False
            
    def _format_telegram_message(self, notification: Dict) -> str:
        """Format message for Telegram"""
        level_emoji = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '🚨',
            'success': '✅'
        }
        
        emoji = level_emoji.get(notification['level'], 'ℹ️')
        return f"{emoji} *{notification['level'].upper()}*\n{notification['message']}"
        
    def _format_email_message(self, notification: Dict) -> str:
        """Format message for email"""
        return f"""
Trading System Notification

Level: {notification['level'].upper()}
Time: {notification['timestamp']}

Message:
{notification['message']}

---
This is an automated notification from your trading system.
"""
        
    def _log_notification(self, notification: Dict, success: bool, 
                         tried_channels: List[str]):
        """Log notification result"""
        if success:
            logger.info(f"Notification sent via {tried_channels[-1]}")
        else:
            logger.error(f"Failed to send notification via {tried_channels}")
            
    def _store_notification(self, notification: Dict, success: bool, 
                          tried_channels: List[str]):
        """Store notification in history"""
        try:
            entry = {
                **notification,
                'success': success,
                'tried_channels': tried_channels,
                'successful_channel': tried_channels[-1] if success else None
            }
            
            self.history.append(entry)
            
            # Trim history if needed
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]
                
        except Exception as e:
            logger.error(f"Error storing notification: {e}")
            
    def get_notification_history(self, limit: int = 100) -> List[Dict]:
        """Get recent notification history"""
        return self.history[-limit:]