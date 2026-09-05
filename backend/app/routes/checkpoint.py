from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
from ..database import get_db
from ..models import UserCheckpoint, Watchlist
from ..engine.market_feed import feed_engine
from pydantic import BaseModel

router = APIRouter(prefix="/api/checkpoint", tags=["Checkpoint"])

class CheckpointResponse(BaseModel):
    id: int
    watchlist_id: int
    last_checked_at: datetime
    prices_snapshot: str

@router.get("", response_model=Optional[CheckpointResponse])
def get_checkpoint(watchlist_id: int, db: Session = Depends(get_db)):
    ckpt = db.query(UserCheckpoint).filter(UserCheckpoint.watchlist_id == watchlist_id).order_by(UserCheckpoint.last_checked_at.desc()).first()
    if not ckpt:
        return None
    return ckpt

@router.post("", response_model=CheckpointResponse)
def save_checkpoint(watchlist_id: int, db: Session = Depends(get_db)):
    wl = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist not found")
        
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
    db.refresh(ckpt)
    return ckpt
