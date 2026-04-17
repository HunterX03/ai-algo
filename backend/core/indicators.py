import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


class TechnicalIndicators:
    @staticmethod
    def _ema(series, period):
        return series.ewm(span=period, adjust=False).mean()

    @staticmethod
    def _sma(series, period):
        return series.rolling(window=period).mean()

    @staticmethod
    def _rsi(close, period=14):
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()
        for i in range(period, len(close)):
            avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
            avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def _atr(high, low, close, period=14):
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    @staticmethod
    def _macd(close, fast=12, slow=26, signal=9):
        fast_ema = close.ewm(span=fast, adjust=False).mean()
        slow_ema = close.ewm(span=slow, adjust=False).mean()
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def _bbands(close, period=20, nbdev=2):
        middle = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        upper = middle + (std * nbdev)
        lower = middle - (std * nbdev)
        return upper, middle, lower

    @staticmethod
    def _adx(high, low, close, period=14):
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        tr = TechnicalIndicators._atr(high, low, close, 1) * 1  # just TR
        atr = TechnicalIndicators._atr(high, low, close, period)
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean()
        return adx

    @staticmethod
    def _obv(close, volume):
        direction = np.sign(close.diff()).fillna(0)
        return (direction * volume).cumsum()

    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < 30:
            return df
        try:
            df = df.copy()
            df['ema_20'] = TechnicalIndicators._ema(df['close'], 20)
            df['ema_50'] = TechnicalIndicators._ema(df['close'], 50)
            df['ema_200'] = TechnicalIndicators._ema(df['close'], 200)
            df['rsi'] = TechnicalIndicators._rsi(df['close'], 14)
            macd, macd_signal, macd_hist = TechnicalIndicators._macd(df['close'])
            df['macd'] = macd
            df['macd_signal'] = macd_signal
            df['macd_hist'] = macd_hist
            upper, middle, lower = TechnicalIndicators._bbands(df['close'])
            df['bb_upper'] = upper
            df['bb_middle'] = middle
            df['bb_lower'] = lower
            df['bb_width'] = (upper - lower) / middle
            df['atr'] = TechnicalIndicators._atr(df['high'], df['low'], df['close'])
            df['adx'] = TechnicalIndicators._adx(df['high'], df['low'], df['close'])
            df['obv'] = TechnicalIndicators._obv(df['close'], df['volume'])
            df['volume_sma_20'] = TechnicalIndicators._sma(df['volume'], 20)
            df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
            df['vwap'] = (df['typical_price'] * df['volume']).cumsum() / df['volume'].cumsum()
            return df
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return df

    @staticmethod
    def get_support_resistance(df: pd.DataFrame, lookback: int = 20) -> Tuple[float, float]:
        if len(df) < lookback:
            return float(df['low'].min()), float(df['high'].max())
        recent = df.tail(lookback)
        return float(recent['low'].min()), float(recent['high'].max())

    @staticmethod
    def calculate_fibonacci_levels(high: float, low: float) -> Dict[str, float]:
        diff = high - low
        return {
            'level_0': round(low, 2),
            'level_236': round(low + diff * 0.236, 2),
            'level_382': round(low + diff * 0.382, 2),
            'level_50': round(low + diff * 0.5, 2),
            'level_618': round(low + diff * 0.618, 2),
            'level_786': round(low + diff * 0.786, 2),
            'level_100': round(high, 2),
        }

    @staticmethod
    def detect_chart_patterns(df: pd.DataFrame) -> List[str]:
        patterns = []
        if len(df) < 3:
            return patterns
        try:
            last = df.iloc[-1]
            body = abs(last['close'] - last['open'])
            total_range = last['high'] - last['low']
            if total_range > 0 and body / total_range < 0.1:
                patterns.append('DOJI')
            if last['close'] > last['open']:
                lower_wick = last['open'] - last['low']
                if total_range > 0 and lower_wick / total_range > 0.6:
                    patterns.append('HAMMER')
            prev = df.iloc[-2]
            if prev['close'] < prev['open'] and last['close'] > last['open']:
                if last['close'] > prev['open'] and last['open'] < prev['close']:
                    patterns.append('BULLISH_ENGULFING')
        except:
            pass
        return patterns
