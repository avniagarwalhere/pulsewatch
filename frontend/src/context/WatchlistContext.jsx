import React, { createContext, useContext, useEffect, useState, useRef, useCallback } from 'react';
import { api, WS_BASE } from '../services/api';

const WatchlistContext = createContext(null);

export const useWatchlist = () => useContext(WatchlistContext);

export const WatchlistProvider = ({ children }) => {
  const [watchlists, setWatchlists] = useState([]);
  const [activeWatchlistId, setActiveWatchlistId] = useState(null);
  
  const [quotes, setQuotes] = useState([]);
  const [breadth, setBreadth] = useState(null);
  
  const [liveQuotes, setLiveQuotes] = useState({});
  const [catchup, setCatchup] = useState({ meaningful_changes: [], minor_changes: [], all_caught_up: true, elapsed_label: 'Never' });
  
  const [checkpoint, setCheckpoint] = useState(null);
  
  const [selectedStock, setSelectedStock] = useState(null);
  const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false);
  const [isHistoryDrawerOpen, setIsHistoryDrawerOpen] = useState(false);
  
  const [lastDataTime, setLastDataTime] = useState(Date.now());
  const [loading, setLoading] = useState(true);

  const wsRef = useRef(null);

  useEffect(() => {
    loadWatchlists();
  }, []);

  useEffect(() => {
    if (activeWatchlistId) {
      loadWatchlistData(activeWatchlistId);
      setupWebSocket();
    }
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [activeWatchlistId]);

  const loadWatchlists = async () => {
    try {
      const data = await api.getWatchlists();
      setWatchlists(data);
      if (data.length > 0 && !activeWatchlistId) {
        setActiveWatchlistId(data[0].id);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadWatchlistData = async (id) => {
    setLoading(true);
    try {
      const [qData, bData, cData, cpData] = await Promise.all([
        api.getQuotes(id),
        api.getBreadth(),
        api.getCatchup(id),
        api.getCheckpoint(id).catch(() => null)
      ]);
      setQuotes(qData || []);
      
      // Seed liveQuotes with the initial watchlist fetch
      if (qData) {
        setLiveQuotes(prev => {
          const next = { ...prev };
          qData.forEach(q => next[q.symbol] = q);
          return next;
        });
      }
      
      setBreadth(bData);
      setCatchup(cData || { meaningful_changes: [], minor_changes: [], all_caught_up: true, elapsed_label: 'Never' });
      setCheckpoint(cpData);
      setLastDataTime(Date.now());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    if (wsRef.current) wsRef.current.close();
    const ws = new WebSocket(WS_BASE);
    wsRef.current = ws;
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'MARKET_TICK' || data.type === 'INITIAL_SNAPSHOT') {
          if (data.breadth) setBreadth(data.breadth);
          if (data.quotes) {
            
            // 1. Maintain global live dictionary for ANY symbol (for StockDetailPage)
            setLiveQuotes(prev => {
              const next = { ...prev };
              for (const incoming of data.quotes) {
                next[incoming.symbol] = incoming;
              }
              return next;
            });

            // 2. Update the specific current watchlist quotes array
            if (activeWatchlistId) {
              setQuotes(prev => {
                const updated = [...prev];
                for (const incoming of data.quotes) {
                  const idx = updated.findIndex(q => q.symbol === incoming.symbol);
                  if (idx >= 0) {
                    updated[idx] = {
                      ...updated[idx],
                      price: incoming.price,
                      change: incoming.change,
                      change_pct: incoming.change_pct,
                      volume: incoming.volume,
                      high: incoming.high,
                      low: incoming.low,
                      sparkline: incoming.sparkline || updated[idx].sparkline,
                    };
                  }
                }
                return updated;
              });
            }
          }
          setLastDataTime(Date.now());
        }
      } catch (e) {
        console.error("WS msg error", e);
      }
    };

    ws.onclose = () => {
      // Reconnect after 3s
      setTimeout(() => {
        if (activeWatchlistId) setupWebSocket();
      }, 3000);
    };
  };

  const markEventSeen = async (eventId) => {
    try {
      await api.markSeen(eventId);
      setCatchup(prev => {
        const mark = (list) => list.map(ev => ev.id === eventId ? { ...ev, seen: true, state: 'SEEN' } : ev);
        const newMeaningful = mark(prev.meaningful_changes || []);
        const newMinor = mark(prev.minor_changes || []);
        const allSeen = [...newMeaningful, ...newMinor].every(ev => ev.seen);
        return {
          ...prev,
          meaningful_changes: newMeaningful,
          minor_changes: newMinor,
          all_caught_up: allSeen,
        };
      });
    } catch (e) {
      console.error(e);
    }
  };

  const markAllEventsSeen = useCallback(async () => {
    if (!activeWatchlistId) return;
    try {
      await api.markAllSeen(activeWatchlistId);
      setCatchup(prev => {
        const mark = (list) => list.map(ev => ({ ...ev, seen: true, state: 'SEEN' }));
        return {
          ...prev,
          meaningful_changes: mark(prev.meaningful_changes || []),
          minor_changes: mark(prev.minor_changes || []),
          all_caught_up: true
        };
      });
    } catch (e) {
      console.error(e);
    }
  }, [activeWatchlistId]);

  const saveCheckpoint = useCallback(async () => {
    if (!activeWatchlistId) return;
    try {
      const cp = await api.saveCheckpoint(activeWatchlistId);
      setCheckpoint(cp);
    } catch (e) {
      console.error(e);
    }
  }, [activeWatchlistId]);

  const openStockDetail = (symbol) => {
    setSelectedStock(symbol);
    setIsDetailDrawerOpen(true);
  };

  const closeStockDetail = useCallback(() => {
    setIsDetailDrawerOpen(false);
    setTimeout(() => setSelectedStock(null), 300);
  }, []);

  return (
    <WatchlistContext.Provider value={{
      watchlists,
      activeWatchlistId,
      setActiveWatchlistId,
      quotes,
      liveQuotes,
      breadth,
      catchup,
      checkpoint,
      loading,
      lastDataTime,
      selectedStock,
      isDetailDrawerOpen,
      isHistoryDrawerOpen,
      setIsHistoryDrawerOpen,
      loadWatchlists,
      loadWatchlistData,
      markEventSeen,
      markAllEventsSeen,
      saveCheckpoint,
      openStockDetail,
      closeStockDetail,
    }}>
      {children}
    </WatchlistContext.Provider>
  );
};
