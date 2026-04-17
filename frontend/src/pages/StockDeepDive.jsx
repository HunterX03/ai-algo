import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { createChart, CandlestickSeries } from 'lightweight-charts';
import { useMarketData } from '../hooks/useMarketData';

const StockDeepDive = () => {
  const [searchParams] = useSearchParams();
  const ticker = searchParams.get('ticker') || 'RELIANCE';
  
  const { loading, fetchStockDetail, fetchSentiment } = useMarketData();
  const [stockData, setStockData] = useState(null);
  const [sentiment, setSentiment] = useState(null);
  const [chartContainer, setChartContainer] = useState(null);
  
  useEffect(() => {
    loadStockData();
  }, [ticker]);
  
  useEffect(() => {
    if (stockData && chartContainer) {
      renderChart();
    }
  }, [stockData, chartContainer]);
  
  const loadStockData = async () => {
    const data = await fetchStockDetail(ticker);
    if (data?.success) {
      setStockData(data);
    }
    
    const sentimentData = await fetchSentiment(ticker);
    if (sentimentData?.success) {
      setSentiment(sentimentData.data);
    }
  };
  
  const renderChart = () => {
    if (!chartContainer || !stockData?.chart_data) return;
    
    chartContainer.innerHTML = '';
    
    const chart = createChart(chartContainer, {
      width: chartContainer.clientWidth,
      height: 400,
      layout: {
        background: { color: '#0A0E1A' },
        textColor: '#9CA3AF',
      },
      grid: {
        vertLines: { color: '#1F2937' },
        horzLines: { color: '#1F2937' },
      },
      timeScale: {
        borderColor: '#1F2937',
      },
      localization: {
        locale: 'en-US',
      },
    });
    
    // Use v5 API: addSeries with CandlestickSeries
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#10B981',
      downColor: '#EF4444',
      borderUpColor: '#10B981',
      borderDownColor: '#EF4444',
      wickUpColor: '#10B981',
      wickDownColor: '#EF4444',
    });
    
    candlestickSeries.setData(stockData.chart_data);
    
    chart.timeScale().fitContent();
  };
  
  return (
    <div className="p-4 md:p-6" data-testid="stock-deep-dive">
      <div className="mb-4">
        <h1 className="text-2xl font-semibold text-[#F9FAFB]" data-testid="stock-title">{ticker}</h1>
        <p className="text-sm text-[#9CA3AF] mt-1">Detailed Technical Analysis</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">Price Chart</h2>
            <div ref={setChartContainer} data-testid="chart-container" />
          </div>
          
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">Technical Indicators</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <span className="text-[10px] font-mono uppercase text-[#6B7280]">RSI</span>
                <div className="text-lg font-mono font-medium text-[#F9FAFB] mt-1" data-testid="rsi-value">
                  {stockData?.indicators?.rsi?.toFixed(2) || '-'}
                </div>
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase text-[#6B7280]">MACD</span>
                <div className="text-lg font-mono font-medium text-[#F9FAFB] mt-1">
                  {stockData?.indicators?.macd?.toFixed(2) || '-'}
                </div>
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase text-[#6B7280]">EMA 20</span>
                <div className="text-lg font-mono font-medium text-[#F9FAFB] mt-1">
                  {stockData?.indicators?.ema_20?.toFixed(2) || '-'}
                </div>
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase text-[#6B7280]">VWAP</span>
                <div className="text-lg font-mono font-medium text-[#F9FAFB] mt-1">
                  {stockData?.indicators?.vwap?.toFixed(2) || '-'}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="space-y-4">
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h3 className="text-base font-medium text-[#F9FAFB] mb-3">Price Levels</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-[#9CA3AF]">Current</span>
                <span className="text-[#F9FAFB] font-mono">₹{stockData?.current_price?.toFixed(2) || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#9CA3AF]">Resistance</span>
                <span className="text-[#EF4444] font-mono">₹{stockData?.resistance?.toFixed(2) || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[#9CA3AF]">Support</span>
                <span className="text-[#10B981] font-mono">₹{stockData?.support?.toFixed(2) || '-'}</span>
              </div>
            </div>
          </div>
          
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h3 className="text-base font-medium text-[#F9FAFB] mb-3">Sentiment</h3>
            {sentiment ? (
              <div>
                <div className={`px-1.5 py-0.5 rounded-sm text-[10px] font-mono uppercase border inline-block ${
                  sentiment.sentiment_label === 'positive' ? 'bg-[#10B981]/10 text-[#10B981] border-[#10B981]/20' :
                  sentiment.sentiment_label === 'negative' ? 'bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20' :
                  'bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20'
                }`}>
                  {sentiment.sentiment_label}
                </div>
                <div className="mt-3 space-y-2">
                  {sentiment.headlines?.slice(0, 3).map((news, idx) => (
                    <div key={idx} className="text-xs text-[#9CA3AF] border-l-2 border-[#1F2937] pl-2">
                      {news.title}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-sm text-[#6B7280]">Loading sentiment...</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockDeepDive;
