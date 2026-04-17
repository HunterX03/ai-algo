import React, { useState, useEffect, useCallback } from 'react';
import { useMarketData } from '../hooks/useMarketData';

const StrategyLab = () => {
  const { fetchStrategies } = useMarketData();
  const [strategies, setStrategies] = useState([]);
  const [enabled, setEnabled] = useState({});

  const loadStrategies = useCallback(async () => {
    const data = await fetchStrategies();
    if (data?.success) {
      setStrategies(data.strategies);
      const state = {};
      data.strategies.forEach(s => { state[s.name] = true; });
      setEnabled(state);
    }
  }, [fetchStrategies]);

  useEffect(() => { loadStrategies(); }, [loadStrategies]);

  const toggleStrategy = (name) => {
    setEnabled(prev => ({ ...prev, [name]: !prev[name] }));
  };

  return (
    <div className="p-4 md:p-6" data-testid="strategy-lab">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-[#F9FAFB]">Strategy Lab</h1>
        <p className="text-sm text-[#9CA3AF] mt-1">Configure and manage trading strategies</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {strategies.map((strategy) => (
          <div key={strategy.name} className="bg-[#111827] border border-[#1F2937] rounded-sm p-4 hover:border-[#3B82F6]/50 transition-colors" data-testid={`strategy-card-${strategy.name}`}>
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h3 className="text-base font-medium text-[#F9FAFB]">{strategy.name}</h3>
                <span className="text-[10px] font-mono uppercase text-[#6B7280] mt-1 inline-block">{strategy.timeframe}</span>
              </div>
              <button onClick={() => toggleStrategy(strategy.name)}
                className={`w-10 h-6 rounded-full transition-colors flex items-center ${enabled[strategy.name] ? 'bg-[#10B981]' : 'bg-[#1F2937]'}`}
                data-testid={`strategy-toggle-${strategy.name}`}>
                <div className={`w-4 h-4 bg-white rounded-full transition-transform ${enabled[strategy.name] ? 'translate-x-5' : 'translate-x-1'}`} />
              </button>
            </div>
            <p className="text-sm text-[#9CA3AF] mb-4">{strategy.description}</p>
            <div className="grid grid-cols-2 gap-3 pt-3 border-t border-[#1F2937]">
              <div><span className="text-[10px] font-mono uppercase text-[#6B7280]">Win Rate</span><div className="text-base font-mono font-medium text-[#F9FAFB] mt-1">{strategy.win_rate}%</div></div>
              <div><span className="text-[10px] font-mono uppercase text-[#6B7280]">Avg R:R</span><div className="text-base font-mono font-medium text-[#F9FAFB] mt-1">{strategy.avg_rr}</div></div>
              <div className="col-span-2"><span className="text-[10px] font-mono uppercase text-[#6B7280]">Best Regime</span><div className="text-sm text-[#F9FAFB] mt-1">{strategy.best_regime?.replace('_', ' ')}</div></div>
            </div>
            <button className="mt-4 w-full bg-[#1F2937] text-[#F9FAFB] hover:bg-[#374151] px-3 py-1.5 text-sm font-medium rounded-sm transition-colors" data-testid={`backtest-button-${strategy.name}`}>Run Backtest</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StrategyLab;
