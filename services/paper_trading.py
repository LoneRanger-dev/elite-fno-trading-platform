"""
🎯 Paper Trading System - Virtual Portfolio Management
High-performance virtual trading with real-time P&L, leaderboards, and advanced analytics
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from enum import Enum

class OrderStatus(Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL = "SL"
    SL_M = "SL-M"

class TransactionType(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class PaperTrade:
    """Virtual trade with complete tracking"""
    trade_id: str
    user_id: str
    symbol: str
    instrument_type: str  # CE, PE, EQUITY, FUTURE
    strike_price: Optional[float]
    expiry_date: Optional[str]
    transaction_type: str  # BUY/SELL
    order_type: str
    quantity: int
    entry_price: float
    current_price: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    status: str
    entry_time: datetime
    exit_time: Optional[datetime]
    pnl: float
    pnl_percentage: float
    brokerage: float
    net_pnl: float
    confidence_score: int
    signal_source: str
    notes: str

@dataclass
class Portfolio:
    """Virtual portfolio with comprehensive tracking"""
    user_id: str
    total_capital: float
    available_capital: float
    invested_capital: float
    current_value: float
    total_pnl: float
    total_pnl_percentage: float
    day_pnl: float
    day_pnl_percentage: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_winning_trade: float
    avg_losing_trade: float
    max_drawdown: float
    sharpe_ratio: float
    risk_score: int
    performance_rank: int
    badges: List[str]
    created_at: datetime
    updated_at: datetime

class PaperTradingEngine:
    """🚀 Advanced Paper Trading Engine with Real Market Data"""
    
    def __init__(self, db_path: str = "data/paper_trading.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for paper trading"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Paper trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paper_trades (
                trade_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                instrument_type TEXT NOT NULL,
                strike_price REAL,
                expiry_date TEXT,
                transaction_type TEXT NOT NULL,
                order_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL NOT NULL,
                target_price REAL,
                stop_loss REAL,
                status TEXT NOT NULL,
                entry_time TIMESTAMP NOT NULL,
                exit_time TIMESTAMP,
                pnl REAL DEFAULT 0,
                pnl_percentage REAL DEFAULT 0,
                brokerage REAL DEFAULT 0,
                net_pnl REAL DEFAULT 0,
                confidence_score INTEGER DEFAULT 0,
                signal_source TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Portfolios table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolios (
                user_id TEXT PRIMARY KEY,
                total_capital REAL DEFAULT 100000,
                available_capital REAL DEFAULT 100000,
                invested_capital REAL DEFAULT 0,
                current_value REAL DEFAULT 100000,
                total_pnl REAL DEFAULT 0,
                total_pnl_percentage REAL DEFAULT 0,
                day_pnl REAL DEFAULT 0,
                day_pnl_percentage REAL DEFAULT 0,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                avg_winning_trade REAL DEFAULT 0,
                avg_losing_trade REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0,
                sharpe_ratio REAL DEFAULT 0,
                risk_score INTEGER DEFAULT 0,
                performance_rank INTEGER DEFAULT 0,
                badges TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Leaderboard view
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_portfolio_pnl ON portfolios(total_pnl_percentage DESC);
        ''')
        
        conn.commit()
        conn.close()
    
    def create_portfolio(self, user_id: str, initial_capital: float = 100000) -> Portfolio:
        """Create new virtual portfolio"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO portfolios (user_id, total_capital, available_capital, current_value)
                VALUES (?, ?, ?, ?)
            ''', (user_id, initial_capital, initial_capital, initial_capital))
            
            conn.commit()
            return self.get_portfolio(user_id)
            
        except sqlite3.IntegrityError:
            # Portfolio already exists
            return self.get_portfolio(user_id)
        finally:
            conn.close()
    
    def get_portfolio(self, user_id: str) -> Optional[Portfolio]:
        """Get user's portfolio with real-time calculations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM portfolios WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # Convert to dictionary
        columns = [desc[0] for desc in cursor.description]
        portfolio_data = dict(zip(columns, row))
        
        # Parse badges JSON
        portfolio_data['badges'] = json.loads(portfolio_data['badges'])
        
        # Calculate real-time metrics
        self._update_portfolio_metrics(user_id, cursor)
        
        conn.close()
        
        return Portfolio(
            user_id=portfolio_data['user_id'],
            total_capital=portfolio_data['total_capital'],
            available_capital=portfolio_data['available_capital'],
            invested_capital=portfolio_data['invested_capital'],
            current_value=portfolio_data['current_value'],
            total_pnl=portfolio_data['total_pnl'],
            total_pnl_percentage=portfolio_data['total_pnl_percentage'],
            day_pnl=portfolio_data['day_pnl'],
            day_pnl_percentage=portfolio_data['day_pnl_percentage'],
            total_trades=portfolio_data['total_trades'],
            winning_trades=portfolio_data['winning_trades'],
            losing_trades=portfolio_data['losing_trades'],
            win_rate=portfolio_data['win_rate'],
            avg_winning_trade=portfolio_data['avg_winning_trade'],
            avg_losing_trade=portfolio_data['avg_losing_trade'],
            max_drawdown=portfolio_data['max_drawdown'],
            sharpe_ratio=portfolio_data['sharpe_ratio'],
            risk_score=portfolio_data['risk_score'],
            performance_rank=portfolio_data['performance_rank'],
            badges=portfolio_data['badges'],
            created_at=datetime.fromisoformat(portfolio_data['created_at']),
            updated_at=datetime.fromisoformat(portfolio_data['updated_at'])
        )
    
    def place_paper_trade(self, user_id: str, trade_data: Dict) -> Dict:
        """🎯 Place virtual trade with validation"""
        try:
            # Validate portfolio
            portfolio = self.get_portfolio(user_id)
            if not portfolio:
                portfolio = self.create_portfolio(user_id)
            
            # Calculate trade value
            trade_value = trade_data['quantity'] * trade_data['entry_price']
            brokerage = self._calculate_brokerage(trade_value, trade_data['instrument_type'])
            total_cost = trade_value + brokerage
            
            # Check available capital for BUY orders
            if trade_data['transaction_type'] == 'BUY' and total_cost > portfolio.available_capital:
                return {
                    'success': False,
                    'message': f'Insufficient funds. Required: ₹{total_cost:,.2f}, Available: ₹{portfolio.available_capital:,.2f}',
                    'error_code': 'INSUFFICIENT_FUNDS'
                }
            
            # Create trade
            trade_id = str(uuid.uuid4())
            trade = PaperTrade(
                trade_id=trade_id,
                user_id=user_id,
                symbol=trade_data['symbol'],
                instrument_type=trade_data['instrument_type'],
                strike_price=trade_data.get('strike_price'),
                expiry_date=trade_data.get('expiry_date'),
                transaction_type=trade_data['transaction_type'],
                order_type=trade_data.get('order_type', 'MARKET'),
                quantity=trade_data['quantity'],
                entry_price=trade_data['entry_price'],
                current_price=trade_data['entry_price'],
                target_price=trade_data.get('target_price'),
                stop_loss=trade_data.get('stop_loss'),
                status=OrderStatus.EXECUTED.value,
                entry_time=datetime.now(),
                exit_time=None,
                pnl=0,
                pnl_percentage=0,
                brokerage=brokerage,
                net_pnl=-brokerage,
                confidence_score=trade_data.get('confidence_score', 0),
                signal_source=trade_data.get('signal_source', 'Manual'),
                notes=trade_data.get('notes', '')
            )
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO paper_trades VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (
                trade.trade_id, trade.user_id, trade.symbol, trade.instrument_type,
                trade.strike_price, trade.expiry_date, trade.transaction_type,
                trade.order_type, trade.quantity, trade.entry_price, trade.current_price,
                trade.target_price, trade.stop_loss, trade.status, trade.entry_time,
                trade.exit_time, trade.pnl, trade.pnl_percentage, trade.brokerage,
                trade.net_pnl, trade.confidence_score, trade.signal_source, trade.notes,
                datetime.now(), datetime.now()
            ))
            
            # Update portfolio
            if trade.transaction_type == 'BUY':
                new_available = portfolio.available_capital - total_cost
                new_invested = portfolio.invested_capital + trade_value
            else:  # SELL
                new_available = portfolio.available_capital + trade_value - brokerage
                new_invested = max(0, portfolio.invested_capital - trade_value)
            
            cursor.execute('''
                UPDATE portfolios 
                SET available_capital = ?, 
                    invested_capital = ?,
                    total_trades = total_trades + 1,
                    updated_at = ?
                WHERE user_id = ?
            ''', (new_available, new_invested, datetime.now(), user_id))
            
            conn.commit()
            conn.close()
            
            # Check for achievements
            self._check_achievements(user_id)
            
            return {
                'success': True,
                'trade_id': trade_id,
                'message': f'✅ Paper trade executed successfully!',
                'trade': asdict(trade),
                'brokerage': brokerage,
                'total_cost': total_cost
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Trade execution failed: {str(e)}',
                'error_code': 'EXECUTION_ERROR'
            }
    
    def update_trade_prices(self, user_id: str, price_updates: Dict[str, float]) -> None:
        """🔄 Update current prices for all active trades"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for symbol, current_price in price_updates.items():
                # Get active trades for this symbol
                cursor.execute('''
                    SELECT trade_id, transaction_type, quantity, entry_price, brokerage
                    FROM paper_trades 
                    WHERE user_id = ? AND symbol = ? AND status = 'EXECUTED' AND exit_time IS NULL
                ''', (user_id, symbol))
                
                trades = cursor.fetchall()
                
                for trade_id, transaction_type, quantity, entry_price, brokerage in trades:
                    # Calculate P&L
                    if transaction_type == 'BUY':
                        pnl = (current_price - entry_price) * quantity
                    else:  # SELL
                        pnl = (entry_price - current_price) * quantity
                    
                    pnl_percentage = (pnl / (entry_price * quantity)) * 100
                    net_pnl = pnl - brokerage
                    
                    # Update trade
                    cursor.execute('''
                        UPDATE paper_trades 
                        SET current_price = ?, pnl = ?, pnl_percentage = ?, net_pnl = ?, updated_at = ?
                        WHERE trade_id = ?
                    ''', (current_price, pnl, pnl_percentage, net_pnl, datetime.now(), trade_id))
            
            conn.commit()
            
            # Update portfolio metrics
            self._update_portfolio_metrics(user_id, cursor)
            
        except Exception as e:
            print(f"Error updating trade prices: {e}")
        finally:
            conn.close()
    
    def close_trade(self, user_id: str, trade_id: str, exit_price: float, reason: str = "Manual") -> Dict:
        """🏁 Close paper trade and update portfolio"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get trade details
            cursor.execute('''
                SELECT * FROM paper_trades WHERE trade_id = ? AND user_id = ? AND exit_time IS NULL
            ''', (trade_id, user_id))
            
            trade_row = cursor.fetchone()
            if not trade_row:
                return {'success': False, 'message': 'Trade not found or already closed'}
            
            # Parse trade data
            columns = [desc[0] for desc in cursor.description]
            trade_data = dict(zip(columns, trade_row))
            
            # Calculate final P&L
            quantity = trade_data['quantity']
            entry_price = trade_data['entry_price']
            transaction_type = trade_data['transaction_type']
            brokerage = trade_data['brokerage']
            
            if transaction_type == 'BUY':
                pnl = (exit_price - entry_price) * quantity
            else:  # SELL
                pnl = (entry_price - exit_price) * quantity
            
            pnl_percentage = (pnl / (entry_price * quantity)) * 100
            exit_brokerage = self._calculate_brokerage(exit_price * quantity, trade_data['instrument_type'])
            total_brokerage = brokerage + exit_brokerage
            net_pnl = pnl - total_brokerage
            
            # Update trade
            cursor.execute('''
                UPDATE paper_trades 
                SET current_price = ?, pnl = ?, pnl_percentage = ?, 
                    net_pnl = ?, brokerage = ?, exit_time = ?, 
                    notes = ?, updated_at = ?
                WHERE trade_id = ?
            ''', (exit_price, pnl, pnl_percentage, net_pnl, total_brokerage, 
                  datetime.now(), f"{trade_data['notes']} | Closed: {reason}", 
                  datetime.now(), trade_id))
            
            # Update portfolio
            portfolio = self.get_portfolio(user_id)
            trade_value = exit_price * quantity
            
            if transaction_type == 'BUY':
                # Return proceeds from selling
                new_available = portfolio.available_capital + trade_value - exit_brokerage
                new_invested = max(0, portfolio.invested_capital - (entry_price * quantity))
            else:  # SELL - cover short position
                # Pay to cover short
                new_available = portfolio.available_capital - trade_value - exit_brokerage
                new_invested = portfolio.invested_capital + (entry_price * quantity)
            
            # Update win/loss counts
            winning_increment = 1 if net_pnl > 0 else 0
            losing_increment = 1 if net_pnl < 0 else 0
            
            cursor.execute('''
                UPDATE portfolios 
                SET available_capital = ?, 
                    invested_capital = ?,
                    total_pnl = total_pnl + ?,
                    winning_trades = winning_trades + ?,
                    losing_trades = losing_trades + ?,
                    updated_at = ?
                WHERE user_id = ?
            ''', (new_available, new_invested, net_pnl, winning_increment, 
                  losing_increment, datetime.now(), user_id))
            
            conn.commit()
            
            # Update metrics and check achievements
            self._update_portfolio_metrics(user_id, cursor)
            self._check_achievements(user_id)
            
            return {
                'success': True,
                'message': f'✅ Trade closed successfully!',
                'pnl': net_pnl,
                'pnl_percentage': pnl_percentage,
                'exit_price': exit_price,
                'total_brokerage': total_brokerage
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Error closing trade: {str(e)}'}
        finally:
            conn.close()
    
    def get_active_trades(self, user_id: str) -> List[Dict]:
        """📊 Get all active trades with real-time P&L"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM paper_trades 
            WHERE user_id = ? AND status = 'EXECUTED' AND exit_time IS NULL
            ORDER BY entry_time DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        trades = []
        for row in rows:
            trade_data = dict(zip(columns, row))
            trade_data['entry_time'] = datetime.fromisoformat(trade_data['entry_time'])
            if trade_data['exit_time']:
                trade_data['exit_time'] = datetime.fromisoformat(trade_data['exit_time'])
            trades.append(trade_data)
        
        conn.close()
        return trades
    
    def get_trade_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """📈 Get complete trade history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM paper_trades 
            WHERE user_id = ? 
            ORDER BY entry_time DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        trades = []
        for row in rows:
            trade_data = dict(zip(columns, row))
            trade_data['entry_time'] = datetime.fromisoformat(trade_data['entry_time'])
            if trade_data['exit_time']:
                trade_data['exit_time'] = datetime.fromisoformat(trade_data['exit_time'])
            trades.append(trade_data)
        
        conn.close()
        return trades
    
    def get_leaderboard(self, period: str = 'all_time', limit: int = 100) -> List[Dict]:
        """🏆 Get leaderboard rankings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update all portfolio rankings first
        cursor.execute('''
            UPDATE portfolios 
            SET performance_rank = (
                SELECT COUNT(*) + 1 
                FROM portfolios p2 
                WHERE p2.total_pnl_percentage > portfolios.total_pnl_percentage
            )
        ''')
        
        cursor.execute('''
            SELECT user_id, total_capital, current_value, total_pnl, total_pnl_percentage,
                   total_trades, win_rate, performance_rank, badges, updated_at
            FROM portfolios 
            WHERE total_trades > 0
            ORDER BY total_pnl_percentage DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        leaderboard = []
        for i, row in enumerate(rows, 1):
            data = dict(zip(columns, row))
            data['badges'] = json.loads(data['badges'])
            data['rank'] = i
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            leaderboard.append(data)
        
        conn.close()
        return leaderboard
    
    def _calculate_brokerage(self, trade_value: float, instrument_type: str) -> float:
        """💰 Calculate realistic brokerage charges"""
        if instrument_type in ['CE', 'PE']:
            # Options: ₹20 per order
            return 20.0
        elif instrument_type == 'FUTURE':
            # Futures: 0.02% or ₹20 whichever is lower
            return min(trade_value * 0.0002, 20.0)
        else:
            # Equity: 0.1% or ₹20 whichever is lower
            return min(trade_value * 0.001, 20.0)
    
    def _update_portfolio_metrics(self, user_id: str, cursor) -> None:
        """📊 Calculate and update portfolio metrics"""
        # Get all closed trades for calculations
        cursor.execute('''
            SELECT net_pnl, pnl_percentage, exit_time 
            FROM paper_trades 
            WHERE user_id = ? AND exit_time IS NOT NULL
        ''', (user_id,))
        
        closed_trades = cursor.fetchall()
        
        if not closed_trades:
            return
        
        # Calculate metrics
        pnls = [trade[0] for trade in closed_trades]
        winning_pnls = [pnl for pnl in pnls if pnl > 0]
        losing_pnls = [pnl for pnl in pnls if pnl < 0]
        
        total_pnl = sum(pnls)
        avg_winning_trade = np.mean(winning_pnls) if winning_pnls else 0
        avg_losing_trade = np.mean(losing_pnls) if losing_pnls else 0
        win_rate = (len(winning_pnls) / len(pnls)) * 100 if pnls else 0
        
        # Calculate Sharpe ratio (simplified)
        if len(pnls) > 1:
            sharpe_ratio = np.std(pnls) / np.mean(pnls) if np.mean(pnls) != 0 else 0
        else:
            sharpe_ratio = 0
        
        # Calculate total portfolio value
        cursor.execute('''
            SELECT available_capital, invested_capital 
            FROM portfolios 
            WHERE user_id = ?
        ''', (user_id,))
        
        portfolio_data = cursor.fetchone()
        if portfolio_data:
            available_capital, invested_capital = portfolio_data
            
            # Get current unrealized P&L
            cursor.execute('''
                SELECT COALESCE(SUM(net_pnl), 0) 
                FROM paper_trades 
                WHERE user_id = ? AND exit_time IS NULL
            ''', (user_id,))
            
            unrealized_pnl = cursor.fetchone()[0] or 0
            current_value = available_capital + invested_capital + unrealized_pnl
            
            # Get original capital
            cursor.execute('SELECT total_capital FROM portfolios WHERE user_id = ?', (user_id,))
            total_capital = cursor.fetchone()[0]
            
            total_pnl_percentage = ((current_value - total_capital) / total_capital) * 100
            
            # Calculate day P&L (simplified - last 24 hours)
            cursor.execute('''
                SELECT COALESCE(SUM(net_pnl), 0) 
                FROM paper_trades 
                WHERE user_id = ? AND exit_time > datetime('now', '-1 day')
            ''', (user_id,))
            
            day_pnl = cursor.fetchone()[0] or 0
            day_pnl_percentage = (day_pnl / total_capital) * 100 if total_capital > 0 else 0
            
            # Update portfolio
            cursor.execute('''
                UPDATE portfolios 
                SET current_value = ?,
                    total_pnl = ?,
                    total_pnl_percentage = ?,
                    day_pnl = ?,
                    day_pnl_percentage = ?,
                    win_rate = ?,
                    avg_winning_trade = ?,
                    avg_losing_trade = ?,
                    sharpe_ratio = ?,
                    updated_at = ?
                WHERE user_id = ?
            ''', (current_value, total_pnl, total_pnl_percentage, day_pnl, 
                  day_pnl_percentage, win_rate, avg_winning_trade, avg_losing_trade, 
                  sharpe_ratio, datetime.now(), user_id))
    
    def _check_achievements(self, user_id: str) -> None:
        """🏅 Check and award achievements/badges"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current portfolio stats
        cursor.execute('''
            SELECT total_trades, winning_trades, win_rate, total_pnl_percentage, badges
            FROM portfolios WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return
        
        total_trades, winning_trades, win_rate, total_pnl_percentage, badges_json = row
        current_badges = json.loads(badges_json)
        new_badges = []
        
        # Achievement logic
        achievements = [
            (total_trades >= 1, "first_trade", "🎯 First Trade"),
            (total_trades >= 10, "trader_10", "📈 10 Trades Completed"),
            (total_trades >= 50, "trader_50", "🚀 50 Trades Milestone"),
            (total_trades >= 100, "trader_100", "💎 Century Trader"),
            (win_rate >= 60 and total_trades >= 10, "consistent_winner", "🏆 Consistent Winner"),
            (win_rate >= 80 and total_trades >= 20, "expert_trader", "⭐ Expert Trader"),
            (total_pnl_percentage >= 10, "profit_10", "💰 10% Profit"),
            (total_pnl_percentage >= 25, "profit_25", "🔥 25% Profit"),
            (total_pnl_percentage >= 50, "profit_50", "💎 50% Profit Master"),
            (winning_trades >= 5, "winner_5", "🎖️ 5 Winning Trades"),
            (winning_trades >= 20, "winner_20", "🏅 20 Winning Trades"),
        ]
        
        for condition, badge_id, badge_name in achievements:
            if condition and badge_id not in current_badges:
                new_badges.append(badge_name)
                current_badges.append(badge_id)
        
        if new_badges:
            cursor.execute('''
                UPDATE portfolios 
                SET badges = ?, updated_at = ?
                WHERE user_id = ?
            ''', (json.dumps(current_badges), datetime.now(), user_id))
            
            conn.commit()
            print(f"🎉 New achievements for {user_id}: {', '.join(new_badges)}")
        
        conn.close()

# Example usage and testing
if __name__ == "__main__":
    # Initialize paper trading engine
    engine = PaperTradingEngine()
    
    # Create test portfolio
    user_id = "test_user_123"
    portfolio = engine.create_portfolio(user_id, 100000)
    print(f"📊 Created portfolio: {portfolio.user_id} with ₹{portfolio.total_capital:,.2f}")
    
    # Place test trade
    trade_data = {
        'symbol': 'NIFTY24JAN22000CE',
        'instrument_type': 'CE',
        'strike_price': 22000,
        'expiry_date': '2024-01-25',
        'transaction_type': 'BUY',
        'quantity': 50,
        'entry_price': 150.0,
        'target_price': 200.0,
        'stop_loss': 120.0,
        'confidence_score': 85,
        'signal_source': 'Advanced FnO Engine',
        'notes': 'Bullish breakout signal'
    }
    
    result = engine.place_paper_trade(user_id, trade_data)
    print(f"🎯 Trade result: {result}")
    
    # Update price and check P&L
    engine.update_trade_prices(user_id, {'NIFTY24JAN22000CE': 175.0})
    
    # Get active trades
    active_trades = engine.get_active_trades(user_id)
    print(f"📈 Active trades: {len(active_trades)}")
    
    if active_trades:
        print(f"Current P&L: ₹{active_trades[0]['net_pnl']:,.2f}")
    
    # Get updated portfolio
    updated_portfolio = engine.get_portfolio(user_id)
    print(f"💰 Portfolio value: ₹{updated_portfolio.current_value:,.2f}")
    print(f"🏆 Badges: {updated_portfolio.badges}")