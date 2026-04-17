import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import datetime
import asyncio
import logging

from core.fyers_client import fyers_client
from core.indicators import TechnicalIndicators
from core.strategies.intraday.orb_modified import ORBModified
from core.strategies.intraday.vwap_reversal import VWAPReversal
from core.strategies.intraday.expiry_day import ExpiryDayMomentum
from core.strategies.swing.bb_squeeze import BBSqueeze
from core.strategies.swing.momentum_delivery import MomentumDelivery
from core.strategies.positional.quality_momentum import QualityMomentum
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
            'intraday': [ORBModified, VWAPReversal, ExpiryDayMomentum],
            'swing': [BBSqueeze, MomentumDelivery],
            'positional': [QualityMomentum]
        }
    
    async def scan_market(self, timeframe: str = "swing", market_regime: str = "SIDEWAYS") -> List[Dict]:
        """Scan market for signals"""
        logger.info(f"Starting market scan for {timeframe} timeframe")
        
        signals = []
        stocks = NSE_TOP_STOCKS[:25]
        
        for ticker in stocks:
            try:
                signal = await self._analyze_stock(ticker, timeframe, market_regime)
                if signal and signal.get('signal') != 'NONE':
                    signals.append(signal)
            except Exception as e:
                logger.error(f"Error analyzing {ticker}: {e}")
        
        ranker = SignalRanker(market_regime)
        ranked_signals = ranker.rank_signals(signals)
        
        logger.info(f"Scan complete. Found {len(ranked_signals)} signals")
        return ranked_signals[:10]
    
    async def _analyze_stock(self, ticker: str, timeframe: str, market_regime: str) -> Dict:
        """Analyze individual stock"""
        try:
            symbol = fyers_client.format_nse_symbol(ticker)
            
            resolution = "D" if timeframe == "positional" else ("D" if timeframe == "swing" else "5")
            days = 365 if timeframe == "positional" else (90 if timeframe == "swing" else 5)
            
            hist_data = fyers_client.get_historical(symbol, resolution=resolution, days=days)
            
            if hist_data.get('s') != 'ok' or not hist_data.get('candles'):
                return None
            
            df = pd.DataFrame(
                hist_data['candles'],
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            
            df = TechnicalIndicators.calculate_all(df)
            
            strategy_signals = []
            strategies_to_use = self.strategies.get(timeframe, self.strategies['swing'])
            
            for strategy_class in strategies_to_use:
                try:
                    signal = strategy_class.analyze(df)
                    if signal.get('signal') != 'NONE':
                        strategy_signals.append({
                            'strategy': strategy_class.name,
                            **signal
                        })
                except Exception as e:
                    logger.error(f"Strategy {strategy_class.name} error: {e}")
            
            if not strategy_signals:
                return None
            
            best_signal = max(strategy_signals, key=lambda x: x.get('confidence', 0))
            
            ranker = SignalRanker(market_regime)
            technical_score = ranker.calculate_technical_score(df)
            volume_score = ranker.calculate_volume_score(df)
            
            current_price = float(df['close'].iloc[-1])
            entry = best_signal.get('entry', current_price)
            target1 = best_signal.get('target1', entry * 1.03)
            target2 = best_signal.get('target2', entry * 1.05)
            stop_loss = best_signal.get('stop_loss', entry * 0.98)
            
            risk_reward = abs((target1 - entry) / (entry - stop_loss)) if entry != stop_loss else 0
            
            return {
                'ticker': ticker,
                'symbol': symbol,
                'signal': best_signal.get('signal', 'NONE'),
                'strategy': best_signal.get('strategy', 'Unknown'),
                'entry_zone': float(entry),
                'target_1': float(target1),
                'target_2': float(target2),
                'stop_loss': float(stop_loss),
                'risk_reward_ratio': round(risk_reward, 2),
                'confidence': best_signal.get('confidence', 50),
                'technical_score': technical_score,
                'volume_score': volume_score,
                'sentiment_score': 0.0,
                'expected_hold': self._get_expected_hold(timeframe),
                'timeframe': timeframe,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
            return None
    
    def _get_expected_hold(self, timeframe: str) -> str:
        """Get expected holding period"""
        periods = {
            'intraday': '1-2 hours',
            'swing': '3-7 days',
            'positional': '30-90 days'
        }
        return periods.get(timeframe, '3-7 days')
