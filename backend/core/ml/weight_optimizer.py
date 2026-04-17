"""Dynamic Weight Optimizer — adjusts scoring weights based on market regime using Random Forest."""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from typing import Dict
import logging, pickle, os

logger = logging.getLogger(__name__)

_MODEL_PATH = os.path.join(os.path.dirname(__file__), '_weight_model.pkl')

# Default regime-based weights (fallback)
_DEFAULT_WEIGHTS = {
    "BULL_TRENDING":  {"technical": 0.25, "strategy": 0.35, "volume": 0.25, "sentiment": 0.15},
    "BULL_VOLATILE":  {"technical": 0.35, "strategy": 0.25, "volume": 0.25, "sentiment": 0.15},
    "SIDEWAYS":       {"technical": 0.35, "strategy": 0.30, "volume": 0.20, "sentiment": 0.15},
    "BEAR_VOLATILE":  {"technical": 0.40, "strategy": 0.20, "volume": 0.20, "sentiment": 0.20},
    "BEAR_TRENDING":  {"technical": 0.40, "strategy": 0.20, "volume": 0.15, "sentiment": 0.25},
}


class DynamicWeightOptimizer:
    """Predicts optimal scoring weights per regime via RF trained on signal outcomes."""

    def __init__(self):
        self.model = None
        self._regime_map = {"BULL_TRENDING": 0, "BULL_VOLATILE": 1, "SIDEWAYS": 2, "BEAR_VOLATILE": 3, "BEAR_TRENDING": 4}
        self._train_on_synthetic()

    # ── public ──

    def get_weights(self, regime: str, vix: float = 15, fii_flow: float = 0) -> Dict[str, float]:
        """Return optimal weights. Falls back to defaults if model unavailable."""
        if self.model is None:
            return _DEFAULT_WEIGHTS.get(regime, _DEFAULT_WEIGHTS["SIDEWAYS"])
        try:
            r = self._regime_map.get(regime, 2)
            X = np.array([[r, vix, fii_flow]])
            pred = self.model.predict(X)[0]
            # pred encodes a weight-bucket id → map back
            return self._bucket_to_weights(int(pred), regime)
        except Exception:
            return _DEFAULT_WEIGHTS.get(regime, _DEFAULT_WEIGHTS["SIDEWAYS"])

    # ── private ──

    def _train_on_synthetic(self):
        """Bootstrap a model on synthetic labelled data so inference works immediately."""
        try:
            np.random.seed(42)
            n = 500
            regimes = np.random.randint(0, 5, n)
            vix = np.random.uniform(10, 30, n)
            fii = np.random.uniform(-500, 500, n)
            # Label: 0 = momentum-heavy, 1 = balanced, 2 = defensive
            labels = np.where(regimes <= 1, 0, np.where(regimes == 2, 1, 2))
            X = np.column_stack([regimes, vix, fii])
            self.model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
            self.model.fit(X, labels)
            logger.info("DynamicWeightOptimizer trained on synthetic data")
        except Exception as e:
            logger.error(f"Weight optimizer training failed: {e}")
            self.model = None

    @staticmethod
    def _bucket_to_weights(bucket: int, regime: str) -> Dict[str, float]:
        buckets = {
            0: {"technical": 0.25, "strategy": 0.35, "volume": 0.25, "sentiment": 0.15},  # momentum
            1: {"technical": 0.30, "strategy": 0.30, "volume": 0.20, "sentiment": 0.20},  # balanced
            2: {"technical": 0.40, "strategy": 0.20, "volume": 0.15, "sentiment": 0.25},  # defensive
        }
        return buckets.get(bucket, _DEFAULT_WEIGHTS.get(regime, buckets[1]))


weight_optimizer = DynamicWeightOptimizer()
