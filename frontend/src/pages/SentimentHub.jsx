import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { useMarketData } from '../hooks/useMarketData';

const SentimentHub = () => {
  const { fetchSentiment, fetchMarketRegime } = useMarketData();
  const [selectedTicker, setSelectedTicker] = useState('RELIANCE');
  const [sentiment, setSentiment] = useState(null);
  const [marketRegime, setMarketRegime] = useState(null);
  
  const tickers = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'ITC', 'SBIN'];
  
  useEffect(() => {
    loadSentiment();
    loadRegime();
  }, [selectedTicker]);
  
  const loadSentiment = async () => {
    const data = await fetchSentiment(selectedTicker);
    if (data?.success) {
      setSentiment(data.data);
    }
  };
  
  const loadRegime = async () => {
    const data = await fetchMarketRegime();
    if (data?.success) {
      setMarketRegime(data.data);
    }
  };
  
  const getSentimentIcon = (label) => {
    if (label === 'positive') return <TrendingUp size={16} className="text-[#10B981]" />;
    if (label === 'negative') return <TrendingDown size={16} className="text-[#EF4444]" />;
    return <Minus size={16} className="text-[#F59E0B]" />;
  };
  
  return (
    <div className="p-4 md:p-6" data-testid="sentiment-hub">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-[#F9FAFB]">Sentiment Hub</h1>
        <p className="text-sm text-[#9CA3AF] mt-1">News and market sentiment analysis</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-[#F9FAFB]">Stock Sentiment</h2>
              <select
                value={selectedTicker}
                onChange={(e) => setSelectedTicker(e.target.value)}
                className="bg-[#0A0E1A] border border-[#1F2937] rounded-sm px-2 py-1.5 text-sm text-[#F9FAFB] focus:outline-none focus:border-[#3B82F6]"
                data-testid="ticker-selector"
              >
                {tickers.map(ticker => (
                  <option key={ticker} value={ticker}>{ticker}</option>
                ))}
              </select>
            </div>
            
            {sentiment && (
              <div>
                <div className="flex items-center gap-4 mb-4 pb-4 border-b border-[#1F2937]">
                  <div>
                    <span className="text-[10px] font-mono uppercase text-[#6B7280]">Overall Sentiment</span>
                    <div className={`mt-1 px-1.5 py-0.5 rounded-sm text-[10px] font-mono uppercase border inline-block ${
                      sentiment.sentiment_label === 'positive' ? 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/20' :
                      sentiment.sentiment_label === 'negative' ? 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20' :
                      'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20'
                    }`}>
                      {sentiment.sentiment_label}
                    </div>
                  </div>
                  
                  <div>
                    <span className="text-[10px] font-mono uppercase text-[#6B7280]">Sentiment Score</span>
                    <div className="mt-1 text-lg font-mono font-medium text-[#F9FAFB]">
                      {sentiment.overall_sentiment?.toFixed(2)}
                    </div>
                  </div>
                  
                  <div>
                    <span className="text-[10px] font-mono uppercase text-[#6B7280]">News Count</span>
                    <div className="mt-1 text-lg font-mono font-medium text-[#F9FAFB]">
                      {sentiment.news_count}
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <h3 className="text-base font-medium text-[#F9FAFB]">Recent Headlines</h3>
                  {sentiment.headlines?.map((news, idx) => (
                    <div key={idx} className="border-l-2 border-[#1F2937] pl-3 py-2 hover:border-[#3B82F6] transition-colors" data-testid={`news-${idx}`}>
                      <div className="flex items-start gap-2">
                        {getSentimentIcon(news.sentiment)}
                        <div className="flex-1">
                          <h4 className="text-sm text-[#F9FAFB] mb-1">{news.title}</h4>
                          <div className="flex items-center gap-3 text-xs text-[#6B7280]">
                            <span>{news.source}</span>
                            <span>•</span>
                            <span>{news.date ? new Date(news.date).toLocaleDateString() : 'Recent'}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
        
        <div className="space-y-4">
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h3 className="text-base font-medium text-[#F9FAFB] mb-3">Market Overview</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-[#9CA3AF]">Regime</span>
                <span className="text-[#F9FAFB] font-mono text-xs">{marketRegime?.regime || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#9CA3AF]">VIX</span>
                <span className="text-[#F9FAFB] font-mono">{marketRegime?.vix?.toFixed(2) || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#9CA3AF]">FII Flow</span>
                <span className={`font-mono ${marketRegime?.fii_flow_5d >= 0 ? 'text-[#10B981]' : 'text-[#EF4444]'}`}>
                  ₹{marketRegime?.fii_flow_5d?.toFixed(0) || '0'} Cr
                </span>
              </div>
            </div>
          </div>
          
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h3 className="text-base font-medium text-[#F9FAFB] mb-3">Sentiment Guide</h3>
            <div className="space-y-2 text-xs text-[#9CA3AF]">
              <div className="flex items-start gap-2">
                <TrendingUp size={14} className="text-[#10B981] mt-0.5" />
                <span>Positive sentiment indicates bullish news flow</span>
              </div>
              <div className="flex items-start gap-2">
                <TrendingDown size={14} className="text-[#EF4444] mt-0.5" />
                <span>Negative sentiment suggests bearish outlook</span>
              </div>
              <div className="flex items-start gap-2">
                <Minus size={14} className="text-[#F59E0B] mt-0.5" />
                <span>Neutral sentiment shows mixed signals</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SentimentHub;