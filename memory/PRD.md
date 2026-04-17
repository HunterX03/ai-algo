# JPM-SwingEdge Pro - Product Requirements Document

## Original Problem Statement
Full-stack quantitative trading dashboard for Indian stock markets (NSE). Signal generation platform with manual trading only.

## Architecture
- Backend: FastAPI + MongoDB + 9 ML models (sklearn, XGBoost, hmmlearn) + 5 quant modules
- Frontend: React + TailwindCSS + TradingView Lightweight Charts + Recharts
- Real-time: WebSocket, ML inference <1ms

## What's Implemented (April 2026)
### Backend: 26+ API Endpoints
- Core: regime, signals, scanner, backtest, sentiment, risk, strategies, intraday, websocket
- ML: regime probabilities, dynamic weights, quality classifier, exit predictor, volume anomaly, news impact, sector rotation, pattern recognition, earnings predictor
- Quant: factor scores, pairs trading, options flow, order flow, vol surface, vol opportunities

### Frontend: 8 Pages
- Command Center, Stock Deep Dive, Strategy Lab, Backtest Suite, Risk Manager, Sentiment Hub, Intraday Monitor, Quant Engine (5 tabs)

### Quant Engine (5 Tiers)
1. Multi-Factor Model (Value/Momentum/Quality/LowVol/Size with regime-dependent weights)
2. Statistical Pairs Trading (cointegration, z-score, 10 NSE pairs)
3. Options Flow (OI buildup, IV spikes, PCR, unusual activity)
4. Order Flow Imbalance (bid/ask pressure, delta, large trade detection)
5. Volatility Surface (IV smile, RV divergence, pre-event/post-event)

### Code Quality
- XSS-safe, useCallback everywhere, stable React keys, secrets module, no console.log
- Extracted sub-components, <50 lines each

## Backlog
### P1
- [ ] Connect real Fyers API (user adds keys)
- [ ] Connect Screener.in for real fundamentals
- [ ] Train ML models on historical signal outcomes
### P2
- [ ] Monthly returns heatmap calendar
- [ ] Expandable signal rows in Command Center
