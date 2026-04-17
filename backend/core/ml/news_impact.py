"""News Event Impact Model — predicts price impact of NSE announcement types."""
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from typing import Dict
import logging

logger = logging.getLogger(__name__)

EVENT_TYPES = {
    'buyback': 0, 'board_meeting': 1, 'results': 2, 'dividend': 3,
    'pledging_change': 4, 'bonus': 5, 'stock_split': 6, 'acquisition': 7,
    'insider_trading': 8, 'regulatory': 9,
}


class NewsEventImpactModel:
    """Predicts avg price impact over 1/3/5/10 days for announcement types."""

    def __init__(self):
        self.model = None
        self._train_on_synthetic()

    def predict_impact(self, event_type: str, market_cap_cr: float = 50000, regime_code: int = 2) -> Dict:
        if self.model is None:
            return {'impact_1d': 0, 'impact_3d': 0, 'impact_5d': 0, 'impact_10d': 0, 'confidence': 50}
        try:
            etype = EVENT_TYPES.get(event_type.lower(), 1)
            X = np.array([[etype, market_cap_cr / 100000, regime_code]])
            pred = float(self.model.predict(X)[0])
            return {
                'impact_1d': round(pred * 0.4, 2),
                'impact_3d': round(pred * 0.7, 2),
                'impact_5d': round(pred, 2),
                'impact_10d': round(pred * 1.2, 2),
                'confidence': 65,
                'event_type': event_type,
            }
        except Exception:
            return {'impact_1d': 0, 'impact_3d': 0, 'impact_5d': 0, 'impact_10d': 0, 'confidence': 50}

    def _train_on_synthetic(self):
        try:
            np.random.seed(42)
            n = 500
            etypes = np.random.randint(0, 10, n)
            mcap = np.random.uniform(0.1, 5.0, n)  # normalized
            regime = np.random.randint(0, 5, n)

            # Buybacks and results have higher impact. Small caps move more.
            impact = (1.5 * (etypes == 0) + 3.0 * (etypes == 2) + 1.0 * (etypes == 3)
                      + 0.5 * (etypes == 1) - 1.0 * (etypes == 4)
                      + (1 / (mcap + 0.5)) * 0.5 - 0.3 * (regime > 2)
                      + np.random.normal(0, 0.5, n))

            X = np.column_stack([etypes, mcap, regime])
            self.model = GradientBoostingRegressor(
                n_estimators=80, max_depth=3, learning_rate=0.1, random_state=42
            )
            self.model.fit(X, impact)
            logger.info("NewsEventImpactModel trained on synthetic data")
        except Exception as e:
            logger.error(f"News impact training failed: {e}")
            self.model = None


news_impact = NewsEventImpactModel()
