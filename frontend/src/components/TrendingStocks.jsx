import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useWatchlist } from '../context/WatchlistContext';
import { LineChart, Line, YAxis, ResponsiveContainer } from 'recharts';

export default function TrendingStocks() {
  const [market, setMarket] = useState('IN'); // 'IN' or 'US'
  const [trending, setTrending] = useState([]);
  const [loading, setLoading] = useState(true);
  const { openStockDetail, liveQuotes } = useWatchlist();

  const fetchTrending = async (m) => {
    setLoading(true);
    try {
      const data = await api.getTrending(m);
      setTrending(data || []);
    } catch(e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrending(market);
    const interval = setInterval(() => fetchTrending(market), 45000);
    return () => clearInterval(interval);
  }, [market]);

  return (
    <div className="space-y-3">
      {/* Market Selector Tabs */}
      <div className="flex items-center space-x-1 p-1 bg-surface rounded-lg border border-border w-full">
        <button
          onClick={() => setMarket('IN')}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-all flex items-center justify-center space-x-1.5 ${
            market === 'IN' 
              ? 'bg-accent/20 text-accent border border-accent/30 shadow-sm' 
              : 'text-muted hover:text-content hover:bg-surface-hover'
          }`}
        >
          <span>🇮🇳</span>
          <span>Indian Stocks</span>
        </button>
        <button
          onClick={() => setMarket('US')}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-all flex items-center justify-center space-x-1.5 ${
            market === 'US' 
              ? 'bg-accent/20 text-accent border border-accent/30 shadow-sm' 
              : 'text-muted hover:text-content hover:bg-surface-hover'
          }`}
        >
          <span>🇺🇸</span>
          <span>US Market</span>
        </button>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 gap-3">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="animate-pulse p-3 bg-surface rounded-lg border border-border">
              <div className="h-4 bg-surface-hover rounded w-1/2 mb-2"></div>
              <div className="h-6 bg-surface-hover rounded w-2/3"></div>
            </div>
          ))}
        </div>
      ) : trending.length === 0 ? (
        <p className="text-xs text-muted text-center py-4">No trending data available.</p>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {trending.slice(0, 8).map((stock, i) => {
            const live = liveQuotes?.[stock.symbol];
            const price = live?.price ?? stock.price;
            const pct = live?.change_pct ?? stock.change_pct;
            const sparkline = live?.sparkline || stock.sparkline || [];
            const isUp = (pct ?? 0) >= 0;
            const isIndian = stock.symbol.endsWith('.NS') || stock.symbol.endsWith('.BO');
            const currency = isIndian ? '₹' : '$';

            return (
              <div
                key={i}
                onClick={() => openStockDetail(stock.symbol)}
                className="p-3 bg-surface rounded-lg border border-border hover:border-muted cursor-pointer transition-all hover:shadow-sm group overflow-hidden"
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="font-semibold text-content text-sm group-hover:text-accent transition-colors truncate">
                    {stock.symbol.replace('.NS', '')}
                  </div>
                  <span className={`text-[11px] font-bold px-1.5 py-0.5 rounded ${
                    isUp ? 'bg-up/15 text-up' : 'bg-down/15 text-down'
                  }`}>
                    {isUp ? '+' : ''}{(pct ?? 0).toFixed(2)}%
                  </span>
                </div>

                <div className="text-[11px] text-muted truncate mb-1.5">{stock.name}</div>
                
                {/* Live Sparkline */}
                {sparkline.length > 2 && (
                  <div className="h-6 w-full opacity-50 group-hover:opacity-80 transition-opacity mb-1.5">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={sparkline.map((val, idx) => ({ v: val, i: idx }))}>
                        <YAxis domain={['auto', 'auto']} hide />
                        <Line 
                          type="monotone" 
                          dataKey="v" 
                          stroke={isUp ? '#22c55e' : '#ef4444'} 
                          strokeWidth={1.2} 
                          dot={false} 
                          isAnimationActive={false} 
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}

                <div className="text-content font-medium tabular-nums text-sm truncate">
                  {currency}{price != null ? price.toLocaleString(isIndian ? 'en-IN' : 'en-US', { maximumFractionDigits: 2 }) : '—'}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
