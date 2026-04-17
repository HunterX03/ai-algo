from typing import Dict, List
import pandas as pd
import numpy as np

class SignalRanker:
    """Composite signal scoring and ranking"""
    
    def __init__(self, market_regime: str = "SIDEWAYS"):
        self.market_regime = market_regime
        self.regime_weights = self._get_regime_weights(market_regime)
    
    def _get_regime_weights(self, regime: str) -> Dict[str, float]:
        """Adjust weights based on market regime"""
        weight_sets = {
            "BULL_TRENDING": {
                "technical": 0.30,
                "strategy": 0.35,
                "volume": 0.20,
                "sentiment": 0.15
            },
            "BULL_VOLATILE": {
                "technical": 0.35,
                "strategy": 0.30,
                "volume": 0.20,
                "sentiment": 0.15
            },
            "SIDEWAYS": {
                "technical": 0.35,
                "strategy": 0.30,
                "volume": 0.20,
                "sentiment": 0.15
            },
            "BEAR_VOLATILE": {
                "technical": 0.40,
                "strategy": 0.25,
                "volume": 0.20,
                "sentiment": 0.15
            },
            "BEAR_TRENDING": {
                "technical": 0.40,
                "strategy": 0.25,
                "volume": 0.20,
                "sentiment": 0.15
            }
        }
        
        return weight_sets.get(regime, weight_sets["SIDEWAYS"])
    
    def calculate_composite_score(self, signal: Dict) -> float:
        """Calculate composite signal score"""
        try:
            technical_score = signal.get('technical_score', 50) / 100
            strategy_score = signal.get('confidence', 50) / 100
            volume_score = signal.get('volume_score', 50) / 100
            sentiment_score = (signal.get('sentiment_score', 0) + 1) / 2
            
            composite = (
                technical_score * self.regime_weights['technical'] +
                strategy_score * self.regime_weights['strategy'] +
                volume_score * self.regime_weights['volume'] +
                sentiment_score * self.regime_weights['sentiment']
            )
            
            return min(max(composite * 100, 0), 100)
        
        except Exception as e:
            print(f"Error calculating composite score: {e}")
            return 50.0
    
    def rank_signals(self, signals: List[Dict]) -> List[Dict]:
        """Rank signals by composite score"""
        for signal in signals:
            signal['composite_score'] = self.calculate_composite_score(signal)
        
        ranked = sorted(signals, key=lambda x: x.get('composite_score', 0), reverse=True)
        
        for idx, signal in enumerate(ranked, 1):
            signal['rank'] = idx
        
        return ranked
    
    @staticmethod
    def calculate_technical_score(df: pd.DataFrame) -> float:
        """Calculate technical score from indicators"""
        if len(df) < 20:
            return 50.0
        
        try:
            score = 50.0
            
            current_price = df['close'].iloc[-1]
            if 'ema_20' in df.columns and 'ema_50' in df.columns:
                ema_20 = df['ema_20'].iloc[-1]
                ema_50 = df['ema_50'].iloc[-1]
                
                if current_price > ema_20 > ema_50:
                    score += 15
                elif current_price < ema_20 < ema_50:
                    score -= 15
            
            if 'rsi' in df.columns:
                rsi = df['rsi'].iloc[-1]
                if 40 < rsi < 60:
                    score += 10
                elif rsi > 70 or rsi < 30:
                    score -= 10
            
            if 'macd_hist' in df.columns:
                macd_hist = df['macd_hist'].iloc[-1]
                prev_macd_hist = df['macd_hist'].iloc[-2]
                
                if macd_hist > 0 and macd_hist > prev_macd_hist:
                    score += 10
                elif macd_hist < 0 and macd_hist < prev_macd_hist:
                    score -= 10
            
            if 'adx' in df.columns:
                adx = df['adx'].iloc[-1]
                if adx > 25:
                    score += 15
            
            return min(max(score, 0), 100)
        
        except Exception as e:
            print(f"Error calculating technical score: {e}")
            return 50.0
    
    @staticmethod
    def calculate_volume_score(df: pd.DataFrame) -> float:
        """Calculate volume score"""
        if len(df) < 20:
            return 50.0
        
        try:
            current_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].tail(20).mean()
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            if volume_ratio > 2.0:
                return 90.0
            elif volume_ratio > 1.5:
                return 75.0
            elif volume_ratio > 1.0:
                return 60.0
            elif volume_ratio > 0.8:
                return 50.0
            else:
                return 35.0
        
        except Exception as e:
            print(f"Error calculating volume score: {e}")
            return 50.0