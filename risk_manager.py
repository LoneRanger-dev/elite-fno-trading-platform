"""
Advanced Risk Management System
Manages trade risk, position sizing, and portfolio exposure
"""
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, time
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class RiskConfig:
    max_account_risk: float = 0.02  # 2% max risk per trade
    max_daily_loss: float = 0.05    # 5% max daily loss
    max_position_size: float = 0.15  # 15% max position size
    max_sector_exposure: float = 0.30  # 30% max sector exposure
    min_risk_reward: float = 1.5    # Minimum risk-reward ratio
    max_open_positions: int = 5     # Maximum concurrent positions
    max_correlated_positions: int = 2  # Max similar positions
    market_hours_start: time = time(9, 15)  # Market opens at 9:15 AM
    market_hours_end: time = time(15, 30)   # Market closes at 3:30 PM

class RiskManager:
    def __init__(self, config: Optional[RiskConfig] = None):
        self.config = config or RiskConfig()
        self.daily_pnl = 0
        self.open_positions: Dict = {}
        self.daily_trades = []
        self.sector_exposure = {}
        
    def can_take_trade(self, signal: Dict, account_balance: float) -> tuple[bool, str]:
        """Check if a trade meets risk management criteria"""
        current_time = datetime.now().time()
        
        # Check market hours
        if not (self.config.market_hours_start <= current_time <= self.config.market_hours_end):
            return False, "Outside market hours"
            
        # Check daily loss limit
        if self.daily_pnl < -(account_balance * self.config.max_daily_loss):
            return False, "Daily loss limit reached"
            
        # Check maximum open positions
        if len(self.open_positions) >= self.config.max_open_positions:
            return False, "Maximum open positions reached"
            
        # Check position correlation
        if not self.check_position_correlation(signal):
            return False, "Too many correlated positions"
            
        # Check sector exposure
        if not self.check_sector_exposure(signal):
            return False, "Sector exposure limit reached"
            
        # Check risk-reward ratio
        rr_ratio = self.calculate_risk_reward_ratio(signal)
        if rr_ratio < self.config.min_risk_reward:
            return False, f"Risk-reward ratio {rr_ratio:.2f} below minimum {self.config.min_risk_reward}"
            
        return True, "Trade approved"
        
    def calculate_position_size(self, signal: Dict, account_balance: float) -> int:
        """Calculate optimal position size based on risk parameters"""
        # Calculate risk amount
        max_risk_amount = account_balance * self.config.max_account_risk
        
        # Calculate per-lot risk
        entry_price = signal['option_entry_price']
        stop_loss = signal['option_stop_loss']
        risk_per_lot = abs(entry_price - stop_loss) * 50  # Standard lot size
        
        # Calculate maximum lots based on risk
        max_lots = int(max_risk_amount / risk_per_lot)
        
        # Check position size limit
        position_value = entry_price * 50  # Value per lot
        max_lots_by_size = int((account_balance * self.config.max_position_size) / position_value)
        
        # Take minimum of risk-based and size-based lots
        recommended_lots = min(max_lots, max_lots_by_size)
        
        # Ensure at least 1 lot but no more than 5
        return max(1, min(recommended_lots, 5))
        
    def check_position_correlation(self, signal: Dict) -> bool:
        """Check for correlated positions"""
        similar_positions = 0
        signal_type = signal['signal_type']
        
        for position in self.open_positions.values():
            if (
                ("BULLISH" in signal_type and "BULLISH" in position['signal_type']) or
                ("BEARISH" in signal_type and "BEARISH" in position['signal_type'])
            ):
                similar_positions += 1
                
        return similar_positions < self.config.max_correlated_positions
        
    def check_sector_exposure(self, signal: Dict) -> bool:
        """Check sector exposure limits"""
        sector = self.get_instrument_sector(signal['instrument'])
        current_exposure = self.sector_exposure.get(sector, 0)
        
        new_exposure = current_exposure + (
            signal['option_entry_price'] * signal.get('lot_size', 50)
        )
        
        return new_exposure <= (
            self.get_total_portfolio_value() * self.config.max_sector_exposure
        )
        
    def get_instrument_sector(self, instrument: str) -> str:
        """Get sector for an instrument"""
        # Simplified sector mapping
        sectors = {
            "NIFTY": "INDEX",
            "BANKNIFTY": "BANKING",
            "FINNIFTY": "FINANCIAL"
        }
        return sectors.get(instrument, "OTHER")
        
    def get_total_portfolio_value(self) -> float:
        """Calculate total portfolio value"""
        return sum(
            position['option_entry_price'] * position.get('lot_size', 50)
            for position in self.open_positions.values()
        )
        
    def calculate_risk_reward_ratio(self, signal: Dict) -> float:
        """Calculate risk-reward ratio for a signal"""
        entry = signal['option_entry_price']
        target = signal['option_target_price']
        stop_loss = signal['option_stop_loss']
        
        risk = abs(entry - stop_loss)
        reward = abs(target - entry)
        
        return reward / risk if risk > 0 else 0
        
    def update_position(self, trade_id: str, current_price: float):
        """Update position P&L and risk metrics"""
        if trade_id not in self.open_positions:
            return
            
        position = self.open_positions[trade_id]
        entry_price = position['option_entry_price']
        lot_size = position.get('lot_size', 50)
        
        # Update P&L
        if "BULLISH" in position['signal_type']:
            pnl = (current_price - entry_price) * lot_size
        else:
            pnl = (entry_price - current_price) * lot_size
            
        position['current_pnl'] = pnl
        self.daily_pnl = sum(p['current_pnl'] for p in self.open_positions.values())
        
    def add_position(self, trade_id: str, signal: Dict):
        """Add new position to tracking"""
        self.open_positions[trade_id] = signal
        
        # Update sector exposure
        sector = self.get_instrument_sector(signal['instrument'])
        self.sector_exposure[sector] = self.sector_exposure.get(sector, 0) + (
            signal['option_entry_price'] * signal.get('lot_size', 50)
        )
        
    def remove_position(self, trade_id: str):
        """Remove closed position from tracking"""
        if trade_id in self.open_positions:
            position = self.open_positions[trade_id]
            sector = self.get_instrument_sector(position['instrument'])
            
            # Update sector exposure
            self.sector_exposure[sector] -= (
                position['option_entry_price'] * position.get('lot_size', 50)
            )
            
            del self.open_positions[trade_id]
            
    def get_risk_metrics(self) -> Dict:
        """Get current risk metrics"""
        return {
            "open_positions": len(self.open_positions),
            "daily_pnl": self.daily_pnl,
            "sector_exposure": self.sector_exposure,
            "total_exposure": self.get_total_portfolio_value()
        }