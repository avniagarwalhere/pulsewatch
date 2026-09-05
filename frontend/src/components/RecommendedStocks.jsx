import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useWatchlist } from '../context/WatchlistContext';
import { LineChart, Line, YAxis, ResponsiveContainer } from 'recharts';

export default function RecommendedStocks() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const { openStockDetail, liveQuotes, quotes } = useWatchlist();

  useEffect(() => {
    const fetchRecs = async () => {
      try {
        // Get recommendations based on first stock in current watchlist
        const watchlistSymbols = quotes.map(q => q.symbol).filter(s => s.endsWith('.NS'));
        if (watchlistSymbols.length === 0) {
          // Fallback: use trending
          const data = await api.getTrending();
          setStocks((data || []).slice(0, 6));
        } else {
          // Use first Indian stock for recommendations
          const sym = watchlistSymbols[0];
          const detail = await api.getDetail(sym);
          if (detail?.similar_stocks?.length > 0) {
            setStocks(detail.similar_stocks);
          } else {
            const data = await api.getTrending();
            setStocks((data || []).slice(0, 6));
          }
        }
      } catch (e) {
        console.error(e);
        try {
          const data = await api.getTrending();
          setStocks((data || []).slice(0, 6));
        } catch(e2) { console.error(e2); }
      } finally {
        setLoading(false);
      }
    };
    fetchRecs();
  }, [quotes]);

  if (loading) {
    return (
      <div className="space-y-2">
        {[1,2,3].map(i => (
          <div key={i} className="animate-pulse flex items-center space-x-3 p-3 bg-surface rounded-lg border border-border">
            <div className="h-4 bg-surface-hover rounded w-16"></div>
            <div className="flex-1 h-4 bg-surface-hover rounded"></div>
            <div className="h-4 bg-surface-hover rounded w-12"></div>
          </div>
        ))}
      </div>
    );
  }

  if (stocks.length === 0) {
    return <p className="text-muted text-sm">Add stocks to your watchlist to get recommendations.</p>;
  }

  return (
    <div className="space-y-2">
      {stocks.map((stock, i) => {
        const live = liveQuotes?.[stock.symbol];
        const price = live?.price ?? stock.price;
        const pct = live?.change_pct ?? stock.change_pct;
        const sparkline = live?.sparkline || [];
        const isUp = (pct ?? 0) >= 0;
        const isIndian = stock.symbol?.endsWith('.NS') || stock.symbol?.endsWith('.BO');
        const currency = isIndian ? '₹' : '$';

        return (
          <div
            key={i}
            onClick={() => openStockDetail(stock.symbol)}
            className="flex items-center space-x-3 p-3 bg-surface rounded-lg border border-border hover:border-muted cursor-pointer transition-all group"
          >
            <div className="flex-1 min-w-0">
              <div className="font-semibold text-sm text-content group-hover:text-accent transition-colors truncate">
                {stock.symbol?.replace('.NS', '')}
              </div>
              <div className="text-[11px] text-muted truncate">{stock.name}</div>
            </div>

            {/* Mini sparkline */}
            {sparkline.length > 2 && (
              <div className="h-6 w-16 opacity-40 group-hover:opacity-80 transition-opacity flex-shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={sparkline.map((val, idx) => ({ v: val, i: idx }))}>
                    <YAxis domain={['auto', 'auto']} hide />
                    <Line type="monotone" dataKey="v" stroke={isUp ? '#22c55e' : '#ef4444'} strokeWidth={1} dot={false} isAnimationActive={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            <div className="text-right flex-shrink-0">
              <div className="text-sm font-medium text-content tabular-nums">
                {currency}{price != null ? price.toLocaleString('en-IN', {maximumFractionDigits: 2}) : '—'}
              </div>
              <div className={`text-[11px] font-semibold ${isUp ? 'text-up' : 'text-down'}`}>
                {isUp ? '+' : ''}{(pct ?? 0).toFixed(2)}%
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
