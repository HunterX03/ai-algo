"""Earnings Surprise Predictor — predicts whether upcoming results will beat/miss estimates."""
import numpy as np
from xgboost import XGBClassifier
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class EarningsSurprisePredictor:
    """Predicts beat/miss probability for PEAD strategy pre-positioning."""

    def __init__(self):
        self.model = None
        self._train_on_synthetic()

    def predict(self, features: Dict) -> Dict:
        if self.model is None:
            return {'beat_probability': 50, 'miss_probability': 50, 'confidence': 40}
        try:
            X = np.array([[
                features.get('delivery_pct_avg_30d', 55),
                features.get('promoter_change_pct', 0),
                features.get('revenue_growth_qoq', 5),
                features.get('sector_momentum', 0),
                features.get('pre_result_volume_spike', 1.0),
            ]])
            prob = float(self.model.predict_proba(X)[0][1]) * 100
            return {
                'beat_probability': round(prob, 1),
                'miss_probability': round(100 - prob, 1),
                'confidence': 60,
                'recommendation': 'Pre-position LONG' if prob > 60 else ('Avoid' if prob < 40 else 'Neutral'),
            }
        except Exception:
            return {'beat_probability': 50, 'miss_probability': 50, 'confidence': 40}

    def _train_on_synthetic(self):
        try:
            np.random.seed(42)
            n = 600
            delivery = np.random.normal(55, 12, n)
            promoter = np.random.normal(0, 2, n)
            revenue = np.random.normal(8, 10, n)
            sector = np.random.normal(0, 5, n)
            vol_spike = np.random.lognormal(0, 0.4, n)

            score = (0.25 * (delivery / 70) + 0.2 * np.clip(promoter / 3, -1, 1) +
                     0.3 * np.clip(revenue / 15, -1, 1) + 0.15 * np.clip(sector / 5, -1, 1) +
                     0.1 * np.clip(vol_spike / 2, 0, 1))
            labels = (score + np.random.normal(0, 0.15, n) > 0.4).astype(int)

            X = np.column_stack([delivery, promoter, revenue, sector, vol_spike])
            self.model = XGBClassifier(
                n_estimators=80, max_depth=3, learning_rate=0.1,
                use_label_encoder=False, eval_metric='logloss', verbosity=0
            )
            self.model.fit(X, labels)
            logger.info("EarningsSurprisePredictor trained on synthetic data")
        except Exception as e:
            logger.error(f"Earnings predictor training failed: {e}")
            self.model = None


earnings_predictor = EarningsSurprisePredictor()
