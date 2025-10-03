"""
User Management Models
Handles user authentication, subscriptions, and premium access
"""

import sqlite3
import hashlib
import jwt
import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import os

class UserRole(Enum):
    FREE = "free"
    PREMIUM = "premium"
    ADMIN = "admin"

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"

@dataclass
class User:
    id: int
    username: str
    email: str
    phone: str
    role: UserRole
    subscription_status: SubscriptionStatus
    subscription_start: Optional[datetime.datetime]
    subscription_end: Optional[datetime.datetime]
    created_at: datetime.datetime
    last_login: Optional[datetime.datetime]
    is_active: bool = True
    payment_id: Optional[str] = None
    telegram_chat_id: Optional[str] = None

@dataclass
class SubscriptionPlan:
    id: int
    name: str
    price: float
    duration_days: int
    features: List[str]
    is_active: bool = True

class UserManager:
    """Manages user authentication and subscription system"""
    
    def __init__(self, db_path: str, secret_key: str):
        self.db_path = db_path
        self.secret_key = secret_key
        self.init_database()
    
    def init_database(self):
        """Initialize user management database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'free',
                subscription_status TEXT DEFAULT 'expired',
                subscription_start TIMESTAMP NULL,
                subscription_end TIMESTAMP NULL,
                payment_id TEXT NULL,
                telegram_chat_id TEXT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Subscription plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscription_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                duration_days INTEGER NOT NULL,
                features TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Payment history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_id INTEGER NOT NULL,
                payment_id TEXT UNIQUE NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                payment_method TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (plan_id) REFERENCES subscription_plans (id)
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Insert default subscription plans
        self.create_default_plans()
    
    def create_default_plans(self):
        """Create default subscription plans"""
        plans = [
            {
                'name': 'Monthly Premium',
                'price': 999.0,
                'duration_days': 30,
                'features': [
                    'Live intraday signals (9:15 AM - 3:30 PM)',
                    'Real-time Telegram alerts',
                    'Entry/Exit/Stop-loss levels',
                    'Technical analysis insights',
                    'Performance tracking',
                    'Customer support'
                ]
            },
            {
                'name': 'Quarterly Premium',
                'price': 2499.0,
                'duration_days': 90,
                'features': [
                    'All Monthly Premium features',
                    'Advanced technical analysis',
                    'Market trend analysis',
                    'Priority customer support',
                    '15% discount vs monthly'
                ]
            },
            {
                'name': 'Annual Premium',
                'price': 7999.0,
                'duration_days': 365,
                'features': [
                    'All Quarterly Premium features',
                    'Exclusive market insights',
                    'Direct access to trading team',
                    'Custom alerts and notifications',
                    '33% discount vs monthly'
                ]
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for plan in plans:
            cursor.execute('''
                INSERT OR IGNORE INTO subscription_plans (name, price, duration_days, features)
                VALUES (?, ?, ?, ?)
            ''', (plan['name'], plan['price'], plan['duration_days'], str(plan['features'])))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, phone: str, password: str) -> Dict[str, Any]:
        """Create new user account"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, email, phone, password_hash)
                VALUES (?, ?, ?, ?)
            ''', (username, email, phone, password_hash))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'user_id': user_id,
                'message': 'User created successfully'
            }
        except sqlite3.IntegrityError as e:
            return {
                'success': False,
                'message': 'Username, email, or phone already exists'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating user: {str(e)}'
            }
    
    def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user login"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT * FROM users 
                WHERE (username = ? OR email = ?) AND password_hash = ? AND is_active = 1
            ''', (username, username, password_hash))
            
            user_data = cursor.fetchone()
            
            if user_data:
                # Update last login
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                ''', (user_data[0],))
                conn.commit()
                
                # Generate JWT token
                token = self.generate_jwt_token(user_data[0])
                
                user = {
                    'id': user_data[0],
                    'username': user_data[1],
                    'email': user_data[2],
                    'phone': user_data[3],
                    'role': user_data[5],
                    'subscription_status': user_data[6],
                    'subscription_end': user_data[8],
                    'token': token
                }
                
                conn.close()
                return {
                    'success': True,
                    'user': user,
                    'message': 'Login successful'
                }
            else:
                conn.close()
                return {
                    'success': False,
                    'message': 'Invalid credentials'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Login error: {str(e)}'
            }
    
    def generate_jwt_token(self, user_id: int) -> str:
        """Generate JWT token for user session"""
        payload = {
            'user_id': user_id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)  # Token expires in 7 days
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[int]:
        """Verify JWT token and return user ID"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                return User(
                    id=user_data[0],
                    username=user_data[1],
                    email=user_data[2],
                    phone=user_data[3],
                    role=UserRole(user_data[5]),
                    subscription_status=SubscriptionStatus(user_data[6]),
                    subscription_start=datetime.datetime.fromisoformat(user_data[7]) if user_data[7] else None,
                    subscription_end=datetime.datetime.fromisoformat(user_data[8]) if user_data[8] else None,
                    created_at=datetime.datetime.fromisoformat(user_data[12]),
                    last_login=datetime.datetime.fromisoformat(user_data[13]) if user_data[13] else None,
                    is_active=bool(user_data[14]),
                    payment_id=user_data[9],
                    telegram_chat_id=user_data[10]
                )
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def has_premium_access(self, user_id: int) -> bool:
        """Check if user has active premium subscription"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        if user.role == UserRole.ADMIN:
            return True
        
        if user.subscription_status != SubscriptionStatus.ACTIVE:
            return False
        
        if user.subscription_end and user.subscription_end < datetime.datetime.now():
            # Update expired subscription
            self.update_subscription_status(user_id, SubscriptionStatus.EXPIRED)
            return False
        
        return True
    
    def update_subscription_status(self, user_id: int, status: SubscriptionStatus):
        """Update user subscription status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET subscription_status = ? WHERE id = ?
            ''', (status.value, user_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating subscription status: {e}")
    
    def activate_subscription(self, user_id: int, plan_id: int, payment_id: str) -> bool:
        """Activate premium subscription for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get plan details
            cursor.execute('SELECT duration_days FROM subscription_plans WHERE id = ?', (plan_id,))
            plan_data = cursor.fetchone()
            
            if not plan_data:
                return False
            
            duration_days = plan_data[0]
            start_date = datetime.datetime.now()
            end_date = start_date + datetime.timedelta(days=duration_days)
            
            # Update user subscription
            cursor.execute('''
                UPDATE users SET 
                    role = 'premium',
                    subscription_status = 'active',
                    subscription_start = ?,
                    subscription_end = ?,
                    payment_id = ?
                WHERE id = ?
            ''', (start_date.isoformat(), end_date.isoformat(), payment_id, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error activating subscription: {e}")
            return False
    
    def get_subscription_plans(self) -> List[SubscriptionPlan]:
        """Get all active subscription plans"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, price, duration_days, features 
                FROM subscription_plans 
                WHERE is_active = 1
                ORDER BY price ASC
            ''')
            
            plans = []
            for row in cursor.fetchall():
                plans.append(SubscriptionPlan(
                    id=row[0],
                    name=row[1],
                    price=row[2],
                    duration_days=row[3],
                    features=eval(row[4])  # Convert string back to list
                ))
            
            conn.close()
            return plans
        except Exception as e:
            print(f"Error getting subscription plans: {e}")
            return []
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics for admin dashboard"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total users
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            # Premium users
            cursor.execute("SELECT COUNT(*) FROM users WHERE subscription_status = 'active'")
            premium_users = cursor.fetchone()[0]
            
            # New users today
            cursor.execute('SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE("now")')
            new_users_today = cursor.fetchone()[0]
            
            # Total revenue
            cursor.execute('SELECT SUM(amount) FROM payments WHERE status = "completed"')
            total_revenue = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_users': total_users,
                'premium_users': premium_users,
                'free_users': total_users - premium_users,
                'new_users_today': new_users_today,
                'total_revenue': total_revenue,
                'conversion_rate': (premium_users / total_users * 100) if total_users > 0 else 0
            }
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {}