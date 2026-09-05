import React, { useRef, useEffect, useState } from 'react';
import { useWatchlist } from '../context/WatchlistContext';
import { LineChart, Line, YAxis, ResponsiveContainer } from 'recharts';
import { api } from '../services/api';

function FlashCell({ value, children, className }) {
  const [flashClass, setFlashClass] = useState('');
  const prevValue = useRef(value);

  useEffect(() => {
    if (prevValue.current !== value && value !== undefined) {
      if (value > prevValue.current) {
        setFlashClass('animate-flash-green');
      } else if (value < prevValue.current) {
        setFlashClass('animate-flash-red');
      }
      const timer = setTimeout(() => setFlashClass(''), 1000);
      prevValue.current = value;
      return () => clearTimeout(timer);
    }
  }, [value]);

  return <td className={`${className} ${flashClass} rounded transition-colors duration-200`}>{children}</td>;
}

export default function WatchlistSection({ onOpenSearch }) {
  const { 
    watchlists, 
    activeWatchlistId, 
    setActiveWatchlistId, 
    quotes, 
    liveQuotes,
    openStockDetail, 
    catchup,
    loadWatchlistData
  } = useWatchlist();

  const [viewMode, setViewMode] = useState('table'); // 'table' or 'heatmap'
  const [recommendations, setRecommendations] = useState([]);
  const [recsLoading, setRecsLoading] = useState(false);
  const [addingSym, setAddingSym] = useState(null);
  const [addedSyms, setAddedSyms] = useState({});
  const [stockSearch, setStockSearch] = useState('');

  // Fetch dynamic recommendations (strictly top 3) based on active watchlist
  useEffect(() => {
    const fetchRecs = async () => {
      setRecsLoading(true);
      try {
        const data = await api.getRecommendations(activeWatchlistId, 3);
        setRecommendations(data || []);
      } catch (e) {
        console.error("Failed to fetch dynamic recommendations:", e);
      } finally {
        setRecsLoading(false);
      }
    };
    fetchRecs();
    const interval = setInterval(fetchRecs, 45000);
    return () => clearInterval(interval);
  }, [activeWatchlistId]);

  const handleAddToWatchlist = async (e, symbol) => {
    e.stopPropagation();
    if (!activeWatchlistId) return;
    setAddingSym(symbol);
    try {
      await api.addStock(activeWatchlistId, symbol);
      setAddedSyms(prev => ({ ...prev, [symbol]: true }));
      loadWatchlistData(activeWatchlistId);
    } catch (err) {
      console.error("Failed to add to watchlist:", err);
    } finally {
      setAddingSym(null);
    }
  };

  if (!watchlists || watchlists.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-12 text-center">
        <p className="text-muted mb-4">Your watchlist is empty. Search for a stock to add it.</p>
        <button onClick={onOpenSearch} className="text-accent hover:text-accent/80 flex items-center justify-center space-x-2 mx-auto">
          <span>🔍</span><span>Search Stocks</span>
        </button>
      </div>
    );
  }

  const hasUnseen = (symbol) => {
    if (!catchup) return false;
    const all = [...(catchup.meaningful_changes || []), ...(catchup.minor_changes || [])];
    return all.some(c => c.symbol === symbol && !c.seen);
  };

  // Preferred order: Indian Markets -> My Watchlist -> US Markets -> Trading -> Long term
  const indianWl = watchlists.find(w => w.name.toLowerCase().includes('indian'));
  const myWl = watchlists.find(w => w.name === 'My Watchlist');
  const usWl = watchlists.find(w => w.name.toLowerCase().includes('us'));
  const otherWls = watchlists.filter(w => w.id !== indianWl?.id && w.id !== myWl?.id && w.id !== usWl?.id);

  const orderedWatchlists = [];
  if (indianWl) orderedWatchlists.push(indianWl);
  if (myWl) orderedWatchlists.push(myWl);
  if (usWl) orderedWatchlists.push(usWl);
  otherWls.forEach(w => orderedWatchlists.push(w));

  // Filter quotes by search query if any
  const filteredQuotes = stockSearch.trim() 
    ? quotes.filter(q => 
        q.symbol.toLowerCase().includes(stockSearch.toLowerCase()) || 
        q.name?.toLowerCase().includes(stockSearch.toLowerCase()) ||
        q.sector?.toLowerCase().includes(stockSearch.toLowerCase())
      )
    : quotes;

  return (
    <div className="py-2 space-y-6">
      {/* Watchlist Tabs Header */}
      <div className="flex items-center justify-between border-b border-border/80 pb-2">
        <div className="flex space-x-6 overflow-x-auto scrollbar-custom flex-1">
          {orderedWatchlists.map((w) => {
            const isActive = activeWatchlistId === w.id;
            const count = w.items?.length || (isActive ? quotes.length : null);
            return (
              <button
                key={w.id}
                onClick={() => setActiveWatchlistId(w.id)}
                className={`text-sm pb-2 border-b-2 whitespace-nowrap transition-all flex items-center space-x-2 ${
                  isActive 
                    ? 'border-accent text-accent font-semibold' 
                    : 'border-transparent text-muted hover:text-content'
                }`}
              >
                <span>{w.name}</span>
                {count != null && (
                  <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded-full ${
                    isActive ? 'bg-accent text-white' : 'bg-surface text-muted-dark border border-border'
                  }`}>
                    {count}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* View Mode & Filter */}
        <div className="flex items-center space-x-3 ml-4">
          <div className="relative hidden sm:block">
            <input
              type="text"
              placeholder="Filter stocks..."
              value={stockSearch}
              onChange={(e) => setStockSearch(e.target.value)}
              className="px-2.5 py-1 text-xs bg-surface border border-border rounded-md text-content placeholder-muted focus:outline-none focus:border-accent w-28 focus:w-40 transition-all"
            />
            {stockSearch && (
              <button onClick={() => setStockSearch('')} className="absolute right-2 top-1 text-xs text-muted hover:text-content">
                ×
              </button>
            )}
          </div>

          <div className="flex bg-surface rounded-md p-0.5 border border-border">
            <button 
              onClick={() => setViewMode('table')}
              className={`px-2.5 py-1 text-xs rounded transition-colors ${viewMode === 'table' ? 'bg-accent/20 text-accent font-semibold' : 'text-muted hover:text-content'}`}
            >
              Table
            </button>
            <button 
              onClick={() => setViewMode('heatmap')}
              className={`px-2.5 py-1 text-xs rounded transition-colors ${viewMode === 'heatmap' ? 'bg-accent/20 text-accent font-semibold' : 'text-muted hover:text-content'}`}
            >
              Heatmap
            </button>
          </div>
        </div>
      </div>

      {/* WATCHLIST CONTENT (TABLE OR HEATMAP) */}
      {viewMode === 'heatmap' ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
          {filteredQuotes.map(quote => {
            const live = liveQuotes?.[quote.symbol];
            const price = live?.price ?? quote.price;
            const pct = live?.change_pct ?? quote.change_pct;
            const isIndian = quote.symbol?.endsWith('.NS') || quote.symbol?.endsWith('.BO') || quote.symbol?.startsWith('^');
            const currency = isIndian ? '₹' : '$';

            return (
              <div 
                key={quote.symbol}
                onClick={() => openStockDetail(quote.symbol)}
                className={`cursor-pointer p-3.5 rounded-lg flex flex-col justify-between aspect-[4/3] transition-transform hover:scale-[1.02] border ${
                  pct >= 0 ? 'bg-green-500/15 hover:bg-green-500/25 border-green-500/30' : 'bg-red-500/15 hover:bg-red-500/25 border-red-500/30'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="font-semibold text-content text-sm">{quote.symbol.replace('.NS', '')}</div>
                  {hasUnseen(quote.symbol) && <span className="text-accent text-xs">●</span>}
                </div>
                <div>
                  <div className="text-base font-light text-content mb-0.5">
                    {price != null ? `${currency}${price.toLocaleString(isIndian ? 'en-IN' : 'en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}` : '—'}
                  </div>
                  <div className={`text-xs font-semibold ${pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {pct != null ? `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%` : '—'}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-border bg-surface/40">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead>
              <tr className="text-muted-dark border-b border-border bg-surface/80 text-xs">
                <th className="py-2.5 px-4 font-medium">Stock ({filteredQuotes.length})</th>
                <th className="py-2.5 px-2 font-medium">Trend</th>
                <th className="py-2.5 px-4 font-medium text-right">Price</th>
                <th className="py-2.5 px-4 font-medium text-right">Today</th>
                <th className="py-2.5 px-4 font-medium text-right">Since Check</th>
                <th className="py-2.5 px-4 font-medium">Volume</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40">
              {filteredQuotes.map(quote => {
                const live = liveQuotes?.[quote.symbol];
                const price = live?.price ?? quote.price;
                const pct = live?.change_pct ?? quote.change_pct;
                const sparkline = live?.sparkline || quote.sparkline || [];
                const volRatio = live?.volume_ratio ?? quote.volume_ratio ?? 1.0;
                const isIndian = quote.symbol?.endsWith('.NS') || quote.symbol?.endsWith('.BO') || quote.symbol?.startsWith('^');
                const currency = isIndian ? '₹' : '$';

                return (
                  <tr 
                    key={quote.symbol} 
                    onClick={() => openStockDetail(quote.symbol)}
                    className="hover:bg-surface-hover/80 cursor-pointer transition-colors group"
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2.5">
                        {hasUnseen(quote.symbol) ? (
                          <span className="text-accent text-[8px]">●</span>
                        ) : (
                          <span className="w-2"></span>
                        )}
                        <div>
                          <div className="font-semibold text-content group-hover:text-accent transition-colors">
                            {quote.symbol.replace('.NS', '')}
                          </div>
                          <div className="text-[11px] text-muted truncate max-w-[150px]">{quote.name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-2 w-28">
                      {sparkline.length > 0 ? (
                        <div className="h-7 w-24 opacity-60 group-hover:opacity-100 transition-opacity">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={sparkline.map((val, i) => ({ value: val, index: i }))}>
                              <YAxis domain={['auto', 'auto']} hide />
                              <Line 
                                type="monotone" 
                                dataKey="value" 
                                stroke={pct >= 0 ? '#22c55e' : '#ef4444'} 
                                strokeWidth={1.5} 
                                dot={false}
                                isAnimationActive={false}
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      ) : (
                        <div className="text-muted text-xs">—</div>
                      )}
                    </td>
                    <FlashCell value={price} className="py-3 px-4 text-right text-content font-medium tabular-nums">
                      {price != null ? `${currency}${price.toLocaleString(isIndian ? 'en-IN' : 'en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}` : '—'}
                    </FlashCell>
                    <FlashCell value={pct} className={`py-3 px-4 text-right font-semibold text-xs tabular-nums ${pct >= 0 ? 'text-up' : 'text-down'}`}>
                      {pct != null ? `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%` : '—'}
                    </FlashCell>
                    <FlashCell value={quote.since_last_check_pct} className={`py-3 px-4 text-right text-xs tabular-nums ${quote.since_last_check_pct >= 0 ? 'text-up' : 'text-down'}`}>
                      {quote.since_last_check_pct != null 
                        ? `${quote.since_last_check_pct >= 0 ? '+' : ''}${quote.since_last_check_pct.toFixed(2)}%` 
                        : '—'}
                    </FlashCell>
                    <td className="py-3 px-4 text-xs tabular-nums text-muted">
                      {volRatio > 1.3 ? (
                        <span className="font-semibold text-accent px-1.5 py-0.5 rounded bg-accent/10 border border-accent/20">
                          {volRatio.toFixed(1)}x avg
                        </span>
                      ) : (
                        `${volRatio.toFixed(1)}x`
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* DYNAMIC RECOMMENDATIONS (TOP 3) - PLACED DIRECTLY UNDER WATCHLIST LIKE BEFORE */}
      <div className="pt-4 border-t border-border/70">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <span className="text-base">💡</span>
            <h3 className="text-sm font-semibold text-content uppercase tracking-wider">
              Recommended for You
            </h3>
            <span className="text-[11px] font-bold px-1.5 py-0.5 rounded-full bg-accent/15 text-accent border border-accent/25">
              3 Live Picks
            </span>
          </div>
          <span className="text-[11px] text-muted hidden sm:inline">
            Correlated with active portfolio & volume breakouts
          </span>
        </div>

        {recsLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="animate-pulse p-3.5 bg-surface rounded-xl border border-border h-24"></div>
            ))}
          </div>
        ) : recommendations.length === 0 ? (
          <p className="text-xs text-muted text-center py-4">Scanning market for high-conviction recommendations...</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {recommendations.slice(0, 3).map((rec) => {
              const live = liveQuotes?.[rec.symbol];
              const price = live?.price ?? rec.price;
              const pct = live?.change_pct ?? rec.change_pct;
              const sparkline = live?.sparkline || rec.sparkline || [];
              const isUp = (pct ?? 0) >= 0;
              const isIndian = rec.symbol.endsWith('.NS') || rec.symbol.endsWith('.BO');
              const currency = isIndian ? '₹' : '$';
              const isAlreadyInWl = quotes.some(q => q.symbol === rec.symbol) || addedSyms[rec.symbol];

              return (
                <div
                  key={rec.symbol}
                  onClick={() => openStockDetail(rec.symbol)}
                  className="p-3.5 bg-surface rounded-xl border border-border hover:border-accent/50 transition-all hover:shadow-md cursor-pointer flex flex-col justify-between group"
                >
                  {/* Header: Symbol, Name & Add Button */}
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <div className="font-bold text-content text-sm group-hover:text-accent transition-colors flex items-center space-x-1.5">
                        <span>{rec.symbol.replace('.NS', '')}</span>
                        <span className="text-[10px] font-semibold px-1.5 py-0.2 rounded bg-surface-hover text-muted border border-border">
                          {rec.sector}
                        </span>
                      </div>
                      <div className="text-[11px] text-muted truncate max-w-[130px]">{rec.name}</div>
                    </div>

                    <button
                      onClick={(e) => handleAddToWatchlist(e, rec.symbol)}
                      disabled={isAlreadyInWl || addingSym === rec.symbol}
                      className={`text-[11px] px-2 py-0.5 rounded border font-medium transition-all ${
                        isAlreadyInWl
                          ? 'bg-up/10 text-up border-up/30 cursor-default'
                          : 'bg-surface-hover hover:bg-accent hover:text-white border-border text-content'
                      }`}
                      title={isAlreadyInWl ? "In Watchlist" : "Save to active watchlist"}
                    >
                      {addingSym === rec.symbol ? "..." : (isAlreadyInWl ? "✓ Added" : "+ Add")}
                    </button>
                  </div>

                  {/* Sparkline Graph */}
                  {sparkline.length > 2 && (
                    <div className="h-6 w-full opacity-50 group-hover:opacity-80 transition-opacity mb-2">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={sparkline.map((val, idx) => ({ v: val, i: idx }))}>
                          <YAxis domain={['auto', 'auto']} hide />
                          <Line 
                            type="monotone" 
                            dataKey="v" 
                            stroke={isUp ? '#22c55e' : '#ef4444'} 
                            strokeWidth={1.3} 
                            dot={false} 
                            isAnimationActive={false} 
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  )}

                  {/* Bottom: Price, Change & Reason */}
                  <div className="pt-2 border-t border-border/50">
                    <div className="flex items-baseline justify-between mb-1">
                      <span className="font-semibold text-content text-sm tabular-nums">
                        {currency}{price != null ? price.toLocaleString(isIndian ? 'en-IN' : 'en-US', { maximumFractionDigits: 2 }) : '—'}
                      </span>
                      <span className={`text-xs font-bold ${isUp ? 'text-up' : 'text-down'}`}>
                        {isUp ? '+' : ''}{(pct ?? 0).toFixed(2)}%
                      </span>
                    </div>

                    <div className="text-[10px] text-accent font-medium truncate flex items-center space-x-1">
                      <span>🎯</span>
                      <span>{rec.reason || 'Quantitative match'}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
