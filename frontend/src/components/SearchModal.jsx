import React, { useState, useEffect } from 'react';
import { useWatchlist } from '../context/WatchlistContext';
import { api } from '../services/api';

export default function SearchModal({ isOpen, onClose }) {
  const { openStockDetail } = useWatchlist();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }
    const timer = setTimeout(() => {
      setLoading(true);
      api.search(query)
        .then(data => setResults(data))
        .catch(console.error)
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  const handleSelect = (symbol) => {
    openStockDetail(symbol.toUpperCase());
    onClose();
    setQuery('');
  };

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const showCustomAdd = query && !results.some(r => r.symbol.toUpperCase() === query.toUpperCase());

  return (
    <div 
      className="fixed inset-0 bg-black/60 z-50 flex items-start justify-center pt-[15vh]"
      onClick={onClose}
    >
      <div 
        className="bg-surface border border-border rounded-lg w-full max-w-lg shadow-2xl flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-4 border-b border-border flex items-center space-x-3">
          <span className="text-muted">
            <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </span>
          <input 
            type="text" 
            autoFocus
            className="flex-1 bg-transparent text-content outline-none placeholder-muted-dark"
            placeholder="Search stocks, ETFs, indices (e.g. ZOMATO.NS)..."
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
          <button onClick={onClose} className="text-muted hover:text-content text-sm">Esc</button>
        </div>
        
        <div className="max-h-96 overflow-y-auto">
          {loading && <div className="p-4 text-center text-sm text-muted">Searching...</div>}
          
          {!loading && results.map(res => (
            <div 
              key={res.symbol}
              onClick={() => handleSelect(res.symbol)}
              className="px-4 py-3 border-b border-border hover:bg-surface-hover cursor-pointer flex justify-between items-center group"
            >
              <div>
                <div className="font-medium text-content">{res.symbol}</div>
                <div className="text-xs text-muted">{res.name}</div>
              </div>
              <button className="text-muted opacity-0 group-hover:opacity-100 transition-opacity text-sm">
                View Details
              </button>
            </div>
          ))}
          
          {!loading && showCustomAdd && (
            <div 
              onClick={() => handleSelect(query)}
              className="px-4 py-3 border-b border-border hover:bg-surface-hover cursor-pointer flex justify-between items-center text-accent group"
            >
              <div>
                <div className="font-medium">Search for "{query.toUpperCase()}"</div>
                <div className="text-xs text-muted">Lookup global ticker directly</div>
              </div>
              <button className="opacity-0 group-hover:opacity-100 transition-opacity text-sm">
                View Details
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
