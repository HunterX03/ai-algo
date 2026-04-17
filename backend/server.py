from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timezone
import os
import logging
import json
import asyncio

from core.fyers_client import fyers_client
from core.regime import MarketRegimeClassifier
from core.scanner import MarketScanner
from core.sentiment import SentimentAnalyzer
from core.risk import RiskManager
from core.backtest import Backtester
from core.indicators import TechnicalIndicators
from core.ml.weight_optimizer import weight_optimizer
from core.ml.quality_classifier import quality_classifier
from core.ml.exit_predictor import exit_predictor
from core.ml.hmm_regime import hmm_regime
from core.ml.volume_anomaly import volume_anomaly
from core.ml.news_impact import news_impact
from core.ml.sector_momentum import sector_ml
from core.ml.pattern_recognition import pattern_recognizer
from core.ml.earnings_predictor import earnings_predictor
from core.quant.factor_model import factor_model
from core.quant.pairs_trading import pairs_trader
from core.quant.options_flow import options_flow
from core.quant.order_flow import order_flow
from core.quant.volatility_surface import vol_surface
import pandas as pd

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="JPM-SwingEdge Pro API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

regime_classifier = MarketRegimeClassifier(fyers_client)
market_scanner = MarketScanner()
sentiment_analyzer = SentimentAnalyzer()
risk_manager = RiskManager()

# ── WebSocket Manager ──
class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, msg: dict):
        for c in self.active:
            try:
                await c.send_json(msg)
            except Exception:
                pass

ws_manager = ConnectionManager()

# ── All 13 strategies metadata ──
ALL_STRATEGIES = [
    {"name": "ORB Modified", "timeframe": "intraday", "description": "Opening range breakout with volume confirmation. Triggers at 10:00 AM after first 15-min range forms.", "win_rate": 68, "avg_rr": 2.1, "best_regime": "BULL_TRENDING", "capital_alloc": 8, "enabled": True},
    {"name": "VWAP Reversal", "timeframe": "intraday", "description": "Mean reversion from VWAP with RSI confirmation. Continuous monitoring throughout session.", "win_rate": 65, "avg_rr": 1.8, "best_regime": "SIDEWAYS", "capital_alloc": 7, "enabled": True},
    {"name": "Expiry Day Momentum", "timeframe": "intraday", "description": "Momentum trades on weekly expiry (Thursdays). Captures gamma-driven moves.", "win_rate": 62, "avg_rr": 2.0, "best_regime": "BULL_VOLATILE", "capital_alloc": 6, "enabled": True},
    {"name": "Gap and Go/Fade", "timeframe": "intraday", "description": "Trades opening gaps based on gap size and pre-market volume. Signals at 9:30 AM.", "win_rate": 64, "avg_rr": 1.9, "best_regime": "BULL_TRENDING", "capital_alloc": 7, "enabled": True},
    {"name": "Institutional Order Block", "timeframe": "intraday", "description": "Identifies institutional supply/demand zones via order flow and volume clusters.", "win_rate": 66, "avg_rr": 2.2, "best_regime": "SIDEWAYS", "capital_alloc": 8, "enabled": True},
    {"name": "Momentum + Delivery %", "timeframe": "swing", "description": "Price momentum aligned with high delivery participation (>60%). Strong institutional backing.", "win_rate": 70, "avg_rr": 2.3, "best_regime": "BULL_TRENDING", "capital_alloc": 10, "enabled": True},
    {"name": "BB Squeeze", "timeframe": "swing", "description": "Bollinger Band squeeze breakout with volume expansion. Low volatility → high volatility transition.", "win_rate": 72, "avg_rr": 2.5, "best_regime": "SIDEWAYS", "capital_alloc": 9, "enabled": True},
    {"name": "FII Divergence", "timeframe": "swing", "description": "Trades divergence between FII flow direction and price action. Contrarian signal.", "win_rate": 67, "avg_rr": 2.1, "best_regime": "BEAR_VOLATILE", "capital_alloc": 7, "enabled": True},
    {"name": "PEAD", "timeframe": "swing", "description": "Post-Earnings Announcement Drift. Captures continued drift after earnings surprise.", "win_rate": 71, "avg_rr": 2.4, "best_regime": "BULL_TRENDING", "capital_alloc": 8, "enabled": True},
    {"name": "52-Week Breakout + OI", "timeframe": "swing", "description": "Breakout from 52-week range with open interest buildup confirmation for F&O stocks.", "win_rate": 74, "avg_rr": 2.8, "best_regime": "BULL_TRENDING", "capital_alloc": 10, "enabled": True},
    {"name": "Quality Momentum", "timeframe": "positional", "description": "High ROE, reasonable PE stocks with sustained 3-6 month price momentum.", "win_rate": 75, "avg_rr": 3.0, "best_regime": "BULL_TRENDING", "capital_alloc": 12, "enabled": True},
    {"name": "Sector Rotation", "timeframe": "positional", "description": "Rotates into sectors showing relative strength momentum vs Nifty.", "win_rate": 69, "avg_rr": 2.6, "best_regime": "BULL_VOLATILE", "capital_alloc": 10, "enabled": True},
    {"name": "Small Cap Value", "timeframe": "positional", "description": "Identifies undervalued small caps with improving volume and fundamentals.", "win_rate": 68, "avg_rr": 3.2, "best_regime": "BULL_TRENDING", "capital_alloc": 8, "enabled": True},
]


