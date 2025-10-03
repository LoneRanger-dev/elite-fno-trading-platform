"""
Paper Trading System for Options
Simulates trading with virtual money for testing strategies
"""
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class PaperTrade:
    trade_id: str
    entry_time: datetime
    instrument: str
    option_symbol: str
    trade_type: str  # BUY/SELL
    quantity: int
    entry_price: float
    target_price: float
    stop_loss: float
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    status: str = "OPEN"  # OPEN, CLOSED, STOPPED
    pnl: float = 0.0
    signal_id: Optional[str] = None

@dataclass
class PaperAccount:
    initial_capital: float
    current_balance: float = None
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    current_positions: Dict[str, PaperTrade] = None
    max_drawdown: float = 0.0
    peak_balance: float = 0.0
    
    def __post_init__(self):
        if self.current_balance is None:
            self.current_balance = self.initial_capital
        self.current_positions = {}
        self.peak_balance = self.initial_capital

class PaperTradingSystem:
    def __init__(self, initial_capital: float = 100000.0):
        self.data_file = Path("paper_trading_data.json")
        self.account = self.load_account(initial_capital)
        self.trade_history: List[PaperTrade] = []
        self.load_history()
        
    def load_account(self, initial_capital: float) -> PaperAccount:
        """Load or create paper trading account"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                return PaperAccount(**data)
        except Exception as e:
            logger.error(f"Error loading account: {e}")
            
        return PaperAccount(initial_capital=initial_capital)
        
    def load_history(self):
        """Load trade history"""
        history_file = Path("paper_trading_history.json")
        try:
            if history_file.exists():
                with open(history_file, 'r') as f:
                    data = json.load(f)
                self.trade_history = [PaperTrade(**trade) for trade in data]
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            
    def save_state(self):
        """Save current state to file"""
        try:
            # Save account state
            with open(self.data_file, 'w') as f:
                json.dump(asdict(self.account), f, indent=2)
                
            # Save trade history
            with open("paper_trading_history.json", 'w') as f:
                history_data = [asdict(trade) for trade in self.trade_history]
                json.dump(history_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving state: {e}")
            
    def enter_trade(self, signal: Dict) -> Optional[PaperTrade]:
        """Enter a new paper trade based on signal"""
        try:
            # Calculate position size
            lot_size = signal.get('lot_size', 50)  # Default NIFTY lot size
            max_risk = self.account.current_balance * 0.02  # 2% risk per trade
            
            entry_price = signal['option_entry_price']
            stop_loss = signal['option_stop_loss']
            risk_per_lot = abs(entry_price - stop_loss) * lot_size
            
            max_lots = int(max_risk / risk_per_lot)
            quantity = max(1, min(max_lots, 2))  # Cap at 2 lots for safety
            
            total_cost = entry_price * quantity * lot_size
            
            if total_cost > self.account.current_balance:
                logger.warning("Insufficient funds for trade")
                return None
                
            trade = PaperTrade(
                trade_id=f"PAPER_{len(self.trade_history)}",
                entry_time=datetime.now(),
                instrument=signal['instrument'],
                option_symbol=signal['option_symbol'],
                trade_type="BUY" if "BULLISH" in signal['signal_type'] else "SELL",
                quantity=quantity,
                entry_price=entry_price,
                target_price=signal['option_target_price'],
                stop_loss=stop_loss,
                signal_id=signal.get('id')
            )
            
            # Update account
            self.account.current_positions[trade.trade_id] = trade
            self.account.current_balance -= total_cost
            self.trade_history.append(trade)
            
            # Update peak balance if needed
            self.account.peak_balance = max(
                self.account.peak_balance,
                self.account.current_balance
            )
            
            self.save_state()
            logger.info(f"Entered paper trade: {trade.trade_id}")
            return trade
            
        except Exception as e:
            logger.error(f"Error entering trade: {e}")
            return None
            
    def update_positions(self, market_data: Dict):
        """Update open positions with current market data"""
        try:
            for trade_id, trade in self.account.current_positions.items():
                current_price = market_data.get(trade.option_symbol, {}).get('last_price')
                if not current_price:
                    continue
                    
                # Check for target or stop loss hit
                if trade.trade_type == "BUY":
                    if current_price >= trade.target_price:
                        self.exit_trade(trade_id, current_price, "TARGET_HIT")
                    elif current_price <= trade.stop_loss:
                        self.exit_trade(trade_id, current_price, "STOP_LOSS")
                else:  # SELL
                    if current_price <= trade.target_price:
                        self.exit_trade(trade_id, current_price, "TARGET_HIT")
                    elif current_price >= trade.stop_loss:
                        self.exit_trade(trade_id, current_price, "STOP_LOSS")
                        
        except Exception as e:
            logger.error(f"Error updating positions: {e}")
            
    def exit_trade(self, trade_id: str, exit_price: float, reason: str):
        """Exit a paper trade"""
        try:
            if trade_id not in self.account.current_positions:
                logger.warning(f"Trade {trade_id} not found")
                return
                
            trade = self.account.current_positions[trade_id]
            trade.exit_price = exit_price
            trade.exit_time = datetime.now()
            trade.status = "CLOSED"
            
            # Calculate P&L
            lot_size = 50  # Standard NIFTY lot size
            if trade.trade_type == "BUY":
                trade.pnl = (exit_price - trade.entry_price) * trade.quantity * lot_size
            else:
                trade.pnl = (trade.entry_price - exit_price) * trade.quantity * lot_size
                
            # Update account statistics
            self.account.current_balance += (
                trade.entry_price * trade.quantity * lot_size + trade.pnl
            )
            self.account.total_trades += 1
            
            if trade.pnl > 0:
                self.account.winning_trades += 1
            else:
                self.account.losing_trades += 1
                
            # Update max drawdown
            drawdown = (
                (self.account.peak_balance - self.account.current_balance) /
                self.account.peak_balance
            )
            self.account.max_drawdown = max(self.account.max_drawdown, drawdown)
            
            # Remove from current positions
            del self.account.current_positions[trade_id]
            
            self.save_state()
            logger.info(
                f"Exited trade {trade_id} with P&L: {trade.pnl:.2f} "
                f"Reason: {reason}"
            )
            
        except Exception as e:
            logger.error(f"Error exiting trade: {e}")
            
    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics"""
        try:
            win_rate = (
                self.account.winning_trades /
                max(self.account.total_trades, 1) * 100
            )
            
            total_pnl = sum(trade.pnl for trade in self.trade_history)
            avg_pnl = (
                total_pnl /
                max(self.account.total_trades, 1)
            )
            
            return {
                "initial_capital": self.account.initial_capital,
                "current_balance": self.account.current_balance,
                "total_pnl": total_pnl,
                "win_rate": win_rate,
                "avg_pnl": avg_pnl,
                "total_trades": self.account.total_trades,
                "winning_trades": self.account.winning_trades,
                "losing_trades": self.account.losing_trades,
                "max_drawdown": self.account.max_drawdown * 100,
                "open_positions": len(self.account.current_positions)
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {}