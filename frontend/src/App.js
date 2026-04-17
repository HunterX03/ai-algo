import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';
import Sidebar from './components/Sidebar';
import CommandCenter from './pages/CommandCenter';
import StockDeepDive from './pages/StockDeepDive';
import StrategyLab from './pages/StrategyLab';
import BacktestSuite from './pages/BacktestSuite';
import RiskManager from './pages/RiskManager';
import SentimentHub from './pages/SentimentHub';
import IntradayMonitor from './pages/IntradayMonitor';
import QuantEngine from './pages/QuantEngine';

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden bg-[#0A0E1A]" data-testid="app-container">
        <Sidebar />
        <main className="flex-1 overflow-y-auto" data-testid="main-content">
          <Routes>
            <Route path="/" element={<CommandCenter />} />
            <Route path="/deep-dive" element={<StockDeepDive />} />
            <Route path="/strategy-lab" element={<StrategyLab />} />
            <Route path="/backtest" element={<BacktestSuite />} />
            <Route path="/risk" element={<RiskManager />} />
            <Route path="/sentiment" element={<SentimentHub />} />
            <Route path="/intraday" element={<IntradayMonitor />} />
            <Route path="/quant" element={<QuantEngine />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;