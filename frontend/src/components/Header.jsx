import React, { useEffect, useState } from 'react';
import { useWatchlist } from '../context/WatchlistContext';

export default function Header({ onOpenSearch, theme, toggleTheme }) {
  const { breadth, lastDataTime, openStockDetail } = useWatchlist();
  const [freshness, setFreshness] = useState('Updated just now');

  useEffect(() => {
    const interval = setInterval(() => {
      const diff = Math.floor((Date.now() - lastDataTime) / 1000);
      if (diff < 30) setFreshness('Updated just now');
      else if (diff < 60) setFreshness(`Updated ${diff} sec ago`);
      else if (diff < 3600) setFreshness(`Updated ${Math.floor(diff/60)} min ago`);
      else setFreshness(`Data delayed · Updated ${Math.floor(diff/3600)}h ago`);
    }, 10000);
    return () => clearInterval(interval);
  }, [lastDataTime]);

  const renderIndex = (name, symbol, changePct) => {
    if (changePct == null) return null;
    const color = changePct >= 0 ? 'text-up' : 'text-down';
    return (
      <span 
        onClick={() => openStockDetail(symbol)}
        className="flex items-center space-x-1 cursor-pointer hover:text-accent transition-colors group"
        title={`View ${name}`}
      >
        <span>{name}</span>
        <span className={color}>{changePct >= 0 ? '+' : ''}{changePct.toFixed(2)}%</span>
      </span>
    );
  };

  return (
    <header className="border-b border-border bg-background px-6 h-14 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center space-x-8">
        <h1 className="text-content font-semibold text-lg tracking-tight">PulseWatch</h1>
        {breadth && (
          <div className="hidden md:flex items-center space-x-4 text-xs text-muted-dark">
            {renderIndex('NIFTY 50', '^NSEI', breadth.nifty_change_pct)}
            {renderIndex('SENSEX', '^BSESN', breadth.sensex_change_pct)}
            {renderIndex('S&P 500', '^GSPC', breadth.sp500_change_pct)}
            <span>VIX {breadth.vix_price?.toFixed(2)}</span>
          </div>
        )}
      </div>

      <div className="flex items-center space-x-6 text-sm">
        <span className="text-muted-dark text-xs">{freshness}</span>
        
        <button 
          onClick={toggleTheme}
          className="text-xl hover:scale-110 transition-transform"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>

        <button 
          onClick={onOpenSearch}
          className="text-accent hover:text-accent/80 transition-colors flex items-center space-x-2 bg-surface px-3 py-1.5 rounded border border-border group"
        >
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span>Search Stocks</span>
          <span className="ml-2 text-[10px] text-muted-dark border border-border/50 rounded px-1.5 py-0.5 bg-background group-hover:border-muted transition-colors">
            ⌘K
          </span>
        </button>
      </div>
    </header>
  );
}
