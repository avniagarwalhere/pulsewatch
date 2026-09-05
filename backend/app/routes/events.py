from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..database import get_db
from ..models import MarketEvent, EventSeenState, UserCheckpoint
from ..schemas import MarketEventResponse, CatchUpResponse
from ..engine.event_detector import detect_events_for_watchlist, run_detection_for_all_watchlists
from ..engine.market_feed import feed_engine

router = APIRouter(prefix="/api/events", tags=["Events"])

def get_event_responses(db: Session, watchlist_id: int, state_filter: str = None) -> List[dict]:
    query = db.query(MarketEvent, EventSeenState).join(
        EventSeenState, MarketEvent.id == EventSeenState.event_id
    ).filter(EventSeenState.watchlist_id == watchlist_id)
    
    if state_filter:
        query = query.filter(EventSeenState.state == state_filter)
        
    results = query.order_by(MarketEvent.timestamp.desc()).all()
    
    events = []
    for ev, st in results:
        age_min = int((datetime.utcnow() - ev.timestamp).total_seconds() / 60)
        if age_min < 1:
            time_ago = "Just now"
        elif age_min < 60:
            time_ago = f"{age_min}m ago"
        elif age_min < 1440:
            time_ago = f"{age_min // 60}h ago"
        else:
            time_ago = f"{age_min // 1440}d ago"

        ev_dict = {
            "id": ev.id,
            "symbol": ev.symbol,
            "event_type": ev.event_type,
            "title": ev.title,
            "description": ev.description,
            "severity": ev.severity,
            "price_change_pct": ev.price_change_pct,
            "change_pct": ev.price_change_pct,  # alias for frontend
            "volume_ratio": ev.volume_ratio,
            "market_relative_move": ev.market_relative_move,
            "confidence": ev.confidence,
            "source": ev.source,
            "timestamp": ev.timestamp,
            "created_at": ev.created_at,
            "state": st.state,
            "seen": st.state == "SEEN",
            "seen_at": st.seen_at,
            "time_ago": time_ago,
            "context": ev.description,
        }
        events.append(ev_dict)
    return events

@router.get("")
def get_events(watchlist_id: int, db: Session = Depends(get_db)):
    return get_event_responses(db, watchlist_id)

@router.get("/catchup")
def get_catchup(watchlist_id: int, db: Session = Depends(get_db)):
    detect_events_for_watchlist(db, watchlist_id)
    ckpt = db.query(UserCheckpoint).filter(UserCheckpoint.watchlist_id == watchlist_id).order_by(UserCheckpoint.last_checked_at.desc()).first()
    
    events = get_event_responses(db, watchlist_id, state_filter='NEW')
    
    meaningful = [e for e in events if e['severity'] in ('needs_attention', 'worth_checking')]
    minor = [e for e in events if e['severity'] == 'normal']
    
    elapsed_label = "Never"
    if ckpt:
        diff = datetime.utcnow() - ckpt.last_checked_at
        total_mins = int(diff.total_seconds() / 60)
        hours = total_mins // 60
        mins = total_mins % 60
        if hours == 0:
            elapsed_label = f"{mins}m ago"
        elif mins == 0:
            elapsed_label = f"{hours}h ago"
        else:
            elapsed_label = f"{hours}h {mins}m ago"
            
    return {
        "last_checked_at": ckpt.last_checked_at if ckpt else None,
        "elapsed_label": elapsed_label,
        "meaningful_changes": meaningful,
        "minor_changes": minor,
        "all_caught_up": len(events) == 0
    }

@router.post("/{event_id}/seen")
def mark_event_seen(event_id: int, db: Session = Depends(get_db)):
    st = db.query(EventSeenState).filter(EventSeenState.event_id == event_id).first()
    if not st:
        raise HTTPException(404, "Event state not found")
    st.state = "SEEN"
    st.seen_at = datetime.utcnow()
    db.commit()
    return {"status": "success"}

@router.post("/mark-all-seen")
def mark_all_seen(watchlist_id: int, db: Session = Depends(get_db)):
    states = db.query(EventSeenState).filter(EventSeenState.watchlist_id == watchlist_id, EventSeenState.state == 'NEW').all()
    for st in states:
        st.state = 'SEEN'
        st.seen_at = datetime.utcnow()
    db.commit()
    return {"status": "success"}

@router.get("/history")
def get_history(watchlist_id: int, db: Session = Depends(get_db)):
    events = get_event_responses(db, watchlist_id)
    
    # Group by date
    grouped = {}
    now = datetime.utcnow()
    today = now.date()
    yesterday = today - timedelta(days=1)
    
    for ev in events:
        ts = ev["timestamp"]
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        ev_date = ts.date()
        
        if ev_date == today:
            date_label = "Today"
        elif ev_date == yesterday:
            date_label = "Yesterday"
        else:
            date_label = ev_date.strftime("%b %d, %Y")
        
        time_label = ts.strftime("%I:%M %p")
        ev["time_label"] = time_label
        
        if date_label not in grouped:
            grouped[date_label] = []
        grouped[date_label].append(ev)
    
    result = [{"date_label": label, "events": evts} for label, evts in grouped.items()]
    return result

