"""Tier 1 — Multi-Factor Model for NSE (Value, Momentum, Quality, Low Vol, Size)
Replaces single-score ranking with a factor-score vector per stock.
Factor weights are regime-dependent — mimics DSP Quant / Nippon India Quant approach.
"""
import numpy as np
import pandas as pd
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Regime-dependent factor weights (sum to 1.0)
REGIME_FACTOR_WEIGHTS = {
    "BULL_TRENDING":  {"value": 0.10, "momentum": 0.35, "quality": 0.20, "low_vol": 0.10, "size": 0.25},
    "BULL_VOLATILE":  {"value": 0.15, "momentum": 0.25, "quality": 0.25, "low_vol": 0.20, "size": 0.15},
    "SIDEWAYS":       {"value": 0.25, "momentum": 0.15, "quality": 0.30, "low_vol": 0.20, "size": 0.10},
    "BEAR_VOLATILE":  {"value": 0.20, "momentum": 0.05, "quality": 0.30, "low_vol": 0.35, "size": 0.10},
    "BEAR_TRENDING":  {"value": 0.30, "momentum": 0.05, "quality": 0.25, "low_vol": 0.30, "size": 0.10},
}

# NSE stock fundamental proxies (demo — replace with Screener.in scraper for production)
NSE_FUNDAMENTALS = {
    "RELIANCE":    {"pe": 28, "pb": 2.5, "roe": 12, "debt_equity": 0.4, "mcap_cr": 1900000, "sector": "ENERGY"},
    "TCS":         {"pe": 32, "pb": 14,  "roe": 45, "debt_equity": 0.01, "mcap_cr": 1400000, "sector": "IT"},
    "HDFCBANK":    {"pe": 20, "pb": 3.2, "roe": 17, "debt_equity": 0.0,  "mcap_cr": 1300000, "sector": "BANKING"},
    "INFY":        {"pe": 28, "pb": 9,   "roe": 32, "debt_equity": 0.0,  "mcap_cr": 620000,  "sector": "IT"},
    "ICICIBANK":   {"pe": 18, "pb": 3.5, "roe": 18, "debt_equity": 0.0,  "mcap_cr": 900000,  "sector": "BANKING"},
    "HINDUNILVR":  {"pe": 55, "pb": 11,  "roe": 20, "debt_equity": 0.0,  "mcap_cr": 550000,  "sector": "FMCG"},
    "ITC":         {"pe": 25, "pb": 7,   "roe": 28, "debt_equity": 0.0,  "mcap_cr": 540000,  "sector": "FMCG"},
    "SBIN":        {"pe": 10, "pb": 1.8, "roe": 18, "debt_equity": 0.0,  "mcap_cr": 700000,  "sector": "BANKING"},
    "BHARTIARTL":  {"pe": 75, "pb": 8,   "roe": 11, "debt_equity": 1.2,  "mcap_cr": 950000,  "sector": "TELECOM"},
    "BAJFINANCE":  {"pe": 35, "pb": 7,   "roe": 22, "debt_equity": 3.5,  "mcap_cr": 420000,  "sector": "NBFC"},
    "ASIANPAINT":  {"pe": 60, "pb": 18,  "roe": 25, "debt_equity": 0.1,  "mcap_cr": 280000,  "sector": "CHEMICALS"},
    "MARUTI":      {"pe": 30, "pb": 5,   "roe": 14, "debt_equity": 0.0,  "mcap_cr": 380000,  "sector": "AUTO"},
    "HCLTECH":     {"pe": 24, "pb": 7,   "roe": 24, "debt_equity": 0.05, "mcap_cr": 460000,  "sector": "IT"},
    "AXISBANK":    {"pe": 14, "pb": 2.2, "roe": 16, "debt_equity": 0.0,  "mcap_cr": 350000,  "sector": "BANKING"},
    "LT":          {"pe": 35, "pb": 5,   "roe": 15, "debt_equity": 0.8,  "mcap_cr": 470000,  "sector": "INFRA"},
    "ULTRACEMCO":  {"pe": 40, "pb": 5,   "roe": 12, "debt_equity": 0.1,  "mcap_cr": 320000,  "sector": "CEMENT"},
    "WIPRO":       {"pe": 22, "pb": 3,   "roe": 16, "debt_equity": 0.2,  "mcap_cr": 270000,  "sector": "IT"},
    "NESTLEIND":   {"pe": 75, "pb": 60,  "roe": 100,"debt_equity": 0.0,  "mcap_cr": 230000,  "sector": "FMCG"},
    "SUNPHARMA":   {"pe": 38, "pb": 5,   "roe": 14, "debt_equity": 0.15, "mcap_cr": 430000,  "sector": "PHARMA"},
    "TITAN":       {"pe": 85, "pb": 22,  "roe": 25, "debt_equity": 0.2,  "mcap_cr": 280000,  "sector": "CONSUMER"},
    "TECHM":       {"pe": 26, "pb": 5,   "roe": 18, "debt_equity": 0.1,  "mcap_cr": 160000,  "sector": "IT"},
    "ONGC":        {"pe": 8,  "pb": 1.0, "roe": 12, "debt_equity": 0.4,  "mcap_cr": 330000,  "sector": "ENERGY"},
    "NTPC":        {"pe": 16, "pb": 2.0, "roe": 12, "debt_equity": 1.0,  "mcap_cr": 340000,  "sector": "POWER"},
    "KOTAKBANK":   {"pe": 22, "pb": 3.5, "roe": 15, "debt_equity": 0.0,  "mcap_cr": 370000,  "sector": "BANKING"},
    "POWERGRID":   {"pe": 14, "pb": 2.5, "roe": 18, "debt_equity": 1.5,  "mcap_cr": 290000,  "sector": "POWER"},
}


