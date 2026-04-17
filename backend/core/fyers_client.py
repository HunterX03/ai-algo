from fyers_apiv3 import fyersModel
import os
import secrets
import logging
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def _secure_float(low: float, high: float) -> float:
    """Cryptographically secure random float in [low, high)."""
    return low + (secrets.randbelow(10_000_000) / 10_000_000) * (high - low)


def _secure_int(low: int, high: int) -> int:
    return low + secrets.randbelow(high - low + 1)


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
                    client_id=self.api_id, token=self.access_token,
                    is_async=False, log_path=""
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
            return self.client.quotes({"symbols": ",".join(symbols[:50])})
        except Exception as e:
            logger.error(f"Error fetching quotes: {e}")
            return self._mock_quotes(symbols)

    def get_historical(self, symbol: str, resolution: str = "D", days: int = 365) -> Dict:
        if self.is_demo:
            return self._mock_historical(symbol, resolution, days)
        try:
            end = datetime.now()
            start = end - timedelta(days=days)
            return self.client.history({
                "symbol": symbol, "resolution": resolution,
                "date_format": "0",
                "range_from": int(start.timestamp()),
                "range_to": int(end.timestamp()),
                "cont_flag": "1"
            })
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return self._mock_historical(symbol, resolution, days)

    def get_market_depth(self, symbol: str) -> Dict:
        if self.is_demo:
            return self._mock_depth(symbol)
        try:
            return self.client.market_depth({"symbols": [symbol], "ohlcv_flag": "1"})
        except Exception as e:
            logger.error(f"Error fetching depth: {e}")
            return self._mock_depth(symbol)

    def format_nse_symbol(self, symbol: str) -> str:
        return symbol if ':' in symbol else f"NSE:{symbol}-EQ"

    # ── Mock data (secure RNG) ──

    _BASE_PRICES = {
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

    def _mock_quotes(self, symbols: List[str]) -> Dict:
        data = {}
        for sym in symbols:
            base = self._BASE_PRICES.get(sym, _secure_int(800, 3000))
            change = base * _secure_float(-0.03, 0.03)
            data[sym] = {
                'ltp': round(base + change, 2),
                'open': round(base - _secure_float(0, base * 0.01), 2),
                'high': round(base + base * _secure_float(0.005, 0.025), 2),
                'low': round(base - base * _secure_float(0.005, 0.025), 2),
                'close': round(base + change, 2),
                'volume': _secure_int(500_000, 15_000_000),
                'change': round(change, 2),
                'change_percent': round((change / base) * 100, 2),
            }
        return {'s': 'ok', 'd': data}

    def _mock_historical(self, symbol: str, resolution: str, days: int) -> Dict:
        import math
        base = self._BASE_PRICES.get(symbol, 1000)
        num = min(days, 365)
        if resolution in ('5', '15', '30', '60'):
            num = min(days * 6 * (60 // int(resolution)), 2000)

        price = base * (1 + _secure_float(-0.15, 0.05))
        trend = _secure_float(-0.0005, 0.001)
        end = datetime.now()
        candles = []

        for i in range(num):
            ts = int((end - timedelta(days=num - i) if resolution == 'D'
                       else end - timedelta(minutes=(num - i) * int(resolution))).timestamp())
            daily_ret = trend + (_secure_float(-0.015, 0.015))
            price *= (1 + daily_ret)
            o = round(price, 2)
            h = round(price * (1 + abs(_secure_float(0, 0.008))), 2)
            l = round(price * (1 - abs(_secure_float(0, 0.008))), 2)
            c = round(price * (1 + _secure_float(-0.005, 0.005)), 2)
            candles.append([ts, o, h, l, c, _secure_int(300_000, 12_000_000)])

        return {'s': 'ok', 'candles': candles}

    def _mock_depth(self, symbol: str) -> Dict:
        base = self._BASE_PRICES.get(symbol, _secure_int(800, 3000))
        return {'s': 'ok', 'd': {
            'ltp': base, 'bid': round(base - 0.5, 2), 'ask': round(base + 0.5, 2),
            'o': round(base * 0.99, 2), 'h': round(base * 1.02, 2),
            'l': round(base * 0.98, 2), 'c': round(base, 2),
            'v': _secure_int(1_000_000, 5_000_000)
        }}


fyers_client = FyersClient()
