import pandas as pd
import numpy as np
from typing import Dict

class QualityMomentum:
    """Quality Momentum Strategy"""
    
    name = "Quality Momentum"
    timeframe = "positional"
    description = "High quality stocks with sustained momentum"
    
    @staticmethod
    def analyze(df: pd.DataFrame, roe: float = 15.0, pe_ratio: float = 25.0) -> Dict:
        """Analyze quality momentum setup"""
        if len(df) < 100:
            return {'signal': 'NONE', 'confidence': 0}
        
        try:
            current_price = df['close'].iloc[-1]
            ema_50 = df['ema_50'].iloc[-1] if 'ema_50' in df.columns else df['close'].ewm(span=50).mean().iloc[-1]
            ema_200 = df['ema_200'].iloc[-1] if 'ema_200' in df.columns else df['close'].ewm(span=200).mean().iloc[-1]
            
            returns_3m = ((current_price - df['close'].iloc[-65]) / df['close'].iloc[-65]) * 100 if len(df) > 65 else 0
            returns_6m = ((current_price - df['close'].iloc[-130]) / df['close'].iloc[-130]) * 100 if len(df) > 130 else 0
            
            quality_ok = roe > 15 and pe_ratio < 35
            momentum_strong = returns_3m > 15 and returns_6m > 25
            trend_aligned = current_price > ema_50 > ema_200
            
            if quality_ok and momentum_strong and trend_aligned:
                atr = df['atr'].iloc[-1] if 'atr' in df.columns else (df['high'].tail(14).mean() - df['low'].tail(14).mean())
                return {
                    'signal': 'BUY',
                    'entry': float(current_price),
                    'target1': float(current_price * 1.15),
                    'target2': float(current_price * 1.25),
                    'stop_loss': float(ema_50),
                    'confidence': 85,
                    'setup_type': 'QUALITY_MOMENTUM_LONG'
                }
            
            return {'signal': 'NONE', 'confidence': 0}
        
        except Exception as e:
            print(f"Quality Momentum error: {e}")
            return {'signal': 'NONE', 'confidence': 0}