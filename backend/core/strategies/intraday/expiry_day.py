import pandas as pd
import numpy as np
from typing import Dict
from datetime import datetime

class ExpiryDayMomentum:
    """Expiry Day Momentum Strategy"""
    
    name = "Expiry Day Momentum"
    timeframe = "intraday"
    description = "Momentum trades on weekly expiry days (Thursdays)"
    
    @staticmethod
    def analyze(df: pd.DataFrame, current_date: datetime = None) -> Dict:
        """Analyze expiry day momentum"""
        if len(df) < 10:
            return {'signal': 'NONE', 'confidence': 0}
        
        try:
            if current_date and current_date.weekday() != 3:
                return {'signal': 'NONE', 'confidence': 0, 'reason': 'Not expiry day'}
            
            current_price = df['close'].iloc[-1]
            price_change_pct = ((current_price - df['open'].iloc[0]) / df['open'].iloc[0]) * 100
            volume_ratio = df['volume'].iloc[-1] / df['volume'].mean()
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else (df['high'].mean() - df['low'].mean())
            
            if price_change_pct > 1.5 and volume_ratio > 2.0:
                return {
                    'signal': 'BUY',
                    'entry': float(current_price),
                    'target1': float(current_price * 1.02),
                    'target2': float(current_price * 1.035),
                    'stop_loss': float(current_price - atr * 1.5),
                    'confidence': 68,
                    'setup_type': 'EXPIRY_MOMENTUM_LONG'
                }
            
            elif price_change_pct < -1.5 and volume_ratio > 2.0:
                return {
                    'signal': 'SELL',
                    'entry': float(current_price),
                    'target1': float(current_price * 0.98),
                    'target2': float(current_price * 0.965),
                    'stop_loss': float(current_price + atr * 1.5),
                    'confidence': 68,
                    'setup_type': 'EXPIRY_MOMENTUM_SHORT'
                }
            
            return {'signal': 'NONE', 'confidence': 0}
        
        except Exception as e:
            print(f"Expiry Day Momentum error: {e}")
            return {'signal': 'NONE', 'confidence': 0}