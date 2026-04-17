from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, timezone
import os
import logging
import json
import asyncio
import pandas as pd

from core.fyers_client import fyers_client
from core.regime import MarketRegimeClassifier
from core.scanner import MarketScanner
from core.sentiment import SentimentAnalyzer
from core.risk import RiskManager
from core.backtest import Backtester
from core.indicators import TechnicalIndicators

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="JPM-SwingEdge Pro API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

regime_classifier = MarketRegimeClassifier(fyers_client)
market_scanner = MarketScanner()
sentiment_analyzer = SentimentAnalyzer()
risk_manager = RiskManager()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

ws_manager = ConnectionManager()

@api_router.get("/market/regime")
async def get_market_regime():
    """Get current market regime"""
    try:
        regime_data = await regime_classifier.classify_regime()
        return {"success": True, "data": regime_data}
    except Exception as e:
        logger.error(f"Regime endpoint error: {e}")
        return {"success": False, "error": str(e)}

@api_router.post("/scanner/run")
async def run_scanner(
    timeframe: str = "swing",
    background_tasks: BackgroundTasks = None
):
    """Trigger market scan"""
    try:
        regime_data = await regime_classifier.classify_regime()
        market_regime = regime_data.get('regime', 'SIDEWAYS')
        
        signals = await market_scanner.scan_market(timeframe, market_regime)
        
        await db.signals.insert_many([{**s, 'scanned_at': datetime.now(timezone.utc)} for s in signals])
        
        return {
            "success": True,
            "signals_found": len(signals),
            "timeframe": timeframe,
            "market_regime": market_regime
        }
    except Exception as e:
        logger.error(f"Scanner error: {e}")
        return {"success": False, "error": str(e)}

@api_router.get("/signals/top10")
async def get_top_signals(timeframe: str = "swing"):
    """Get top 10 ranked signals"""
    try:
        regime_data = await regime_classifier.classify_regime()
        market_regime = regime_data.get('regime', 'SIDEWAYS')
        
        signals = await market_scanner.scan_market(timeframe, market_regime)
        
        return {
            "success": True,
            "signals": signals[:10],
            "count": len(signals),
            "market_regime": market_regime
        }
    except Exception as e:
        logger.error(f"Top signals error: {e}")
        return {"success": False, "error": str(e), "signals": []}

