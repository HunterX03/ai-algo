import pandas as pd
import numpy as np
from typing import Dict

class MomentumDelivery:
    """Momentum + Delivery % Strategy"""
    
    name = "Momentum + Delivery %"
    timeframe = "swing"
    description = "Price momentum with strong delivery participation"
    
    @staticmethod
    def analyze(df: pd.DataFrame, delivery_pct: float = 65.0) -> Dict:
        """Analyze momentum with delivery"""
        if len(df) < 20:
            return {'signal': 'NONE', 'confidence': 0}
        
        try:
            current_price = df['close'].iloc[-1]
            ema_20 = df['ema_20'].iloc[-1] if 'ema_20' in df.columns else df['close'].ewm(span=20).mean().iloc[-1]
            ema_50 = df['ema_50'].iloc[-1] if 'ema_50' in df.columns else df['close'].ewm(span=50).mean().iloc[-1]
            rsi = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else (df['high'].iloc[-1] - df['low'].iloc[-1])
            
            strong_delivery = delivery_pct > 60
            bullish_momentum = current_price > ema_20 > ema_50 and rsi > 55
            bearish_momentum = current_price < ema_20 < ema_50 and rsi < 45
            
            if bullish_momentum and strong_delivery:
                return {
                    'signal': 'BUY',
                    'entry': float(current_price),
                    'target1': float(current_price * 1.05),
                    'target2': float(current_price * 1.08),
                    'stop_loss': float(current_price - atr * 2),
                    'confidence': 80,
                    'setup_type': 'MOMENTUM_DELIVERY_LONG'
                }
            
            elif bearish_momentum and strong_delivery:
                return {
                    'signal': 'SELL',
                    'entry': float(current_price),
                    'target1': float(current_price * 0.95),
                    'target2': float(current_price * 0.92),
                    'stop_loss': float(current_price + atr * 2),
                    'confidence': 75,
                    'setup_type': 'MOMENTUM_DELIVERY_SHORT'
                }
            
            return {'signal': 'NONE', 'confidence': 0}
        
        except Exception as e:
            print(f"Momentum Delivery error: {e}")
            return {'signal': 'NONE', 'confidence': 0}