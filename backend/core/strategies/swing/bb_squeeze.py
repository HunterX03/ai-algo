import pandas as pd
import numpy as np
from typing import Dict

class BBSqueeze:
    """Bollinger Band Squeeze Strategy"""
    
    name = "BB Squeeze"
    timeframe = "swing"
    description = "Volatility breakout from BB squeeze with volume"
    
    @staticmethod
    def analyze(df: pd.DataFrame) -> Dict:
        """Analyze BB squeeze setup"""
        if len(df) < 30 or 'bb_width' not in df.columns:
            return {'signal': 'NONE', 'confidence': 0}
        
        try:
            current_bb_width = df['bb_width'].iloc[-1]
            avg_bb_width = df['bb_width'].tail(50).mean()
            current_price = df['close'].iloc[-1]
            bb_upper = df['bb_upper'].iloc[-1]
            bb_lower = df['bb_lower'].iloc[-1]
            volume_ratio = df['volume'].iloc[-1] / df['volume'].tail(20).mean()
            
            is_squeezed = current_bb_width < avg_bb_width * 0.7
            
            if is_squeezed:
                if current_price > bb_upper and volume_ratio > 1.3:
                    target_distance = bb_upper - bb_lower
                    return {
                        'signal': 'BUY',
                        'entry': float(current_price),
                        'target1': float(current_price + target_distance),
                        'target2': float(current_price + target_distance * 1.5),
                        'stop_loss': float(bb_lower),
                        'confidence': 78,
                        'setup_type': 'BB_SQUEEZE_BREAKOUT'
                    }
                
                elif current_price < bb_lower and volume_ratio > 1.3:
                    target_distance = bb_upper - bb_lower
                    return {
                        'signal': 'SELL',
                        'entry': float(current_price),
                        'target1': float(current_price - target_distance),
                        'target2': float(current_price - target_distance * 1.5),
                        'stop_loss': float(bb_upper),
                        'confidence': 78,
                        'setup_type': 'BB_SQUEEZE_BREAKDOWN'
                    }
            
            return {'signal': 'NONE', 'confidence': 0}
        
        except Exception as e:
            print(f"BB Squeeze error: {e}")
            return {'signal': 'NONE', 'confidence': 0}