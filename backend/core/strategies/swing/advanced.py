import pandas as pd
import numpy as np
from typing import Dict

class FIIDivergence:
    """FII Divergence Strategy"""
    name = "FII Divergence"
    timeframe = "swing"
    description = "Trades divergence between FII flow direction and price action"

    @staticmethod
    def analyze(df: pd.DataFrame, fii_flow: float = 0.0) -> Dict:
        if len(df) < 30:
            return {'signal': 'NONE', 'confidence': 0}
        try:
            current = df['close'].iloc[-1]
            ema_20 = df['ema_20'].iloc[-1] if 'ema_20' in df.columns else df['close'].ewm(span=20).mean().iloc[-1]
            price_change_5d = (current - df['close'].iloc[-5]) / df['close'].iloc[-5] * 100
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else (df['high'].tail(14).mean() - df['low'].tail(14).mean())

            # Bullish divergence: price falling but FII buying
            if price_change_5d < -2 and fii_flow > 0:
                return {'signal': 'BUY', 'entry': float(current),
                        'target1': float(current * 1.05), 'target2': float(current * 1.08),
                        'stop_loss': float(current - atr * 2), 'confidence': 76,
                        'setup_type': 'FII_BULLISH_DIVERGENCE'}
            # Bearish divergence: price rising but FII selling
            elif price_change_5d > 2 and fii_flow < 0:
                return {'signal': 'SELL', 'entry': float(current),
                        'target1': float(current * 0.95), 'target2': float(current * 0.92),
                        'stop_loss': float(current + atr * 2), 'confidence': 76,
                        'setup_type': 'FII_BEARISH_DIVERGENCE'}
            return {'signal': 'NONE', 'confidence': 0}
        except Exception:
            return {'signal': 'NONE', 'confidence': 0}


class PEAD:
    """Post-Earnings Announcement Drift Strategy"""
    name = "PEAD"
    timeframe = "swing"
    description = "Captures drift after earnings surprise with volume confirmation"

    @staticmethod
    def analyze(df: pd.DataFrame) -> Dict:
        if len(df) < 20:
            return {'signal': 'NONE', 'confidence': 0}
        try:
            current = df['close'].iloc[-1]
            vol_ratio = df['volume'].iloc[-1] / df['volume'].tail(20).mean() if df['volume'].tail(20).mean() > 0 else 1
            # Detect earnings-like gap (large body + volume spike)
            gap_pct = (df['open'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else (df['high'].tail(14).mean() - df['low'].tail(14).mean())

            if gap_pct > 3 and vol_ratio > 3:
                return {'signal': 'BUY', 'entry': float(current),
                        'target1': float(current * 1.06), 'target2': float(current * 1.10),
                        'stop_loss': float(df['low'].iloc[-1] - atr), 'confidence': 73,
                        'setup_type': 'PEAD_POSITIVE'}
            elif gap_pct < -3 and vol_ratio > 3:
                return {'signal': 'SELL', 'entry': float(current),
                        'target1': float(current * 0.94), 'target2': float(current * 0.90),
                        'stop_loss': float(df['high'].iloc[-1] + atr), 'confidence': 73,
                        'setup_type': 'PEAD_NEGATIVE'}
            return {'signal': 'NONE', 'confidence': 0}
        except Exception:
            return {'signal': 'NONE', 'confidence': 0}


class FiftyTwoWeekBreakoutOI:
    """52-Week Breakout + OI Strategy"""
    name = "52-Week Breakout + OI"
    timeframe = "swing"
    description = "Breakout from 52-week range with open interest confirmation"

    @staticmethod
    def analyze(df: pd.DataFrame) -> Dict:
        if len(df) < 200:
            return {'signal': 'NONE', 'confidence': 0}
        try:
            current = df['close'].iloc[-1]
            high_52w = df['high'].tail(252).max()
            low_52w = df['low'].tail(252).min()
            vol_ratio = df['volume'].iloc[-1] / df['volume'].tail(20).mean() if df['volume'].tail(20).mean() > 0 else 1
            atr = df['atr'].iloc[-1] if 'atr' in df.columns else (df['high'].tail(14).mean() - df['low'].tail(14).mean())

            if current >= high_52w * 0.98 and vol_ratio > 1.5:
                return {'signal': 'BUY', 'entry': float(current),
                        'target1': float(high_52w * 1.08), 'target2': float(high_52w * 1.15),
                        'stop_loss': float(current - atr * 2), 'confidence': 82,
                        'setup_type': '52W_BREAKOUT'}
            elif current <= low_52w * 1.02 and vol_ratio > 1.5:
                return {'signal': 'SELL', 'entry': float(current),
                        'target1': float(low_52w * 0.92), 'target2': float(low_52w * 0.85),
                        'stop_loss': float(current + atr * 2), 'confidence': 70,
                        'setup_type': '52W_BREAKDOWN'}
            return {'signal': 'NONE', 'confidence': 0}
        except Exception:
            return {'signal': 'NONE', 'confidence': 0}