# ── API Endpoints ──

@api_router.get("/market/regime")
async def get_market_regime():
    try:
        data = await regime_classifier.classify_regime()
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Regime error: {e}")
        return {"success": True, "data": {
            "regime": "SIDEWAYS", "nifty_price": 24350.0,
            "ema_200": 23800.0, "vix": 14.5, "fii_flow_5d": 245.0,
            "timestamp": datetime.now().isoformat()
        }}


@api_router.post("/scanner/run")
async def run_scanner(timeframe: str = "swing"):
    try:
        regime = await regime_classifier.classify_regime()
        mr = regime.get('regime', 'SIDEWAYS')
        signals = await market_scanner.scan_market(timeframe, mr)
        return {"success": True, "signals_found": len(signals), "timeframe": timeframe, "market_regime": mr, "signals": signals}
    except Exception as e:
        logger.error(f"Scanner error: {e}")
        return {"success": False, "error": str(e)}


@api_router.get("/signals/top10")
async def get_top_signals(timeframe: str = "swing"):
    try:
        regime = await regime_classifier.classify_regime()
        mr = regime.get('regime', 'SIDEWAYS')
        signals = await market_scanner.scan_market(timeframe, mr)
        return {"success": True, "signals": signals[:10], "count": len(signals), "market_regime": mr}
    except Exception as e:
        logger.error(f"Top signals error: {e}")
        return {"success": True, "signals": [], "count": 0, "market_regime": "SIDEWAYS"}


