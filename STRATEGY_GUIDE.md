# JPM-SwingEdge Pro — Developer & Strategy Guide

## Quick Start

1. **Add API Keys**: Edit `/app/backend/.env` and replace placeholders:
   ```
   FYERS_API_ID=your_client_id
   FYERS_API_SECRET=your_secret
   FYERS_ACCESS_TOKEN=your_access_token
   SERP_API_KEY=your_serp_key
   ```
2. **Restart backend**: `sudo supervisorctl restart backend`
3. The app auto-switches from demo to live data when valid keys are detected.

---

## Adding a New Trading Strategy

### Step 1: Create the Strategy File

Create a new Python file in the appropriate folder:
- **Intraday**: `/app/backend/core/strategies/intraday/`
- **Swing**: `/app/backend/core/strategies/swing/`
- **Positional**: `/app/backend/core/strategies/positional/`

**Template** (`/app/backend/core/strategies/swing/my_strategy.py`):
```python
import pandas as pd
from typing import Dict

class MyStrategy:
    """Description of your strategy."""
    name = "My Custom Strategy"          # Display name
    timeframe = "swing"                   # intraday | swing | positional
    description = "What this strategy does in one sentence"

    @staticmethod
    def analyze(df: pd.DataFrame) -> Dict:
        """
        Analyze a DataFrame with columns: timestamp, open, high, low, close, volume
        Plus indicators: ema_20, ema_50, ema_200, rsi, macd, macd_hist, bb_upper, bb_lower, etc.

        Must return:
          - {'signal': 'NONE', 'confidence': 0}  if no signal
          - {'signal': 'BUY'|'SELL', 'entry': float, 'target1': float,
             'target2': float, 'stop_loss': float, 'confidence': int (0-100),
             'setup_type': 'MY_SETUP_NAME'}
        """
        if len(df) < 20:
            return {'signal': 'NONE', 'confidence': 0}

        current_price = df['close'].iloc[-1]
        # ... your logic here ...

        return {'signal': 'NONE', 'confidence': 0}
```

### Step 2: Register in the Scanner

Edit `/app/backend/core/scanner.py`:
```python
# Add import at top
from core.strategies.swing.my_strategy import MyStrategy

# Add to the strategies dict in __init__
self.strategies = {
    'swing': [BBSqueeze, MomentumDelivery, FIIDivergence, PEAD, FiftyTwoWeekBreakoutOI, MyStrategy],
    # ...
}
```

### Step 3: Add to Strategy List

Edit `/app/backend/server.py`, add to `ALL_STRATEGIES` list:
```python
{"name": "My Custom Strategy", "timeframe": "swing",
 "description": "What this strategy does",
 "win_rate": 65, "avg_rr": 2.0, "best_regime": "BULL_TRENDING",
 "capital_alloc": 8, "enabled": True},
```

### Step 4: Done!
The strategy will appear in:
- Strategy Lab page (with toggle and backtest button)
- Scanner results (Command Center top 10)
- Backtest Suite (available for backtesting)

---

## Modifying an Existing Strategy

1. Open the strategy file (e.g., `/app/backend/core/strategies/swing/bb_squeeze.py`)
2. Modify the `analyze()` method logic
3. Save — backend hot-reloads automatically
4. Test via: `curl https://your-app.preview.emergentagent.com/api/signals/top10?timeframe=swing`

---

## Adding a New ML Model

### Step 1: Create the Model File

Create in `/app/backend/core/ml/`:
```python
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class MyModel:
    def __init__(self):
        self.model = None
        self._train_on_synthetic()

    def predict(self, features: Dict) -> Dict:
        if self.model is None:
            return {'score': 0, 'confidence': 0}
        X = np.array([[features.get('feature1', 0), features.get('feature2', 0)]])
        pred = float(self.model.predict(X)[0])
        return {'score': pred, 'confidence': 70}

    def _train_on_synthetic(self):
        # Train on synthetic data. Replace with real data for production.
        np.random.seed(42)
        X = np.random.randn(500, 2)
        y = (X[:, 0] + X[:, 1] > 0).astype(int)
        self.model = GradientBoostingClassifier(n_estimators=50)
        self.model.fit(X, y)

my_model = MyModel()
```

### Step 2: Add API Endpoint

