import pandas as pd
import numpy as np
from typing import Dict

class InstitutionalOrderBlock:
    """Institutional Order Block Strategy"""
    name = "Institutional Order Block"
    timeframe = "intraday"
    description = "Identifies institutional supply/demand zones via order flow"

    @staticmethod
    def analyze(df: pd.DataFrame) -> Dict:
        if len(df) < 20:
            return {'signal': 'NONE', 'confidence': 0}
        try:
            current = df['close'].iloc[-1]
            vol_avg = df['volume'].tail(20).mean()
            atr = (df['high'].tail(14).mean() - df['low'].tail(14).mean())
            # Find demand zone: big bullish candle after sell-off
            for i in range(-5, -1):
                candle = df.iloc[i]
                body = candle['close'] - candle['open']
                rng = candle['high'] - candle['low']
                if body > 0 and rng > atr * 1.5 and candle['volume'] > vol_avg * 2:
                    demand_zone = candle['low']
                    if current <= demand_zone * 1.01 and current >= demand_zone * 0.99:
                        return {'signal': 'BUY', 'entry': float(current),
                                'target1': float(current + atr * 2), 'target2': float(current + atr * 3),
                                'stop_loss': float(demand_zone - atr * 0.5), 'confidence': 74,
                                'setup_type': 'ORDER_BLOCK_DEMAND'}
            # Find supply zone
            for i in range(-5, -1):
                candle = df.iloc[i]
                body = candle['open'] - candle['close']
                rng = candle['high'] - candle['low']
                if body > 0 and rng > atr * 1.5 and candle['volume'] > vol_avg * 2:
                    supply_zone = candle['high']
                    if current >= supply_zone * 0.99 and current <= supply_zone * 1.01:
                        return {'signal': 'SELL', 'entry': float(current),
                                'target1': float(current - atr * 2), 'target2': float(current - atr * 3),
                                'stop_loss': float(supply_zone + atr * 0.5), 'confidence': 74,
                                'setup_type': 'ORDER_BLOCK_SUPPLY'}
            return {'signal': 'NONE', 'confidence': 0}
        except Exception:
            return {'signal': 'NONE', 'confidence': 0}
