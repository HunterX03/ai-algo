"""Optimal Exit Predictor — Gradient Boosting to suggest dynamic exit targets."""
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class OptimalExitPredictor:
    """Predicts optimal exit % instead of fixed Target 1/Target 2."""

    def __init__(self):
        self.model = None
        self._train_on_synthetic()

    def predict_exit(self, features: Dict) -> Dict:
        """Returns optimal exit pct and adjusted targets."""
        if self.model is None:
            return {'optimal_exit_pct': 5.0, 'confidence': 50}
        try:
            X = np.array([[
                features.get('atr_pct', 0.02),
                features.get('rsi', 50),
                features.get('adx', 20),
                features.get('volume_ratio', 1.0),
                features.get('bb_width', 0.05),
                features.get('regime_code', 2),
            ]])
            exit_pct = float(self.model.predict(X)[0])
            exit_pct = max(1.0, min(exit_pct, 20.0))  # clamp 1-20%
            return {'optimal_exit_pct': round(exit_pct, 2), 'confidence': 70}
        except Exception:
            return {'optimal_exit_pct': 5.0, 'confidence': 50}

    def _train_on_synthetic(self):
        try:
            np.random.seed(42)
            n = 800
            atr = np.random.uniform(0.01, 0.04, n)
            rsi = np.random.uniform(25, 75, n)
            adx = np.random.uniform(10, 50, n)
            vol = np.random.uniform(0.5, 3.0, n)
            bbw = np.random.uniform(0.01, 0.1, n)
            regime = np.random.randint(0, 5, n)

            # Target: higher ATR + ADX = larger moves. Bull regimes = larger.
            targets = (3 + atr * 100 + adx * 0.08 + vol * 0.5 - (regime > 2) * 1.5
                       + np.random.normal(0, 1, n))
            targets = np.clip(targets, 1, 20)

            X = np.column_stack([atr, rsi, adx, vol, bbw, regime])
            self.model = GradientBoostingRegressor(
                n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42
            )
            self.model.fit(X, targets)
            logger.info("OptimalExitPredictor trained on synthetic data")
        except Exception as e:
            logger.error(f"Exit predictor training failed: {e}")
            self.model = None


exit_predictor = OptimalExitPredictor()
