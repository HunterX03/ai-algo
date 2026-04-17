import React, { useState, useEffect, useCallback } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SectorHeatmap = ({ sectors }) => {
  const getColor = (prob) => prob > 60 ? '#10B981' : prob > 45 ? '#F59E0B' : '#EF4444';
  return (
    <div className="grid grid-cols-5 gap-1" data-testid="sector-heatmap">
      {sectors.map(s => (
        <div key={s.sector} className="p-2 rounded-sm text-center border border-[#1F2937]"
          style={{ backgroundColor: `${getColor(s.probability)}15` }}>
          <div className="text-[10px] font-mono text-[#9CA3AF]">{s.sector}</div>
          <div className="text-sm font-mono font-medium" style={{ color: getColor(s.probability) }}>
            {s.probability}%
          </div>
        </div>
      ))}
    </div>
  );
};

const PairCard = ({ pair }) => (
  <div className="bg-[#0A0E1A] border border-[#1F2937] rounded-sm p-3" data-testid={`pair-${pair.pair}`}>
    <div className="flex justify-between items-center mb-2">
      <span className="text-sm font-mono font-medium text-[#F9FAFB]">{pair.pair}</span>
      <span className={`px-1.5 py-0.5 rounded-sm text-[10px] font-mono uppercase border ${
        pair.signal.includes('LONG_A') ? 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/20' :
        pair.signal.includes('SHORT_A') ? 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20' :
        'bg-[#1F2937] text-[#9CA3AF] border-[#374151]'
      }`}>{pair.signal.replace(/_/g, ' ')}</span>
    </div>
    <div className="grid grid-cols-3 gap-2 text-xs">
      <div><span className="text-[#6B7280]">Z-Score</span><div className="font-mono text-[#F9FAFB]">{pair.z_score}</div></div>
      <div><span className="text-[#6B7280]">Hedge</span><div className="font-mono text-[#F9FAFB]">{pair.hedge_ratio}</div></div>
      <div><span className="text-[#6B7280]">Conf</span><div className="font-mono text-[#F9FAFB]">{pair.confidence}%</div></div>
    </div>
    <div className="text-xs text-[#6B7280] mt-2">{pair.description}</div>
  </div>
);

const FactorBar = ({ name, value }) => (
  <div className="flex items-center gap-2">
    <span className="text-xs text-[#9CA3AF] w-16">{name}</span>
    <div className="flex-1 h-2 bg-[#1F2937] rounded-sm overflow-hidden">
      <div className="h-full rounded-sm transition-all" style={{
        width: `${value}%`,
        backgroundColor: value > 70 ? '#10B981' : value > 40 ? '#3B82F6' : '#EF4444'
      }} />
    </div>
    <span className="text-xs font-mono text-[#F9FAFB] w-8">{value}</span>
  </div>
);

