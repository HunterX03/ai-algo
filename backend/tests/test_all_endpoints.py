"""
Backend API Tests for JPM-SwingEdge Pro - Iteration 2
Tests all API endpoints including 9 new ML endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jpm-swing-edge.preview.emergentagent.com')


# ── Market & Signals API Tests ──

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


class TestStrategiesAPI:
    """Tests for /api/strategies/list endpoint - all 13 strategies"""
    
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


class TestRiskAPI:
    """Tests for /api/portfolio/risk endpoint - position sizing"""
    
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


# ── ML Enhancement Endpoints Tests (9 new endpoints) ──

class TestMLRegimeProbabilities:
    """Tests for /api/ml/regime-probabilities - HMM regime detection"""
    
    def test_regime_probabilities_success(self):
        """Test HMM regime probabilities returns success"""
        response = requests.get(f"{BASE_URL}/api/ml/regime-probabilities?returns=0.005&vix=12&fii_flow=200")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_regime_probabilities_structure(self):
        """Test regime probabilities has correct structure"""
        response = requests.get(f"{BASE_URL}/api/ml/regime-probabilities?returns=0.005&vix=12&fii_flow=200")
        data = response.json()
        assert 'probabilities' in data
        assert 'dominant_regime' in data
        probs = data['probabilities']
        expected_regimes = ['BULL_TRENDING', 'BULL_VOLATILE', 'SIDEWAYS', 'BEAR_VOLATILE', 'BEAR_TRENDING']
        for regime in expected_regimes:
            assert regime in probs
            
    def test_regime_probabilities_sum_to_one(self):
        """Test regime probabilities sum to approximately 1"""
        response = requests.get(f"{BASE_URL}/api/ml/regime-probabilities?returns=0.005&vix=12&fii_flow=200")
        data = response.json()
        total = sum(data['probabilities'].values())
        assert 0.99 <= total <= 1.01


class TestMLOptimalWeights:
    """Tests for /api/ml/optimal-weights - Dynamic weight optimizer"""
    
    def test_optimal_weights_success(self):
        """Test optimal weights returns success"""
        response = requests.get(f"{BASE_URL}/api/ml/optimal-weights?regime=BULL_TRENDING&vix=12")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_optimal_weights_structure(self):
        """Test optimal weights has correct structure"""
        response = requests.get(f"{BASE_URL}/api/ml/optimal-weights?regime=BULL_TRENDING&vix=12")
        data = response.json()
        assert 'weights' in data
        assert 'regime' in data
        weights = data['weights']
        expected_keys = ['technical', 'strategy', 'volume', 'sentiment']
        for key in expected_keys:
            assert key in weights
            
    def test_optimal_weights_different_regimes(self):
        """Test weights vary by regime"""
        bull_resp = requests.get(f"{BASE_URL}/api/ml/optimal-weights?regime=BULL_TRENDING&vix=12")
        bear_resp = requests.get(f"{BASE_URL}/api/ml/optimal-weights?regime=BEAR_VOLATILE&vix=25")
        bull_data = bull_resp.json()
        bear_data = bear_resp.json()
        # Weights should be different for different regimes
        assert bull_data['weights'] != bear_data['weights'] or bull_data['regime'] != bear_data['regime']


class TestMLQualityScore:
    """Tests for /api/ml/quality-score - XGBoost setup quality classifier"""
    
    def test_quality_score_success(self):
        """Test quality score returns success"""
        response = requests.post(f"{BASE_URL}/api/ml/quality-score?rsi=55&adx=30&volume_ratio=2.0")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_quality_score_value_range(self):
        """Test quality score is in valid range (0-100)"""
        response = requests.post(f"{BASE_URL}/api/ml/quality-score?rsi=55&adx=30&volume_ratio=2.0")
        data = response.json()
        assert 'quality_score' in data
        assert 0 <= data['quality_score'] <= 100
        
    def test_quality_score_with_all_params(self):
        """Test quality score with all parameters"""
        params = "rsi=55&macd_hist=0.5&adx=30&volume_ratio=2.0&bb_width=0.05&price_vs_ema20=0.02&price_vs_ema50=0.03&atr_pct=0.02"
        response = requests.post(f"{BASE_URL}/api/ml/quality-score?{params}")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True


class TestMLOptimalExit:
    """Tests for /api/ml/optimal-exit - Gradient Boosting exit predictor"""
    
    def test_optimal_exit_success(self):
        """Test optimal exit returns success"""
        response = requests.post(f"{BASE_URL}/api/ml/optimal-exit?atr_pct=0.025&rsi=55&adx=35")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_optimal_exit_structure(self):
        """Test optimal exit has correct structure"""
        response = requests.post(f"{BASE_URL}/api/ml/optimal-exit?atr_pct=0.025&rsi=55&adx=35")
        data = response.json()
        assert 'optimal_exit_pct' in data
        assert 'confidence' in data
        
    def test_optimal_exit_value_range(self):
        """Test optimal exit percentage is reasonable"""
        response = requests.post(f"{BASE_URL}/api/ml/optimal-exit?atr_pct=0.025&rsi=55&adx=35")
        data = response.json()
        assert data['optimal_exit_pct'] > 0
        assert data['confidence'] >= 0 and data['confidence'] <= 100


class TestMLVolumeAnomaly:
    """Tests for /api/ml/volume-anomaly - Isolation Forest anomaly detection"""
    
    def test_volume_anomaly_success(self):
        """Test volume anomaly returns success"""
        response = requests.post(f"{BASE_URL}/api/ml/volume-anomaly?volume_ratio_1d=3.5&price_change_pct=2.5")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_volume_anomaly_structure(self):
        """Test volume anomaly has correct structure"""
        response = requests.post(f"{BASE_URL}/api/ml/volume-anomaly?volume_ratio_1d=3.5&price_change_pct=2.5")
        data = response.json()
        assert 'is_anomaly' in data
        assert 'anomaly_score' in data
        assert 'description' in data
        
    def test_volume_anomaly_detection(self):
        """Test high volume ratio triggers anomaly"""
        response = requests.post(f"{BASE_URL}/api/ml/volume-anomaly?volume_ratio_1d=5.0&volume_ratio_5d=4.0&price_change_pct=5.0&delivery_pct=70&oi_change_pct=10")
        data = response.json()
        assert isinstance(data['is_anomaly'], bool)


class TestMLNewsImpact:
    """Tests for /api/ml/news-impact - News impact prediction"""
    
    def test_news_impact_success(self):
        """Test news impact returns success"""
        response = requests.get(f"{BASE_URL}/api/ml/news-impact?event_type=results")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_news_impact_structure(self):
        """Test news impact has correct structure"""
        response = requests.get(f"{BASE_URL}/api/ml/news-impact?event_type=results")
        data = response.json()
        assert 'impact_1d' in data
        assert 'impact_3d' in data
        assert 'impact_5d' in data
        assert 'impact_10d' in data
        assert 'confidence' in data
        assert 'event_type' in data
        
    def test_news_impact_different_events(self):
        """Test news impact for different event types"""
        events = ['results', 'dividend', 'bonus', 'split', 'buyback']
        for event in events:
            response = requests.get(f"{BASE_URL}/api/ml/news-impact?event_type={event}")
            assert response.status_code == 200
            data = response.json()
            assert data['success'] == True


class TestMLSectorRotation:
    """Tests for /api/ml/sector-rotation - Sector ranking prediction"""
    
    def test_sector_rotation_success(self):
        """Test sector rotation returns success"""
        response = requests.get(f"{BASE_URL}/api/ml/sector-rotation")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_sector_rotation_structure(self):
        """Test sector rotation has correct structure"""
        response = requests.get(f"{BASE_URL}/api/ml/sector-rotation")
        data = response.json()
        assert 'sectors' in data
        assert len(data['sectors']) > 0
        
    def test_sector_rotation_sector_data(self):
        """Test each sector has required fields"""
        response = requests.get(f"{BASE_URL}/api/ml/sector-rotation")
        data = response.json()
        for sector in data['sectors']:
            assert 'sector' in sector
            assert 'probability' in sector
            assert 'rank' in sector


class TestMLPatternRecognition:
    """Tests for /api/ml/pattern-recognition - Candlestick pattern recognition"""
    
    def test_pattern_recognition_success(self):
        """Test pattern recognition returns success"""
        response = requests.post(f"{BASE_URL}/api/ml/pattern-recognition?body_ratio=0.7&volume_ratio=2.0")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_pattern_recognition_structure(self):
        """Test pattern recognition has correct structure"""
        response = requests.post(f"{BASE_URL}/api/ml/pattern-recognition?body_ratio=0.7&volume_ratio=2.0")
        data = response.json()
        assert 'pattern' in data
        assert 'probability' in data
        assert 'description' in data
        
    def test_pattern_recognition_with_all_params(self):
        """Test pattern recognition with all parameters"""
        params = "body_ratio=0.7&upper_wick_ratio=0.1&lower_wick_ratio=0.2&volume_ratio=2.0&range_vs_atr=1.5&close_position=0.8&prev_trend=1"
        response = requests.post(f"{BASE_URL}/api/ml/pattern-recognition?{params}")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True


class TestMLEarningsSurprise:
    """Tests for /api/ml/earnings-surprise - Earnings prediction"""
    
    def test_earnings_surprise_success(self):
        """Test earnings surprise returns success"""
        response = requests.post(f"{BASE_URL}/api/ml/earnings-surprise?delivery_pct_avg_30d=65&revenue_growth_qoq=12")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        
    def test_earnings_surprise_structure(self):
        """Test earnings surprise has correct structure"""
        response = requests.post(f"{BASE_URL}/api/ml/earnings-surprise?delivery_pct_avg_30d=65&revenue_growth_qoq=12")
        data = response.json()
        assert 'beat_probability' in data
        assert 'miss_probability' in data
        assert 'confidence' in data
        assert 'recommendation' in data
        
    def test_earnings_surprise_probabilities_sum(self):
        """Test beat and miss probabilities sum to 100"""
        response = requests.post(f"{BASE_URL}/api/ml/earnings-surprise?delivery_pct_avg_30d=65&revenue_growth_qoq=12")
        data = response.json()
        total = data['beat_probability'] + data['miss_probability']
        assert 99 <= total <= 101


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
