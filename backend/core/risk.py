import pandas as pd
import numpy as np
from typing import Dict, List
import math

class RiskManager:
    """Position sizing and risk management"""
    
    @staticmethod
    def calculate_position_size_fixed_fractional(
        capital: float,
        risk_percent: float,
        entry_price: float,
        stop_loss: float
    ) -> Dict:
        """Calculate position size using fixed fractional method"""
        try:
            risk_amount = capital * (risk_percent / 100)
            
            risk_per_share = abs(entry_price - stop_loss)
            if risk_per_share == 0:
                risk_per_share = entry_price * 0.02
            
            shares = math.floor(risk_amount / risk_per_share)
            
            position_value = shares * entry_price
            max_position_value = capital * 0.20
            
            if position_value > max_position_value:
                shares = math.floor(max_position_value / entry_price)
                position_value = shares * entry_price
            
            return {
                'method': 'Fixed Fractional',
                'shares': int(shares),
                'position_value': float(position_value),
                'capital_at_risk': float(shares * risk_per_share),
                'risk_percent': float((shares * risk_per_share / capital) * 100),
                'max_loss': float(shares * risk_per_share)
            }
        
        except Exception as e:
            print(f"Error calculating fixed fractional: {e}")
            return {
                'method': 'Fixed Fractional',
                'shares': 0,
                'position_value': 0,
                'capital_at_risk': 0,
                'risk_percent': 0,
                'max_loss': 0
            }
    
    @staticmethod
    def calculate_kelly_criterion(
        capital: float,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        entry_price: float,
        kelly_fraction: float = 0.5
    ) -> Dict:
        """Calculate position size using Kelly Criterion"""
        try:
            if avg_loss == 0:
                avg_loss = 1.0
            
            win_loss_ratio = avg_win / avg_loss
            
            kelly_percent = (win_rate - ((1 - win_rate) / win_loss_ratio)) * 100
            
            kelly_percent = max(0, min(kelly_percent, 25))
            
            adjusted_kelly = kelly_percent * kelly_fraction
            
            position_value = capital * (adjusted_kelly / 100)
            shares = math.floor(position_value / entry_price)
            actual_position_value = shares * entry_price
            
            growth_rate = win_rate * math.log(1 + (avg_win / 100)) + (1 - win_rate) * math.log(1 - (avg_loss / 100))
            
            return {
                'method': 'Kelly Criterion',
                'kelly_full': float(kelly_percent),
                'kelly_half': float(kelly_percent * 0.5),
                'kelly_quarter': float(kelly_percent * 0.25),
                'recommended_kelly': float(adjusted_kelly),
                'shares': int(shares),
                'position_value': float(actual_position_value),
                'expected_growth_rate': float(growth_rate * 100),
                'win_loss_ratio': float(win_loss_ratio)
            }
        
        except Exception as e:
            print(f"Error calculating Kelly: {e}")
            return {
                'method': 'Kelly Criterion',
                'kelly_full': 0,
                'kelly_half': 0,
                'kelly_quarter': 0,
                'recommended_kelly': 0,
                'shares': 0,
                'position_value': 0,
                'expected_growth_rate': 0,
                'win_loss_ratio': 0
            }
    
    @staticmethod
    def get_risk_recommendations(
        capital: float,
        market_regime: str,
        strategy_win_rate: float
    ) -> Dict:
        """Get risk management recommendations based on regime"""
        recommendations = {
            "BULL_TRENDING": {
                "recommended_method": "Fixed Fractional",
                "risk_per_trade": 2.0,
                "max_positions": 8,
                "reasoning": "Strong trend allows larger position sizes"
            },
            "BULL_VOLATILE": {
                "recommended_method": "Fixed Fractional",
                "risk_per_trade": 1.5,
                "max_positions": 6,
                "reasoning": "Volatility requires tighter risk control"
            },
            "SIDEWAYS": {
                "recommended_method": "Kelly Criterion (Half)",
                "risk_per_trade": 1.0,
                "max_positions": 5,
                "reasoning": "Range-bound market needs conservative sizing"
            },
            "BEAR_VOLATILE": {
                "recommended_method": "Fixed Fractional",
                "risk_per_trade": 1.0,
                "max_positions": 4,
                "reasoning": "High volatility requires minimal risk"
            },
            "BEAR_TRENDING": {
                "recommended_method": "Fixed Fractional",
                "risk_per_trade": 0.5,
                "max_positions": 3,
                "reasoning": "Bear market demands smallest position sizes"
            }
        }
        
        regime_rec = recommendations.get(market_regime, recommendations["SIDEWAYS"])
        
        if strategy_win_rate > 0.65:
            regime_rec["risk_per_trade"] *= 1.2
            regime_rec["reasoning"] += ". High win rate allows slight increase."
        elif strategy_win_rate < 0.45:
            regime_rec["risk_per_trade"] *= 0.8
            regime_rec["reasoning"] += ". Low win rate requires reduction."
        
        regime_rec["capital"] = capital
        regime_rec["market_regime"] = market_regime
        
        return regime_rec