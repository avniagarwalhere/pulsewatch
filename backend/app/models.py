from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Watchlist(Base):
    __tablename__ = 'watchlists'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    is_default = Column(Boolean, default=False)
    color = Column(String(30), default='#8b5cf6')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship('WatchlistItem', back_populates='watchlist', cascade='all, delete-orphan')
    snapshots = relationship('UserSnapshot', back_populates='watchlist', cascade='all, delete-orphan')
    checkpoints = relationship('UserCheckpoint', back_populates='watchlist', cascade='all, delete-orphan')

class WatchlistItem(Base):
    __tablename__ = 'watchlist_items'

    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey('watchlists.id', ondelete='CASCADE'), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    sector = Column(String(50), default='Technology')
    notes = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    added_at = Column(DateTime, default=datetime.utcnow)

    watchlist = relationship('Watchlist', back_populates='items')

class UserSnapshot(Base):
    __tablename__ = 'user_snapshots'

    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey('watchlists.id', ondelete='CASCADE'), nullable=False)
    label = Column(String(100), default='Auto Checkpoint')
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    snapshot_json = Column(Text, nullable=False)

    watchlist = relationship('Watchlist', back_populates='snapshots')

class UserCheckpoint(Base):
    __tablename__ = 'user_checkpoints'
    
    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey('watchlists.id', ondelete='CASCADE'), nullable=False)
    last_checked_at = Column(DateTime, default=datetime.utcnow, index=True)
    prices_snapshot = Column(Text, nullable=True)  # JSON of prices at checkpoint time
    
    watchlist = relationship('Watchlist', back_populates='checkpoints')

class MarketEvent(Base):
    __tablename__ = 'market_events'
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # PRICE_MOVE, VOLUME_SPIKE, EARNINGS, NEWS, GUIDANCE_CHANGE, MARKET_RELATIVE_MOVE, UNUSUAL_VOLATILITY, DATA_WARNING
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), default='normal')  # needs_attention, worth_checking, normal
    price_change_pct = Column(Float, nullable=True)
    volume_ratio = Column(Float, nullable=True)
    market_relative_move = Column(Float, nullable=True)
    confidence = Column(Float, default=0.8)
    source = Column(String(100), default='PulseWatch')
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EventSeenState(Base):
    __tablename__ = 'event_seen_state'
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('market_events.id', ondelete='CASCADE'), nullable=False)
    watchlist_id = Column(Integer, ForeignKey('watchlists.id', ondelete='CASCADE'), nullable=False)
    state = Column(String(20), default='NEW')  # NEW, SEEN, DISMISSED
    seen_at = Column(DateTime, nullable=True)
