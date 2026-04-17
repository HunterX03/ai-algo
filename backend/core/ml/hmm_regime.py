"""HMM-based Regime Probability Model — outputs regime probabilities instead of hard labels."""
import numpy as np
from hmmlearn.hmm import GaussianHMM
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class HMMRegimeModel:
    """Hidden Markov Model for regime classification with probability outputs."""

    REGIME_NAMES = ["BULL_TRENDING", "BULL_VOLATILE", "SIDEWAYS", "BEAR_VOLATILE", "BEAR_TRENDING"]

    def __init__(self):
        self.model = None
        self._train_on_synthetic()

    def predict_regime_probs(self, returns: float, vix: float, fii_flow: float) -> Dict:
        """Return dict of regime name → probability."""
        if self.model is None:
            return {r: 0.2 for r in self.REGIME_NAMES}
        try:
            obs = np.array([[returns, vix, fii_flow]])
            log_prob, state_seq = self.model.decode(obs, algorithm="viterbi")
            # Get posterior probabilities
            posteriors = self.model.predict_proba(obs)[0]
            result = {}
            for i, name in enumerate(self.REGIME_NAMES):
                result[name] = round(float(posteriors[i]), 3) if i < len(posteriors) else 0.0
            return result
        except Exception:
            return {r: 0.2 for r in self.REGIME_NAMES}

    def get_dominant_regime(self, returns: float, vix: float, fii_flow: float) -> str:
        probs = self.predict_regime_probs(returns, vix, fii_flow)
        return max(probs, key=probs.get)

    def _train_on_synthetic(self):
        try:
            np.random.seed(42)
            n = 500
            # Simulate 5-regime market: returns, vix, fii_flow
            returns = np.concatenate([
                np.random.normal(0.005, 0.008, 100),   # bull trending
                np.random.normal(0.003, 0.02, 100),    # bull volatile
                np.random.normal(0.0, 0.012, 100),     # sideways
                np.random.normal(-0.003, 0.02, 100),   # bear volatile
                np.random.normal(-0.005, 0.01, 100),   # bear trending
            ])
            vix = np.concatenate([
                np.random.normal(12, 2, 100),
                np.random.normal(18, 3, 100),
                np.random.normal(15, 2, 100),
                np.random.normal(22, 4, 100),
                np.random.normal(25, 3, 100),
            ])
            fii = np.concatenate([
                np.random.normal(200, 80, 100),
                np.random.normal(50, 150, 100),
                np.random.normal(0, 100, 100),
                np.random.normal(-100, 120, 100),
                np.random.normal(-300, 100, 100),
            ])
            X = np.column_stack([returns, vix, fii])
            self.model = GaussianHMM(n_components=5, covariance_type="diag",
                                      n_iter=100, random_state=42)
            self.model.fit(X)
            logger.info("HMMRegimeModel trained on synthetic data")
        except Exception as e:
            logger.error(f"HMM regime training failed: {e}")
            self.model = None


hmm_regime = HMMRegimeModel()
