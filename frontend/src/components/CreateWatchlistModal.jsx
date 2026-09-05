import React, { useState } from 'react';
import { useWatchlist } from '../context/WatchlistContext';
import { api } from '../services/api';

export default function CreateWatchlistModal({ isOpen, onClose }) {
  const { loadWatchlists } = useWatchlist();
  const [name, setName] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    await api.createWatchlist(name.trim());
    loadWatchlists();
    onClose();
    setName('');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center">
      <div className="bg-surface border border-border rounded-lg w-full max-w-sm shadow-2xl p-6">
        <h3 className="text-lg font-medium text-content mb-4">Create Watchlist</h3>
        <form onSubmit={handleSubmit}>
          <input 
            type="text"
            autoFocus
            className="w-full bg-background border border-border rounded px-3 py-2 text-content outline-none focus:border-accent mb-6"
            placeholder="Watchlist name"
            value={name}
            onChange={e => setName(e.target.value)}
          />
          <div className="flex justify-end space-x-3 text-sm">
            <button 
              type="button" 
              onClick={onClose}
              className="text-muted hover:text-content px-3 py-2"
            >
              Cancel
            </button>
            <button 
              type="submit"
              className="bg-accent text-white px-4 py-2 rounded hover:bg-accent/90 transition-colors"
            >
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
