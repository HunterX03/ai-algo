import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { createChart, CandlestickSeries } from 'lightweight-charts';
import { useMarketData } from '../hooks/useMarketData';

const IndicatorCard = ({ label, value, testId }) => (
  <div>
    <span className="text-[10px] font-mono uppercase text-[#6B7280]">{label}</span>
    <div className="text-lg font-mono font-medium text-[#F9FAFB] mt-1" data-testid={testId}>
      {value ?? '-'}
    </div>
  </div>
);

const PriceLevel = ({ label, value, color = 'text-[#F9FAFB]' }) => (
  <div className="flex justify-between">
    <span className="text-[#9CA3AF]">{label}</span>
    <span className={`${color} font-mono`}>{value != null ? `₹${value.toFixed(2)}` : '-'}</span>
  </div>
);

const StockDeepDive = () => {
  const [searchParams] = useSearchParams();
  const ticker = searchParams.get('ticker') || 'RELIANCE';

  const { fetchStockDetail, fetchSentiment } = useMarketData();
  const [stockData, setStockData] = useState(null);
  const [sentiment, setSentiment] = useState(null);
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);

  const loadStockData = useCallback(async () => {
    const [data, sentimentData] = await Promise.all([
      fetchStockDetail(ticker),
      fetchSentiment(ticker),
    ]);
    if (data?.success) setStockData(data);
    if (sentimentData?.success) setSentiment(sentimentData.data);
  }, [ticker, fetchStockDetail, fetchSentiment]);

  const renderChart = useCallback(() => {
    if (!chartRef.current || !stockData?.chart_data) return;

    // Dispose previous chart instance safely (no innerHTML)
    if (chartInstanceRef.current) {
      chartInstanceRef.current.remove();
      chartInstanceRef.current = null;
    }

    const chart = createChart(chartRef.current, {
      width: chartRef.current.clientWidth,
      height: 400,
      layout: { background: { color: '#0A0E1A' }, textColor: '#9CA3AF' },
      grid: { vertLines: { color: '#1F2937' }, horzLines: { color: '#1F2937' } },
      timeScale: { borderColor: '#1F2937' },
      localization: { locale: 'en-US' },
    });

    chartInstanceRef.current = chart;

    const series = chart.addSeries(CandlestickSeries, {
      upColor: '#10B981', downColor: '#EF4444',
      borderUpColor: '#10B981', borderDownColor: '#EF4444',
      wickUpColor: '#10B981', wickDownColor: '#EF4444',
    });
    series.setData(stockData.chart_data);
    chart.timeScale().fitContent();
  }, [stockData]);

  useEffect(() => { loadStockData(); }, [loadStockData]);
  useEffect(() => { renderChart(); }, [renderChart]);

  const ind = stockData?.indicators;

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
            <div ref={chartRef} data-testid="chart-container" />
          </div>

          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h2 className="text-lg font-semibold text-[#F9FAFB] mb-4">Technical Indicators</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <IndicatorCard label="RSI" value={ind?.rsi?.toFixed(2)} testId="rsi-value" />
              <IndicatorCard label="MACD" value={ind?.macd?.toFixed(2)} />
              <IndicatorCard label="EMA 20" value={ind?.ema_20?.toFixed(2)} />
              <IndicatorCard label="VWAP" value={ind?.vwap?.toFixed(2)} />
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-[#111827] border border-[#1F2937] rounded-sm p-4">
            <h3 className="text-base font-medium text-[#F9FAFB] mb-3">Price Levels</h3>
            <div className="space-y-2 text-sm">
              <PriceLevel label="Current" value={stockData?.current_price} />
              <PriceLevel label="Resistance" value={stockData?.resistance} color="text-[#EF4444]" />
              <PriceLevel label="Support" value={stockData?.support} color="text-[#10B981]" />
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
                }`}>{sentiment.sentiment_label}</div>
                <div className="mt-3 space-y-2">
                  {sentiment.headlines?.slice(0, 3).map((news) => (
                    <div key={`${news.title}-${news.source}`} className="text-xs text-[#9CA3AF] border-l-2 border-[#1F2937] pl-2">
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
