"""Tier 2 — Statistical Pairs Trading (Cointegration-based)
Finds cointegrated NSE pairs, computes z-score of spread, signals at +/-2 std dev.
Market neutral — works in any regime.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from scipy import stats
import logging

logger = logging.getLogger(__name__)

# Known NSE pairs that historically show cointegration
CANDIDATE_PAIRS = [
    ("HDFCBANK", "ICICIBANK"),
    ("RELIANCE", "ONGC"),
    ("INFY", "TCS"),
    ("SBIN", "AXISBANK"),
    ("HCLTECH", "TECHM"),
    ("NTPC", "POWERGRID"),
    ("SUNPHARMA", "NESTLEIND"),
    ("MARUTI", "BAJFINANCE"),
    ("ITC", "HINDUNILVR"),
    ("LT", "ULTRACEMCO"),
]


class PairsTrader:
    """Statistical pairs trading engine using cointegration and z-score."""

    def __init__(self):
        self.lookback = 60  # days for z-score calc
        self.entry_z = 2.0
        self.exit_z = 0.5

    def analyze_pair(self, ticker_a: str, ticker_b: str,
                     prices_a: pd.Series, prices_b: pd.Series) -> Dict:
        """Analyze a pair for trading signal."""
        if len(prices_a) < self.lookback or len(prices_b) < self.lookback:
            return self._no_signal(ticker_a, ticker_b)

        # Align lengths
        n = min(len(prices_a), len(prices_b))
        a = prices_a.values[-n:].astype(float)
        b = prices_b.values[-n:].astype(float)

        # Cointegration test (Engle-Granger)
        coint_stat, hedge_ratio = self._cointegration_test(a, b)

        # Compute spread and z-score
        spread = a - hedge_ratio * b
        spread_mean = np.mean(spread[-self.lookback:])
        spread_std = np.std(spread[-self.lookback:])
        if spread_std == 0:
            return self._no_signal(ticker_a, ticker_b)

        z_score = (spread[-1] - spread_mean) / spread_std

        signal = "NONE"
        if z_score > self.entry_z:
            signal = "SHORT_A_LONG_B"  # spread too wide, short A, long B
        elif z_score < -self.entry_z:
            signal = "LONG_A_SHORT_B"  # spread too narrow, long A, short B
        elif abs(z_score) < self.exit_z:
            signal = "EXIT"  # mean reverted

        return {
            "pair": f"{ticker_a}/{ticker_b}",
            "ticker_a": ticker_a,
            "ticker_b": ticker_b,
            "hedge_ratio": round(float(hedge_ratio), 4),
            "z_score": round(float(z_score), 3),
            "spread_mean": round(float(spread_mean), 2),
            "spread_std": round(float(spread_std), 2),
            "current_spread": round(float(spread[-1]), 2),
            "cointegration_stat": round(float(coint_stat), 4),
            "is_cointegrated": bool(coint_stat < -2.5),
            "signal": signal,
            "confidence": self._calc_confidence(coint_stat, z_score),
            "description": self._describe_signal(signal, ticker_a, ticker_b, z_score),
        }

    def scan_all_pairs(self, price_data: Dict[str, pd.Series]) -> List[Dict]:
        """Scan all candidate pairs and return signals."""
        results = []
        for a, b in CANDIDATE_PAIRS:
            if a in price_data and b in price_data:
                result = self.analyze_pair(a, b, price_data[a], price_data[b])
                results.append(result)
        # Sort by absolute z-score (most extreme first)
        results.sort(key=lambda x: abs(x["z_score"]), reverse=True)
        return results

    @staticmethod
    def _cointegration_test(a: np.ndarray, b: np.ndarray) -> Tuple[float, float]:
        """Engle-Granger cointegration test. Returns (ADF stat, hedge ratio)."""
        # OLS regression: a = beta * b + residual
        slope, intercept, _, _, _ = stats.linregress(b, a)
        residuals = a - slope * b - intercept
        # ADF on residuals (simplified)
        diff_res = np.diff(residuals)
        lagged = residuals[:-1]
        if np.std(lagged) == 0:
            return 0.0, slope
        slope_adf, _, _, _, _ = stats.linregress(lagged, diff_res)
        se = np.std(diff_res - slope_adf * lagged) / (np.std(lagged) * np.sqrt(len(lagged)))
        adf_stat = slope_adf / se if se > 0 else 0
        return adf_stat, slope

    @staticmethod
    def _calc_confidence(coint_stat: float, z_score: float) -> int:
        base = 50
        if coint_stat < -3.5:
            base += 20
        elif coint_stat < -2.5:
            base += 10
        if abs(z_score) > 2.5:
            base += 15
        elif abs(z_score) > 2.0:
            base += 10
        return min(95, base)

    @staticmethod
    def _describe_signal(signal: str, a: str, b: str, z: float) -> str:
        if signal == "SHORT_A_LONG_B":
            return f"Spread widened ({z:.1f}σ). Short {a}, Long {b}. Expect mean reversion."
        elif signal == "LONG_A_SHORT_B":
            return f"Spread narrowed ({z:.1f}σ). Long {a}, Short {b}. Expect mean reversion."
        elif signal == "EXIT":
            return f"Spread near mean ({z:.1f}σ). Close existing pair position."
        return "No actionable signal. Spread within normal range."

    @staticmethod
    def _no_signal(a: str, b: str) -> Dict:
        return {
            "pair": f"{a}/{b}", "ticker_a": a, "ticker_b": b,
            "hedge_ratio": 0, "z_score": 0, "spread_mean": 0, "spread_std": 0,
            "current_spread": 0, "cointegration_stat": 0, "is_cointegrated": False,
            "signal": "NONE", "confidence": 0, "description": "Insufficient data",
        }


pairs_trader = PairsTrader()
