# JPM-SwingEdge Pro - Product Requirements Document

## Original Problem Statement
Build a full-stack quantitative trading dashboard for Indian stock markets (NSE). Signal generation platform — no automated execution, manual trading only.

## Architecture
- **Backend**: FastAPI (Python) + MongoDB
- **Frontend**: React + TailwindCSS + TradingView Lightweight Charts
- **ML**: scikit-learn, XGBoost, hmmlearn (9 models)
- **Real-time**: WebSocket between FastAPI and React
- **Data**: Fyers API (with mock fallback), SERP API for news

## What's Implemented (April 2026)
### Backend - 20+ API Endpoints
- Market regime, signals, scanner, backtest, sentiment, risk, strategies, intraday, websocket
- 9 ML endpoints: regime probabilities, dynamic weights, quality classifier, exit predictor, volume anomaly, news impact, sector rotation, pattern recognition, earnings predictor
### Frontend - 7 Pages
- Command Center, Stock Deep Dive, Strategy Lab, Backtest Suite, Risk Manager, Sentiment Hub, Intraday Monitor
### Code Quality
- XSS-safe (useRef, no innerHTML), useCallback for all hooks, stable React keys
- secrets module (no predictable random), no console.log in production
- Extracted sub-components for maintainability

## Prioritized Backlog
### P1 - Connect real data
- [ ] Fyers API live data (user adds keys)
- [ ] SERP API live news
- [ ] Train ML models on real historical data
### P2 - UI Enhancements
- [ ] Sector heatmap, FII/DII flow chart
- [ ] Monthly returns heatmap calendar in Backtest Suite
- [ ] Expandable signal rows, OI buildup charts