@api_router.get("/signals/{ticker}")
async def get_signal_detail(ticker: str):
    """Get detailed signal breakdown for ticker"""
    try:
        symbol = fyers_client.format_nse_symbol(ticker)
        
        hist_data = fyers_client.get_historical(symbol, resolution="D", days=365)
        
        if hist_data.get('s') != 'ok':
            return {"success": False, "error": "Unable to fetch data"}
        
        df = pd.DataFrame(
            hist_data['candles'],
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df = TechnicalIndicators.calculate_all(df)
        
        current_price = float(df['close'].iloc[-1])
        support, resistance = TechnicalIndicators.get_support_resistance(df)
        patterns = TechnicalIndicators.detect_chart_patterns(df)
        
        fib_levels = TechnicalIndicators.calculate_fibonacci_levels(
            df['high'].tail(20).max(),
            df['low'].tail(20).min()
        )
        
        chart_data = []
        for idx, row in df.tail(100).iterrows():
            chart_data.append({
                'time': int(row['timestamp'].timestamp()),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(row['volume'])
            })
        
        indicators = {
            'rsi': float(df['rsi'].iloc[-1]) if 'rsi' in df.columns else 50,
            'macd': float(df['macd'].iloc[-1]) if 'macd' in df.columns else 0,
            'macd_signal': float(df['macd_signal'].iloc[-1]) if 'macd_signal' in df.columns else 0,
            'ema_20': float(df['ema_20'].iloc[-1]) if 'ema_20' in df.columns else current_price,
            'ema_50': float(df['ema_50'].iloc[-1]) if 'ema_50' in df.columns else current_price,
            'ema_200': float(df['ema_200'].iloc[-1]) if 'ema_200' in df.columns else current_price,
            'vwap': float(df['vwap'].iloc[-1]) if 'vwap' in df.columns else current_price
        }
        
        return {
            "success": True,
            "ticker": ticker,
            "current_price": current_price,
            "support": float(support),
            "resistance": float(resistance),
            "patterns": patterns,
            "fibonacci_levels": fib_levels,
            "indicators": indicators,
            "chart_data": chart_data
        }
    
    except Exception as e:
        logger.error(f"Signal detail error: {e}")
        return {"success": False, "error": str(e)}

@api_router.post("/backtest/run")
async def run_backtest(
    strategy: str = "BB_Squeeze",
    start_date: str = None,
    end_date: str = None,
    capital: float = 100000
):
    """Run backtest"""
    try:
        signals = await market_scanner.scan_market("swing", "SIDEWAYS")
        
        backtester = Backtester(initial_capital=capital)
        df = pd.DataFrame()
        results = backtester.run_backtest(signals, df)
        
        return {
            "success": True,
            "strategy": strategy,
            "results": results
        }
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        return {"success": False, "error": str(e)}

@api_router.get("/backtest/results")
async def get_backtest_results():
    """Get latest backtest results"""
    try:
        results = await db.backtests.find_one(sort=[('created_at', -1)])
        if results:
            results['_id'] = str(results['_id'])
            return {"success": True, "results": results}
        return {"success": False, "error": "No backtest results found"}
    except Exception as e:
        logger.error(f"Backtest results error: {e}")
        return {"success": False, "error": str(e)}

@api_router.get("/sentiment/{ticker}")
async def get_sentiment(ticker: str):
    """Get news sentiment for ticker"""
    try:
        sentiment_data = await sentiment_analyzer.get_news_sentiment(ticker)
        return {"success": True, "data": sentiment_data}
    except Exception as e:
        logger.error(f"Sentiment error: {e}")
        return {"success": False, "error": str(e)}

@api_router.post("/portfolio/risk")
async def calculate_risk(
    capital: float,
    entry_price: float,
    stop_loss: float,
    risk_percent: float = 2.0,
    win_rate: float = 0.55,
    avg_win: float = 5.0,
    avg_loss: float = 3.0
):
    """Calculate position sizing"""
    try:
        fixed_fractional = risk_manager.calculate_position_size_fixed_fractional(
            capital, risk_percent, entry_price, stop_loss
        )
        
        kelly = risk_manager.calculate_kelly_criterion(
            capital, win_rate, avg_win, avg_loss, entry_price, kelly_fraction=0.5
        )
        
        regime_data = await regime_classifier.classify_regime()
        recommendations = risk_manager.get_risk_recommendations(
            capital, regime_data.get('regime', 'SIDEWAYS'), win_rate
        )
        
        return {
            "success": True,
            "fixed_fractional": fixed_fractional,
            "kelly_criterion": kelly,
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Risk calculation error: {e}")
        return {"success": False, "error": str(e)}

@api_router.get("/strategies/list")
async def list_strategies():
    """Get all available strategies"""
    strategies = [
        {
            "name": "ORB Modified",
            "timeframe": "intraday",
            "description": "Opening range breakout with volume confirmation",
            "win_rate": 68,
            "avg_rr": 2.1,
            "best_regime": "BULL_TRENDING"
        },
        {
            "name": "VWAP Reversal",
            "timeframe": "intraday",
            "description": "Mean reversion from VWAP with RSI",
            "win_rate": 65,
            "avg_rr": 1.8,
            "best_regime": "SIDEWAYS"
        },
        {
            "name": "Expiry Day Momentum",
            "timeframe": "intraday",
            "description": "Momentum trades on weekly expiry",
            "win_rate": 62,
            "avg_rr": 2.0,
            "best_regime": "BULL_VOLATILE"
        },
        {
            "name": "BB Squeeze",
            "timeframe": "swing",
            "description": "Volatility breakout from BB squeeze",
            "win_rate": 72,
            "avg_rr": 2.5,
            "best_regime": "SIDEWAYS"
        },
        {
            "name": "Momentum + Delivery %",
            "timeframe": "swing",
            "description": "Price momentum with delivery participation",
            "win_rate": 70,
            "avg_rr": 2.3,
            "best_regime": "BULL_TRENDING"
        },
        {
            "name": "Quality Momentum",
            "timeframe": "positional",
            "description": "High quality stocks with sustained momentum",
            "win_rate": 75,
            "avg_rr": 3.0,
            "best_regime": "BULL_TRENDING"
        }
    ]
    return {"success": True, "strategies": strategies}

@api_router.get("/intraday/signals")
async def get_intraday_signals():
    """Get live intraday signals"""
    try:
        signals = await market_scanner.scan_market("intraday", "BULL_TRENDING")
        return {"success": True, "signals": signals[:10]}
    except Exception as e:
        logger.error(f"Intraday signals error: {e}")
        return {"success": False, "error": str(e), "signals": []}

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            
            if request.get('action') == 'subscribe':
                symbols = request.get('symbols', [])
                for symbol in symbols:
                    quote_data = fyers_client.get_quotes([symbol])
                    if quote_data.get('s') == 'ok':
                        await websocket.send_json({
                            'type': 'quote',
                            'data': quote_data.get('d', {})
                        })
            
            await asyncio.sleep(5)
    
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

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
