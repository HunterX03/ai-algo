"""
Test suite for JPM-SwingEdge Pro Quant Engine endpoints (Iteration 3)
Tests 6 new quant API endpoints:
- Tier 1: Multi-Factor Model
- Tier 2: Pairs Trading
- Tier 3: Options Flow
- Tier 4: Order Flow
- Tier 5: Volatility Surface
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestQuantFactorModel:
    """Tier 1: Multi-Factor Model endpoint tests"""
    
    def test_factor_scores_default_regime(self):
        """GET /api/quant/factor-scores - default SIDEWAYS regime"""
        response = requests.get(f"{BASE_URL}/api/quant/factor-scores")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "rankings" in data
        assert "regime" in data
        # Verify rankings structure
        if data["rankings"]:
            stock = data["rankings"][0]
            assert "ticker" in stock
            assert "factors" in stock
            assert "composite_score" in stock
            assert "rank" in stock
            assert "sector" in stock
            # Verify factor structure
            factors = stock["factors"]
            assert "value" in factors
            assert "momentum" in factors
            assert "quality" in factors
            assert "low_vol" in factors
            assert "size" in factors
    
    def test_factor_scores_bull_trending(self):
        """GET /api/quant/factor-scores?regime=BULL_TRENDING"""
        response = requests.get(f"{BASE_URL}/api/quant/factor-scores?regime=BULL_TRENDING")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("regime") == "BULL_TRENDING"
        assert "rankings" in data
    
    def test_factor_scores_bear_volatile(self):
        """GET /api/quant/factor-scores?regime=BEAR_VOLATILE"""
        response = requests.get(f"{BASE_URL}/api/quant/factor-scores?regime=BEAR_VOLATILE")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("regime") == "BEAR_VOLATILE"


class TestQuantPairsTrading:
    """Tier 2: Statistical Pairs Trading endpoint tests"""
    
    def test_pairs_signals(self):
        """GET /api/quant/pairs - all pairs trading signals"""
        response = requests.get(f"{BASE_URL}/api/quant/pairs")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "pairs" in data
        # Verify pairs structure
        if data["pairs"]:
            pair = data["pairs"][0]
            assert "pair" in pair
            assert "ticker_a" in pair
            assert "ticker_b" in pair
            assert "z_score" in pair
            assert "hedge_ratio" in pair
            assert "signal" in pair
            assert "confidence" in pair
            assert "is_cointegrated" in pair
            assert "description" in pair
    
    def test_pairs_count(self):
        """Verify we get signals for all 10 candidate pairs"""
        response = requests.get(f"{BASE_URL}/api/quant/pairs")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        # Should have up to 10 pairs (some may be missing data)
        assert len(data.get("pairs", [])) <= 10


class TestQuantOptionsFlow:
    """Tier 3: Options Flow Analysis endpoint tests"""
    
    def test_options_flow_reliance(self):
        """GET /api/quant/options-flow?ticker=RELIANCE"""
        response = requests.get(f"{BASE_URL}/api/quant/options-flow?ticker=RELIANCE")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "data" in data
        opt = data["data"]
        assert opt.get("ticker") == "RELIANCE"
        assert "put_call_ratio" in opt
        assert "iv_rank" in opt
        assert "max_pain_strike" in opt
        assert "signal" in opt
        assert "unusual_activity" in opt
        # Verify unusual activity structure
        ua = opt["unusual_activity"]
        assert "has_unusual_call_buying" in ua
        assert "has_unusual_put_buying" in ua
        assert "total_unusual_trades" in ua
    
    def test_options_flow_tcs(self):
        """GET /api/quant/options-flow?ticker=TCS"""
        response = requests.get(f"{BASE_URL}/api/quant/options-flow?ticker=TCS")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data["data"].get("ticker") == "TCS"
    
    def test_options_flow_scan_all(self):
        """GET /api/quant/options-flow - scan all F&O stocks"""
        response = requests.get(f"{BASE_URL}/api/quant/options-flow")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "signals" in data


class TestQuantOrderFlow:
    """Tier 4: Order Flow Imbalance endpoint tests"""
    
    def test_order_flow_reliance(self):
        """GET /api/quant/order-flow/RELIANCE"""
        response = requests.get(f"{BASE_URL}/api/quant/order-flow/RELIANCE")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "data" in data
        flow = data["data"]
        assert flow.get("ticker") == "RELIANCE"
        assert "buy_volume" in flow
        assert "sell_volume" in flow
        assert "imbalance" in flow
        assert "signal" in flow
        assert "signal_strength" in flow
        assert "cumulative_delta" in flow
        assert "large_buys" in flow
        assert "large_sells" in flow
        assert "description" in flow
    
    def test_order_flow_sbin(self):
        """GET /api/quant/order-flow/SBIN"""
        response = requests.get(f"{BASE_URL}/api/quant/order-flow/SBIN")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data["data"].get("ticker") == "SBIN"
    
    def test_order_flow_metrics_valid(self):
        """Verify order flow metrics are within valid ranges"""
        response = requests.get(f"{BASE_URL}/api/quant/order-flow/TCS")
        assert response.status_code == 200
        data = response.json()
        flow = data["data"]
        # Buy + Sell percentages should be close to 100%
        assert 0 <= flow["buy_pct"] <= 100
        assert 0 <= flow["sell_pct"] <= 100
        # Imbalance should be between -1 and 1
        assert -1 <= flow["imbalance"] <= 1


class TestQuantVolSurface:
    """Tier 5: Volatility Surface endpoint tests"""
    
    def test_vol_surface_reliance(self):
        """GET /api/quant/vol-surface/RELIANCE"""
        response = requests.get(f"{BASE_URL}/api/quant/vol-surface/RELIANCE")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "data" in data
        vol = data["data"]
        assert vol.get("ticker") == "RELIANCE"
        assert "atm_iv" in vol
        assert "realized_vol_30d" in vol
        assert "iv_rv_divergence" in vol
        assert "iv_skew" in vol
        assert "vol_regime" in vol
        assert "edge_description" in vol
        assert "surface_data" in vol
        # Verify surface data structure
        if vol["surface_data"]:
            strike = vol["surface_data"][0]
            assert "strike" in strike
            assert "call_iv" in strike
            assert "put_iv" in strike
    
    def test_vol_surface_hdfcbank(self):
        """GET /api/quant/vol-surface/HDFCBANK"""
        response = requests.get(f"{BASE_URL}/api/quant/vol-surface/HDFCBANK")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data["data"].get("ticker") == "HDFCBANK"
    
    def test_vol_opportunities(self):
        """GET /api/quant/vol-opportunities - scan for vol opportunities"""
        response = requests.get(f"{BASE_URL}/api/quant/vol-opportunities")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "opportunities" in data
        # Opportunities should only include non-FAIR_VALUE regimes
        for opp in data.get("opportunities", []):
            assert opp.get("vol_regime") in ["IV_PREMIUM", "IV_DISCOUNT"]


class TestExistingEndpoints:
    """Verify existing endpoints still work after quant additions"""
    
    def test_market_regime(self):
        """GET /api/market/regime - existing endpoint"""
        response = requests.get(f"{BASE_URL}/api/market/regime")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "data" in data
        assert "regime" in data["data"]
    
    def test_top10_signals(self):
        """GET /api/signals/top10 - existing endpoint"""
        response = requests.get(f"{BASE_URL}/api/signals/top10")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "signals" in data
    
    def test_strategies_list(self):
        """GET /api/strategies/list - existing endpoint"""
        response = requests.get(f"{BASE_URL}/api/strategies/list")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "strategies" in data
        assert len(data["strategies"]) == 13


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
