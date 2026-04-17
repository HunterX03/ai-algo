import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import talib as ta

class TechnicalIndicators:
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        if df.empty or len(df) < 50:
            return df
        
        try:
            df = df.copy()
            
            df['ema_20'] = ta.EMA(df['close'].values, timeperiod=20)
            df['ema_50'] = ta.EMA(df['close'].values, timeperiod=50)
            df['ema_200'] = ta.EMA(df['close'].values, timeperiod=200)
            
            df['rsi'] = ta.RSI(df['close'].values, timeperiod=14)
            
            macd, macd_signal, macd_hist = ta.MACD(df['close'].values)
            df['macd'] = macd
            df['macd_signal'] = macd_signal
            df['macd_hist'] = macd_hist
            
            upper_band, middle_band, lower_band = ta.BBANDS(
                df['close'].values, timeperiod=20, nbdevup=2, nbdevdn=2
            )
            df['bb_upper'] = upper_band
            df['bb_middle'] = middle_band
            df['bb_lower'] = lower_band
            df['bb_width'] = (upper_band - lower_band) / middle_band
            
            df['atr'] = ta.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)
            
            df['adx'] = ta.ADX(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)
            
            df['obv'] = ta.OBV(df['close'].values, df['volume'].values)
            
            df['volume_sma_20'] = ta.SMA(df['volume'].values, timeperiod=20)
            
            df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
            df['vwap'] = (df['typical_price'] * df['volume']).cumsum() / df['volume'].cumsum()
            
            df['stoch_k'], df['stoch_d'] = ta.STOCH(
                df['high'].values, df['low'].values, df['close'].values
            )
            
            return df
        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return df
    
    @staticmethod
    def get_support_resistance(df: pd.DataFrame, lookback: int = 20) -> Tuple[float, float]:
        """Calculate support and resistance levels"""
        if len(df) < lookback:
            return df['low'].min(), df['high'].max()
        
        recent = df.tail(lookback)
        support = recent['low'].min()
        resistance = recent['high'].max()
        return support, resistance
    
    @staticmethod
    def calculate_fibonacci_levels(high: float, low: float) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels"""
        diff = high - low
        return {
            'level_0': low,
            'level_236': low + (diff * 0.236),
            'level_382': low + (diff * 0.382),
            'level_50': low + (diff * 0.5),
            'level_618': low + (diff * 0.618),
            'level_786': low + (diff * 0.786),
            'level_100': high
        }
    
    @staticmethod
    def detect_chart_patterns(df: pd.DataFrame) -> List[str]:
        """Detect basic chart patterns"""
        patterns = []
        
        if len(df) < 3:
            return patterns
        
        try:
            if ta.CDLDOJI(df['open'].values, df['high'].values, df['low'].values, df['close'].values)[-1] != 0:
                patterns.append('DOJI')
            
            if ta.CDLHAMMER(df['open'].values, df['high'].values, df['low'].values, df['close'].values)[-1] != 0:
                patterns.append('HAMMER')
            
            if ta.CDLENGULFING(df['open'].values, df['high'].values, df['low'].values, df['close'].values)[-1] != 0:
                patterns.append('ENGULFING')
        except:
            pass
        
        return patterns