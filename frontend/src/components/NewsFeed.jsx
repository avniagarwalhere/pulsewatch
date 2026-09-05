import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function NewsFeed() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const data = await api.getNews();
        setNews(data || []);
      } catch (e) {
        console.error('News fetch error:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchNews();
    const interval = setInterval(fetchNews, 120000); // refresh every 2 min
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="space-y-3">
        {[1,2,3,4].map(i => (
          <div key={i} className="animate-pulse p-4 bg-surface rounded-lg border border-border">
            <div className="h-4 bg-surface-hover rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-surface-hover rounded w-1/3"></div>
          </div>
        ))}
      </div>
    );
  }

  if (news.length === 0) {
    return <p className="text-muted text-sm">No news available right now.</p>;
  }

  return (
    <div className="space-y-3">
      {news.map((item, i) => {
        const timeAgo = item.providerPublishTime
          ? formatTimeAgo(item.providerPublishTime)
          : '';
        return (
          <a
            key={i}
            href={item.link}
            target="_blank"
            rel="noopener noreferrer"
            className="block p-4 bg-surface rounded-lg border border-border hover:border-muted hover:bg-surface-hover transition-all group"
          >
            <div className="flex items-start space-x-3">
              {item.thumbnail && (
                <img 
                  src={item.thumbnail} 
                  alt="" 
                  className="w-16 h-12 object-cover rounded flex-shrink-0"
                  onError={(e) => e.target.style.display = 'none'}
                />
              )}
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-content group-hover:text-accent transition-colors line-clamp-2 leading-tight">
                  {item.title}
                </h4>
                <div className="flex items-center space-x-2 mt-1.5">
                  <span className="text-xs text-muted">{item.publisher}</span>
                  {timeAgo && <span className="text-xs text-muted-dark">· {timeAgo}</span>}
                </div>
              </div>
            </div>
          </a>
        );
      })}
    </div>
  );
}

function formatTimeAgo(timestamp) {
  const now = Math.floor(Date.now() / 1000);
  const diff = now - timestamp;
  if (diff < 60) return 'Just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}
