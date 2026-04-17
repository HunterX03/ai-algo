"""Tier 3 — Options Flow as Leading Indicator
Reads OI buildup, IV spikes, and unusual options activity to generate equity signals.
Uses mock data when Fyers API is not configured.
"""
import numpy as np
import secrets
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# NSE F&O stocks
FNO_STOCKS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN",
    "BAJFINANCE", "BHARTIARTL", "HCLTECH", "AXISBANK", "LT",
    "MARUTI", "TITAN", "SUNPHARMA", "WIPRO", "TECHM", "KOTAKBANK"
]


def _sf(lo, hi):
    return lo + (secrets.randbelow(10_000_000) / 10_000_000) * (hi - lo)


class OptionsFlowAnalyzer:
    """Analyzes NSE options data for unusual activity that precedes equity moves."""

    def __init__(self, fyers_client=None):
        self.client = fyers_client

    def analyze_stock_options(self, ticker: str) -> Dict:
        """Full options flow analysis for a single F&O stock."""
        data = self._get_options_data(ticker)
        pcr = data["put_oi"] / data["call_oi"] if data["call_oi"] > 0 else 1.0
        max_pain = data["max_pain_strike"]
        iv_rank = data["iv_rank"]
        unusual = self._detect_unusual_activity(data)

        signal = "NONE"
        if pcr > 1.5 and unusual["has_unusual_call_buying"]:
            signal = "BULLISH"
        elif pcr < 0.7 and unusual["has_unusual_put_buying"]:
            signal = "BEARISH"
        elif iv_rank > 80:
            signal = "HIGH_IV_WARNING"
        elif iv_rank < 20 and unusual["total_unusual_trades"] > 3:
            signal = "IV_EXPANSION_EXPECTED"

        return {
            "ticker": ticker,
            "put_call_ratio": round(pcr, 3),
            "total_call_oi": data["call_oi"],
            "total_put_oi": data["put_oi"],
            "max_pain_strike": max_pain,
            "iv_rank": round(iv_rank, 1),
            "current_iv": round(data["current_iv"], 1),
            "iv_percentile": round(data["iv_percentile"], 1),
            "unusual_activity": unusual,
            "signal": signal,
            "confidence": self._calc_confidence(pcr, iv_rank, unusual),
            "timestamp": datetime.now().isoformat(),
        }

    def scan_all_fno(self) -> List[Dict]:
        """Scan all F&O stocks for options flow signals."""
        results = []
        for t in FNO_STOCKS:
            r = self.analyze_stock_options(t)
            if r["signal"] != "NONE":
                results.append(r)
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results

    def _get_options_data(self, ticker: str) -> Dict:
        """Get options chain data — mock when API not available."""
        # Production: use Fyers API option chain endpoint
        # For now: generate realistic mock data
        base_price = {
            "RELIANCE": 2450, "TCS": 3800, "HDFCBANK": 1680, "INFY": 1520,
            "ICICIBANK": 1250, "SBIN": 780, "BAJFINANCE": 6800,
        }.get(ticker, 1000)

        strike_step = max(50, int(base_price * 0.02))
        atm_strike = round(base_price / strike_step) * strike_step

        return {
            "call_oi": int(_sf(5e6, 50e6)),
            "put_oi": int(_sf(4e6, 55e6)),
            "call_volume": int(_sf(1e6, 20e6)),
            "put_volume": int(_sf(1e6, 25e6)),
            "max_pain_strike": atm_strike,
            "current_iv": _sf(15, 45),
            "iv_rank": _sf(10, 90),
            "iv_percentile": _sf(15, 85),
            "atm_strike": atm_strike,
            "strikes": self._generate_strikes(atm_strike, strike_step),
        }

    @staticmethod
    def _generate_strikes(atm: int, step: int) -> List[Dict]:
        strikes = []
        for i in range(-5, 6):
            s = atm + i * step
            strikes.append({
                "strike": s,
                "call_oi": int(_sf(1e5, 5e6)),
                "put_oi": int(_sf(1e5, 5e6)),
                "call_iv": round(_sf(15, 40), 1),
                "put_iv": round(_sf(15, 40), 1),
                "call_volume": int(_sf(1e4, 1e6)),
                "put_volume": int(_sf(1e4, 1e6)),
            })
        return strikes

    @staticmethod
    def _detect_unusual_activity(data: Dict) -> Dict:
        unusual_calls = 0
        unusual_puts = 0
        for strike in data.get("strikes", []):
            if strike["call_volume"] > 5e5 and strike["call_oi"] > 3e6:
                unusual_calls += 1
            if strike["put_volume"] > 5e5 and strike["put_oi"] > 3e6:
                unusual_puts += 1
        return {
            "has_unusual_call_buying": unusual_calls >= 2,
            "has_unusual_put_buying": unusual_puts >= 2,
            "unusual_call_strikes": unusual_calls,
            "unusual_put_strikes": unusual_puts,
            "total_unusual_trades": unusual_calls + unusual_puts,
        }

    @staticmethod
    def _calc_confidence(pcr: float, iv_rank: float, unusual: Dict) -> int:
        c = 40
        if abs(pcr - 1.0) > 0.5:
            c += 15
        if iv_rank > 70 or iv_rank < 30:
            c += 10
        c += min(20, unusual["total_unusual_trades"] * 5)
        return min(95, c)


options_flow = OptionsFlowAnalyzer()
