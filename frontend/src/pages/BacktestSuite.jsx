import React, { useState } from 'react';
import { useMarketData } from '../hooks/useMarketData';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

const BacktestSuite = () => {
  const { loading, runBacktest } = useMarketData();
  const [results, setResults] = useState(null);
  const [capital, setCapital] = useState(100000);
  const [strategy, setStrategy] = useState('BB_Squeeze');
  const [running, setRunning] = useState(false);
  
  const handleRunBacktest = async () => {
    setRunning(true);
    const data = await runBacktest(strategy, capital);
    if (data?.success) {
      setResults(data.results);
    }
    setRunning(false);
  };
  
  return (
    <div className="p-4 md:p-6" data-testid="backtest-suite">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-[#F9FAFB]">Backtest Suite</h1>
        <p className="text-sm text-[#9CA3AF] mt-1">Historical strategy performance analysis</p>
      </div>
      
      <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4 mb-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          <div>
            <label className="text-[10px] font-mono uppercase text-[#6B7280] mb-2 block">Strategy</label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full bg-[#0A0E1A] border border-[#1F2937] rounded-sm px-2 py-1.5 text-sm text-[#F9FAFB] focus:outline-none focus:border-[#3B82F6]"
              data-testid="strategy-selector"
            >
              <option value="BB_Squeeze">BB Squeeze</option>
              <option value="Momentum_Delivery">Momentum + Delivery</option>
              <option value="Quality_Momentum">Quality Momentum</option>
            </select>
          </div>
          
          <div>
            <label className="text-[10px] font-mono uppercase text-[#6B7280] mb-2 block">Capital</label>
            <input
              type="number"
              value={capital}
              onChange={(e) => setCapital(Number(e.target.value))}
              className="w-full bg-[#0A0E1A] border border-[#1F2937] rounded-sm px-2 py-1.5 text-sm text-[#F9FAFB] focus:outline-none focus:border-[#3B82F6]"
              data-testid="capital-input"
            />
          </div>
          
          <div className="md:col-span-2">
            <button
              onClick={handleRunBacktest}
              disabled={running}
              className="w-full bg-[#3B82F6] text-white hover:bg-[#3B82F6]/90 px-3 py-1.5 text-sm font-medium rounded-sm transition-colors disabled:opacity-50"
              data-testid="run-backtest-button"
            >
              {running ? 'Running...' : 'Run Backtest'}
            </button>
          </div>
        </div>
      </div>
      
      {results && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Return', value: `${results.metrics?.total_return?.toFixed(2)}%`, color: results.metrics?.total_return >= 0 ? 'text-[#10B981]' : 'text-[#EF4444]' },
              { label: 'Sharpe Ratio', value: results.metrics?.sharpe_ratio?.toFixed(2), color: 'text-[#F9FAFB]' },
              { label: 'Max Drawdown', value: `${results.metrics?.max_drawdown?.toFixed(2)}%`, color: 'text-[#EF4444]' },
              { label: 'Win Rate', value: `${results.metrics?.win_rate?.toFixed(1)}%`, color: 'text-[#F9FAFB]' },
            ].map((metric) => (
              <div key={metric.label} className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
                <span className="text-[10px] font-mono uppercase text-[#6B7280]">{metric.label}</span>
                <div className={`text-2xl font-mono font-medium mt-2 ${metric.color}`} data-testid={`metric-${metric.label}`}>
                  {metric.value}
                </div>
              </div>
            ))}
          </div>
          
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">Equity Curve</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={results.equity_curve?.map((val, idx) => ({ index: idx, value: val }))}>
                <XAxis dataKey="index" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #1F2937' }} />
                <Line type="monotone" dataKey="value" stroke="#3B82F6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">Recent Trades</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#1F2937]">
                    <th className="text-left pb-2 text-[10px] font-mono uppercase text-[#6B7280]">Ticker</th>
                    <th className="text-left pb-2 text-[10px] font-mono uppercase text-[#6B7280]">Signal</th>
                    <th className="text-right pb-2 text-[10px] font-mono uppercase text-[#6B7280]">Entry</th>
                    <th className="text-right pb-2 text-[10px] font-mono uppercase text-[#6B7280]">Exit</th>
                    <th className="text-right pb-2 text-[10px] font-mono uppercase text-[#6B7280]">P&L %</th>
                  </tr>
                </thead>
                <tbody>
                  {results.trades?.slice(0, 10).map((trade) => (
                    <tr key={`${trade.ticker}-${trade.entry_price}-${trade.pnl_pct}`} className="border-b border-[#1F2937]/50">
                      <td className="py-2 text-sm text-[#F9FAFB] font-mono">{trade.ticker}</td>
                      <td className="py-2 text-sm text-[#9CA3AF]">{trade.signal}</td>
                      <td className="py-2 text-sm text-[#F9FAFB] font-mono text-right">₹{trade.entry_price?.toFixed(2)}</td>
                      <td className="py-2 text-sm text-[#F9FAFB] font-mono text-right">₹{trade.exit_price?.toFixed(2)}</td>
                      <td className={`py-2 text-sm font-mono text-right ${trade.pnl_pct >= 0 ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                        {trade.pnl_pct >= 0 ? '+' : ''}{trade.pnl_pct?.toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
      
      {!results && (
        <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-12 text-center">
          <p className="text-[#6B7280]">Configure parameters and run backtest to see results</p>
        </div>
      )}
    </div>
  );
};

export default BacktestSuite;