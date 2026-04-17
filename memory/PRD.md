# JPM-SwingEdge Pro - Product Requirements Document

## Original Problem Statement
Build a full-stack quantitative trading dashboard for Indian stock markets (NSE). Signal generation platform — no automated execution, manual trading only.

## Architecture
- **Backend**: FastAPI (Python) + MongoDB
- **Frontend**: React + TailwindCSS + TradingView Lightweight Charts
- **Real-time**: WebSocket between FastAPI and React
- **Data**: Fyers API (with mock fallback), SERP API for news

## User Personas
- **Quantitative Traders**: Need signal generation, backtesting, risk management
- **Swing/Positional Traders**: NSE-focused, Indian market specific tools
- **Manual Traders**: Signal-only platform, no automated execution

## Core Requirements
- 7 dashboard pages with institutional-grade dark UI
- 13 trading strategies (5 intraday, 5 swing, 3 positional)
- Real-time market regime classification
- Position sizing (Fixed Fractional + Kelly Criterion)
- Backtesting engine with equity curves and metrics
- Sentiment analysis via news headlines
- WebSocket for live data streaming

## What's Been Implemented (April 2026)
### Backend
- All 11 API endpoints functional
- 13 trading strategies implemented
- Market regime classifier (Bull/Bear/Sideways)
- Composite signal scoring engine
- Risk manager (Fixed Fractional + Kelly Criterion)
- Backtesting engine
- Lightweight keyword-based sentiment analyzer
- Mock data layer for demo mode
- WebSocket endpoint for live updates

### Frontend
- 7 pages: Command Center, Stock Deep Dive, Strategy Lab, Backtest Suite, Risk Manager, Sentiment Hub, Intraday Monitor
- TradingView Lightweight Charts integration
- Zustand state management
- Dark institutional theme (IBM Plex fonts)
- Responsive layout with sidebar navigation

## Prioritized Backlog
### P0 (Critical)
- [x] All 13 strategies implemented
- [x] All API endpoints working
- [x] All 7 pages rendering
- [x] Mock data layer for demo mode

### P1 (High Priority)
- [ ] Connect real Fyers API (user adds credentials)
- [ ] Connect real SERP API for live news
- [ ] Add sector heatmap to Command Center
- [ ] Monthly returns heatmap in Backtest Suite
- [ ] FII/DII flow bar chart

### P2 (Medium Priority)
- [ ] Expandable signal rows in Command Center
- [ ] Fibonacci levels overlay toggle in Deep Dive
- [ ] OI buildup chart for F&O stocks
- [ ] Delivery percentage chart (30 days)
- [ ] Put/Call ratio gauge
- [ ] Market depth indicator

## Next Tasks
1. User adds Fyers API credentials → live data
2. User adds SERP API key → live news sentiment
3. Add sector heatmap visualization
4. Enhance backtest with monthly returns heatmap
5. Add comparison chart in Risk Manager
