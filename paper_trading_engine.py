"""
🎯 Elite Paper Trading Engine
Virtual trading system for customers to practice risk-free
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import uuid
import random

logger = logging.getLogger(__name__)

class PaperTradingEngine:
    def __init__(self, initial_capital: float = 100000.0):
        self.data_file = "paper_trading_data.json"
        self.accounts = {}
        self.initial_capital = initial_capital
        self.load_data()
    
    def load_data(self):
        """Load paper trading data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.accounts = data.get('accounts', {})
            else:
                self.accounts = {}
        except Exception as e:
            logger.error(f"Error loading paper trading data: {e}")
            self.accounts = {}
    
    def save_data(self):
        """Save paper trading data to file"""
        try:
            data = {
                'accounts': self.accounts,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving paper trading data: {e}")
    
    def create_portfolio(self, user_id: str, initial_balance: float = 100000.0) -> Dict:
        """Create a new paper trading portfolio"""
        portfolio = {
            'user_id': user_id,
            'balance': initial_balance,
            'initial_balance': initial_balance,
            'positions': {},
            'trade_history': [],
            'pnl': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'max_profit': 0.0,
            'max_loss': 0.0,
            'created_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat()
        }
        
        self.accounts[user_id] = portfolio
        self.save_data()
        
        logger.info(f"Created paper trading portfolio for user {user_id}")
        return portfolio
    
    def get_portfolio(self, user_id: str) -> Optional[Dict]:
        """Get user's paper trading portfolio"""
        return self.portfolios.get(user_id)
    
    def place_order(self, user_id: str, symbol: str, quantity: int, 
                   price: float, order_type: str = "BUY") -> Dict:
        """Place a paper trading order"""
        if user_id not in self.portfolios:
            self.create_portfolio(user_id)
        
        portfolio = self.portfolios[user_id]
        order_value = quantity * price
        
        # Generate order ID
        order_id = str(uuid.uuid4())[:8]
        
        # Check if user has enough balance for BUY orders
        if order_type == "BUY" and portfolio['balance'] < order_value:
            return {
                'success': False,
                'message': 'Insufficient balance',
                'required': order_value,
                'available': portfolio['balance']
            }
        
        # Check if user has the position for SELL orders
        if order_type == "SELL":
            if symbol not in portfolio['positions'] or portfolio['positions'][symbol]['quantity'] < quantity:
                return {
                    'success': False,
                    'message': 'Insufficient quantity to sell',
                    'available': portfolio['positions'].get(symbol, {}).get('quantity', 0)
                }
        
        # Execute the order
        trade = {
            'order_id': order_id,
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'order_type': order_type,
            'timestamp': datetime.now().isoformat(),
            'status': 'EXECUTED'
        }
        
        if order_type == "BUY":
            # Deduct money and add position
            portfolio['balance'] -= order_value
            
            if symbol in portfolio['positions']:
                # Average price calculation
                existing_qty = portfolio['positions'][symbol]['quantity']
                existing_price = portfolio['positions'][symbol]['avg_price']
                total_qty = existing_qty + quantity
                avg_price = ((existing_qty * existing_price) + (quantity * price)) / total_qty
                
                portfolio['positions'][symbol] = {
                    'quantity': total_qty,
                    'avg_price': avg_price,
                    'current_price': price,
                    'invested_amount': total_qty * avg_price,
                    'current_value': total_qty * price,
                    'pnl': (price - avg_price) * total_qty,
                    'last_updated': datetime.now().isoformat()
                }
            else:
                portfolio['positions'][symbol] = {
                    'quantity': quantity,
                    'avg_price': price,
                    'current_price': price,
                    'invested_amount': order_value,
                    'current_value': order_value,
                    'pnl': 0.0,
                    'last_updated': datetime.now().isoformat()
                }
        
        elif order_type == "SELL":
            # Add money back and reduce position
            portfolio['balance'] += order_value
            position = portfolio['positions'][symbol]
            
            # Calculate P&L for this trade
            trade_pnl = (price - position['avg_price']) * quantity
            
            # Update position
            remaining_qty = position['quantity'] - quantity
            if remaining_qty > 0:
                portfolio['positions'][symbol]['quantity'] = remaining_qty
                portfolio['positions'][symbol]['current_price'] = price
                portfolio['positions'][symbol]['current_value'] = remaining_qty * price
                portfolio['positions'][symbol]['pnl'] = (price - position['avg_price']) * remaining_qty
            else:
                # Position closed completely
                del portfolio['positions'][symbol]
            
            # Update trade statistics
            portfolio['total_trades'] += 1
            if trade_pnl > 0:
                portfolio['winning_trades'] += 1
                if trade_pnl > portfolio['max_profit']:
                    portfolio['max_profit'] = trade_pnl
            else:
                portfolio['losing_trades'] += 1
                if trade_pnl < portfolio['max_loss']:
                    portfolio['max_loss'] = trade_pnl
            
            portfolio['win_rate'] = (portfolio['winning_trades'] / portfolio['total_trades']) * 100
            trade['pnl'] = trade_pnl
        
        # Add to trade history
        portfolio['trade_history'].append(trade)
        portfolio['last_activity'] = datetime.now().isoformat()
        
        # Calculate total P&L
        total_pnl = portfolio['balance'] - portfolio['initial_balance']
        for pos in portfolio['positions'].values():
            total_pnl += pos['pnl']
        portfolio['pnl'] = total_pnl
        
        self.save_data()
        
        return {
            'success': True,
            'message': f'{order_type} order executed successfully',
            'order_id': order_id,
            'trade': trade,
            'portfolio_summary': {
                'balance': portfolio['balance'],
                'total_pnl': portfolio['pnl'],
                'positions': len(portfolio['positions'])
            }
        }
    
    def update_market_prices(self, price_data: Dict[str, float]):
        """Update current market prices for all positions"""
        for user_id, portfolio in self.portfolios.items():
            for symbol, position in portfolio['positions'].items():
                if symbol in price_data:
                    new_price = price_data[symbol]
                    position['current_price'] = new_price
                    position['current_value'] = position['quantity'] * new_price
                    position['pnl'] = (new_price - position['avg_price']) * position['quantity']
                    position['last_updated'] = datetime.now().isoformat()
        
        self.save_data()
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top performers leaderboard"""
        users = []
        for user_id, portfolio in self.portfolios.items():
            # Calculate current portfolio value
            current_value = portfolio['balance']
            for position in portfolio['positions'].values():
                current_value += position['current_value']
            
            return_pct = ((current_value - portfolio['initial_balance']) / portfolio['initial_balance']) * 100
            
            users.append({
                'user_id': user_id,
                'portfolio_value': current_value,
                'initial_balance': portfolio['initial_balance'],
                'pnl': current_value - portfolio['initial_balance'],
                'return_percentage': return_pct,
                'total_trades': portfolio['total_trades'],
                'win_rate': portfolio['win_rate'],
                'max_profit': portfolio['max_profit'],
                'max_loss': portfolio['max_loss']
            })
        
        # Sort by return percentage
        users.sort(key=lambda x: x['return_percentage'], reverse=True)
        return users[:limit]
    
    def generate_demo_data(self):
        """Generate demo portfolios for demonstration"""
        demo_users = [
            ('demo_trader_1', 150000, 250),
            ('demo_trader_2', 120000, 180),
            ('demo_trader_3', 100000, 120),
            ('pro_trader_alpha', 200000, 380),
            ('market_wizard', 180000, 320)
        ]
        
        symbols = ['NIFTY', 'BANKNIFTY', 'RELIANCE', 'TCS', 'HDFC', 'ICICI']
        
        for user_id, balance, trades in demo_users:
            if user_id not in self.accounts:
                portfolio = self.create_portfolio(user_id, 100000)
                
                # Set custom balance and trades
                portfolio['balance'] = balance
                portfolio['total_trades'] = trades
                portfolio['winning_trades'] = int(trades * random.uniform(0.6, 0.8))
                portfolio['losing_trades'] = trades - portfolio['winning_trades']
                portfolio['win_rate'] = (portfolio['winning_trades'] / trades) * 100
                portfolio['max_profit'] = random.uniform(5000, 15000)
                portfolio['max_loss'] = random.uniform(-3000, -8000)
                
                # Add some positions
                for _ in range(random.randint(2, 5)):
                    symbol = random.choice(symbols)
                    qty = random.randint(1, 10)
                    price = random.uniform(100, 2000)
                    
                    portfolio['positions'][f"{symbol}_CE"] = {
                        'quantity': qty,
                        'avg_price': price,
                        'current_price': price * random.uniform(0.9, 1.1),
                        'invested_amount': qty * price,
                        'current_value': qty * price * random.uniform(0.9, 1.1),
                        'pnl': qty * price * random.uniform(-0.1, 0.1),
                        'last_updated': datetime.now().isoformat()
                    }
        
        self.save_data()

# Global paper trading engine instance
paper_trading_engine = PaperTradingEngine()

# Generate demo data on first run
if not paper_trading_engine.accounts:
    paper_trading_engine.generate_demo_data()