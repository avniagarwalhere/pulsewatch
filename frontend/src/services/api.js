const isHttps = typeof window !== 'undefined' && window.location.protocol === 'https:';
const host = typeof window !== 'undefined' ? window.location.host : 'localhost:3000';
const wsProtocol = isHttps ? 'wss:' : 'ws:';

export const API_BASE = typeof window !== 'undefined' 
  ? `${window.location.origin}/api` 
  : 'http://localhost:8000/api';

export const WS_BASE = typeof window !== 'undefined'
  ? `${wsProtocol}//${host}/ws`
  : 'ws://localhost:8000/ws';

export const api = {
  getWatchlists: () => fetch(`${API_BASE}/watchlists`).then(r => r.json()),
  createWatchlist: (name) => fetch(`${API_BASE}/watchlists`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  }).then(r => r.json()),
  deleteWatchlist: (id) => fetch(`${API_BASE}/watchlists/${id}`, { method: 'DELETE' }),
  
  addStock: (watchlistId, symbol) => fetch(`${API_BASE}/watchlists/${watchlistId}/items`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol })
  }).then(r => r.json()),
  removeStock: (watchlistId, symbol) => fetch(`${API_BASE}/watchlists/${watchlistId}/items/${symbol}`, { method: 'DELETE' }),

  getQuotes: (watchlistId) => fetch(`${API_BASE}/market/quotes?watchlist_id=${watchlistId}`).then(r => r.json()),
  getDetail: (symbol) => fetch(`${API_BASE}/market/detail/${symbol}`).then(r => r.json()),
  getBreadth: () => fetch(`${API_BASE}/market/breadth`).then(r => r.json()),
  search: (q) => fetch(`${API_BASE}/market/search?q=${encodeURIComponent(q)}`).then(r => r.json()),

   getNews: async () => {
    const r = await fetch(`${API_BASE}/market/news`);
    return r.json();
  },
  getTrending: async (market = 'IN') => {
    const r = await fetch(`${API_BASE}/market/trending?market=${market}`);
    return r.json();
  },
  getRecommendations: async (watchlistId, limit = 3) => {
    const r = await fetch(`${API_BASE}/market/recommendations?limit=${limit}${watchlistId ? `&watchlist_id=${watchlistId}` : ''}`);
    return r.json();
  },
  getSectors: async () => {
    const r = await fetch(`${API_BASE}/market/sectors`);
    return r.json();
  },
  getDigest: async (watchlistId) => {
    const r = await fetch(`${API_BASE}/events/digest${watchlistId ? `?watchlist_id=${watchlistId}` : ''}`);
    return r.json();
  },

  getCatchup: (watchlistId) => fetch(`${API_BASE}/events/catchup?watchlist_id=${watchlistId}`).then(r => r.json()),
  markSeen: (eventId) => fetch(`${API_BASE}/events/${eventId}/seen`, { method: 'POST' }).then(r => r.json()),
  markAllSeen: (watchlistId) => fetch(`${API_BASE}/events/mark-all-seen?watchlist_id=${watchlistId}`, { method: 'POST' }).then(r => r.json()),
  getHistory: (watchlistId) => fetch(`${API_BASE}/events/history?watchlist_id=${watchlistId}`).then(r => r.json()),

  saveCheckpoint: (watchlistId) => fetch(`${API_BASE}/checkpoint?watchlist_id=${watchlistId}`, { method: 'POST' }).then(r => r.json()),
  getCheckpoint: (watchlistId) => fetch(`${API_BASE}/checkpoint?watchlist_id=${watchlistId}`).then(r => r.json()),
};
