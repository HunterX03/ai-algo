import pandas as pd
import numpy as np
from typing import Dict

class GapAndGo:
    """Gap and Go / Fade Strategy"""
    name = "Gap and Go/Fade"
    timeframe = "intraday"
    description = "Trades gaps at market open based on volume and gap size"

    @staticmethod
    def analyze(df: pd.DataFrame) -> Dict:
        if len(df) < 10:
            return {'signal': 'NONE', 'confidence': 0}
        try:
            prev_close = df['close'].iloc[-2] if len(df) > 1 else df['open'].iloc[0]
            open_price = df['open'].iloc[-1]
            current = df['close'].iloc[-1]
            gap_pct = ((open_price - prev_close) / prev_close) * 100
            vol_ratio = df['volume'].iloc[-1] / df['volume'].tail(20).mean() if df['volume'].tail(20).mean() > 0 else 1
            atr = (df['high'].tail(14).mean() - df['low'].tail(14).mean()) if len(df) >= 14 else abs(df['high'].iloc[-1] - df['low'].iloc[-1])

            if gap_pct > 1.5 and vol_ratio > 1.5 and current > open_price:
                return {'signal': 'BUY', 'entry': float(current), 'target1': float(current + atr * 1.5),
                        'target2': float(current + atr * 2.5), 'stop_loss': float(open_price - atr * 0.5),
                        'confidence': 72, 'setup_type': 'GAP_AND_GO'}
            elif gap_pct < -1.5 and vol_ratio > 1.5 and current < open_price:
                return {'signal': 'SELL', 'entry': float(current), 'target1': float(current - atr * 1.5),
                        'target2': float(current - atr * 2.5), 'stop_loss': float(open_price + atr * 0.5),
                        'confidence': 72, 'setup_type': 'GAP_AND_FADE'}
            return {'signal': 'NONE', 'confidence': 0}
        except Exception:
            return {'signal': 'NONE', 'confidence': 0}