In `/app/backend/server.py`:
```python
from core.ml.my_model import my_model

@api_router.get("/ml/my-prediction")
async def my_prediction(feature1: float = Query(0), feature2: float = Query(0)):
    result = my_model.predict({'feature1': feature1, 'feature2': feature2})
    return {"success": True, **result}
```

---

## Modifying Scoring Weights

The composite scoring formula is:
```
Score = (Technical x W1) + (Strategy x W2) + (Volume x W3) + (Sentiment x W4)
```

**Static weights**: Edit `/app/backend/core/ranking.py` → `_get_regime_weights()`
**Dynamic weights**: The ML weight optimizer auto-adjusts. See `/app/backend/core/ml/weight_optimizer.py`

---

## Changing Position Sizing Logic

Edit `/app/backend/core/risk.py`:
- `calculate_position_size_fixed_fractional()` — Fixed Fractional method
- `calculate_kelly_criterion()` — Kelly Criterion method
- `get_risk_recommendations()` — Regime-based recommendations

---

## Adding a New Frontend Page

1. Create component in `/app/frontend/src/pages/MyPage.jsx`
2. Add route in `/app/frontend/src/App.js`:
   ```jsx
   import MyPage from './pages/MyPage';
   // In Routes:
   <Route path="/my-page" element={<MyPage />} />
   ```
3. Add nav item in `/app/frontend/src/components/Sidebar.jsx`:
   ```jsx
   { path: '/my-page', icon: SomeIcon, label: 'My Page' },
   ```

---

## API Reference

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/market/regime` | Current market regime + VIX + FII flow |
| POST | `/api/scanner/run?timeframe=swing` | Trigger full NSE scan |
| GET | `/api/signals/top10?timeframe=swing` | Top 10 ranked signals |
| GET | `/api/signals/{ticker}` | Detailed signal for one stock |
| POST | `/api/backtest/run?strategy=X&capital=Y` | Run backtest |
| GET | `/api/sentiment/{ticker}` | News sentiment |
| GET | `/api/portfolio/risk?capital=X&entry_price=Y&stop_loss=Z` | Position sizing |
| GET | `/api/strategies/list` | All 13 strategies |
| GET | `/api/intraday/signals` | Live intraday signals |
| WS | `/ws/live` | WebSocket for real-time updates |

### ML Enhancement Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ml/regime-probabilities` | HMM regime probabilities |
| GET | `/api/ml/optimal-weights` | Dynamic scoring weights |
| POST | `/api/ml/quality-score` | Setup quality classifier |
| POST | `/api/ml/optimal-exit` | Dynamic exit target prediction |
| POST | `/api/ml/volume-anomaly` | Isolation Forest volume detection |
| GET | `/api/ml/news-impact` | News event price impact prediction |
| GET | `/api/ml/sector-rotation` | ML sector rotation ranking |
| POST | `/api/ml/pattern-recognition` | Intraday pattern classifier |
| POST | `/api/ml/earnings-surprise` | Earnings beat/miss prediction |

---

## Architecture Overview

```
backend/
  server.py              ← All API endpoints
  core/
    fyers_client.py      ← Fyers API wrapper + mock data
    indicators.py        ← Technical indicators (pure numpy)
    regime.py            ← Market regime classifier
    scanner.py           ← Market scanner (orchestrates strategies)
    sentiment.py         ← News sentiment analysis
    ranking.py           ← Composite signal scoring
    risk.py              ← Position sizing (FF + Kelly)
    backtest.py          ← Backtesting engine
    strategies/
      intraday/          ← 5 intraday strategies
      swing/             ← 5 swing strategies
      positional/        ← 3 positional strategies
    ml/
      weight_optimizer.py     ← Dynamic weight optimizer (RF)
      quality_classifier.py   ← Setup quality (XGBoost)
      exit_predictor.py       ← Optimal exit (GBR)
      hmm_regime.py           ← HMM regime probabilities
      volume_anomaly.py       ← Volume anomaly (Isolation Forest)
      news_impact.py          ← News event impact (GBR)
      sector_momentum.py      ← Sector rotation (XGBoost)
      pattern_recognition.py  ← Candle patterns (XGBoost)
      earnings_predictor.py   ← Earnings surprise (XGBoost)
```

## Performance Notes
- All ML models are pre-trained at startup and cached in memory
- Inference is <1ms per prediction (numpy array → sklearn predict)
- Mock data uses `secrets` module for cryptographically secure randomness
- Frontend uses `useCallback` to prevent unnecessary re-renders
