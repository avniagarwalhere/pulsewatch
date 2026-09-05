import React, { useEffect, useState } from 'react';
import { useWatchlist } from '../context/WatchlistContext';
import { api } from '../services/api';

export default function ChangeHistoryDrawer() {
  const { isHistoryDrawerOpen, setIsHistoryDrawerOpen, activeWatchlistId } = useWatchlist();
  const [history, setHistoryData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isHistoryDrawerOpen && activeWatchlistId) {
      setLoading(true);
      api.getHistory(activeWatchlistId)
        .then(data => setHistoryData(data))
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [isHistoryDrawerOpen, activeWatchlistId]);

  if (!isHistoryDrawerOpen) return null;

  return (
    <>
      <div 
        className="fixed inset-0 bg-black/40 z-40 transition-opacity"
        onClick={() => setIsHistoryDrawerOpen(false)}
      />
      <div className={`fixed inset-y-0 right-0 w-full max-w-md bg-surface border-l border-border z-50 flex flex-col`}>
        <div className="p-6 border-b border-border flex items-center justify-between">
          <h2 className="text-lg font-medium text-content">History</h2>
          <button onClick={() => setIsHistoryDrawerOpen(false)} className="text-muted hover:text-content text-xl">×</button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="text-muted text-sm text-center">Loading history...</div>
          ) : history.length === 0 ? (
            <div className="text-muted text-sm text-center">No history available.</div>
          ) : (
            <div className="space-y-6">
              {history.map((group, i) => (
                <div key={i}>
                  <h3 className="text-xs font-semibold text-muted-dark uppercase tracking-wider mb-4">
                    {group.date_label}
                  </h3>
                  <div className="space-y-4">
                    {group.events.map(ev => (
                      <div key={ev.id} className="flex space-x-3 text-sm">
                        <div className="text-muted-dark whitespace-nowrap">{ev.time_label}</div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-medium text-content">{ev.symbol}</span>
                            {ev.change_pct != null && (
                              <span className={ev.change_pct >= 0 ? 'text-up' : 'text-down'}>
                                {ev.change_pct >= 0 ? '+' : ''}{ev.change_pct.toFixed(2)}%
                              </span>
                            )}
                          </div>
                          <p className="text-muted mt-0.5">{ev.title}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
