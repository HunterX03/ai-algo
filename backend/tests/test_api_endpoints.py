"""
Backend API Tests for JPM-SwingEdge Pro
Tests all 8 main API endpoints for the quantitative trading dashboard
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jpm-swing-edge.preview.emergentagent.com')


class TestMarketRegimeAPI:
    """Tests for /api/market/regime endpoint"""
    
    def test_market_regime_returns_success(self):
        """Test market regime endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/market/regime")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_market_regime_data_structure(self):
        """Test market regime returns correct data structure"""
        response = requests.get(f"{BASE_URL}/api/market/regime")
        data = response.json()
        assert 'data' in data
        regime_data = data['data']
        # Verify all required fields
        assert 'regime' in regime_data
        assert 'nifty_price' in regime_data
        assert 'vix' in regime_data
        assert 'fii_flow_5d' in regime_data
        assert 'ema_200' in regime_data
        assert 'timestamp' in regime_data
        
    def test_market_regime_valid_values(self):
        """Test market regime returns valid regime type"""
        response = requests.get(f"{BASE_URL}/api/market/regime")
        data = response.json()
        valid_regimes = ['BULL_TRENDING', 'BULL_VOLATILE', 'SIDEWAYS', 'BEAR_VOLATILE', 'BEAR_TRENDING']
        assert data['data']['regime'] in valid_regimes


class TestSignalsAPI:
    """Tests for /api/signals endpoints"""
    
    def test_top10_signals_swing(self):
        """Test top 10 signals for swing timeframe"""
        response = requests.get(f"{BASE_URL}/api/signals/top10?timeframe=swing")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'signals' in data
        assert 'market_regime' in data
        
    def test_top10_signals_intraday(self):
        """Test top 10 signals for intraday timeframe"""
        response = requests.get(f"{BASE_URL}/api/signals/top10?timeframe=intraday")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_top10_signals_positional(self):
        """Test top 10 signals for positional timeframe"""
        response = requests.get(f"{BASE_URL}/api/signals/top10?timeframe=positional")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_signal_data_structure(self):
        """Test signal data has correct structure"""
        response = requests.get(f"{BASE_URL}/api/signals/top10?timeframe=swing")
        data = response.json()
        if data['signals']:
            signal = data['signals'][0]
            required_fields = ['ticker', 'signal', 'strategy', 'entry_zone', 
                             'target_1', 'stop_loss', 'risk_reward_ratio', 'confidence']
            for field in required_fields:
                assert field in signal, f"Missing field: {field}"


class TestStockDetailAPI:
    """Tests for /api/signals/{ticker} endpoint"""
    
    def test_stock_detail_reliance(self):
        """Test stock detail for RELIANCE"""
        response = requests.get(f"{BASE_URL}/api/signals/RELIANCE")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['ticker'] == 'RELIANCE'
        
    def test_stock_detail_has_chart_data(self):
        """Test stock detail includes chart data"""
        response = requests.get(f"{BASE_URL}/api/signals/RELIANCE")
        data = response.json()
        assert 'chart_data' in data
        assert len(data['chart_data']) > 0
        
    def test_stock_detail_has_indicators(self):
        """Test stock detail includes technical indicators"""
        response = requests.get(f"{BASE_URL}/api/signals/RELIANCE")
        data = response.json()
        assert 'indicators' in data
        indicators = data['indicators']
        expected_indicators = ['rsi', 'macd', 'ema_20', 'ema_50', 'ema_200', 'vwap', 'atr']
        for ind in expected_indicators:
            assert ind in indicators, f"Missing indicator: {ind}"
            
    def test_stock_detail_has_levels(self):
        """Test stock detail includes support/resistance levels"""
        response = requests.get(f"{BASE_URL}/api/signals/TCS")
        data = response.json()
        assert 'support' in data
        assert 'resistance' in data
        assert 'fibonacci_levels' in data


class TestStrategiesAPI:
    """Tests for /api/strategies/list endpoint"""
    
    def test_strategies_list_returns_13(self):
        """Test strategies list returns all 13 strategies"""
        response = requests.get(f"{BASE_URL}/api/strategies/list")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert len(data['strategies']) == 13
        
    def test_strategies_have_required_fields(self):
        """Test each strategy has required fields"""
        response = requests.get(f"{BASE_URL}/api/strategies/list")
        data = response.json()
        for strategy in data['strategies']:
            assert 'name' in strategy
            assert 'timeframe' in strategy
            assert 'description' in strategy
            assert 'win_rate' in strategy
            assert 'avg_rr' in strategy
            assert 'best_regime' in strategy
            
    def test_strategies_timeframes(self):
        """Test strategies cover all timeframes"""
        response = requests.get(f"{BASE_URL}/api/strategies/list")
        data = response.json()
        timeframes = set(s['timeframe'] for s in data['strategies'])
        assert 'intraday' in timeframes
        assert 'swing' in timeframes
        assert 'positional' in timeframes


