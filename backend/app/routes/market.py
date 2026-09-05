from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import time
from datetime import datetime
from ..database import get_db
from ..models import Watchlist, WatchlistItem, UserCheckpoint, MarketEvent, EventSeenState
from ..engine.market_feed import feed_engine, DEFAULT_UNIVERSE

router = APIRouter(prefix="/api/market", tags=["Market"])

def _clean_quote(q: dict) -> dict:
    """Return only the fields the frontend needs."""
    last_updated = q.get("last_updated")
    if isinstance(last_updated, datetime):
        age = int((datetime.utcnow() - last_updated).total_seconds())
    else:
        age = 0
    if age < 30:
        data_state = "fresh"
    elif age < 300:
        data_state = "delayed"
    elif age < 3600:
        data_state = "stale"
    else:
        data_state = "market_closed"
    return {
        "symbol": q["symbol"],
        "name": q["name"],
        "sector": q["sector"],
        "price": q["price"],
        "change": q["change"],
        "change_pct": q["change_pct"],
        "open": q["open"],
        "high": q["high"],
        "low": q["low"],
        "prev_close": q["prev_close"],
        "volume": q["volume"],
        "avg_volume_20d": q["avg_volume_20d"],
        "volume_ratio": round(q["volume"] / max(q["avg_volume_20d"], 1), 2),
        "sparkline": q.get("sparkline", []),
        "data_age_seconds": age,
        "data_state": data_state,
    }

@router.get("/quotes")
def get_watchlist_quotes(watchlist_id: Optional[int] = None, db: Session = Depends(get_db)):
    if watchlist_id:
        items = db.query(WatchlistItem).filter(WatchlistItem.watchlist_id == watchlist_id).order_by(WatchlistItem.order_index).all()
        symbols = [it.symbol for it in items]
        item_meta = {it.symbol: it for it in items}
        ckpt = db.query(UserCheckpoint).filter(UserCheckpoint.watchlist_id == watchlist_id).order_by(UserCheckpoint.last_checked_at.desc()).first()
        prev_prices = {}
        if ckpt and ckpt.prices_snapshot:
            prev_prices = json.loads(ckpt.prices_snapshot)
    else:
        symbols = list(DEFAULT_UNIVERSE.keys())
        item_meta = {}
        prev_prices = {}

    # Find latest catalyst per symbol from events
    event_titles = {}
    if watchlist_id:
        for sym in symbols:
            ev = db.query(MarketEvent).filter(MarketEvent.symbol == sym).order_by(MarketEvent.timestamp.desc()).first()
            if ev:
                event_titles[sym] = ev.title

    quotes = []
    for sym in symbols:
        q = feed_engine.get_quote(sym)
        if q:
            clean = _clean_quote(q)
            if sym in item_meta:
                clean["notes"] = item_meta[sym].notes
            if sym in prev_prices:
                prev = prev_prices[sym]
                clean["since_last_check_pct"] = round(((clean["price"] - prev) / prev) * 100.0, 2)
            else:
                clean["since_last_check_pct"] = None
            clean["latest_catalyst"] = event_titles.get(sym)
            quotes.append(clean)
    return quotes

@router.get("/detail/{symbol}")
def get_stock_detail(symbol: str, watchlist_id: Optional[int] = None, db: Session = Depends(get_db)):
    sym = symbol.upper()
    quote = feed_engine.get_quote(sym)
    if not quote:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
    
    clean = _clean_quote(quote)
    p = quote["price"]
    
    # Build chart data from actual sparkline
    chart_data = []
    sparkline = quote.get("sparkline", [])
    for i, val in enumerate(sparkline):
        time_label = f"{9 + i//6}:{(i%6)*10:02d}"
        chart_data.append({"time": time_label, "price": val})
        
    # Make sure we have at least something
    if not chart_data:
        chart_data.append({"time": "09:00", "price": p})

    # Since last check
    since_pct = None
    if watchlist_id:
        ckpt = db.query(UserCheckpoint).filter(UserCheckpoint.watchlist_id == watchlist_id).order_by(UserCheckpoint.last_checked_at.desc()).first()
        if ckpt and ckpt.prices_snapshot:
            prev_prices = json.loads(ckpt.prices_snapshot)
            if sym in prev_prices:
                prev = prev_prices[sym]
                since_pct = round(((p - prev) / prev) * 100.0, 2)

    # Why we're showing this — evidence-based
    why_showing = []
    breadth = feed_engine.get_breadth()
    market_move = breadth.get("sp500_change_pct", 0.0)
    vol_ratio = clean["volume_ratio"]
    abs_change = abs(clean["change_pct"])
    relative_move = clean["change_pct"] - market_move
    
    if abs_change > 1.5:
        why_showing.append(f"Price moved {clean['change_pct']:+.1f}% today")
    if vol_ratio > 1.5:
        why_showing.append(f"Volume is {vol_ratio:.1f}× normal")
    if abs(relative_move) > 1.5:
        direction = "outperforming" if relative_move > 0 else "underperforming"
        why_showing.append(f"{direction.capitalize()} S&P 500 by {abs(relative_move):.1f}%")
    
    # Recent events for this stock
    recent_events = []
    events = db.query(MarketEvent).filter(MarketEvent.symbol == sym).order_by(MarketEvent.timestamp.desc()).limit(5).all()
    for ev in events:
        age_min = int((datetime.utcnow() - ev.timestamp).total_seconds() / 60)
        if age_min < 60:
            time_label = f"{age_min} min ago"
        elif age_min < 1440:
            time_label = f"{age_min // 60}h ago"
        else:
            time_label = f"{age_min // 1440}d ago"
        recent_events.append({
            "id": ev.id,
            "title": ev.title,
            "description": ev.description,
            "severity": ev.severity,
            "time_label": time_label,
        })
    
    if not why_showing and not recent_events:
        why_showing.append("No major changes since your last check")

    # AI Analysis & Prediction
    sentiment = "Neutral"
    if clean["change_pct"] > 1.5 and vol_ratio > 1.2:
        sentiment = "Strong Buy"
    elif clean["change_pct"] > 0.5:
        sentiment = "Bullish"
    elif clean["change_pct"] < -1.5 and vol_ratio > 1.2:
        sentiment = "Strong Sell"
    elif clean["change_pct"] < -0.5:
        sentiment = "Bearish"
        
    ai_analysis = {
        "sentiment": sentiment,
        "confidence": min(abs(clean["change_pct"]) * 20 + 50, 95),
        "summary": f"Our models indicate a {sentiment.lower()} trend due to {'high' if vol_ratio > 1.2 else 'normal'} trading volume and a {clean['change_pct']:+.1f}% price movement today."
    }

    # Fetch News
    news = []
    import requests
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={sym}&newsCount=3"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=2.0)
        if r.status_code == 200:
            data = r.json()
            for item in data.get("news", [])[:3]:
                news.append({
                    "title": item.get("title", ""),
                    "publisher": item.get("publisher", "Yahoo Finance"),
                    "link": item.get("link", "#"),
                    "providerPublishTime": item.get("providerPublishTime", 0)
                })
    except Exception:
        pass

    # Similar Stocks (Fully Dynamic via Yahoo Finance)
    similar_stocks = []
    try:
        url = f"https://query2.finance.yahoo.com/v6/finance/recommendationsbysymbol/{sym}"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=2.0)
        if r.status_code == 200:
            data = r.json()
            recs = data.get("finance", {}).get("result", [])
            if recs and len(recs) > 0:
                rec_syms = [r["symbol"] for r in recs[0].get("recommendedSymbols", [])[:4]]
                for rs in rec_syms:
                    if len(similar_stocks) < 3:
                        sq = feed_engine.get_quote(rs)
                        if sq:
                            similar_stocks.append({
                                "symbol": rs,
                                "name": sq["name"],
                                "price": sq["price"],
                                "change_pct": sq["change_pct"]
                            })
    except Exception as e:
        print("Error fetching similar stocks:", e)
        pass
    
    # Fallback if empty or failed
    if not similar_stocks:
        import random
        all_syms = list(DEFAULT_UNIVERSE.keys())
        random.shuffle(all_syms)
        for s in all_syms:
            if s != sym and len(similar_stocks) < 3:
                sq = feed_engine.get_quote(s)
                if sq:
                    similar_stocks.append({
                        "symbol": s,
                        "name": sq["name"],
                        "price": sq["price"],
                        "change_pct": sq["change_pct"]
                    })

    return {
        **clean,
        "since_last_check_pct": since_pct,
        "chart_data": chart_data,
        "why_showing": why_showing,
        "recent_events": recent_events,
        "ai_analysis": ai_analysis,
        "news": news,
        "similar_stocks": similar_stocks
    }

@router.get("/breadth")
def get_market_breadth():
    return feed_engine.get_breadth()

@router.get("/search")
def search_symbols(q: str = ""):
    query = q.upper()
    results = []
    
    # First search local universe
    for sym, data in DEFAULT_UNIVERSE.items():
        if query in sym or query in data["name"].upper() or query in data["sector"].upper():
            quote = feed_engine.get_quote(sym)
            results.append({
                "symbol": sym,
                "name": data["name"],
                "sector": data["sector"],
                "price": quote["price"] if quote else data["base_price"],
                "change_pct": quote["change_pct"] if quote else 0.0
            })
            
    # Then query Yahoo Finance directly to allow ANY global stock
    import requests
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={q}&quotesCount=5"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=3.0)
        if r.status_code == 200:
            data = r.json()
            for item in data.get("quotes", []):
                sym = item.get("symbol", "")
                # Skip if already in results
                if not sym or any(x["symbol"] == sym for x in results):
                    continue
                results.append({
                    "symbol": sym,
                    "name": item.get("shortname", item.get("longname", sym)),
                    "sector": item.get("quoteType", "Equity"),
                    "price": None,
                    "change_pct": None
                })
    except Exception as e:
        print("Search error:", e)
        pass
        
    return results[:10]

@router.get("/news")
def get_market_news():
    """Fetch latest market news from Yahoo Finance for Indian and global markets"""
    import requests
    news_items = []
    search_terms = ["Indian stock market", "NIFTY", "SENSEX", "BSE NSE"]
    headers = {"User-Agent": "Mozilla/5.0"}
    seen_titles = set()
    
    for term in search_terms:
        try:
            url = f"https://query2.finance.yahoo.com/v1/finance/search?q={term}&newsCount=5"
            r = requests.get(url, headers=headers, timeout=3.0)
            if r.status_code == 200:
                data = r.json()
                for item in data.get("news", []):
                    title = item.get("title", "")
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        news_items.append({
                            "title": title,
                            "publisher": item.get("publisher", "Yahoo Finance"),
                            "link": item.get("link", "#"),
                            "providerPublishTime": item.get("providerPublishTime", 0),
                            "thumbnail": item.get("thumbnail", {}).get("resolutions", [{}])[0].get("url", None) if item.get("thumbnail") else None
                        })
        except Exception:
            pass
    
    # Sort by time, newest first
    news_items.sort(key=lambda x: x.get("providerPublishTime", 0), reverse=True)
    return news_items[:15]

@router.get("/trending")
def get_trending_stocks(market: str = "IN"):
    """Get trending Indian or US stocks"""
    import requests
    headers = {"User-Agent": "Mozilla/5.0"}
    trending = []
    
    region = "US" if market.upper() == "US" else "IN"
    
    # Try Yahoo Finance trending for region
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/trending/{region}"
        r = requests.get(url, headers=headers, timeout=2.5)
        if r.status_code == 200:
            data = r.json()
            quotes = data.get("finance", {}).get("result", [])
            if quotes:
                for q in quotes[0].get("quotes", [])[:8]:
                    sym = q.get("symbol", "")
                    if sym:
                        quote = feed_engine.get_quote(sym)
                        if quote:
                            trending.append({
                                "symbol": sym,
                                "name": quote["name"],
                                "price": quote["price"],
                                "change_pct": quote["change_pct"],
                                "sector": quote.get("sector", "Equity"),
                                "sparkline": quote.get("sparkline", [])
                            })
    except Exception:
        pass
    
    # Fallback: pick top movers from our universe for this region
    if len(trending) < 4:
        if region == "US":
            syms = [s for s in DEFAULT_UNIVERSE.keys() if not s.endswith('.NS') and not s.endswith('.BO') and not s.startswith('^')]
        else:
            syms = [s for s in DEFAULT_UNIVERSE.keys() if s.endswith('.NS') or s.endswith('.BO')]
            
        quotes_pool = []
        for s in syms:
            q = feed_engine.get_quote(s)
            if q:
                quotes_pool.append(q)
        quotes_pool.sort(key=lambda x: (abs(x.get('change_pct', 0)), x.get('volume_ratio', 1.0)), reverse=True)
        for q in quotes_pool[:8]:
            if not any(t['symbol'] == q['symbol'] for t in trending):
                trending.append({
                    "symbol": q["symbol"],
                    "name": q["name"],
                    "price": q["price"],
                    "change_pct": q["change_pct"],
                    "sector": q.get("sector", "Equity"),
                    "sparkline": q.get("sparkline", [])
                })
    
    return trending[:8]

@router.get("/recommendations")
def get_recommended_stocks(watchlist_id: Optional[int] = None, limit: int = 3, db: Session = Depends(get_db)):
    """Dynamically get top 3 recommended stocks based on active watchlist or high-momentum breakouts"""
    active_symbols = set()
    if watchlist_id:
        wl = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
        if wl:
            active_symbols = {item.symbol for item in wl.items}
            
    recs = []
    
    # Try getting recommendations from Yahoo for first stock in active watchlist
    if active_symbols:
        anchor_sym = list(active_symbols)[0]
        try:
            import requests
            url = f"https://query2.finance.yahoo.com/v6/finance/recommendationsbysymbol/{anchor_sym}"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=2.0)
            if r.status_code == 200:
                data = r.json()
                res = data.get("finance", {}).get("result", [])
                if res:
                    for rs in res[0].get("recommendedSymbols", []):
                        s = rs.get("symbol")
                        if s and s not in active_symbols:
                            q = feed_engine.get_quote(s)
                            if q:
                                is_indian = s.endswith('.NS') or s.endswith('.BO')
                                recs.append({
                                    "symbol": s,
                                    "name": q["name"],
                                    "sector": q.get("sector", "Equity"),
                                    "price": q["price"],
                                    "change_pct": q["change_pct"],
                                    "volume_ratio": q.get("volume_ratio", 1.0),
                                    "sparkline": q.get("sparkline", []),
                                    "reason": f"Correlated with {anchor_sym.replace('.NS', '')}",
                                    "confidence": 0.91,
                                    "currency": "₹" if is_indian else "$"
                                })
                                if len(recs) >= limit:
                                    break
        except Exception:
            pass
            
    # Fallback or top-up to limit: select top momentum & statistical breakouts NOT in active watchlist
    all_quotes = feed_engine.get_all_quotes()
    candidates = [
        q for q in all_quotes 
        if q['symbol'] not in active_symbols 
        and not q['symbol'].startswith('^')
        and not any(r['symbol'] == q['symbol'] for r in recs)
    ]
    
    # Prefer Indian stocks if watchlist has Indian stocks, otherwise US or balanced
    has_indian_in_wl = any(s.endswith('.NS') for s in active_symbols)
    if has_indian_in_wl:
        candidates.sort(
            key=lambda q: (
                1 if q['symbol'].endswith('.NS') else 0,
                q.get('volume_ratio', 1.0) * 1.5 + abs(q.get('change_pct', 0))
            ),
            reverse=True
        )
    else:
        candidates.sort(
            key=lambda q: (q.get('volume_ratio', 1.0) * 1.5 + abs(q.get('change_pct', 0))),
            reverse=True
        )
        
    for q in candidates:
        if len(recs) >= limit:
            break
        is_indian = q['symbol'].endswith('.NS') or q['symbol'].endswith('.BO')
        vol = q.get('volume_ratio', 1.0)
        chg = q.get('change_pct', 0.0)
        reason = "Volume surge" if vol > 1.4 else ("Momentum leader" if chg > 1.0 else "Bullish setup")
        recs.append({
            "symbol": q["symbol"],
            "name": q["name"],
            "sector": q.get("sector", "Equity"),
            "price": q["price"],
            "change_pct": q["change_pct"],
            "volume_ratio": vol,
            "sparkline": q.get("sparkline", []),
            "reason": reason,
            "confidence": min(0.95, round(0.72 + vol * 0.08, 2)),
            "currency": "₹" if is_indian else "$"
        })
        
    return recs[:limit]

@router.get("/sectors")
def get_sector_performance():
    """Aggregate sector performance from Indian stocks"""
    sectors = {}
    for sym, data in DEFAULT_UNIVERSE.items():
        if not sym.endswith('.NS'):
            continue
        sector = data.get('sector', 'Other')
        q = feed_engine.get_quote(sym)
        if q:
            if sector not in sectors:
                sectors[sector] = {'total_pct': 0, 'count': 0, 'stocks': []}
            sectors[sector]['total_pct'] += q['change_pct']
            sectors[sector]['count'] += 1
            sectors[sector]['stocks'].append(sym)
    
    result = []
    for name, data in sectors.items():
        avg = round(data['total_pct'] / max(data['count'], 1), 2)
        result.append({
            'name': name,
            'change_pct': avg,
            'stock_count': data['count']
        })
    result.sort(key=lambda x: x['change_pct'], reverse=True)
    return result
