import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import time

class ORBModified:
    """Opening Range Breakout Modified Strategy"""
    
    name = "ORB Modified"
    timeframe = "intraday"
    description = "Breakout from first 15-min range with volume confirmation"
    
    @staticmethod
    def analyze(df: pd.DataFrame, current_time: Optional[time] = None) -> Dict:
        """Analyze ORB setup"""
        if len(df) < 20:
            return {'signal': 'NONE', 'confidence': 0}
        
        try:
            first_15min = df.head(3)
            orb_high = first_15min['high'].max()
            orb_low = first_15min['low'].min()
            current_price = df['close'].iloc[-1]
            volume_avg = df['volume'].tail(20).mean()
            current_volume = df['volume'].iloc[-1]
            
            if current_price > orb_high and current_volume > volume_avg * 1.5:
                return {
                    'signal': 'BUY',
                    'entry': float(current_price),
                    'target1': float(current_price + (orb_high - orb_low) * 1.5),
                    'target2': float(current_price + (orb_high - orb_low) * 2.5),
                    'stop_loss': float(orb_low),
                    'confidence': 75,
                    'setup_type': 'ORB_BREAKOUT'
                }
            
            elif current_price < orb_low and current_volume > volume_avg * 1.5:
                return {
                    'signal': 'SELL',
                    'entry': float(current_price),
                    'target1': float(current_price - (orb_high - orb_low) * 1.5),
                    'target2': float(current_price - (orb_high - orb_low) * 2.5),
                    'stop_loss': float(orb_high),
                    'confidence': 75,
                    'setup_type': 'ORB_BREAKDOWN'
                }
            
            return {'signal': 'NONE', 'confidence': 0}
        
        except Exception as e:
            print(f"ORB analysis error: {e}")
            return {'signal': 'NONE', 'confidence': 0}