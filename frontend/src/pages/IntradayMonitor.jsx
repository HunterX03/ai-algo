import React, { useState, useEffect } from 'react';
import { RefreshCw, Clock } from 'lucide-react';
import { useMarketData } from '../hooks/useMarketData';

const IntradayMonitor = () => {
  const { fetchTopSignals } = useMarketData();
  const [signals, setSignals] = useState([]);
  const [countdown, setCountdown] = useState(300);
  const [isMarketOpen, setIsMarketOpen] = useState(true);
  
  useEffect(() => {
    checkMarketHours();
    loadSignals();
    
    const interval = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          loadSignals();
          return 300;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  const checkMarketHours = () => {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const currentTime = hours * 60 + minutes;
    
    const marketOpen = 9 * 60 + 15;
    const marketClose = 15 * 60 + 30;
    
    setIsMarketOpen(currentTime >= marketOpen && currentTime <= marketClose);
  };
  
  const loadSignals = async () => {
    const data = await fetchTopSignals('intraday');
    if (data?.success) {
      setSignals(data.signals || []);
    }
  };
  
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  return (
    <div className="p-4 md:p-6" data-testid="intraday-monitor">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-[#F9FAFB]">Intraday Monitor</h1>
            <p className="text-sm text-[#9CA3AF] mt-1">Live intraday signals (9:15 AM - 3:30 PM IST)</p>
          </div>
          
          <div className="flex items-center gap-3">
            <div className={`px-3 py-1.5 rounded-sm text-[10px] font-mono uppercase border ${
              isMarketOpen
                ? 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/20'
                : 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20'
            }`}>
              {isMarketOpen ? 'Market Open' : 'Market Closed'}
            </div>
            
            <div className="flex items-center gap-2 bg-[#111827] border border-[#1F2937] rounded-sm px-3 py-1.5">
              <Clock size={14} className="text-[#9CA3AF]" />
              <span className="text-sm font-mono text-[#F9FAFB]" data-testid="countdown-timer">
                Next refresh: {formatTime(countdown)}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      {!isMarketOpen && (
        <div className="bg-[#EF4444]/10 border border-[#EF4444]/20 rounded-sm p-4 mb-4">
          <p className="text-sm text-[#EF4444]">
            Market is currently closed. Intraday signals are only generated during market hours (9:15 AM - 3:30 PM IST).
          </p>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {signals.length === 0 ? (
          <div className="col-span-full bg-[#111827] border border-[#1F2937] rounded-sm p-12 text-center">
            <RefreshCw size={32} className="text-[#6B7280] mx-auto mb-4" />
            <p className="text-[#6B7280]">
              {isMarketOpen ? 'Scanning for intraday signals...' : 'No active signals. Market is closed.'}
            </p>
          </div>
        ) : (
          signals.map((signal, idx) => (
            <div
              key={idx}
              className="bg-[#111827] border border-[#1F2937] rounded-sm p-4 hover:border-[#3B82F6]/50 transition-colors"
              data-testid={`intraday-signal-${idx}`}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-lg font-mono font-semibold text-[#F9FAFB]">{signal.ticker}</h3>
                  <span className="text-[10px] font-mono uppercase text-[#6B7280]">{signal.setup_type || signal.strategy}</span>
                </div>
                <div className={`px-1.5 py-0.5 rounded-sm text-[10px] font-mono uppercase border ${
                  signal.signal === 'BUY'
                    ? 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/20'
                    : 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20'
                }`}>
                  {signal.signal}
                </div>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-[#9CA3AF]">Entry</span>
                  <span className="text-[#F9FAFB] font-mono">₹{signal.entry_zone?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#9CA3AF]">Target</span>
                  <span className="text-[#10B981] font-mono">₹{signal.target_1?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#9CA3AF]">Stop Loss</span>
                  <span className="text-[#EF4444] font-mono">₹{signal.stop_loss?.toFixed(2)}</span>
                </div>
                <div className="flex justify-between pt-2 border-t border-[#1F2937]">
                  <span className="text-[#9CA3AF]">R:R Ratio</span>
                  <span className="text-[#F9FAFB] font-mono font-medium">{signal.risk_reward_ratio?.toFixed(1)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#9CA3AF]">Confidence</span>
                  <span className="text-[#F9FAFB] font-mono">{signal.confidence || 0}%</span>
                </div>
              </div>
              
              <div className="mt-3 pt-3 border-t border-[#1F2937]">
                <div className="text-xs text-[#6B7280]">
                  Expected Hold: {signal.expected_hold || '1-2 hours'}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default IntradayMonitor;