import pandas as pd
import numpy as np
from typing import Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MarketRegimeClassifier:
    def __init__(self, fyers_client):
        self.fyers_client = fyers_client
        self.regimes = [
            "BULL_TRENDING",
            "BULL_VOLATILE",
            "SIDEWAYS",
            "BEAR_VOLATILE",
            "BEAR_TRENDING"
        ]
    
    async def classify_regime(self) -> Dict:
        """Classify current market regime"""
        try:
            nifty_symbol = "NSE:NIFTY50-INDEX"
            vix_symbol = "NSE:INDIAVIX-INDEX"
            
            nifty_hist = self.fyers_client.get_historical(nifty_symbol, resolution="D", days=250)
            vix_quote = self.fyers_client.get_quotes([vix_symbol])
            
            if nifty_hist.get('s') != 'ok':
                return self._default_regime()
            
            candles = nifty_hist.get('candles', [])
            if not candles:
                return self._default_regime()
            
            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()
            
            current_price = df['close'].iloc[-1]
            ema_200 = df['ema_200'].iloc[-1]
            
            vix_value = 15.0
            if vix_quote.get('s') == 'ok' and vix_quote.get('d'):
                vix_data = list(vix_quote['d'].values())[0]
                vix_value = vix_data.get('ltp', 15.0)
            
            fii_flow = self._estimate_fii_flow(df)
            
            regime = self._determine_regime(current_price, ema_200, vix_value, fii_flow)
            
            return {
                'regime': regime,
                'nifty_price': float(current_price),
                'ema_200': float(ema_200),
                'vix': float(vix_value),
                'fii_flow_5d': float(fii_flow),
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error classifying regime: {e}")
            return self._default_regime()
    
    def _determine_regime(self, price: float, ema_200: float, vix: float, fii_flow: float) -> str:
        """Determine regime based on parameters"""
        above_ema = price > ema_200
        
        if above_ema:
            if vix < 15 and fii_flow > 0:
                return "BULL_TRENDING"
            elif vix >= 15 and vix <= 20:
                return "BULL_VOLATILE"
            else:
                return "SIDEWAYS"
        else:
            if vix > 20 and fii_flow < 0:
                return "BEAR_TRENDING"
            elif vix >= 15:
                return "BEAR_VOLATILE"
            else:
                return "SIDEWAYS"
    
    def _estimate_fii_flow(self, df: pd.DataFrame) -> float:
        """Estimate FII flow based on volume and price movement"""
        if len(df) < 5:
            return 0.0
        
        recent = df.tail(5)
        price_change = (recent['close'].iloc[-1] - recent['close'].iloc[0]) / recent['close'].iloc[0]
        volume_ratio = recent['volume'].mean() / df['volume'].mean()
        
        flow_estimate = price_change * volume_ratio * 1000
        return flow_estimate
    
    def _default_regime(self) -> Dict:
        """Return default regime when data unavailable"""
        return {
            'regime': 'SIDEWAYS',
            'nifty_price': 0.0,
            'ema_200': 0.0,
            'vix': 15.0,
            'fii_flow_5d': 0.0,
            'timestamp': datetime.now().isoformat()
        }