"""Volume Anomaly Detection — Isolation Forest to flag unusual accumulation/distribution."""
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class VolumeAnomalyDetector:
    """Detects unusual volume patterns that precede large moves."""

    def __init__(self):
        self.model = None
        self._train_on_synthetic()

    def detect(self, volume_features: Dict) -> Dict:
        """Return anomaly score and flag. Score < -0.5 = highly anomalous."""
        if self.model is None:
            return {'is_anomaly': False, 'anomaly_score': 0.0, 'description': 'Model unavailable'}
        try:
            X = np.array([[
                volume_features.get('volume_ratio_1d', 1.0),
                volume_features.get('volume_ratio_5d', 1.0),
                volume_features.get('price_change_pct', 0.0),
                volume_features.get('delivery_pct', 50.0),
                volume_features.get('oi_change_pct', 0.0),
            ]])
            score = float(self.model.decision_function(X)[0])
            is_anomaly = self.model.predict(X)[0] == -1

            desc = 'Normal volume pattern'
            if is_anomaly:
                if volume_features.get('price_change_pct', 0) > 0:
                    desc = 'Unusual accumulation detected — possible institutional buying'
                else:
                    desc = 'Unusual distribution detected — possible institutional selling'

            return {'is_anomaly': bool(is_anomaly), 'anomaly_score': round(score, 3), 'description': desc}
        except Exception:
            return {'is_anomaly': False, 'anomaly_score': 0.0, 'description': 'Error'}

    def _train_on_synthetic(self):
        try:
            np.random.seed(42)
            n = 1000
            vol_1d = np.random.lognormal(0, 0.5, n)
            vol_5d = np.random.lognormal(0, 0.3, n)
            price = np.random.normal(0, 1.5, n)
            delivery = np.random.normal(50, 15, n)
            oi = np.random.normal(0, 5, n)

            X = np.column_stack([vol_1d, vol_5d, price, delivery, oi])
            self.model = IsolationForest(
                n_estimators=100, contamination=0.05, random_state=42
            )
            self.model.fit(X)
            logger.info("VolumeAnomalyDetector trained on synthetic data")
        except Exception as e:
            logger.error(f"Volume anomaly training failed: {e}")
            self.model = None


volume_anomaly = VolumeAnomalyDetector()
