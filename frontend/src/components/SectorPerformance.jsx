import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function SectorPerformance() {
  const [sectors, setSectors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSectors = async () => {
      try {
        const data = await api.getSectors();
        setSectors(data || []);
      } catch(e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchSectors();
    const interval = setInterval(fetchSectors, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading || sectors.length === 0) return null;

  const maxAbs = Math.max(...sectors.map(s => Math.abs(s.change_pct)), 1);

  return (
    <div className="space-y-2">
      {sectors.map((sector, i) => {
        const isUp = sector.change_pct >= 0;
        const barWidth = Math.min((Math.abs(sector.change_pct) / maxAbs) * 100, 100);
        return (
          <div key={i} className="flex items-center space-x-3">
            <div className="w-32 text-xs text-content font-medium truncate">{sector.name}</div>
            <div className="flex-1 h-5 bg-surface-hover rounded-full overflow-hidden relative">
              <div
                className={`h-full rounded-full transition-all duration-500 ${isUp ? 'bg-up/30' : 'bg-down/30'}`}
                style={{ width: `${barWidth}%` }}
              />
            </div>
            <div className={`w-16 text-right text-xs font-semibold tabular-nums ${isUp ? 'text-up' : 'text-down'}`}>
              {isUp ? '+' : ''}{sector.change_pct.toFixed(2)}%
            </div>
            <div className="w-8 text-right text-[10px] text-muted">{sector.stock_count}</div>
          </div>
        );
      })}
    </div>
  );
}
