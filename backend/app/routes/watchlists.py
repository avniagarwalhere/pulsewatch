from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import json
from ..database import get_db
from ..models import Watchlist, WatchlistItem, UserCheckpoint
from ..schemas import WatchlistCreate, WatchlistResponse, WatchlistItemCreate, WatchlistItemUpdate, WatchlistItemResponse
from ..engine.market_feed import DEFAULT_UNIVERSE, feed_engine

router = APIRouter(prefix="/api/watchlists", tags=["Watchlists"])

@router.get("", response_model=List[WatchlistResponse])
def get_all_watchlists(db: Session = Depends(get_db)):
    lists = db.query(Watchlist).all()
    if not lists:
        init_default_watchlists(db)
        lists = db.query(Watchlist).all()
    return lists

@router.post("", response_model=WatchlistResponse)
def create_watchlist(payload: WatchlistCreate, db: Session = Depends(get_db)):
    wl = Watchlist(
        name=payload.name,
        description=payload.description,
        color=payload.color or "#8b5cf6",
        is_default=payload.is_default or False
    )
    db.add(wl)
    db.commit()
    db.refresh(wl)

    if payload.symbols:
        for idx, item in enumerate(payload.symbols):
            meta = DEFAULT_UNIVERSE.get(item.symbol.upper(), {})
            w_item = WatchlistItem(
                watchlist_id=wl.id,
                symbol=item.symbol.upper(),
                name=item.name or meta.get("name", item.symbol.upper()),
                sector=item.sector or meta.get("sector", "Technology"),
                notes=item.notes,
                order_index=idx
            )
            db.add(w_item)
        db.commit()
        db.refresh(wl)
        _create_checkpoint(db, wl.id)

    return wl

@router.get("/{watchlist_id}", response_model=WatchlistResponse)
def get_watchlist(watchlist_id: int, db: Session = Depends(get_db)):
    wl = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    return wl

@router.delete("/{watchlist_id}")
def delete_watchlist(watchlist_id: int, db: Session = Depends(get_db)):
    wl = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    if wl.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default system watchlist")
    db.delete(wl)
    db.commit()
    return {"status": "success", "message": f"Watchlist {watchlist_id} deleted"}

@router.post("/{watchlist_id}/items", response_model=WatchlistItemResponse)
def add_item_to_watchlist(watchlist_id: int, item: WatchlistItemCreate, db: Session = Depends(get_db)):
    wl = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    meta = DEFAULT_UNIVERSE.get(item.symbol.upper(), {})
    count = db.query(WatchlistItem).filter(WatchlistItem.watchlist_id == watchlist_id).count()
    
    w_item = WatchlistItem(
        watchlist_id=watchlist_id,
        symbol=item.symbol.upper(),
        name=item.name or meta.get("name", item.symbol.upper()),
        sector=item.sector or meta.get("sector", "General Equities"),
        notes=item.notes,
        order_index=count
    )
    db.add(w_item)
    db.commit()
    db.refresh(w_item)
    _create_checkpoint(db, watchlist_id)
    return w_item

@router.delete("/{watchlist_id}/items/{symbol}")
def remove_item_from_watchlist(watchlist_id: int, symbol: str, db: Session = Depends(get_db)):
    item = db.query(WatchlistItem).filter(
        WatchlistItem.watchlist_id == watchlist_id,
        WatchlistItem.symbol == symbol.upper()
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Symbol not found in watchlist")
    db.delete(item)
    db.commit()
    return {"status": "success", "message": f"{symbol} removed from watchlist"}

@router.put("/{watchlist_id}/items/{symbol}", response_model=WatchlistItemResponse)
def update_watchlist_item(watchlist_id: int, symbol: str, payload: WatchlistItemUpdate, db: Session = Depends(get_db)):
    item = db.query(WatchlistItem).filter(
        WatchlistItem.watchlist_id == watchlist_id,
        WatchlistItem.symbol == symbol.upper()
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Symbol not found in watchlist")
    
    if payload.notes is not None:
        item.notes = payload.notes
    if payload.order_index is not None:
        item.order_index = payload.order_index

    db.commit()
    db.refresh(item)
    return item

def _create_checkpoint(db: Session, watchlist_id: int):
    wl = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
    if not wl:
        return
    prices = {}
    for item in wl.items:
        q = feed_engine.get_quote(item.symbol)
        if q:
            prices[item.symbol] = q['price']
            
    ckpt = UserCheckpoint(
        watchlist_id=watchlist_id,
        prices_snapshot=json.dumps(prices),
        last_checked_at=datetime.utcnow()
    )
    db.add(ckpt)
    db.commit()

def init_default_watchlists(db: Session):
    w1 = Watchlist(name="My Watchlist", description="Core holdings", is_default=True, color="#8b5cf6")
    w2 = Watchlist(name="Long term", description="Long term plays", is_default=False, color="#10b981")
    w3 = Watchlist(name="Trading", description="Short term momentum", is_default=False, color="#f59e0b")
    db.add_all([w1, w2, w3])
    db.commit()
    db.refresh(w1)
    db.refresh(w2)
    db.refresh(w3)

    all_indian_syms = [s for s in DEFAULT_UNIVERSE.keys() if s.endswith('.NS') or s.endswith('.BO')]
    all_us_syms = [s for s in DEFAULT_UNIVERSE.keys() if not s.endswith('.NS') and not s.endswith('.BO') and not s.startswith('^')]

    w1_syms = [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
        'ZOMATO.NS', 'TATAMOTORS.NS', 'BHARTIARTL.NS', 'SBIN.NS', 'LT.NS',
        'ITC.NS', 'TITAN.NS', 'BAJFINANCE.NS', 'SUNPHARMA.NS',
        'NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA'
    ]
    for idx, sym in enumerate(w1_syms):
        meta = DEFAULT_UNIVERSE.get(sym, {})
        db.add(WatchlistItem(watchlist_id=w1.id, symbol=sym, name=meta.get("name", sym), sector=meta.get("sector", "Equity"), order_index=idx))

    w2_syms = [
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'LT.NS', 'ITC.NS',
        'HINDUNILVR.NS', 'TITAN.NS', 'ASIANPAINT.NS', 'ULTRACEMCO.NS',
        'MSFT', 'AAPL', 'GOOGL', 'AMZN', 'BRK-B'
    ]
    for idx, sym in enumerate(w2_syms):
        meta = DEFAULT_UNIVERSE.get(sym, {})
        db.add(WatchlistItem(watchlist_id=w2.id, symbol=sym, name=meta.get("name", sym), sector=meta.get("sector", "Equity"), order_index=idx))

    w3_syms = [
        'ZOMATO.NS', 'TATAMOTORS.NS', 'ADANIENT.NS', 'BAJFINANCE.NS', 'JIOFIN.NS',
        'NVDA', 'TSLA', 'AMD', 'COIN', 'PLTR', 'SPY', 'QQQ'
    ]
    for idx, sym in enumerate(w3_syms):
        meta = DEFAULT_UNIVERSE.get(sym, {})
        db.add(WatchlistItem(watchlist_id=w3.id, symbol=sym, name=meta.get("name", sym), sector=meta.get("sector", "Equity"), order_index=idx))

    w4 = Watchlist(name="Indian Markets", description="Top NIFTY 50 Stocks", is_default=False, color="#ec4899")
    w5 = Watchlist(name="US Markets", description="Top US Tech & Broad Market", is_default=False, color="#3b82f6")
    db.add_all([w4, w5])
    db.commit()
    db.refresh(w4)
    db.refresh(w5)

    for idx, sym in enumerate(all_indian_syms):
        meta = DEFAULT_UNIVERSE.get(sym, {})
        db.add(WatchlistItem(watchlist_id=w4.id, symbol=sym, name=meta.get("name", sym), sector=meta.get("sector", "Equity"), order_index=idx))

    for idx, sym in enumerate(all_us_syms):
        meta = DEFAULT_UNIVERSE.get(sym, {})
        db.add(WatchlistItem(watchlist_id=w5.id, symbol=sym, name=meta.get("name", sym), sector=meta.get("sector", "Equity"), order_index=idx))

    db.commit()
    
    _create_checkpoint(db, w1.id)
    _create_checkpoint(db, w2.id)
    _create_checkpoint(db, w3.id)
    _create_checkpoint(db, w4.id)
    _create_checkpoint(db, w5.id)

