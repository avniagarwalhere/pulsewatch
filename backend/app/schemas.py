from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class WatchlistItemBase(BaseModel):
    symbol: str
    name: Optional[str] = None
    sector: Optional[str] = 'Technology'
    notes: Optional[str] = None
    order_index: Optional[int] = 0

class WatchlistItemCreate(WatchlistItemBase):
    pass

class WatchlistItemUpdate(BaseModel):
    notes: Optional[str] = None
    order_index: Optional[int] = None

class WatchlistItemResponse(WatchlistItemBase):
    id: int
    watchlist_id: int
    added_at: datetime
    model_config = ConfigDict(from_attributes=True)

class WatchlistBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = '#8b5cf6'
    is_default: Optional[bool] = False

class WatchlistCreate(WatchlistBase):
    symbols: Optional[List[WatchlistItemCreate]] = None

class WatchlistResponse(WatchlistBase):
    id: int
    created_at: datetime
    updated_at: datetime
    items: List[WatchlistItemResponse] = []
    model_config = ConfigDict(from_attributes=True)

class StockQuote(BaseModel):
    symbol: str
    name: str
    sector: str
    price: float
    change: float
    change_pct: float
    open: float
    high: float
    low: float
    prev_close: float
    volume: int
    avg_volume_20d: int
    data_age_seconds: int
    data_state: str  # "fresh"|"delayed"|"stale"|"market_closed"
    volume_ratio: float
    since_last_check_pct: Optional[float] = None
    sparkline: List[float]
    notes: Optional[str] = None

class MarketBreadth(BaseModel):
    sp500_price: float
    sp500_change_pct: float
    nasdaq_price: float
    nasdaq_change_pct: float
    vix_price: float
    vix_change_pct: float
    nifty_price: float
    nifty_change_pct: float
    sensex_price: float
    sensex_change_pct: float
    us10y_yield: float
    us10y_change_bp: float
    advancers: int
    decliners: int
    market_phase: str
    data_feed_status: str
    latency_ms: int

class MarketEventResponse(BaseModel):
    id: int
    symbol: str
    event_type: str
    title: str
    description: Optional[str] = None
    severity: str
    price_change_pct: Optional[float] = None
    volume_ratio: Optional[float] = None
    market_relative_move: Optional[float] = None
    confidence: float
    source: str
    timestamp: datetime
    created_at: datetime
    state: str = 'NEW'  # NEW, SEEN, DISMISSED
    seen_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class CatchUpResponse(BaseModel):
    last_checked_at: Optional[datetime] = None
    elapsed_label: str
    meaningful_changes: List[MarketEventResponse]
    minor_changes: List[MarketEventResponse]
    all_caught_up: bool

class EventSeenStateUpdate(BaseModel):
    state: str

class ShockRequest(BaseModel):
    symbol: str
    shock_type: str
    magnitude_pct: Optional[float] = None
    headline: Optional[str] = None

class FeedModeRequest(BaseModel):
    feed_mode: str
