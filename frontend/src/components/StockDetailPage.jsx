import React, { useEffect, useState } from 'react';
import { useWatchlist } from '../context/WatchlistContext';
import { api } from '../services/api';
import { AdvancedRealTimeChart } from 'react-ts-tradingview-widgets';

const getTVSymbol = (symbol) => {
  if (!symbol) return "AAPL";
  if (symbol === "^NSEI") return "NIFTY"; // TradingView blocks NSE:NIFTY in widgets, so we let it auto-resolve or use the CFD
  if (symbol === "^BSESN") return "BSE:SENSEX";
  if (symbol === "^GSPC") return "SP:SPX";
  // Strip Yahoo Finance suffixes and let TradingView auto-resolve the best exchange
  return symbol.replace(/\.(NS|BO)$/, "");
};

export default function StockDetailPage({ theme }) {
  const { selectedStock, closeStockDetail, activeWatchlistId, loadWatchlistData, markEventSeen, catchup, quotes, liveQuotes, watchlists, loadWatchlists, openStockDetail } = useWatchlist();
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showWatchlistMenu, setShowWatchlistMenu] = useState(false);

  useEffect(() => {
    if (selectedStock) {
      setLoading(true);
      const url = activeWatchlistId 
        ? `${selectedStock}?watchlist_id=${activeWatchlistId}` 
        : selectedStock;
      
      api.getDetail(url)
        .then(data => setDetail(data))
        .catch(err => console.error(err))
        .finally(() => setLoading(false));

      // Mark unread events as seen when opening detail
      if (catchup && activeWatchlistId) {
        const events = [...(catchup.meaningful_changes||[]), ...(catchup.minor_changes||[])];
        events.forEach(ev => {
          if (ev.symbol === selectedStock && ev.seen_state === 'NEW') {
            markEventSeen(ev.id);
          }
        });
      }
    }
  }, [selectedStock, activeWatchlistId, catchup, markEventSeen]);

  if (!selectedStock) return null;

  // Real-time overrides
  const displayPrice = liveQuotes?.[selectedStock]?.price ?? detail?.price;
  const displayChange = liveQuotes?.[selectedStock]?.change_pct ?? detail?.change_pct;

  // Check if stock is in a specific watchlist
  const isInWatchlist = (w) => w.items?.some(i => i.symbol === detail?.symbol);


  return (
    <div className="fixed top-14 left-0 right-0 bottom-0 bg-background z-40 overflow-y-auto">
      {loading || !detail ? (
        <div className="max-w-7xl mx-auto px-6 py-8 animate-pulse flex flex-col space-y-6">
          <div className="h-12 bg-surface-hover rounded w-64"></div>
          <div className="h-96 bg-surface-hover rounded w-full"></div>
        </div>
      ) : (
        <div className="max-w-7xl mx-auto px-6 py-8">
          
          {/* Header */}
          <div className="flex items-start justify-between mb-8">
            <div className="flex items-center space-x-6">
              <button 
                onClick={closeStockDetail} 
                className="p-2 bg-surface border border-border rounded hover:bg-surface-hover transition-colors flex items-center text-muted hover:text-content"
              >
                ← Back
              </button>
              <div>
                <h2 className="text-3xl font-semibold text-content tracking-tight flex items-center space-x-3">
                  <span>{detail.name === detail.symbol ? detail.name.replace(/\.(NS|BO)$/, "") : detail.name}</span>
                  <div className="relative">
                    <button 
                      onClick={() => setShowWatchlistMenu(!showWatchlistMenu)}
                      className={`p-1.5 rounded-full transition-colors ${
                        watchlists.some(isInWatchlist)
                          ? 'bg-accent/20 text-accent hover:bg-accent/30'
                          : 'bg-surface border border-border hover:bg-surface-hover text-muted-dark hover:text-content'
                      }`}
                      title="Manage Watchlists"
                    >
                      <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M17 3H7c-1.1 0-2 .9-2 2v16l7-3 7 3V5c0-1.1-.9-2-2-2z" />
                      </svg>
                    </button>
                    {showWatchlistMenu && (
                      <>
                        <div 
                          className="fixed inset-0 z-40" 
                          onClick={() => setShowWatchlistMenu(false)}
                        ></div>
                        <div className="absolute top-full left-0 mt-2 w-56 bg-surface border border-border rounded-lg shadow-xl z-50 py-2">
                          <div className="px-3 pb-2 mb-2 border-b border-border text-xs font-semibold text-muted uppercase tracking-wider">
                            Save to Watchlist
                          </div>
                          {watchlists.map(w => {
                            const active = isInWatchlist(w);
                            return (
                              <label key={w.id} className="flex items-center px-3 py-2 hover:bg-surface-hover cursor-pointer transition-colors group">
                                <input 
                                  type="checkbox" 
                                  checked={active}
                                  onChange={async () => {
                                    if (active) {
                                      await api.removeStock(w.id, detail.symbol);
                                    } else {
                                      await api.addStock(w.id, detail.symbol);
                                    }
                                    await loadWatchlists();
                                    if (activeWatchlistId === w.id) {
                                      loadWatchlistData(activeWatchlistId);
                                    }
                                  }}
                                  className="mr-3 w-4 h-4 accent-accent rounded border-border bg-background cursor-pointer"
                                />
                                <span className="text-sm font-medium text-content group-hover:text-accent">{w.name}</span>
                              </label>
                            );
                          })}
                        </div>
                      </>
                    )}
                  </div>
                </h2>
                {detail.name !== detail.symbol && (
                  <p className="text-base text-muted mt-1">{detail.symbol}</p>
                )}
              </div>
            </div>
            
            <div className="text-right flex flex-col items-end">
              <div className="text-4xl font-light text-content tracking-tight mb-2 flex items-center space-x-3">
                <span>{displayPrice != null ? `${detail.symbol?.endsWith('.NS') || detail.symbol?.endsWith('.BO') || detail.symbol?.startsWith('^') ? '₹' : '$'}${displayPrice.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}` : '—'}</span>
                {liveQuotes?.[selectedStock]?.price && (
                  <span className="flex h-3 w-3 relative" title="Live update">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-up opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-up"></span>
                  </span>
                )}
              </div>
              <div className={`text-lg font-medium ${displayChange >= 0 ? 'text-up' : 'text-down'}`}>
                {displayChange >= 0 ? '+' : ''}{displayChange?.toFixed(2)}% today
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content (Chart & News) */}
            <div className="lg:col-span-2 space-y-8">
              
              {/* TradingView Chart */}
              <div className="bg-surface border border-border rounded-lg overflow-hidden h-[500px]">
                <AdvancedRealTimeChart 
                  key={theme + detail.symbol}
                  symbol={getTVSymbol(detail.symbol)} 
                  theme={theme} 
                  interval="D"
                  autosize
                  hide_top_toolbar={false}
                  hide_legend={false}
                  save_image={false}
                />
              </div>

              {/* News */}
              {detail.news && detail.news.length > 0 && (
                <div className="bg-surface border border-border rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-content mb-6">Latest Headlines</h3>
                  <div className="space-y-6">
                    {detail.news.map((item, i) => (
                      <a key={i} href={item.link} target="_blank" rel="noreferrer" className="block group">
                        <div className="text-lg font-medium text-content/90 group-hover:text-accent transition-colors leading-snug">
                          {item.title}
                        </div>
                        <div className="text-xs uppercase tracking-wider text-muted mt-2">
                          {item.publisher}
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right Sidebar (Stats, AI, Events) */}
            <div className="space-y-8">
              
              {/* AI Analysis */}
              {detail.ai_analysis && (
                <div className="bg-surface border border-border rounded-lg p-6 shadow-sm">
                  <h3 className="text-sm font-semibold text-content mb-4 uppercase tracking-wider text-muted">AI Sentiment Analysis</h3>
                  <div className="flex items-center justify-between mb-4">
                    <span className={`text-2xl font-bold ${
                      detail.ai_analysis.sentiment.includes('Buy') || detail.ai_analysis.sentiment === 'Bullish' ? 'text-green-400' :
                      detail.ai_analysis.sentiment.includes('Sell') || detail.ai_analysis.sentiment === 'Bearish' ? 'text-red-400' :
                      'text-yellow-400'
                    }`}>
                      {detail.ai_analysis.sentiment}
                    </span>
                    <span className="text-sm font-mono text-muted bg-background px-3 py-1 rounded border border-border">
                      {detail.ai_analysis.confidence.toFixed(0)}% Conf.
                    </span>
                  </div>
                  <p className="text-sm text-content/80 leading-relaxed">
                    {detail.ai_analysis.summary}
                  </p>
                </div>
              )}

              {/* Market Depth */}
              <div className="bg-surface border border-border rounded-lg p-6">
                <h3 className="text-sm font-semibold text-content mb-4 uppercase tracking-wider text-muted">Market Depth & Stats</h3>
                <div className="grid grid-cols-1 gap-y-4 text-sm">
                  <div className="flex justify-between border-b border-border/50 pb-2">
                    <span className="text-muted">Open</span>
                    <span className="text-content font-medium">{detail.open?.toFixed(2) || '—'}</span>
                  </div>
                  <div className="flex justify-between border-b border-border/50 pb-2">
                    <span className="text-muted">High</span>
                    <span className="text-content font-medium">{detail.high?.toFixed(2) || '—'}</span>
                  </div>
                  <div className="flex justify-between border-b border-border/50 pb-2">
                    <span className="text-muted">Low</span>
                    <span className="text-content font-medium">{detail.low?.toFixed(2) || '—'}</span>
                  </div>
                  <div className="flex justify-between border-b border-border/50 pb-2">
                    <span className="text-muted">Prev Close</span>
                    <span className="text-content font-medium">{detail.prev_close?.toFixed(2) || '—'}</span>
                  </div>
                  <div className="flex justify-between border-b border-border/50 pb-2">
                    <span className="text-muted">Volume</span>
                    <span className="text-content font-medium">{(detail.volume / 1000000).toFixed(2)}M</span>
                  </div>
                </div>
              </div>

              {/* Similar Stocks */}
              {detail.similar_stocks && detail.similar_stocks.length > 0 && (
                <div className="bg-surface border border-border rounded-lg p-6">
                  <h3 className="text-sm font-semibold text-content mb-4 uppercase tracking-wider text-muted">People Also Watch</h3>
                  <div className="grid grid-cols-1 gap-3">
                    {detail.similar_stocks.map((sim, i) => {
                      const pct = sim.change_pct != null ? sim.change_pct : 0;
                      return (
                        <div key={i} className="flex justify-between items-center p-3 bg-background border border-border rounded-lg hover:border-muted transition-colors cursor-pointer" onClick={() => openStockDetail(sim.symbol)}>
                          <div className="font-semibold text-content flex items-center space-x-2">
                            <span>{sim.name === sim.symbol ? sim.name.replace(/\.(NS|BO)$/, "") : sim.name}</span>
                            <span className="text-xs text-muted font-normal">{sim.symbol}</span>
                          </div>
                          <div className={`font-medium ${pct >= 0 ? 'text-up' : 'text-down'}`}>
                            {pct >= 0 ? '+' : ''}{pct.toFixed(2)}%
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Why we're showing this & Events */}
              {(detail.why_showing?.length > 0 || detail.recent_events?.length > 0) && (
                <div className="bg-surface border border-border rounded-lg p-6">
                  {detail.why_showing?.length > 0 && (
                    <div className="mb-6">
                      <h3 className="text-sm font-semibold text-content mb-3 uppercase tracking-wider text-muted">Why we're showing this</h3>
                      <ul className="space-y-3">
                        {detail.why_showing.map((item, i) => (
                          <li key={i} className="text-sm text-content/80 flex items-start space-x-3">
                            <span className="text-accent mt-1.5 text-[8px]">●</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {detail.recent_events?.length > 0 && (
                    <div>
                      <h3 className="text-sm font-semibold text-content mb-4 uppercase tracking-wider text-muted">Recent Activity</h3>
                      <div className="space-y-5">
                        {detail.recent_events.map(ev => (
                          <div key={ev.id} className="flex items-start space-x-3">
                            <div className={`mt-1 w-2.5 h-2.5 rounded-full shrink-0 ${
                              ev.severity === 'critical' ? 'bg-red-500' :
                              ev.severity === 'needs_attention' ? 'bg-yellow-500' : 'bg-blue-500'
                            }`} />
                            <div>
                              <div className="text-sm font-medium text-content">{ev.title}</div>
                              <div className="text-xs text-muted mt-1">{ev.description}</div>
                              <div className="text-[10px] text-muted-dark mt-1.5 uppercase tracking-wider">{ev.time_label}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

            </div>
          </div>
        </div>
      )}
    </div>
  );
}
