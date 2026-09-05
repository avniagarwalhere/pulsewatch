import React, { useState, useEffect } from 'react';
import { WatchlistProvider, useWatchlist } from './context/WatchlistContext';
import Header from './components/Header';
import MarketOverview from './components/MarketOverview';
import WhileYouWereAway from './components/WhileYouWereAway';
import WatchlistSection from './components/WatchlistSection';
import StockDetailPage from './components/StockDetailPage';
import ChangeHistoryDrawer from './components/ChangeHistoryDrawer';
import DigestPage from './components/DigestPage';
import SearchModal from './components/SearchModal';
import CreateWatchlistModal from './components/CreateWatchlistModal';
import NewsFeed from './components/NewsFeed';
import TrendingStocks from './components/TrendingStocks';
import SectorPerformance from './components/SectorPerformance';

function AppContent() {
  const { 
    loading, 
    catchup, 
    setIsHistoryDrawerOpen, 
    activeWatchlistId,
    saveCheckpoint
  } = useWatchlist();
  
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isCreateWatchlistOpen, setIsCreateWatchlistOpen] = useState(false);
  const [theme, setTheme] = useState('dark');
  const [currentTab, setCurrentTab] = useState('dashboard');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark');

  // Save checkpoint on unmount or visibility change
  useEffect(() => {
    const handleVisibility = () => {
      if (document.visibilityState === 'hidden' && activeWatchlistId) {
        saveCheckpoint();
      }
    };
    window.addEventListener('visibilitychange', handleVisibility);
    
    const handleBeforeUnload = () => {
      if (activeWatchlistId) saveCheckpoint();
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    // Global keyboard shortcuts
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsSearchOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('visibilitychange', handleVisibility);
      window.removeEventListener('beforeunload', handleBeforeUnload);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [activeWatchlistId, saveCheckpoint]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-muted">
        Loading PulseWatch...
      </div>
    );
  }

  const allChanges = [...(catchup?.meaningful_changes || []), ...(catchup?.minor_changes || [])];

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Header onOpenSearch={() => setIsSearchOpen(true)} theme={theme} toggleTheme={toggleTheme} />
      
      <div className="border-b border-border bg-background sticky top-14 z-20">
        <div className="max-w-7xl mx-auto px-6 flex space-x-8">
          <button 
            onClick={() => setCurrentTab('dashboard')}
            className={`py-4 text-sm font-medium border-b-2 transition-colors ${
              currentTab === 'dashboard' ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-content'
            }`}
          >
            Dashboard
          </button>
          <button 
            onClick={() => setCurrentTab('digest')}
            className={`py-4 text-sm font-medium border-b-2 transition-colors flex items-center space-x-2 ${
              currentTab === 'digest' ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-content'
            }`}
          >
            <span>Digest Feed</span>
            {allChanges.length > 0 && (
              <span className="bg-accent text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                {allChanges.length}
              </span>
            )}
          </button>
          <button 
            onClick={() => setCurrentTab('news')}
            className={`py-4 text-sm font-medium border-b-2 transition-colors ${
              currentTab === 'news' ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-content'
            }`}
          >
            News
          </button>
        </div>
      </div>

      <main className="flex-1">
        {currentTab === 'dashboard' ? (
          <>
            <MarketOverview />
            <div className="max-w-7xl mx-auto px-6 py-8">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2">
                  <WatchlistSection onOpenSearch={() => setIsSearchOpen(true)} />
                </div>
                <div className="space-y-8">
                  <div>
                    <h3 className="text-sm font-semibold text-muted-dark uppercase tracking-wider mb-4">🔥 Market Movers</h3>
                    <TrendingStocks />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-muted-dark uppercase tracking-wider mb-4">Sector Performance</h3>
                    <SectorPerformance />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-muted-dark uppercase tracking-wider mb-4">Latest News</h3>
                    <NewsFeed />
                  </div>
                </div>
              </div>
            </div>
          </>
        ) : currentTab === 'digest' ? (
          <DigestPage />
        ) : (
          <div className="max-w-4xl mx-auto px-6 py-8">
            <h2 className="text-xl font-semibold text-content mb-6">Market News</h2>
            <NewsFeed />
          </div>
        )}
      </main>

      <footer className="border-t border-border bg-background py-6 text-center">
        <div className="text-sm text-muted">
          <span>{allChanges.length} recent events</span>
          <span className="mx-3">·</span>
          <button 
            onClick={() => setIsHistoryDrawerOpen(true)}
            className="hover:text-content transition-colors underline decoration-border underline-offset-4"
          >
            View full history
          </button>
        </div>
      </footer>

      <StockDetailPage theme={theme} />
      <ChangeHistoryDrawer />
      
      <SearchModal 
        isOpen={isSearchOpen} 
        onClose={() => setIsSearchOpen(false)} 
      />
      
      <CreateWatchlistModal
        isOpen={isCreateWatchlistOpen}
        onClose={() => setIsCreateWatchlistOpen(false)}
      />
    </div>
  );
}

export default function App() {
  return (
    <WatchlistProvider>
      <AppContent />
    </WatchlistProvider>
  );
}
