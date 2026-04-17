import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, TrendingDown, Activity, RefreshCw } from 'lucide-react';
import { useMarketData } from '../hooks/useMarketData';

const CommandCenter = () => {
  const navigate = useNavigate();
  const { loading, fetchMarketRegime, fetchTopSignals, runScanner } = useMarketData();
  
  const [marketRegime, setMarketRegime] = useState(null);
  const [signals, setSignals] = useState([]);
  const [timeframe, setTimeframe] = useState('swing');
  const [scanning, setScanning] = useState(false);
  
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    const regimeData = await fetchMarketRegime();
    if (regimeData?.success) {
      setMarketRegime(regimeData.data);
    }
    
    const signalsData = await fetchTopSignals(timeframe);
    if (signalsData?.success) {
      setSignals(signalsData.signals || []);
    }
  };
  
  const handleScan = async () => {
    setScanning(true);
    await runScanner(timeframe);
    await loadData();
    setScanning(false);
  };
  
  const getRegimeColor = (regime) => {
    if (!regime) return 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20';
    if (regime.includes('BULL')) return 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/20';
    if (regime.includes('BEAR')) return 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20';
    return 'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20';
  };
  
  return (
    <div className="p-4 md:p-6" data-testid="command-center">
      <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4 mb-4" data-testid="header-bar">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-6">
            <div>
              <span className="text-[10px] font-mono uppercase text-[#6B7280]">Market Regime</span>
              <div className={`mt-1 px-1.5 py-0.5 rounded-sm text-[10px] font-mono uppercase border inline-block ${getRegimeColor(marketRegime?.regime)}`} data-testid="market-regime-badge">
                {marketRegime?.regime || 'LOADING...'}
              </div>
            </div>
            
            <div>
              <span className="text-[10px] font-mono uppercase text-[#6B7280]">Nifty 50</span>
              <div className="mt-1 text-lg font-mono font-medium text-[#F9FAFB]" data-testid="nifty-price">
                {marketRegime?.nifty_price?.toFixed(2) || '-'}
              </div>
            </div>
            
            <div>
              <span className="text-[10px] font-mono uppercase text-[#6B7280]">India VIX</span>
              <div className="mt-1 text-lg font-mono font-medium text-[#F9FAFB]" data-testid="vix-value">
                {marketRegime?.vix?.toFixed(2) || '-'}
              </div>
            </div>
            
            <div>
              <span className="text-[10px] font-mono uppercase text-[#6B7280]">FII Flow (5D)</span>
              <div className={`mt-1 text-lg font-mono font-medium ${marketRegime?.fii_flow_5d >= 0 ? 'text-[#10B981]' : 'text-[#EF4444]'}`} data-testid="fii-flow">
                ₹{marketRegime?.fii_flow_5d?.toFixed(0) || '0'} Cr
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-3">
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-[#F9FAFB]" data-testid="signals-title">Top 10 Signals</h2>
              
              <div className="flex items-center gap-2">
                <select
                  value={timeframe}
                  onChange={(e) => setTimeframe(e.target.value)}
                  className="bg-[#0A0E1A] border border-[#1F2937] rounded-sm px-2 py-1.5 text-sm text-[#F9FAFB] focus:outline-none focus:border-[#3B82F6] focus:ring-1 focus:ring-[#3B82F6]"
                  data-testid="timeframe-selector"
                >
                  <option value="intraday">Intraday</option>
                  <option value="swing">Swing</option>
                  <option value="positional">Positional</option>
                </select>
                
                <button
                  onClick={handleScan}
                  disabled={scanning || loading}
                  className="bg-[#3B82F6] text-white hover:bg-[#3B82F6]/90 px-3 py-1.5 text-sm font-medium rounded-sm transition-colors flex items-center gap-2 disabled:opacity-50"
                  data-testid="run-scan-button"
                >
                  <RefreshCw size={14} className={scanning ? 'animate-spin' : ''} />
                  {scanning ? 'Scanning...' : 'Run Scan'}
                </button>
              </div>
            </div>
            
            <div className="w-full overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#1F2937]">
                    <th className="text-left pb-2 text-[10px] font-mono uppercase text-[#6B7280]">Rank</th>
                    <th className="text-left pb-2 text-[10px] font-mono uppercase text-[#6B7280]">Ticker</th>
                    <th className="text-left pb-2 text-[10px] font-mono uppercase text-[#6B7280]">Strategy</th>
                    <th className="text-right pb-2 text-[10px] font-mono uppercase text-[#6B7280]">Entry Zone</th>
                    <th className="text-right pb-2 text-[10px] font-mono uppercase text-[#6B7280]">Target 1</th>
                    <th className="text-right pb-2 text-[10px] font-mono uppercase text-[#6B7280]">Stop Loss</th>
                    <th className="text-right pb-2 text-[10px] font-mono uppercase text-[#6B7280]">R:R</th>
                    <th className="text-right pb-2 text-[10px] font-mono uppercase text-[#6B7280]">Confidence</th>
                    <th className="text-left pb-2 text-[10px] font-mono uppercase text-[#6B7280]">Hold</th>
                  </tr>
                </thead>
                <tbody>
                  {signals.length === 0 ? (
                    <tr>
                      <td colSpan="9" className="text-center py-8 text-[#6B7280]">
                        {loading ? 'Loading signals...' : 'No signals found. Run scanner to generate signals.'}
                      </td>
                    </tr>
                  ) : (
                    signals.map((signal, idx) => (
                      <tr
                        key={idx}
                        className="border-b border-[#1F2937]/50 hover:bg-[#1F2937]/30 transition-colors cursor-pointer"
                        onClick={() => navigate(`/deep-dive?ticker=${signal.ticker}`)}
                        data-testid={`signal-row-${idx}`}
                      >
                        <td className="py-2 px-1 text-sm text-[#F9FAFB] font-mono">{signal.rank || idx + 1}</td>
                        <td className="py-2 px-1 text-sm text-[#F9FAFB] font-mono font-medium">{signal.ticker}</td>
                        <td className="py-2 px-1 text-sm text-[#9CA3AF]">{signal.strategy}</td>
                        <td className="py-2 px-1 text-sm text-[#F9FAFB] font-mono text-right">₹{signal.entry_zone?.toFixed(2)}</td>
                        <td className="py-2 px-1 text-sm text-[#10B981] font-mono text-right">₹{signal.target_1?.toFixed(2)}</td>
                        <td className="py-2 px-1 text-sm text-[#EF4444] font-mono text-right">₹{signal.stop_loss?.toFixed(2)}</td>
                        <td className="py-2 px-1 text-sm text-[#F9FAFB] font-mono text-right">{signal.risk_reward_ratio?.toFixed(1)}</td>
                        <td className="py-2 px-1 text-right">
                          <span className="text-sm font-mono text-[#F9FAFB]">{signal.confidence || 0}%</span>
                        </td>
                        <td className="py-2 px-1 text-sm text-[#9CA3AF]">{signal.expected_hold}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <div className="space-y-4">
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h3 className="text-base font-medium text-[#F9FAFB] mb-3">Regime Details</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-[#9CA3AF]">EMA 200</span>
                <span className="text-[#F9FAFB] font-mono">{marketRegime?.ema_200?.toFixed(2) || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#9CA3AF]">Price vs EMA</span>
                <span className={`font-mono ${marketRegime?.nifty_price > marketRegime?.ema_200 ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                  {marketRegime?.nifty_price && marketRegime?.ema_200 ? (marketRegime.nifty_price > marketRegime.ema_200 ? 'Above' : 'Below') : '-'}
                </span>
              </div>
            </div>
          </div>
          
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h3 className="text-base font-medium text-[#F9FAFB] mb-3">Quick Stats</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-[#9CA3AF]">Active Signals</span>
                <span className="text-[#F9FAFB] font-mono">{signals.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#9CA3AF]">Timeframe</span>
                <span className="text-[#F9FAFB] font-mono uppercase text-xs">{timeframe}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommandCenter;