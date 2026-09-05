import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base, SessionLocal
from .models import Watchlist
from .routes import watchlists, market, events, checkpoint
from .routes.watchlists import init_default_watchlists
from .engine.market_feed import feed_engine
from .engine.event_detector import run_detection_for_all_watchlists
from .websocket_manager import ws_manager

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    if db.query(Watchlist).count() == 0:
        init_default_watchlists(db)

async def market_tick_loop():
    tick_count = 0
    while True:
        try:
            if tick_count % 6 == 0:
                await feed_engine.fetch_real_market_quotes()

            feed_engine.tick()
            
            # Periodically check for meaningful changes
            if tick_count % 15 == 0:
                with SessionLocal() as db:
                    run_detection_for_all_watchlists(db)

            quotes = feed_engine.get_all_quotes()
            breadth = feed_engine.get_breadth()
            await ws_manager.broadcast_json({
                "type": "MARKET_TICK",
                "quotes": quotes,
                "breadth": breadth
            })
            tick_count += 1
        except Exception as e:
            pass
        await asyncio.sleep(1.8)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await feed_engine.fetch_real_market_quotes()
    task = asyncio.create_task(market_tick_loop())
    yield
    task.cancel()

app = FastAPI(
    title="PulseWatch Market Inbox API",
    description="Market Inbox API",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(watchlists.router)
app.include_router(market.router)
app.include_router(events.router)
app.include_router(checkpoint.router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "INITIAL_SNAPSHOT",
            "quotes": feed_engine.get_all_quotes(),
            "breadth": feed_engine.get_breadth()
        })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "PulseWatch Inbox API"}