class TestBacktestAPI:
    """Tests for /api/backtest/run endpoint"""
    
    def test_backtest_run_success(self):
        """Test backtest run returns success"""
        response = requests.post(f"{BASE_URL}/api/backtest/run?strategy=BB_Squeeze&capital=100000")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert data['strategy'] == 'BB_Squeeze'
        
    def test_backtest_results_structure(self):
        """Test backtest results have correct structure"""
        response = requests.post(f"{BASE_URL}/api/backtest/run?strategy=BB_Squeeze&capital=100000")
        data = response.json()
        assert 'results' in data
        results = data['results']
        assert 'metrics' in results
        assert 'trades' in results
        assert 'equity_curve' in results
        
    def test_backtest_metrics_fields(self):
        """Test backtest metrics have required fields"""
        response = requests.post(f"{BASE_URL}/api/backtest/run?strategy=BB_Squeeze&capital=100000")
        data = response.json()
        metrics = data['results']['metrics']
        required_metrics = ['total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate']
        for metric in required_metrics:
            assert metric in metrics, f"Missing metric: {metric}"


class TestSentimentAPI:
    """Tests for /api/sentiment/{ticker} endpoint"""
    
    def test_sentiment_reliance(self):
        """Test sentiment for RELIANCE"""
        response = requests.get(f"{BASE_URL}/api/sentiment/RELIANCE")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_sentiment_data_structure(self):
        """Test sentiment data has correct structure"""
        response = requests.get(f"{BASE_URL}/api/sentiment/RELIANCE")
        data = response.json()
        sentiment_data = data['data']
        assert 'ticker' in sentiment_data
        assert 'overall_sentiment' in sentiment_data
        assert 'sentiment_label' in sentiment_data
        assert 'headlines' in sentiment_data
        
    def test_sentiment_label_valid(self):
        """Test sentiment label is valid"""
        response = requests.get(f"{BASE_URL}/api/sentiment/TCS")
        data = response.json()
        valid_labels = ['positive', 'negative', 'neutral']
        assert data['data']['sentiment_label'] in valid_labels
        
    def test_sentiment_headlines_present(self):
        """Test sentiment includes news headlines"""
        response = requests.get(f"{BASE_URL}/api/sentiment/RELIANCE")
        data = response.json()
        assert len(data['data']['headlines']) > 0


class TestRiskAPI:
    """Tests for /api/portfolio/risk endpoint"""
    
    def test_risk_calculation_success(self):
        """Test risk calculation returns success"""
        response = requests.get(f"{BASE_URL}/api/portfolio/risk?capital=100000&entry_price=1000&stop_loss=950")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_risk_fixed_fractional(self):
        """Test fixed fractional calculation"""
        response = requests.get(f"{BASE_URL}/api/portfolio/risk?capital=100000&entry_price=1000&stop_loss=950")
        data = response.json()
        assert 'fixed_fractional' in data
        ff = data['fixed_fractional']
        assert 'shares' in ff
        assert 'position_value' in ff
        assert 'max_loss' in ff
        assert ff['shares'] > 0
        
    def test_risk_kelly_criterion(self):
        """Test Kelly criterion calculation"""
        response = requests.get(f"{BASE_URL}/api/portfolio/risk?capital=100000&entry_price=1000&stop_loss=950")
        data = response.json()
        assert 'kelly_criterion' in data
        kelly = data['kelly_criterion']
        assert 'kelly_full' in kelly
        assert 'kelly_half' in kelly
        assert 'shares' in kelly
        
    def test_risk_recommendations(self):
        """Test risk recommendations"""
        response = requests.get(f"{BASE_URL}/api/portfolio/risk?capital=100000&entry_price=1000&stop_loss=950")
        data = response.json()
        assert 'recommendations' in data
        rec = data['recommendations']
        assert 'recommended_method' in rec
        assert 'max_positions' in rec


class TestIntradayAPI:
    """Tests for /api/intraday/signals endpoint"""
    
    def test_intraday_signals_success(self):
        """Test intraday signals returns success"""
        response = requests.get(f"{BASE_URL}/api/intraday/signals")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_intraday_signals_structure(self):
        """Test intraday signals have correct structure"""
        response = requests.get(f"{BASE_URL}/api/intraday/signals")
        data = response.json()
        assert 'signals' in data
        if data['signals']:
            signal = data['signals'][0]
            assert signal['timeframe'] == 'intraday'
            assert signal['expected_hold'] == '1-2 hours'


class TestScannerAPI:
    """Tests for /api/scanner/run endpoint"""
    
    def test_scanner_run_swing(self):
        """Test scanner run for swing timeframe"""
        response = requests.post(f"{BASE_URL}/api/scanner/run?timeframe=swing")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'signals_found' in data
        assert 'market_regime' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
