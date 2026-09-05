import React from 'react';
import { useWatchlist } from '../context/WatchlistContext';

export default function WhileYouWereAway() {
  const { catchup, markEventSeen, markAllEventsSeen, openStockDetail } = useWatchlist();

  if (!catchup) return null;

  const changes = catchup.meaningful_changes || [];
  const unseenChanges = changes.filter(c => !c.seen);
  const allCaughtUp = catchup.all_caught_up || (changes.length > 0 && unseenChanges.length === 0);

  if (allCaughtUp) {
    return (
      <section className="py-16 border-b border-border">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <div className="text-3xl mb-3">✓</div>
          <h2 className="text-lg font-medium text-content mb-2">You're all caught up</h2>
          <p className="text-sm text-muted">
            Nothing meaningful changed since you last checked.
          </p>
          {catchup.elapsed_label && catchup.elapsed_label !== 'Never' && (
            <p className="text-xs text-muted-dark mt-2">Last checked {catchup.elapsed_label}</p>
          )}
        </div>
      </section>
    );
  }

  return (
    <section className="py-10 border-b border-border bg-surface">
      <div className="max-w-3xl mx-auto px-6">
        <div className="flex items-end justify-between mb-8">
          <div>
            <h2 className="text-xl font-medium text-content mb-1">While you were away</h2>
            <p className="text-sm text-muted">
              {unseenChanges.length} meaningful change{unseenChanges.length !== 1 ? 's' : ''}
              {catchup.elapsed_label && catchup.elapsed_label !== 'Never' && (
                <span className="text-muted-dark"> · Last checked {catchup.elapsed_label}</span>
              )}
            </p>
          </div>
          {unseenChanges.length > 0 && (
            <button 
              onClick={markAllEventsSeen}
              className="text-xs text-muted hover:text-content transition-colors"
            >
              Mark all as seen
            </button>
          )}
        </div>

        <div className="space-y-3">
          {changes.map(change => (
            <div 
              key={change.id}
              onClick={() => {
                if (!change.seen) markEventSeen(change.id);
                openStockDetail(change.symbol);
              }}
              className={`p-5 rounded-lg border cursor-pointer transition-all duration-200 ${
                change.seen 
                  ? 'bg-surface/30 border-border/50 opacity-60' 
                  : 'bg-surface border-border hover:border-muted'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center space-x-2.5">
                  {!change.seen && <span className="text-accent text-[10px]">●</span>}
                  <span className="font-semibold text-content tracking-tight">{change.symbol}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded ${
                    change.severity === 'needs_attention' 
                      ? 'bg-down/10 text-down' 
                      : 'bg-accent/10 text-accent'
                  }`}>
                    {change.severity === 'needs_attention' ? 'Needs attention' : 'Worth checking'}
                  </span>
                </div>
                {change.change_pct != null && (
                  <span className={`text-sm font-medium ${change.change_pct >= 0 ? 'text-up' : 'text-down'}`}>
                    {change.change_pct >= 0 ? '+' : ''}{change.change_pct.toFixed(1)}%
                  </span>
                )}
              </div>
              <p className="text-sm text-content/80 mb-1">{change.title}</p>
              {change.context && (
                <p className="text-xs text-muted mb-2">{change.context}</p>
              )}
              <div className="text-[11px] text-muted-dark">
                {change.time_ago || 'Recently'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
