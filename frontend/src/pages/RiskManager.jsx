import React, { useState, useEffect } from 'react';
import { useMarketData } from '../hooks/useMarketData';

const RiskManager = () => {
  const { calculateRisk } = useMarketData();
  const [capital, setCapital] = useState(100000);
  const [entryPrice, setEntryPrice] = useState(1000);
  const [stopLoss, setStopLoss] = useState(950);
  const [riskPercent, setRiskPercent] = useState(2);
  const [results, setResults] = useState(null);
  
  useEffect(() => {
    handleCalculate();
  }, [capital, entryPrice, stopLoss, riskPercent]);
  
  const handleCalculate = async () => {
    const data = await calculateRisk({
      capital,
      entry_price: entryPrice,
      stop_loss: stopLoss,
      risk_percent: riskPercent,
      win_rate: 0.55,
      avg_win: 5.0,
      avg_loss: 3.0
    });
    
    if (data?.success) {
      setResults(data);
    }
  };
  
  return (
    <div className="p-4 md:p-6" data-testid="risk-manager">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-[#F9FAFB]">Risk Manager</h1>
        <p className="text-sm text-[#9CA3AF] mt-1">Position sizing and risk calculation</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
          <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">Input Parameters</h2>
          
          <div className="space-y-4">
            <div>
              <label className="text-[10px] font-mono uppercase text-[#6B7280] mb-2 block">Capital (₹)</label>
              <input
                type="number"
                value={capital}
                onChange={(e) => setCapital(Number(e.target.value))}
                className="w-full bg-[#0A0E1A] border border-[#1F2937] rounded-sm px-2 py-1.5 text-sm text-[#F9FAFB] focus:outline-none focus:border-[#3B82F6]"
                data-testid="capital-input"
              />
            </div>
            
            <div>
              <label className="text-[10px] font-mono uppercase text-[#6B7280] mb-2 block">Entry Price (₹)</label>
              <input
                type="number"
                value={entryPrice}
                onChange={(e) => setEntryPrice(Number(e.target.value))}
                className="w-full bg-[#0A0E1A] border border-[#1F2937] rounded-sm px-2 py-1.5 text-sm text-[#F9FAFB] focus:outline-none focus:border-[#3B82F6]"
                data-testid="entry-price-input"
              />
            </div>
            
            <div>
              <label className="text-[10px] font-mono uppercase text-[#6B7280] mb-2 block">Stop Loss (₹)</label>
              <input
                type="number"
                value={stopLoss}
                onChange={(e) => setStopLoss(Number(e.target.value))}
                className="w-full bg-[#0A0E1A] border border-[#1F2937] rounded-sm px-2 py-1.5 text-sm text-[#F9FAFB] focus:outline-none focus:border-[#3B82F6]"
                data-testid="stop-loss-input"
              />
            </div>
            
            <div>
              <label className="text-[10px] font-mono uppercase text-[#6B7280] mb-2 block">Risk Per Trade (%)</label>
              <input
                type="range"
                min="0.5"
                max="5"
                step="0.5"
                value={riskPercent}
                onChange={(e) => setRiskPercent(Number(e.target.value))}
                className="w-full h-1 bg-[#1F2937] rounded-sm appearance-none accent-[#3B82F6]"
                data-testid="risk-slider"
              />
              <div className="text-sm text-[#F9FAFB] font-mono mt-1">{riskPercent}%</div>
            </div>
          </div>
        </div>
        
        <div className="space-y-4">
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">Fixed Fractional</h2>
            {results?.fixed_fractional && (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-[#9CA3AF]">Position Size</span>
                  <span className="text-sm text-[#F9FAFB] font-mono" data-testid="ff-shares">{results.fixed_fractional.shares} shares</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#9CA3AF]">Position Value</span>
                  <span className="text-sm text-[#F9FAFB] font-mono">₹{results.fixed_fractional.position_value?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#9CA3AF]">Capital at Risk</span>
                  <span className="text-sm text-[#EF4444] font-mono">₹{results.fixed_fractional.capital_at_risk?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#9CA3AF]">Max Loss</span>
                  <span className="text-sm text-[#EF4444] font-mono">₹{results.fixed_fractional.max_loss?.toFixed(2)}</span>
                </div>
              </div>
            )}
          </div>
          
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">Kelly Criterion</h2>
            {results?.kelly_criterion && (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-[#9CA3AF]">Full Kelly</span>
                  <span className="text-sm text-[#F9FAFB] font-mono">{results.kelly_criterion.kelly_full?.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#9CA3AF]">Half Kelly (Recommended)</span>
                  <span className="text-sm text-[#10B981] font-mono" data-testid="half-kelly">{results.kelly_criterion.kelly_half?.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#9CA3AF]">Position Size</span>
                  <span className="text-sm text-[#F9FAFB] font-mono">{results.kelly_criterion.shares} shares</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#9CA3AF]">Position Value</span>
                  <span className="text-sm text-[#F9FAFB] font-mono">₹{results.kelly_criterion.position_value?.toFixed(2)}</span>
                </div>
              </div>
            )}
          </div>
          
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">Recommendation</h2>
            {results?.recommendations && (
              <div>
                <div className="text-sm text-[#10B981] font-medium mb-2">
                  {results.recommendations.recommended_method}
                </div>
                <div className="text-xs text-[#9CA3AF]">
                  {results.recommendations.reasoning}
                </div>
                <div className="mt-3 pt-3 border-t border-[#1F2937]">
                  <div className="flex justify-between text-sm">
                    <span className="text-[#9CA3AF]">Max Positions</span>
                    <span className="text-[#F9FAFB] font-mono">{results.recommendations.max_positions}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskManager;