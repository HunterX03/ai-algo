"""Tier 4 — Intraday Order Flow Imbalance
Measures buying vs selling pressure at bid/ask level from tick data.
Replaces pure indicator entries with order flow signals for ORB/VWAP strategies.
"""
import numpy as np
import pandas as pd
from typing import Dict, List
from datetime import datetime
import secrets
import logging

logger = logging.getLogger(__name__)


def _sf(lo, hi):
    return lo + (secrets.randbelow(10_000_000) / 10_000_000) * (hi - lo)


class OrderFlowAnalyzer:
    """Approximates institutional order flow from tick-level data."""

    def __init__(self):
        self.imbalance_threshold = 0.6  # 60% directional = significant

    def analyze_order_flow(self, ticker: str, tick_data: pd.DataFrame = None) -> Dict:
        """Compute order flow imbalance metrics."""
        if tick_data is None or tick_data.empty:
            tick_data = self._generate_mock_ticks(ticker)

        metrics = self._compute_flow_metrics(tick_data)
        signal = self._generate_signal(metrics)

        return {
            "ticker": ticker,
            **metrics,
            "signal": signal["signal"],
            "signal_strength": signal["strength"],
            "description": signal["description"],
            "timestamp": datetime.now().isoformat(),
        }

    def _compute_flow_metrics(self, df: pd.DataFrame) -> Dict:
        """Compute buying/selling pressure metrics."""
        total_volume = df['volume'].sum()
        if total_volume == 0:
            return self._empty_metrics()

        # Classify trades: uptick = buy, downtick = sell
        df = df.copy()
        df['price_change'] = df['price'].diff()
        df['is_buy'] = df['price_change'] > 0
        df['is_sell'] = df['price_change'] < 0

        buy_volume = df.loc[df['is_buy'], 'volume'].sum()
        sell_volume = df.loc[df['is_sell'], 'volume'].sum()

        imbalance = (buy_volume - sell_volume) / total_volume if total_volume > 0 else 0
        buy_pct = buy_volume / total_volume * 100
        sell_pct = sell_volume / total_volume * 100

        # Volume-weighted average price of buys vs sells
        vwap_buy = (df.loc[df['is_buy'], 'price'] * df.loc[df['is_buy'], 'volume']).sum() / max(buy_volume, 1)
        vwap_sell = (df.loc[df['is_sell'], 'price'] * df.loc[df['is_sell'], 'volume']).sum() / max(sell_volume, 1)

        # Large trade detection (> 2x average)
        avg_trade = df['volume'].mean()
        large_buys = len(df[(df['is_buy']) & (df['volume'] > avg_trade * 2)])
        large_sells = len(df[(df['is_sell']) & (df['volume'] > avg_trade * 2)])

        # Delta (cumulative buying pressure)
        df['delta'] = np.where(df['is_buy'], df['volume'], -df['volume'])
        cumulative_delta = float(df['delta'].sum())

        return {
            "buy_volume": int(buy_volume),
            "sell_volume": int(sell_volume),
            "total_volume": int(total_volume),
            "buy_pct": round(buy_pct, 1),
            "sell_pct": round(sell_pct, 1),
            "imbalance": round(float(imbalance), 4),
            "vwap_buy": round(float(vwap_buy), 2),
            "vwap_sell": round(float(vwap_sell), 2),
            "large_buys": large_buys,
            "large_sells": large_sells,
            "cumulative_delta": round(cumulative_delta, 0),
            "delta_intensity": round(abs(cumulative_delta) / max(total_volume, 1) * 100, 2),
        }

    def _generate_signal(self, metrics: Dict) -> Dict:
        imb = metrics.get("imbalance", 0)
        delta_int = metrics.get("delta_intensity", 0)
        large_buys = metrics.get("large_buys", 0)
        large_sells = metrics.get("large_sells", 0)

        if imb > self.imbalance_threshold and large_buys > large_sells * 1.5:
            return {
                "signal": "STRONG_BUY_PRESSURE",
                "strength": min(95, int(50 + imb * 50)),
                "description": f"Heavy buying pressure (imb: {imb:.2f}). {large_buys} large buy blocks detected.",
            }
        elif imb < -self.imbalance_threshold and large_sells > large_buys * 1.5:
            return {
                "signal": "STRONG_SELL_PRESSURE",
                "strength": min(95, int(50 + abs(imb) * 50)),
                "description": f"Heavy selling pressure (imb: {imb:.2f}). {large_sells} large sell blocks.",
            }
        elif delta_int > 5:
            direction = "bullish" if metrics.get("cumulative_delta", 0) > 0 else "bearish"
            return {
                "signal": f"MODERATE_{direction.upper()}_FLOW",
                "strength": min(70, int(40 + delta_int * 3)),
                "description": f"Moderate {direction} flow. Delta intensity: {delta_int:.1f}%.",
            }
        return {"signal": "NEUTRAL_FLOW", "strength": 30, "description": "Balanced order flow. No directional bias."}

    @staticmethod
    def _generate_mock_ticks(ticker: str) -> pd.DataFrame:
        """Generate realistic mock tick data."""
        base = {"RELIANCE": 2450, "TCS": 3800, "SBIN": 780}.get(ticker, 1000)
        n = 500
        prices = [base]
        for _ in range(n - 1):
            prices.append(prices[-1] * (1 + _sf(-0.002, 0.002)))
        volumes = [int(_sf(100, 5000)) for _ in range(n)]
        return pd.DataFrame({"price": prices, "volume": volumes})

    @staticmethod
    def _empty_metrics() -> Dict:
        return {
            "buy_volume": 0, "sell_volume": 0, "total_volume": 0,
            "buy_pct": 50, "sell_pct": 50, "imbalance": 0,
            "vwap_buy": 0, "vwap_sell": 0, "large_buys": 0, "large_sells": 0,
            "cumulative_delta": 0, "delta_intensity": 0,
        }


order_flow = OrderFlowAnalyzer()