class MultiFactorModel:
    """NSE multi-factor ranking engine with regime-dependent weighting."""

    def score_stock(self, ticker: str, df: pd.DataFrame, regime: str = "SIDEWAYS") -> Dict:
        """Compute 5-factor score vector + composite for a single stock."""
        fund = NSE_FUNDAMENTALS.get(ticker, {})
        if not fund or df.empty or len(df) < 60:
            return self._empty_score(ticker)

        factors = {
            "value":    self._value_factor(fund),
            "momentum": self._momentum_factor(df),
            "quality":  self._quality_factor(fund),
            "low_vol":  self._low_vol_factor(df),
            "size":     self._size_factor(fund),
        }

        weights = REGIME_FACTOR_WEIGHTS.get(regime, REGIME_FACTOR_WEIGHTS["SIDEWAYS"])
        composite = sum(factors[f] * weights[f] for f in factors)

        return {
            "ticker": ticker,
            "factors": {k: round(v, 2) for k, v in factors.items()},
            "weights": weights,
            "composite_score": round(composite, 2),
            "regime": regime,
            "sector": fund.get("sector", "UNKNOWN"),
        }

    def rank_universe(self, tickers: List[str], price_data: Dict[str, pd.DataFrame],
                      regime: str = "SIDEWAYS") -> List[Dict]:
        """Rank entire universe by composite factor score."""
        scored = []
        for t in tickers:
            df = price_data.get(t, pd.DataFrame())
            scored.append(self.score_stock(t, df, regime))
        scored.sort(key=lambda x: x["composite_score"], reverse=True)
        for i, s in enumerate(scored):
            s["rank"] = i + 1
        return scored

    # ── Factor calculations (0-100 scale) ──

    @staticmethod
    def _value_factor(fund: Dict) -> float:
        pe = fund.get("pe", 30)
        pb = fund.get("pb", 5)
        # Lower PE/PB = higher value. Normalize to 0-100.
        pe_score = max(0, min(100, (50 - pe) * 2 + 50))
        pb_score = max(0, min(100, (5 - pb) * 10 + 50))
        return 0.6 * pe_score + 0.4 * pb_score

    @staticmethod
    def _momentum_factor(df: pd.DataFrame) -> float:
        if len(df) < 252:
            ret_12m = ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100
        else:
            ret_12m = ((df['close'].iloc[-1] - df['close'].iloc[-252]) / df['close'].iloc[-252]) * 100
        # 12-1 month: exclude last month
        if len(df) > 22:
            ret_1m = ((df['close'].iloc[-1] - df['close'].iloc[-22]) / df['close'].iloc[-22]) * 100
            mom_12_1 = ret_12m - ret_1m
        else:
            mom_12_1 = ret_12m
        return max(0, min(100, mom_12_1 * 2 + 50))

    @staticmethod
    def _quality_factor(fund: Dict) -> float:
        roe = fund.get("roe", 15)
        de = fund.get("debt_equity", 0.5)
        roe_score = max(0, min(100, roe * 3))
        debt_score = max(0, min(100, (2 - de) * 30 + 40))
        return 0.6 * roe_score + 0.4 * debt_score

    @staticmethod
    def _low_vol_factor(df: pd.DataFrame) -> float:
        if len(df) < 60:
            return 50.0
        returns = df['close'].pct_change().dropna().tail(60)
        vol = returns.std() * np.sqrt(252) * 100
        # Lower vol = higher score
        return max(0, min(100, (30 - vol) * 3 + 50))

    @staticmethod
    def _size_factor(fund: Dict) -> float:
        mcap = fund.get("mcap_cr", 100000)
        # Small cap premium: lower mcap → higher score
        if mcap < 50000:
            return 90
        elif mcap < 200000:
            return 70
        elif mcap < 500000:
            return 50
        else:
            return 30

    @staticmethod
    def _empty_score(ticker: str) -> Dict:
        return {
            "ticker": ticker,
            "factors": {"value": 50, "momentum": 50, "quality": 50, "low_vol": 50, "size": 50},
            "weights": REGIME_FACTOR_WEIGHTS["SIDEWAYS"],
            "composite_score": 50,
            "regime": "SIDEWAYS",
            "sector": "UNKNOWN",
        }


factor_model = MultiFactorModel()
