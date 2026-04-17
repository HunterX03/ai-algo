import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime
import logging

from core.fyers_client import fyers_client
from core.indicators import TechnicalIndicators
from core.strategies.intraday.orb_modified import ORBModified
from core.strategies.intraday.vwap_reversal import VWAPReversal
from core.strategies.intraday.expiry_day import ExpiryDayMomentum
from core.strategies.intraday.gap_and_go import GapAndGo
from core.strategies.intraday.institutional_order_block import InstitutionalOrderBlock
from core.strategies.swing.bb_squeeze import BBSqueeze
from core.strategies.swing.momentum_delivery import MomentumDelivery
from core.strategies.swing.advanced import FIIDivergence, PEAD, FiftyTwoWeekBreakoutOI
from core.strategies.positional.quality_momentum import QualityMomentum
from core.strategies.positional.advanced import SectorRotation, SmallCapValue
from core.ranking import SignalRanker

logger = logging.getLogger(__name__)

NSE_TOP_STOCKS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "BAJFINANCE",
    "ASIANPAINT", "MARUTI", "HCLTECH", "AXISBANK", "LT",
    "ULTRACEMCO", "WIPRO", "NESTLEIND", "SUNPHARMA", "TITAN",
    "TECHM", "ONGC", "NTPC", "KOTAKBANK", "POWERGRID"
]


class MarketScanner:
    def __init__(self):
        self.strategies = {
            'intraday': [ORBModified, VWAPReversal, ExpiryDayMomentum, GapAndGo, InstitutionalOrderBlock],
            'swing': [BBSqueeze, MomentumDelivery, FIIDivergence, PEAD, FiftyTwoWeekBreakoutOI],
            'positional': [QualityMomentum, SectorRotation, SmallCapValue]
        }

    async def scan_market(self, timeframe: str = "swing", market_regime: str = "SIDEWAYS") -> List[Dict]:
        logger.info(f"Starting market scan for {timeframe}")
        signals = []
        for ticker in NSE_TOP_STOCKS:
            try:
                signal = await self._analyze_stock(ticker, timeframe, market_regime)
                if signal and signal.get('signal') != 'NONE':
                    signals.append(signal)
            except Exception as e:
                logger.error(f"Error analyzing {ticker}: {e}")

        ranker = SignalRanker(market_regime)
        ranked = ranker.rank_signals(signals)
        logger.info(f"Scan complete. Found {len(ranked)} signals")
        return ranked[:10]

    async def _analyze_stock(self, ticker: str, timeframe: str, market_regime: str) -> Dict:
        try:
            symbol = fyers_client.format_nse_symbol(ticker)
            resolution = "D" if timeframe in ("positional", "swing") else "5"
            days = 365 if timeframe == "positional" else (90 if timeframe == "swing" else 5)

            hist = fyers_client.get_historical(symbol, resolution=resolution, days=days)
            if hist.get('s') != 'ok' or not hist.get('candles'):
                return None

            df = pd.DataFrame(hist['candles'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df = TechnicalIndicators.calculate_all(df)

            best_signal = None
            best_confidence = 0
            for strategy_class in self.strategies.get(timeframe, self.strategies['swing']):
                try:
                    sig = strategy_class.analyze(df)
                    if sig.get('signal') != 'NONE' and sig.get('confidence', 0) > best_confidence:
                        best_confidence = sig['confidence']
                        best_signal = {**sig, 'strategy': strategy_class.name}
                except Exception as e:
                    logger.error(f"Strategy {strategy_class.name} error on {ticker}: {e}")

            if not best_signal:
                return None

            ranker = SignalRanker(market_regime)
            technical_score = ranker.calculate_technical_score(df)
            volume_score = ranker.calculate_volume_score(df)

            current = float(df['close'].iloc[-1])
            entry = best_signal.get('entry', current)
            t1 = best_signal.get('target1', entry * 1.03)
            t2 = best_signal.get('target2', entry * 1.05)
            sl = best_signal.get('stop_loss', entry * 0.98)
            rr = abs((t1 - entry) / (entry - sl)) if entry != sl else 0

            return {
                'ticker': ticker, 'symbol': symbol,
                'signal': best_signal['signal'],
                'strategy': best_signal['strategy'],
                'entry_zone': round(entry, 2),
                'target_1': round(t1, 2),
                'target_2': round(t2, 2),
                'stop_loss': round(sl, 2),
                'risk_reward_ratio': round(rr, 2),
                'confidence': best_signal.get('confidence', 50),
                'technical_score': technical_score,
                'volume_score': volume_score,
                'sentiment_score': 0.0,
                'expected_hold': self._hold(timeframe),
                'timeframe': timeframe,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
            return None

    @staticmethod
    def _hold(tf):
        return {'intraday': '1-2 hours', 'swing': '3-7 days', 'positional': '30-90 days'}.get(tf, '3-7 days')