const QuantEngine = () => {
  const [activeTab, setActiveTab] = useState('factors');
  const [factorData, setFactorData] = useState([]);
  const [pairsData, setPairsData] = useState([]);
  const [optionsData, setOptionsData] = useState(null);
  const [orderFlowData, setOrderFlowData] = useState(null);
  const [volData, setVolData] = useState(null);
  const [sectorData, setSectorData] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState('RELIANCE');
  const [loading, setLoading] = useState(false);

  const FNO_TICKERS = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'SBIN', 'BAJFINANCE'];

  const loadTab = useCallback(async (tab) => {
    setLoading(true);
    try {
      if (tab === 'factors') {
        const [res, sectorRes] = await Promise.all([
          axios.get(`${API}/quant/factor-scores?regime=SIDEWAYS`),
          axios.get(`${API}/ml/sector-rotation`),
        ]);
        if (res.data?.success) setFactorData(res.data.rankings);
        if (sectorRes.data?.success) setSectorData(sectorRes.data.sectors);
      } else if (tab === 'pairs') {
        const res = await axios.get(`${API}/quant/pairs`);
        if (res.data?.success) setPairsData(res.data.pairs);
      } else if (tab === 'options') {
        const res = await axios.get(`${API}/quant/options-flow?ticker=${selectedTicker}`);
        if (res.data?.success) setOptionsData(res.data.data);
      } else if (tab === 'orderflow') {
        const res = await axios.get(`${API}/quant/order-flow/${selectedTicker}`);
        if (res.data?.success) setOrderFlowData(res.data.data);
      } else if (tab === 'volsurface') {
        const res = await axios.get(`${API}/quant/vol-surface/${selectedTicker}`);
        if (res.data?.success) setVolData(res.data.data);
      }
    } catch { /* handled gracefully */ }
    setLoading(false);
  }, [selectedTicker]);

  useEffect(() => { loadTab(activeTab); }, [activeTab, loadTab]);

  const tabs = [
    { id: 'factors', label: 'Factor Model' },
    { id: 'pairs', label: 'Pairs Trading' },
    { id: 'options', label: 'Options Flow' },
    { id: 'orderflow', label: 'Order Flow' },
    { id: 'volsurface', label: 'Vol Surface' },
  ];

  return (
    <div className="p-4 md:p-6" data-testid="quant-engine">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-[#F9FAFB]">Quant Engine</h1>
        <p className="text-sm text-[#9CA3AF] mt-1">Institutional-grade quantitative analysis modules</p>
      </div>

      <div className="flex gap-2 mb-4 overflow-x-auto">
        {tabs.map(t => (
          <button key={t.id} onClick={() => setActiveTab(t.id)} data-testid={`tab-${t.id}`}
            className={`px-3 py-1.5 text-sm font-medium rounded-sm transition-colors whitespace-nowrap ${
              activeTab === t.id ? 'bg-[#3B82F6] text-white' : 'bg-[#1F2937] text-[#9CA3AF] hover:text-[#F9FAFB]'
            }`}>{t.label}</button>
        ))}
      </div>

      {/* TIER 1: Factor Model */}
      {activeTab === 'factors' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">Multi-Factor Rankings</h2>
            {factorData.length === 0 ? (
              <p className="text-[#6B7280] text-center py-8">Loading factor scores...</p>
            ) : (
              <div className="space-y-3">
                {factorData.slice(0, 10).map(stock => (
                  <div key={stock.ticker} className="bg-[#0A0E1A] border border-[#1F2937] rounded-sm p-3">
                    <div className="flex justify-between items-center mb-2">
                      <div className="flex items-center gap-3">
                        <span className="text-[10px] font-mono text-[#6B7280]">#{stock.rank}</span>
                        <span className="text-sm font-mono font-medium text-[#F9FAFB]">{stock.ticker}</span>
                        <span className="text-[10px] font-mono text-[#6B7280] uppercase">{stock.sector}</span>
                      </div>
                      <span className="text-lg font-mono font-medium text-[#3B82F6]">{stock.composite_score}</span>
                    </div>
                    <div className="space-y-1">
                      <FactorBar name="Value" value={stock.factors.value} />
                      <FactorBar name="Momentum" value={stock.factors.momentum} />
                      <FactorBar name="Quality" value={stock.factors.quality} />
                      <FactorBar name="Low Vol" value={stock.factors.low_vol} />
                      <FactorBar name="Size" value={stock.factors.size} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="space-y-4">
            <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
              <h3 className="text-base font-medium text-[#F9FAFB] mb-3">Sector Momentum ML</h3>
              <SectorHeatmap sectors={sectorData} />
            </div>
          </div>
        </div>
      )}

      {/* TIER 2: Pairs Trading */}
      {activeTab === 'pairs' && (
        <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
          <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">Statistical Pairs Trading</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {pairsData.map(p => <PairCard key={p.pair} pair={p} />)}
          </div>
        </div>
      )}

      {/* TIER 3: Options Flow */}
      {activeTab === 'options' && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <select value={selectedTicker} onChange={e => { setSelectedTicker(e.target.value); loadTab('options'); }}
              className="bg-[#0A0E1A] border border-[#1F2937] rounded-sm px-2 py-1.5 text-sm text-[#F9FAFB]" data-testid="options-ticker">
              {FNO_TICKERS.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          {optionsData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
                <h3 className="text-base font-medium text-[#F9FAFB] mb-3">Options Overview</h3>
                <div className="space-y-2 text-sm">
                  {[
                    { l: 'Put/Call Ratio', v: optionsData.put_call_ratio, c: optionsData.put_call_ratio > 1 ? 'text-[#10B981]' : 'text-[#EF4444]' },
                    { l: 'IV Rank', v: `${optionsData.iv_rank}%` },
                    { l: 'Max Pain', v: `₹${optionsData.max_pain_strike}` },
                    { l: 'Signal', v: optionsData.signal, c: optionsData.signal === 'BULLISH' ? 'text-[#10B981]' : optionsData.signal === 'BEARISH' ? 'text-[#EF4444]' : 'text-[#F59E0B]' },
                  ].map(r => (
                    <div key={r.l} className="flex justify-between">
                      <span className="text-[#9CA3AF]">{r.l}</span>
                      <span className={`font-mono ${r.c || 'text-[#F9FAFB]'}`}>{r.v}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
                <h3 className="text-base font-medium text-[#F9FAFB] mb-3">Unusual Activity</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span className="text-[#9CA3AF]">Unusual Call Strikes</span><span className="text-[#F9FAFB] font-mono">{optionsData.unusual_activity?.unusual_call_strikes}</span></div>
                  <div className="flex justify-between"><span className="text-[#9CA3AF]">Unusual Put Strikes</span><span className="text-[#F9FAFB] font-mono">{optionsData.unusual_activity?.unusual_put_strikes}</span></div>
                  <div className="flex justify-between"><span className="text-[#9CA3AF]">Total Unusual</span><span className="text-[#F9FAFB] font-mono">{optionsData.unusual_activity?.total_unusual_trades}</span></div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TIER 4: Order Flow */}
      {activeTab === 'orderflow' && (
        <div className="space-y-4">
          <select value={selectedTicker} onChange={e => { setSelectedTicker(e.target.value); loadTab('orderflow'); }}
            className="bg-[#0A0E1A] border border-[#1F2937] rounded-sm px-2 py-1.5 text-sm text-[#F9FAFB]">
            {FNO_TICKERS.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
          {orderFlowData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
                <h3 className="text-base font-medium text-[#F9FAFB] mb-3">Order Flow Imbalance</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={[
                    { name: 'Buy', value: orderFlowData.buy_pct, fill: '#10B981' },
                    { name: 'Sell', value: orderFlowData.sell_pct, fill: '#EF4444' },
                  ]}>
                    <XAxis dataKey="name" stroke="#6B7280" />
                    <YAxis stroke="#6B7280" />
                    <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #1F2937' }} />
                    <Bar dataKey="value">
                      {[{ fill: '#10B981' }, { fill: '#EF4444' }].map((entry, i) => (
                        <Cell key={i} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
                <h3 className="text-base font-medium text-[#F9FAFB] mb-3">Flow Metrics</h3>
                <div className="space-y-2 text-sm">
                  {[
                    { l: 'Signal', v: orderFlowData.signal, c: orderFlowData.signal?.includes('BUY') ? 'text-[#10B981]' : orderFlowData.signal?.includes('SELL') ? 'text-[#EF4444]' : 'text-[#F59E0B]' },
                    { l: 'Imbalance', v: orderFlowData.imbalance },
                    { l: 'Cumulative Delta', v: orderFlowData.cumulative_delta?.toLocaleString() },
                    { l: 'Large Buys', v: orderFlowData.large_buys },
                    { l: 'Large Sells', v: orderFlowData.large_sells },
                    { l: 'Delta Intensity', v: `${orderFlowData.delta_intensity}%` },
                  ].map(r => (
                    <div key={r.l} className="flex justify-between">
                      <span className="text-[#9CA3AF]">{r.l}</span>
                      <span className={`font-mono ${r.c || 'text-[#F9FAFB]'}`}>{r.v}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-3 pt-3 border-t border-[#1F2937] text-xs text-[#9CA3AF]">{orderFlowData.description}</div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TIER 5: Volatility Surface */}
      {activeTab === 'volsurface' && (
        <div className="space-y-4">
          <select value={selectedTicker} onChange={e => { setSelectedTicker(e.target.value); loadTab('volsurface'); }}
            className="bg-[#0A0E1A] border border-[#1F2937] rounded-sm px-2 py-1.5 text-sm text-[#F9FAFB]">
            {FNO_TICKERS.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
          {volData && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2 bg-[#111827] border border-[#1F2937] rounded-sm p-4">
                <h3 className="text-base font-medium text-[#F9FAFB] mb-3">IV Surface</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={volData.surface_data?.map(s => ({
                    strike: s.strike, call_iv: s.call_iv, put_iv: s.put_iv,
                  }))}>
                    <XAxis dataKey="strike" stroke="#6B7280" fontSize={10} />
                    <YAxis stroke="#6B7280" />
                    <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #1F2937' }} />
                    <Bar dataKey="call_iv" fill="#3B82F6" name="Call IV" />
                    <Bar dataKey="put_iv" fill="#F59E0B" name="Put IV" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
                <h3 className="text-base font-medium text-[#F9FAFB] mb-3">Vol Analysis</h3>
                <div className="space-y-2 text-sm">
                  {[
                    { l: 'ATM IV', v: `${volData.atm_iv}%` },
                    { l: 'Realized Vol 30D', v: `${volData.realized_vol_30d}%` },
                    { l: 'IV-RV Divergence', v: `${volData.iv_rv_divergence}%`, c: volData.iv_rv_divergence > 0 ? 'text-[#EF4444]' : 'text-[#10B981]' },
                    { l: 'IV Skew', v: `${volData.iv_skew}%` },
                    { l: 'Term Structure', v: `${volData.iv_term_structure}%` },
                    { l: 'Vol Regime', v: volData.vol_regime, c: volData.vol_regime === 'IV_PREMIUM' ? 'text-[#EF4444]' : volData.vol_regime === 'IV_DISCOUNT' ? 'text-[#10B981]' : 'text-[#F59E0B]' },
                  ].map(r => (
                    <div key={r.l} className="flex justify-between">
                      <span className="text-[#9CA3AF]">{r.l}</span>
                      <span className={`font-mono ${r.c || 'text-[#F9FAFB]'}`}>{r.v}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-3 pt-3 border-t border-[#1F2937] text-xs text-[#10B981]">{volData.edge_description}</div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default QuantEngine;
