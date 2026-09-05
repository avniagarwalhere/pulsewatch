import json
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import UserCheckpoint, MarketEvent, EventSeenState, Watchlist
from .market_feed import feed_engine

def detect_events_for_watchlist(db: Session, watchlist_id: int):
    # Get latest checkpoint
    checkpoint = db.query(UserCheckpoint).filter(UserCheckpoint.watchlist_id == watchlist_id).order_by(UserCheckpoint.last_checked_at.desc()).first()
    if not checkpoint or not checkpoint.prices_snapshot:
        return
    
    try:
        prev_prices = json.loads(checkpoint.prices_snapshot)
    except Exception:
        return

    wl = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
    if not wl:
        return
    
    symbols = [item.symbol for item in wl.items]
    
    for sym in symbols:
        quote = feed_engine.get_quote(sym)
        if not quote:
            continue
            
        current_price = quote['price']
        prev_price = prev_prices.get(sym)
        
        if not prev_price:
            continue
            
        # Significance Score Engine logic
        price_then = prev_price
        if price_then == 0:
            price_then = current_price
            
        pct_move = ((current_price - price_then) / price_then) * 100.0
        
        # 1. Volatility-normalized move (z-score vs the stock's own ATR)
        atr_pct = max(quote.get('atr', 2.0) / price_then * 100, 0.1)
        z_score = abs(pct_move) / atr_pct
        move_component = min(z_score / 3, 1.0) * 30
        
        # 2. Relative volume
        rel_volume = quote.get('volume_ratio', quote.get('rvol', 1.0))
        volume_component = min(rel_volume / 3, 1.0) * 25
        
        # 3. Technical level crossing
        level_component = 0
        tags = []
        high52 = quote.get('high52')
        low52 = quote.get('low52')
        
        if high52 and current_price >= high52 and price_then < high52:
            level_component = 15
            tags.append("crossed_52w_high")
        elif low52 and current_price <= low52 and price_then > low52:
            level_component = 15
            tags.append("crossed_52w_low")
            
        # 4. News correlation (mocked for now)
        news_component = 0
        
        # 5. Session gap (time since last seen)
        if checkpoint.last_checked_at:
            hours_since_seen = (datetime.utcnow() - checkpoint.last_checked_at).total_seconds() / 3600
            gap_component = min(hours_since_seen / 24, 1.0) * 10
        else:
            gap_component = 0
            
        # 6. Custom user alert (skipped in base version)
        custom_component = 0
        
        if rel_volume >= 2:
            tags.append("volume_spike")
        if abs(pct_move) > atr_pct * 1.5:
            tags.append("outsized_move")
            
        total_score = round(min(move_component + volume_component + level_component + news_component + gap_component + custom_component, 100), 1)
        
        conviction = "high_signal" if total_score >= 60 else "watch" if total_score >= 35 else "noise"
        
        if conviction == "noise":
            continue
            
        # Map back to MarketEvent structure
        sev = 'needs_attention' if conviction == "high_signal" else 'worth_checking'
        direction = 'up' if pct_move > 0 else 'down'
        
        # Determine event type based on dominant tag
        event_type = 'PRICE_MOVE'
        if "crossed_52w_high" in tags or "crossed_52w_low" in tags:
            event_type = 'TECHNICAL_LEVEL'
        elif "volume_spike" in tags and move_component < volume_component:
            event_type = 'VOLUME_SPIKE'
            
        title = f"{sym} moved {abs(pct_move):.1f}% {direction}"
        if "crossed_52w_high" in tags:
            title = f"{sym} broke 52-week High"
        elif "crossed_52w_low" in tags:
            title = f"{sym} broke 52-week Low"
        elif "volume_spike" in tags and event_type == 'VOLUME_SPIKE':
            title = f"Unusual volume in {sym}"
            
        desc_tags = ", ".join([t.replace('_', ' ') for t in tags])
        description = f"Significance Score: {total_score}/100. Tags: {desc_tags}." if tags else f"Significance Score: {total_score}/100."
        
        # Determine market relative move
        breadth = feed_engine.get_breadth()
        market_move = breadth.get('sp500_change_pct', 0.0)
        relative_move = pct_move - market_move

        # Check if recently created to avoid spam (within last 4 hours)
        from datetime import timedelta
        four_hours_ago = datetime.utcnow() - timedelta(hours=4)
        
        recent = db.query(MarketEvent).filter(
            MarketEvent.symbol == sym,
            MarketEvent.event_type == event_type,
            MarketEvent.timestamp > four_hours_ago
        ).first()
        
        if not recent:
            new_event = MarketEvent(
                symbol=sym,
                event_type=event_type,
                title=title,
                description=description,
                severity=sev,
                price_change_pct=pct_move,
                volume_ratio=rel_volume,
                market_relative_move=relative_move,
                timestamp=datetime.utcnow(),
                confidence=(total_score / 100.0) # Map score to confidence
            )
            db.add(new_event)
            db.flush() # get id
            
            seen_state = EventSeenState(
                event_id=new_event.id,
                watchlist_id=watchlist_id,
                state='NEW'
            )
            db.add(seen_state)
    
    db.commit()

def run_detection_for_all_watchlists(db: Session):
    watchlists = db.query(Watchlist).all()
    for wl in watchlists:
        detect_events_for_watchlist(db, wl.id)