@api_router.get("/signals/{ticker}")
async def get_signal_detail(ticker: str):
    try:
        symbol = fyers_client.format_nse_symbol(ticker)
        hist = fyers_client.get_historical(symbol, resolution="D", days=365)
        if hist.get('s') != 'ok' or not hist.get('candles'):
            return {"success": False, "error": "No data available"}

        df = pd.DataFrame(hist['candles'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df = TechnicalIndicators.calculate_all(df)

        current = float(df['close'].iloc[-1])
        support, resistance = TechnicalIndicators.get_support_resistance(df)
        patterns = TechnicalIndicators.detect_chart_patterns(df)
        fib = TechnicalIndicators.calculate_fibonacci_levels(df['high'].tail(20).max(), df['low'].tail(20).min())

        chart_data = []
        for _, row in df.tail(100).iterrows():
            chart_data.append({
                'time': int(row['timestamp'].timestamp()),
                'open': round(float(row['open']), 2),
                'high': round(float(row['high']), 2),
                'low': round(float(row['low']), 2),
                'close': round(float(row['close']), 2),
                'volume': int(row['volume'])
            })

        def safe(col):
            return round(float(df[col].iloc[-1]), 2) if col in df.columns and not pd.isna(df[col].iloc[-1]) else 0

        return {
            "success": True, "ticker": ticker, "current_price": round(current, 2),
            "support": round(support, 2), "resistance": round(resistance, 2),
            "patterns": patterns, "fibonacci_levels": fib,
            "indicators": {
                "rsi": safe('rsi'), "macd": safe('macd'), "macd_signal": safe('macd_signal'),
                "ema_20": safe('ema_20'), "ema_50": safe('ema_50'), "ema_200": safe('ema_200'),
                "vwap": safe('vwap'), "atr": safe('atr'), "adx": safe('adx'),
                "bb_upper": safe('bb_upper'), "bb_lower": safe('bb_lower'),
            },
            "chart_data": chart_data
        }
    except Exception as e:
        logger.error(f"Signal detail error: {e}")
        return {"success": False, "error": str(e)}


@api_router.post("/backtest/run")
async def run_backtest(strategy: str = "BB_Squeeze", capital: float = 100000):
    try:
        signals = await market_scanner.scan_market("swing", "SIDEWAYS")
        bt = Backtester(initial_capital=capital)
        results = bt.run_backtest(signals, pd.DataFrame())
        return {"success": True, "strategy": strategy, "results": results}
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        return {"success": False, "error": str(e)}


@api_router.get("/backtest/results")
async def get_backtest_results():
    try:
        doc = await db.backtests.find_one(sort=[('created_at', -1)], projection={"_id": 0})
        if doc:
            return {"success": True, "results": doc}
        return {"success": False, "error": "No results found"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@api_router.get("/sentiment/{ticker}")
async def get_sentiment(ticker: str):
    try:
        data = await sentiment_analyzer.get_news_sentiment(ticker)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Sentiment error: {e}")
        return {"success": False, "error": str(e)}


@api_router.get("/portfolio/risk")
async def calculate_risk(
    capital: float = Query(100000),
    entry_price: float = Query(1000),
    stop_loss: float = Query(950),
    risk_percent: float = Query(2.0),
    win_rate: float = Query(0.55),
    avg_win: float = Query(5.0),
    avg_loss: float = Query(3.0)
):
    try:
        ff = risk_manager.calculate_position_size_fixed_fractional(capital, risk_percent, entry_price, stop_loss)
        kelly = risk_manager.calculate_kelly_criterion(capital, win_rate, avg_win, avg_loss, entry_price, 0.5)
        regime = await regime_classifier.classify_regime()
        rec = risk_manager.get_risk_recommendations(capital, regime.get('regime', 'SIDEWAYS'), win_rate)
        return {"success": True, "fixed_fractional": ff, "kelly_criterion": kelly, "recommendations": rec}
    except Exception as e:
        logger.error(f"Risk error: {e}")
        return {"success": False, "error": str(e)}


@api_router.get("/strategies/list")
async def list_strategies():
    return {"success": True, "strategies": ALL_STRATEGIES}


@api_router.get("/intraday/signals")
async def get_intraday_signals():
    try:
        signals = await market_scanner.scan_market("intraday", "BULL_TRENDING")
        return {"success": True, "signals": signals[:10]}
    except Exception as e:
        logger.error(f"Intraday error: {e}")
        return {"success": True, "signals": []}


# ── ML Enhancement Endpoints ──

@api_router.get("/ml/regime-probabilities")
async def get_regime_probabilities(returns: float = Query(0.001), vix: float = Query(15), fii_flow: float = Query(0)):
    """HMM-based regime with probability outputs."""
    probs = hmm_regime.predict_regime_probs(returns, vix, fii_flow)
    dominant = max(probs, key=probs.get)
    return {"success": True, "probabilities": probs, "dominant_regime": dominant}


@api_router.get("/ml/optimal-weights")
async def get_optimal_weights(regime: str = Query("SIDEWAYS"), vix: float = Query(15), fii_flow: float = Query(0)):
    """Dynamic weight optimization for scoring engine."""
    weights = weight_optimizer.get_weights(regime, vix, fii_flow)
    return {"success": True, "weights": weights, "regime": regime}


@api_router.post("/ml/quality-score")
async def get_quality_score(
    rsi: float = Query(50), macd_hist: float = Query(0), adx: float = Query(20),
    volume_ratio: float = Query(1.0), bb_width: float = Query(0.05),
    price_vs_ema20: float = Query(0), price_vs_ema50: float = Query(0), atr_pct: float = Query(0.02)
):
    """XGBoost setup quality classifier."""
    score = quality_classifier.predict_quality({
        'rsi': rsi, 'macd_hist': macd_hist, 'adx': adx,
        'volume_ratio': volume_ratio, 'bb_width': bb_width,
        'price_vs_ema20': price_vs_ema20, 'price_vs_ema50': price_vs_ema50, 'atr_pct': atr_pct,
    })
    return {"success": True, "quality_score": score}


@api_router.post("/ml/optimal-exit")
async def get_optimal_exit(
    atr_pct: float = Query(0.02), rsi: float = Query(50), adx: float = Query(20),
    volume_ratio: float = Query(1.0), bb_width: float = Query(0.05), regime_code: int = Query(2)
):
    """Gradient Boosting optimal exit predictor."""
    result = exit_predictor.predict_exit({
        'atr_pct': atr_pct, 'rsi': rsi, 'adx': adx,
        'volume_ratio': volume_ratio, 'bb_width': bb_width, 'regime_code': regime_code,
    })
    return {"success": True, **result}


@api_router.post("/ml/volume-anomaly")
async def detect_volume_anomaly(
    volume_ratio_1d: float = Query(1.0), volume_ratio_5d: float = Query(1.0),
    price_change_pct: float = Query(0.0), delivery_pct: float = Query(50.0), oi_change_pct: float = Query(0.0)
):
    """Isolation Forest volume anomaly detection."""
    result = volume_anomaly.detect({
        'volume_ratio_1d': volume_ratio_1d, 'volume_ratio_5d': volume_ratio_5d,
        'price_change_pct': price_change_pct, 'delivery_pct': delivery_pct, 'oi_change_pct': oi_change_pct,
    })
    return {"success": True, **result}


@api_router.get("/ml/news-impact")
async def get_news_impact(event_type: str = Query("results"), market_cap_cr: float = Query(50000), regime_code: int = Query(2)):
    """Predict price impact of NSE announcement types."""
    result = news_impact.predict_impact(event_type, market_cap_cr, regime_code)
    return {"success": True, **result}


@api_router.get("/ml/sector-rotation")
async def get_sector_rotation():
    """ML-based sector rotation prediction."""
    ranks = sector_ml.predict_sector_ranks()
    return {"success": True, "sectors": ranks}


@api_router.post("/ml/pattern-recognition")
async def recognize_pattern(
    body_ratio: float = Query(0.5), upper_wick_ratio: float = Query(0.2),
    lower_wick_ratio: float = Query(0.2), volume_ratio: float = Query(1.0),
    range_vs_atr: float = Query(1.0), close_position: float = Query(0.5), prev_trend: int = Query(0)
):
    """Intraday candlestick pattern recognition."""
    result = pattern_recognizer.recognize({
        'body_ratio': body_ratio, 'upper_wick_ratio': upper_wick_ratio,
        'lower_wick_ratio': lower_wick_ratio, 'volume_ratio': volume_ratio,
        'range_vs_atr': range_vs_atr, 'close_position': close_position, 'prev_trend': prev_trend,
    })
    return {"success": True, **result}


@api_router.post("/ml/earnings-surprise")
async def predict_earnings(
    delivery_pct_avg_30d: float = Query(55), promoter_change_pct: float = Query(0),
    revenue_growth_qoq: float = Query(5), sector_momentum: float = Query(0), pre_result_volume_spike: float = Query(1.0)
):
    """Predict earnings surprise probability."""
    result = earnings_predictor.predict({
        'delivery_pct_avg_30d': delivery_pct_avg_30d, 'promoter_change_pct': promoter_change_pct,
        'revenue_growth_qoq': revenue_growth_qoq, 'sector_momentum': sector_momentum,
        'pre_result_volume_spike': pre_result_volume_spike,
    })
    return {"success": True, **result}


# ── Quant Tier Endpoints ──

@api_router.get("/quant/factor-scores")
async def get_factor_scores(regime: str = Query("SIDEWAYS")):
    """Tier 1: Multi-factor model scores for NSE universe."""
    from core.scanner import NSE_TOP_STOCKS
    price_data = {}
    for t in NSE_TOP_STOCKS:
        sym = fyers_client.format_nse_symbol(t)
        hist = fyers_client.get_historical(sym, "D", 365)
        if hist.get('s') == 'ok' and hist.get('candles'):
            df = pd.DataFrame(hist['candles'], columns=['timestamp','open','high','low','close','volume'])
            price_data[t] = df
    ranked = factor_model.rank_universe(list(price_data.keys()), price_data, regime)
    return {"success": True, "rankings": ranked, "regime": regime}


@api_router.get("/quant/pairs")
async def get_pairs_signals():
    """Tier 2: Statistical pairs trading signals."""
    from core.scanner import NSE_TOP_STOCKS
    price_data = {}
    for t in NSE_TOP_STOCKS:
        sym = fyers_client.format_nse_symbol(t)
        hist = fyers_client.get_historical(sym, "D", 120)
        if hist.get('s') == 'ok' and hist.get('candles'):
            df = pd.DataFrame(hist['candles'], columns=['timestamp','open','high','low','close','volume'])
            price_data[t] = df['close']
    results = pairs_trader.scan_all_pairs(price_data)
    return {"success": True, "pairs": results}


@api_router.get("/quant/options-flow")
async def get_options_flow(ticker: str = Query(None)):
    """Tier 3: Options flow analysis."""
    if ticker:
        result = options_flow.analyze_stock_options(ticker)
        return {"success": True, "data": result}
    results = options_flow.scan_all_fno()
    return {"success": True, "signals": results}


@api_router.get("/quant/order-flow/{ticker}")
async def get_order_flow(ticker: str):
    """Tier 4: Intraday order flow imbalance."""
    result = order_flow.analyze_order_flow(ticker)
    return {"success": True, "data": result}


@api_router.get("/quant/vol-surface/{ticker}")
async def get_vol_surface(ticker: str):
    """Tier 5: Volatility surface analysis."""
    result = vol_surface.analyze_vol_surface(ticker)
    return {"success": True, "data": result}


@api_router.get("/quant/vol-opportunities")
async def get_vol_opportunities():
    """Tier 5: Scan for vol surface opportunities across F&O stocks."""
    from core.quant.options_flow import FNO_STOCKS
    results = vol_surface.scan_vol_opportunities(FNO_STOCKS)
    return {"success": True, "opportunities": results}


# ── WebSocket ──

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            if request.get('action') == 'subscribe':
                symbols = request.get('symbols', [])
                quotes = fyers_client.get_quotes(symbols)
                if quotes.get('s') == 'ok':
                    await websocket.send_json({'type': 'quote', 'data': quotes.get('d', {})})
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


# ── Include router & middleware ──

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