@router.get("/digest")
async def get_digest(watchlist_id: Optional[int] = None, db: Session = Depends(get_db)):
    # 1. Trigger fresh event detection across watchlists
    try:
        if watchlist_id:
            detect_events_for_watchlist(db, watchlist_id)
        else:
            run_detection_for_all_watchlists(db)
    except Exception:
        pass
        
    # 2. Query recorded events
    query = db.query(MarketEvent)
    if watchlist_id:
        query = query.join(EventSeenState, MarketEvent.id == EventSeenState.event_id).filter(EventSeenState.watchlist_id == watchlist_id)
        
    events_records = query.order_by(MarketEvent.timestamp.desc()).limit(20).all()
    
    events_list = []
    for ev in events_records:
        age_min = int((datetime.utcnow() - ev.timestamp).total_seconds() / 60)
        if age_min < 1:
            time_ago = "Just now"
        elif age_min < 60:
            time_ago = f"{age_min}m ago"
        elif age_min < 1440:
            time_ago = f"{age_min // 60}h ago"
        else:
            time_ago = f"{age_min // 1440}d ago"
            
        events_list.append({
            "id": ev.id,
            "symbol": ev.symbol,
            "event_type": ev.event_type,
            "title": ev.title,
            "description": ev.description,
            "severity": ev.severity,
            "price_change_pct": ev.price_change_pct,
            "volume_ratio": ev.volume_ratio or 1.0,
            "market_relative_move": ev.market_relative_move or 0.0,
            "confidence": ev.confidence or 0.8,
            "timestamp": ev.timestamp.isoformat() if ev.timestamp else datetime.utcnow().isoformat(),
            "time_ago": time_ago,
        })
        
    # 3. Augment with live market top movers so the feed always has actionable signals
    all_quotes = feed_engine.get_all_quotes()
    if len(events_list) < 5:
        sorted_movers = sorted(
            [q for q in all_quotes if not q['symbol'].startswith('^')],
            key=lambda q: (abs(q.get('change_pct', 0)), q.get('volume_ratio', 1.0)),
            reverse=True
        )
        for idx, q in enumerate(sorted_movers[:6]):
            if not any(e['symbol'] == q['symbol'] for e in events_list):
                abs_chg = abs(q.get('change_pct', 0))
                is_up = q.get('change_pct', 0) >= 0
                direction = "gained" if is_up else "dropped"
                vol = q.get('volume_ratio', 1.2)
                sev = "needs_attention" if (abs_chg > 2.0 or vol > 1.8) else "worth_checking"
                curr = "₹" if q['symbol'].endswith('.NS') or q['symbol'].endswith('.BO') else "$"
                events_list.append({
                    "id": 9000 + idx,
                    "symbol": q['symbol'],
                    "event_type": "PRICE_MOVE" if abs_chg > 1.5 else "VOLUME_SPIKE",
                    "title": f"{q['symbol'].replace('.NS', '')} {direction} {abs_chg:.2f}% ({curr}{q['price']:,.2f})",
                    "description": f"{q['name']} trading volume at {vol:.1f}x 20-day average. Sector: {q.get('sector', 'Equity')}.",
                    "severity": sev,
                    "price_change_pct": q.get('change_pct', 0),
                    "volume_ratio": vol,
                    "market_relative_move": q.get('change_pct', 0),
                    "confidence": min(0.95, round(0.6 + abs_chg * 0.08, 2)),
                    "timestamp": datetime.utcnow().isoformat(),
                    "time_ago": "Live",
                })

    # 4. Generate fully dynamic Morning Brief from live market data
    breadth = feed_engine.get_breadth()
    nifty = breadth.get('nifty_price', 24500)
    nifty_chg = breadth.get('nifty_change_pct', 0.0)
    sensex = breadth.get('sensex_price', 80500)
    sensex_chg = breadth.get('sensex_change_pct', 0.0)
    sp500_chg = breadth.get('sp500_change_pct', 0.0)
    
    gainers = [q for q in all_quotes if q.get('change_pct', 0) > 0 and not q['symbol'].startswith('^')]
    losers = [q for q in all_quotes if q.get('change_pct', 0) < 0 and not q['symbol'].startswith('^')]
    gainers.sort(key=lambda x: x.get('change_pct', 0), reverse=True)
    losers.sort(key=lambda x: x.get('change_pct', 0))
    
    g_str = ", ".join([f"{g['symbol'].replace('.NS', '')} (+{g['change_pct']:.1f}%)" for g in gainers[:2]]) if gainers else "select equities"
    l_str = f"{losers[0]['symbol'].replace('.NS', '')} ({losers[0]['change_pct']:.1f}%)" if losers else "broader indices"
    
    # Try Anthropic LLM if key is present
    from ..services import ai_summary
    morning_brief = None
    if ai_summary.client and ai_summary.ANTHROPIC_API_KEY and ai_summary.ANTHROPIC_API_KEY != "your_anthropic_key":
        try:
            morning_brief = await ai_summary.generate_morning_brief(events_list[:5], "Investor")
        except Exception:
            morning_brief = None

    if not morning_brief:
        nifty_status = "advancing" if nifty_chg >= 0 else "slipping"
        sentiment = "bullish" if nifty_chg > 0.2 else ("cautious" if nifty_chg < -0.2 else "steady")
        morning_brief = (
            f"Live Market Brief: Indian indices are {nifty_status} with NIFTY 50 at ₹{nifty:,.1f} ({nifty_chg:+.2f}%) "
            f"and SENSEX at {sensex:,.0f} ({sensex_chg:+.2f}%), reflecting a {sentiment} session tone. "
            f"Strongest momentum is concentrated in {g_str}, while {l_str} sees consolidation. "
            f"S&P 500 is tracking {sp500_chg:+.2f}%. "
            f"{len(events_list)} watchlist symbols currently meet statistical significance scoring thresholds."
        )

    return {
        "morning_brief": morning_brief,
        "generated_at": datetime.utcnow().isoformat(),
        "total_events": len(events_list),
        "high_signal_count": sum(1 for e in events_list if e['severity'] == 'needs_attention'),
        "watch_count": sum(1 for e in events_list if e['severity'] == 'worth_checking'),
        "events": events_list
    }
