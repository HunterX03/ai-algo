"""Intraday Pattern Recognition — lightweight feature-based classifier (no CNN/torch)."""
import numpy as np
from xgboost import XGBClassifier
from typing import Dict
import logging

logger = logging.getLogger(__name__)

PATTERN_NAMES = ['NO_PATTERN', 'BULLISH_REVERSAL', 'BEARISH_REVERSAL', 'BREAKOUT_UP', 'BREAKOUT_DOWN', 'CONSOLIDATION']


class IntradayPatternRecognizer:
    """Extracts statistical features from 15-min candles and classifies pattern type."""

    def __init__(self):
        self.model = None
        self._train_on_synthetic()

    def recognize(self, candle_features: Dict) -> Dict:
        if self.model is None:
            return {'pattern': 'NO_PATTERN', 'probability': 0, 'description': 'Model unavailable'}
        try:
            X = np.array([[
                candle_features.get('body_ratio', 0.5),
                candle_features.get('upper_wick_ratio', 0.2),
                candle_features.get('lower_wick_ratio', 0.2),
                candle_features.get('volume_ratio', 1.0),
                candle_features.get('range_vs_atr', 1.0),
                candle_features.get('close_position', 0.5),  # where close is in range (0=low, 1=high)
                candle_features.get('prev_trend', 0),  # -1 down, 0 flat, 1 up
            ]])
            pred = int(self.model.predict(X)[0])
            probs = self.model.predict_proba(X)[0]
            prob = float(probs[pred]) * 100

            pattern = PATTERN_NAMES[pred] if pred < len(PATTERN_NAMES) else 'NO_PATTERN'
            descs = {
                'BULLISH_REVERSAL': 'Bullish reversal pattern detected — potential long entry',
                'BEARISH_REVERSAL': 'Bearish reversal — potential short or exit longs',
                'BREAKOUT_UP': 'Upside breakout pattern — momentum entry candidate',
                'BREAKOUT_DOWN': 'Downside breakdown — avoid longs, potential short',
                'CONSOLIDATION': 'Consolidation phase — wait for directional signal',
                'NO_PATTERN': 'No recognizable pattern',
            }
            return {'pattern': pattern, 'probability': round(prob, 1), 'description': descs.get(pattern, '')}
        except Exception:
            return {'pattern': 'NO_PATTERN', 'probability': 0, 'description': 'Error'}

    def _train_on_synthetic(self):
        try:
            np.random.seed(42)
            n = 1200
            body = np.random.uniform(0.1, 0.9, n)
            upper_w = np.random.uniform(0, 0.4, n)
            lower_w = np.random.uniform(0, 0.4, n)
            vol = np.random.lognormal(0, 0.5, n)
            rng = np.random.uniform(0.5, 2.5, n)
            close_pos = np.random.uniform(0, 1, n)
            trend = np.random.choice([-1, 0, 1], n)

            # Heuristic labelling
            labels = np.zeros(n, dtype=int)
            labels[(close_pos > 0.7) & (lower_w > 0.25) & (trend == -1)] = 1  # bullish reversal
            labels[(close_pos < 0.3) & (upper_w > 0.25) & (trend == 1)] = 2   # bearish reversal
            labels[(body > 0.6) & (vol > 1.5) & (close_pos > 0.7)] = 3        # breakout up
            labels[(body > 0.6) & (vol > 1.5) & (close_pos < 0.3)] = 4        # breakout down
            labels[(body < 0.2) & (rng < 0.8)] = 5                             # consolidation

            X = np.column_stack([body, upper_w, lower_w, vol, rng, close_pos, trend])
            self.model = XGBClassifier(
                n_estimators=80, max_depth=4, num_class=6, objective='multi:softprob',
                use_label_encoder=False, eval_metric='mlogloss', verbosity=0
            )
            self.model.fit(X, labels)
            logger.info("IntradayPatternRecognizer trained on synthetic data")
        except Exception as e:
            logger.error(f"Pattern recognition training failed: {e}")
            self.model = None


pattern_recognizer = IntradayPatternRecognizer()
