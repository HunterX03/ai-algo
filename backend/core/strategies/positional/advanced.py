import pandas as pd
import numpy as np
from typing import Dict

class SectorRotation:
    """Sector Rotation Strategy"""
    name = "Sector Rotation"
    timeframe = "positional"
    description = "Rotates into sectors showing relative strength momentum"

    @staticmethod
    def analyze(df: pd.DataFrame) -> Dict:
        if len(df) < 60:
            return {'signal': 'NONE', 'confidence': 0}
        try:
            current = df['close'].iloc[-1]
            ret_1m = (current - df['close'].iloc[-22]) / df['close'].iloc[-22] * 100 if len(df) > 22 else 0
            ret_3m = (current - df['close'].iloc[-65]) / df['close'].iloc[-65] * 100 if len(df) > 65 else 0
            ema_50 = df['ema_50'].iloc[-1] if 'ema_50' in df.columns else df['close'].ewm(span=50).mean().iloc[-1]
            vol_ratio = df['volume'].iloc[-5:].mean() / df['volume'].tail(20).mean() if df['volume'].tail(20).mean() > 0 else 1

            if ret_1m > 5 and ret_3m > 10 and current > ema_50 and vol_ratio > 1.2:
                atr = df['atr'].iloc[-1] if 'atr' in df.columns else (df['high'].tail(14).mean() - df['low'].tail(14).mean())
                return {'signal': 'BUY', 'entry': float(current),
                        'target1': float(current * 1.10), 'target2': float(current * 1.18),
                        'stop_loss': float(ema_50), 'confidence': 78,
                        'setup_type': 'SECTOR_ROTATION_LONG'}
            return {'signal': 'NONE', 'confidence': 0}
        except Exception:
            return {'signal': 'NONE', 'confidence': 0}


class SmallCapValue:
    """Small Cap Value Strategy"""
    name = "Small Cap Value"
    timeframe = "positional"
    description = "Identifies undervalued small caps with improving fundamentals"

    @staticmethod
    def analyze(df: pd.DataFrame, pe_ratio: float = 15.0) -> Dict:
        if len(df) < 100:
            return {'signal': 'NONE', 'confidence': 0}
        try:
            current = df['close'].iloc[-1]
            ema_200 = df['ema_200'].iloc[-1] if 'ema_200' in df.columns else df['close'].ewm(span=200).mean().iloc[-1]
            vol_trend = df['volume'].tail(10).mean() / df['volume'].tail(50).mean() if df['volume'].tail(50).mean() > 0 else 1
            ret_6m = (current - df['close'].iloc[-130]) / df['close'].iloc[-130] * 100 if len(df) > 130 else 0

            is_value = pe_ratio < 20
            vol_increasing = vol_trend > 1.3
            momentum_turn = ret_6m > 0 and current > ema_200

            if is_value and vol_increasing and momentum_turn:
                atr = df['atr'].iloc[-1] if 'atr' in df.columns else (df['high'].tail(14).mean() - df['low'].tail(14).mean())
                return {'signal': 'BUY', 'entry': float(current),
                        'target1': float(current * 1.20), 'target2': float(current * 1.35),
                        'stop_loss': float(ema_200 * 0.95), 'confidence': 80,
                        'setup_type': 'SMALL_CAP_VALUE'}
            return {'signal': 'NONE', 'confidence': 0}
        except Exception:
            return {'signal': 'NONE', 'confidence': 0}
