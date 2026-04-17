import pandas as pd
import numpy as np
from typing import Dict

class VWAPReversal:
    """VWAP Reversal Strategy"""
    
    name = "VWAP Reversal"
    timeframe = "intraday"
    description = "Mean reversion from VWAP with RSI confirmation"
    
    @staticmethod
    def analyze(df: pd.DataFrame) -> Dict:
        """Analyze VWAP reversal setup"""
        if len(df) < 20 or 'vwap' not in df.columns or 'rsi' not in df.columns:
            return {'signal': 'NONE', 'confidence': 0}
        
        try:
            current_price = df['close'].iloc[-1]
            vwap = df['vwap'].iloc[-1]
            rsi = df['rsi'].iloc[-1]
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else (df['high'].iloc[-1] - df['low'].iloc[-1])
            
            deviation = abs(current_price - vwap) / vwap
            
            if current_price < vwap * 0.98 and rsi < 35 and deviation > 0.015:
                return {
                    'signal': 'BUY',
                    'entry': float(current_price),
                    'target1': float(vwap),
                    'target2': float(vwap * 1.01),
                    'stop_loss': float(current_price - atr * 1.5),
                    'confidence': 70,
                    'setup_type': 'VWAP_LONG'
                }
            
            elif current_price > vwap * 1.02 and rsi > 65 and deviation > 0.015:
                return {
                    'signal': 'SELL',
                    'entry': float(current_price),
                    'target1': float(vwap),
                    'target2': float(vwap * 0.99),
                    'stop_loss': float(current_price + atr * 1.5),
                    'confidence': 70,
                    'setup_type': 'VWAP_SHORT'
                }
            
            return {'signal': 'NONE', 'confidence': 0}
        
        except Exception as e:
            print(f"VWAP Reversal error: {e}")
            return {'signal': 'NONE', 'confidence': 0}