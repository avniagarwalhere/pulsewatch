import React, { useRef, useEffect, useState } from 'react';
import { useWatchlist } from '../context/WatchlistContext';
import { LineChart, Line, YAxis, ResponsiveContainer } from 'recharts';

function FlashDiv({ value, children, className }) {
  const [flashClass, setFlashClass] = useState('');
  const prevValue = useRef(value);

  useEffect(() => {
    if (prevValue.current !== value && value !== undefined) {
      if (value > prevValue.current) {
        setFlashClass('animate-flash-green');
      } else if (value < prevValue.current) {
        setFlashClass('animate-flash-red');
      }
      const timer = setTimeout(() => setFlashClass(''), 1000);
      prevValue.current = value;
      return () => clearTimeout(timer);
    }
  }, [value]);

  return <div className={`${className} ${flashClass} rounded transition-colors duration-200`}>{children}</div>;
}

export default function MarketOverview() {
  const { breadth, openStockDetail, liveQuotes } = useWatchlist();

  if (!breadth) return null;

  const cards = [
    { name: 'NIFTY 50', symbol: '^NSEI', price: breadth.nifty_price, pct: breadth.nifty_change_pct, currency: '₹' },
    { name: 'SENSEX', symbol: '^BSESN', price: breadth.sensex_price, pct: breadth.sensex_change_pct, currency: '₹' },
    { name: 'S&P 500', symbol: '^GSPC', price: breadth.sp500_price, pct: breadth.sp500_change_pct, currency: '$' },
  ];

  return (
    <section className="py-6 border-b border-border bg-background">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xs font-semibold text-muted-dark uppercase tracking-wider">Market Pulse</h2>
          <div className="flex items-center space-x-2">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-up opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-up"></span>
            </span>
            <span className="text-[10px] text-muted uppercase tracking-wider">Live</span>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {cards.map((idx, i) => {
            const sparkline = liveQuotes?.[idx.symbol]?.sparkline || [];
            const isUp = idx.pct >= 0;
            return (
              <div 
                key={i} 
                onClick={() => openStockDetail(idx.symbol)}
                className="p-4 rounded-lg border border-border bg-surface hover:border-muted transition-colors cursor-pointer group"
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="text-sm font-medium text-content group-hover:text-accent transition-colors">{idx.name}</div>
                  <FlashDiv value={idx.pct} className={`text-sm font-semibold px-2 py-0.5 rounded ${isUp ? 'bg-up/10 text-up' : 'bg-down/10 text-down'}`}>
                    {idx.pct >= 0 ? '+' : ''}{idx.pct?.toFixed(2)}%
                  </FlashDiv>
                </div>
                
                {/* Sparkline graph */}
                {sparkline.length > 2 && (
                  <div className="h-10 w-full opacity-40 group-hover:opacity-70 transition-opacity mb-2">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={sparkline.map((val, j) => ({ v: val, i: j }))}>
                        <YAxis domain={['auto', 'auto']} hide />
                        <Line type="monotone" dataKey="v" stroke={isUp ? '#22c55e' : '#ef4444'} strokeWidth={1.5} dot={false} isAnimationActive={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}

                <FlashDiv value={idx.price} className="text-2xl font-light text-content tabular-nums px-1 w-fit">
                  {idx.currency}{idx.price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </FlashDiv>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
