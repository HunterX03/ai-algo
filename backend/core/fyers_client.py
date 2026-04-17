from fyers_apiv3 import fyersModel
import os
import logging
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FyersClient:
    def __init__(self):
        self.api_id = os.getenv('FYERS_API_ID', '')
        self.secret = os.getenv('FYERS_API_SECRET', '')
        self.access_token = os.getenv('FYERS_ACCESS_TOKEN', '')
        self.client = None
        self._is_configured = False
        
        if self.access_token and 'PUT_YOUR' not in self.access_token:
            try:
                self.client = fyersModel.FyersModel(
                    client_id=self.api_id,
                    token=self.access_token,
                    is_async=False,
                    log_path=""
                )
                self._is_configured = True
                logger.info("Fyers client initialized with real credentials")
            except Exception as e:
                logger.warning(f"Fyers client init failed: {e}")
        else:
            logger.info("Fyers API not configured — running in demo mode")
    
    @property
    def is_demo(self):
        return not self._is_configured
    
    def get_quotes(self, symbols: List[str]) -> Dict:
        if self.is_demo:
            return self._mock_quotes(symbols)
        try:
            symbol_string = ",".join(symbols[:50])
            response = self.client.quotes({"symbols": symbol_string})
            return response
        except Exception as e:
            logger.error(f"Error fetching quotes: {e}")
            return self._mock_quotes(symbols)
    
    def get_historical(self, symbol: str, resolution: str = "D", days: int = 365) -> Dict:
        if self.is_demo:
            return self._mock_historical(symbol, resolution, days)
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            data = {
                "symbol": symbol,
                "resolution": resolution,
                "date_format": "0",
                "range_from": int(start_date.timestamp()),
                "range_to": int(end_date.timestamp()),
                "cont_flag": "1"
            }
            response = self.client.history(data)
            return response
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return self._mock_historical(symbol, resolution, days)
    
    def get_market_depth(self, symbol: str) -> Dict:
        if self.is_demo:
            return self._mock_depth(symbol)
        try:
            data = {"symbols": [symbol], "ohlcv_flag": "1"}
            response = self.client.market_depth(data)
            return response
        except Exception as e:
            logger.error(f"Error fetching market depth: {e}")
            return self._mock_depth(symbol)
    
    def format_nse_symbol(self, symbol: str) -> str:
        if ':' in symbol:
            return symbol
        return f"NSE:{symbol}-EQ"
    
    # ── Mock data generators ──
    
    def _mock_quotes(self, symbols: List[str]) -> Dict:
        import random
        data = {}
        base_prices = {
            'NSE:RELIANCE-EQ': 2450, 'NSE:TCS-EQ': 3800, 'NSE:HDFCBANK-EQ': 1680,
            'NSE:INFY-EQ': 1520, 'NSE:ICICIBANK-EQ': 1250, 'NSE:HINDUNILVR-EQ': 2350,
            'NSE:ITC-EQ': 430, 'NSE:SBIN-EQ': 780, 'NSE:BHARTIARTL-EQ': 1650,
            'NSE:BAJFINANCE-EQ': 6800, 'NSE:ASIANPAINT-EQ': 2900, 'NSE:MARUTI-EQ': 12500,
            'NSE:HCLTECH-EQ': 1720, 'NSE:AXISBANK-EQ': 1150, 'NSE:LT-EQ': 3400,
            'NSE:ULTRACEMCO-EQ': 11200, 'NSE:WIPRO-EQ': 520, 'NSE:NESTLEIND-EQ': 2400,
            'NSE:SUNPHARMA-EQ': 1780, 'NSE:TITAN-EQ': 3200, 'NSE:TECHM-EQ': 1640,
            'NSE:ONGC-EQ': 260, 'NSE:NTPC-EQ': 350, 'NSE:KOTAKBANK-EQ': 1850,
            'NSE:POWERGRID-EQ': 310,
        }
        for sym in symbols:
            base = base_prices.get(sym, 1000 + random.randint(0, 2000))
            change = base * random.uniform(-0.03, 0.03)
            data[sym] = {
                'ltp': round(base + change, 2),
                'open': round(base - random.uniform(0, base * 0.01), 2),
                'high': round(base + base * random.uniform(0.005, 0.025), 2),
                'low': round(base - base * random.uniform(0.005, 0.025), 2),
                'close': round(base + change, 2),
                'volume': random.randint(500000, 15000000),
                'change': round(change, 2),
                'change_percent': round((change / base) * 100, 2),
            }
        return {'s': 'ok', 'd': data}
    
    def _mock_historical(self, symbol: str, resolution: str, days: int) -> Dict:
        import random
        import numpy as np
        
        base_prices = {
            'NSE:RELIANCE-EQ': 2450, 'NSE:TCS-EQ': 3800, 'NSE:HDFCBANK-EQ': 1680,
            'NSE:INFY-EQ': 1520, 'NSE:ICICIBANK-EQ': 1250, 'NSE:HINDUNILVR-EQ': 2350,
            'NSE:ITC-EQ': 430, 'NSE:SBIN-EQ': 780, 'NSE:BHARTIARTL-EQ': 1650,
            'NSE:BAJFINANCE-EQ': 6800, 'NSE:ASIANPAINT-EQ': 2900, 'NSE:MARUTI-EQ': 12500,
            'NSE:HCLTECH-EQ': 1720, 'NSE:AXISBANK-EQ': 1150, 'NSE:LT-EQ': 3400,
            'NSE:ULTRACEMCO-EQ': 11200, 'NSE:WIPRO-EQ': 520, 'NSE:NESTLEIND-EQ': 2400,
            'NSE:SUNPHARMA-EQ': 1780, 'NSE:TITAN-EQ': 3200, 'NSE:TECHM-EQ': 1640,
            'NSE:ONGC-EQ': 260, 'NSE:NTPC-EQ': 350, 'NSE:KOTAKBANK-EQ': 1850,
            'NSE:POWERGRID-EQ': 310,
        }
        base = base_prices.get(symbol, 1000)
        
        candles = []
        end = datetime.now()
        
        num_candles = min(days, 365)
        if resolution in ['5', '15', '30', '60']:
            num_candles = min(days * 6 * (60 // int(resolution)), 2000)
        
        price = base * (1 + random.uniform(-0.15, 0.05))
        trend = random.uniform(-0.0005, 0.001)
        
        for i in range(num_candles):
            if resolution == 'D':
                ts = int((end - timedelta(days=num_candles - i)).timestamp())
            else:
                ts = int((end - timedelta(minutes=(num_candles - i) * int(resolution))).timestamp())
            
            daily_return = trend + random.gauss(0, 0.015)
            price = price * (1 + daily_return)
            
            o = round(price, 2)
            h = round(price * (1 + abs(random.gauss(0, 0.008))), 2)
            l = round(price * (1 - abs(random.gauss(0, 0.008))), 2)
            c = round(price * (1 + random.gauss(0, 0.005)), 2)
            v = random.randint(300000, 12000000)
            
            candles.append([ts, o, h, l, c, v])
        
        return {'s': 'ok', 'candles': candles}
    
    def _mock_depth(self, symbol: str) -> Dict:
        import random
        base = 1000 + random.randint(0, 2000)
        return {
            's': 'ok',
            'd': {
                'ltp': base,
                'bid': round(base - 0.5, 2),
                'ask': round(base + 0.5, 2),
                'o': round(base * 0.99, 2),
                'h': round(base * 1.02, 2),
                'l': round(base * 0.98, 2),
                'c': round(base, 2),
                'v': random.randint(1000000, 5000000)
            }
        }


fyers_client = FyersClient()
