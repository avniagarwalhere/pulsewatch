import React, { useState, useEffect } from 'react';
import { useWatchlist } from '../context/WatchlistContext';
import { api } from '../services/api';

export default function DigestPage() {
  const { activeWatchlistId, openStockDetail } = useWatchlist();
  const [digest, setDigest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showAll, setShowAll] = useState(false);

  const fetchDigest = async (isManual = false) => {
    if (isManual) setRefreshing(true);
    try {
      const data = await api.getDigest(activeWatchlistId);
      setDigest(data);
    } catch (e) {
      console.error("Digest fetch error:", e);
    } finally {
      setLoading(false);
      if (isManual) setRefreshing(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    fetchDigest();
    const interval = setInterval(() => fetchDigest(), 45000);
    return () => clearInterval(interval);
  }, [activeWatchlistId]);

  if (loading && !digest) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-12 animate-pulse space-y-6">
        <div className="h-32 bg-surface rounded-xl w-full border border-border"></div>
        <div className="h-24 bg-surface rounded-xl w-full border border-border"></div>
        <div className="h-24 bg-surface rounded-xl w-full border border-border"></div>
      </div>
    );
  }

  const events = digest?.events || [];
  const visibleEvents = showAll 
    ? events 
    : events.filter(e => e.severity === 'needs_attention' || e.severity === 'worth_checking');

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      {/* Morning Brief Card */}
      <div className="mb-8 p-6 bg-surface border border-accent/30 rounded-xl shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-accent/5 rounded-full blur-2xl pointer-events-none"></div>
        
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <span className="flex h-2.5 w-2.5 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-accent"></span>
            </span>
            <h2 className="text-xs font-bold text-accent uppercase tracking-widest">Live AI Market Brief</h2>
          </div>
          
          <button
            onClick={() => fetchDigest(true)}
            disabled={refreshing}
            className="text-xs text-muted hover:text-content transition-colors flex items-center space-x-1.5 px-2.5 py-1 rounded bg-background border border-border hover:border-muted"
          >
            <span className={`inline-block ${refreshing ? 'animate-spin' : ''}`}>🔄</span>
            <span>{refreshing ? 'Analyzing...' : 'Refresh'}</span>
          </button>
        </div>

        <p className="text-base sm:text-lg text-content font-normal leading-relaxed">
          {digest?.morning_brief || "Analyzing current market conditions and significance metrics..."}
        </p>

        <div className="mt-4 pt-3 border-t border-border/60 flex flex-wrap items-center justify-between gap-3 text-xs text-muted">
          <div className="flex items-center space-x-3">
            <span className="font-medium text-content">
              {digest?.total_events || events.length} Signals Detected
            </span>
            {digest?.high_signal_count > 0 && (
              <span className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-500 font-semibold border border-amber-500/20">
                {digest.high_signal_count} High Priority
              </span>
            )}
            <span className="px-2 py-0.5 rounded-full bg-surface-hover text-muted-dark font-medium border border-border">
              {digest?.watch_count || 0} Watchlist Moves
            </span>
          </div>

          <div className="text-muted-dark font-mono text-[11px]">
            Generated {digest?.generated_at ? new Date(digest.generated_at).toLocaleTimeString() : new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Signal Feed Controls */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-semibold text-content tracking-tight">Signal Feed</h2>
          <p className="text-xs text-muted mt-0.5">Statistical significance scores calculated against Average True Range (ATR)</p>
        </div>
        <button 
          onClick={() => setShowAll(!showAll)} 
          className="text-xs font-medium px-3 py-1.5 rounded-md border border-border bg-surface text-muted hover:text-content hover:border-muted transition-colors"
        >
          {showAll ? "Showing all changes" : "Show high signal only"}
        </button>
      </div>

      {/* Events List */}
      {visibleEvents.length === 0 ? (
        <div className="text-center py-16 border border-dashed border-border rounded-xl bg-surface/50">
          <p className="text-content font-medium mb-1">No anomalous signals detected right now</p>
          <p className="text-muted text-xs">All watched symbols are currently trading within normal volatility bands.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {visibleEvents.map((ev) => {
            const isHighSignal = ev.severity === 'needs_attention';
            const isUp = (ev.price_change_pct ?? 0) >= 0;
            const score = ev.confidence ? Math.round(ev.confidence * 100) : 75;

            return (
              <div 
                key={ev.id} 
                onClick={() => openStockDetail(ev.symbol)}
                className={`p-4 rounded-xl border transition-all cursor-pointer hover:shadow-md hover:scale-[1.005] group ${
                  isHighSignal 
                    ? 'bg-surface border-l-4 border-l-amber-500 border-border hover:border-amber-500/50' 
                    : 'bg-surface border-l-4 border-l-slate-400 border-border hover:border-slate-400/50'
                }`}
              >
                <div className="flex justify-between items-baseline mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-content text-lg group-hover:text-accent transition-colors">
                      {ev.symbol.replace('.NS', '')}
                    </span>
                    <span className="text-xs text-muted-dark uppercase tracking-wider">
                      {ev.symbol.endsWith('.NS') ? 'NSE India' : 'US Market'}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`text-xs font-semibold tabular-nums px-2 py-0.5 rounded ${
                      isUp ? 'bg-up/15 text-up' : 'bg-down/15 text-down'
                    }`}>
                      {isUp ? '+' : ''}{(ev.price_change_pct ?? 0).toFixed(2)}%
                    </span>
                    <span className="text-xs text-muted-dark">
                      {ev.time_ago || (ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '')}
                    </span>
                  </div>
                </div>

                <h3 className="text-content font-medium text-sm mb-1 group-hover:text-content/90 leading-snug">
                  {ev.title}
                </h3>
                <p className="text-muted text-xs leading-relaxed mb-3">
                  {ev.description}
                </p>
                
                <div className="flex flex-wrap items-center gap-2 pt-1">
                  <span className={`px-2.5 py-0.5 text-[11px] font-semibold rounded-full border ${
                    isHighSignal 
                      ? 'bg-amber-500/10 text-amber-500 border-amber-500/30' 
                      : 'bg-surface-hover text-muted border-border'
                  }`}>
                    Significance: {score}/100
                  </span>

                  {ev.volume_ratio > 1.3 && (
                    <span className="px-2.5 py-0.5 text-[11px] font-semibold bg-accent/10 text-accent border border-accent/20 rounded-full">
                      Vol: {ev.volume_ratio.toFixed(1)}x avg
                    </span>
                  )}

                  <span className="text-[10px] text-muted-dark ml-auto">
                    Click to inspect chart →
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
