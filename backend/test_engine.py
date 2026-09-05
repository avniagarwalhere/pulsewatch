from app.database import SessionLocal
from app.engine.event_detector import detect_events_for_watchlist
from app.models import MarketEvent, Watchlist, UserCheckpoint

db = SessionLocal()
w = db.query(Watchlist).first()

# Force detection
detect_events_for_watchlist(db, w.id)

events = db.query(MarketEvent).order_by(MarketEvent.id.desc()).limit(5).all()
for e in events:
    print(f"[{e.event_type}] {e.title} - {e.description} (Sev: {e.severity}, Conf: {e.confidence})")
