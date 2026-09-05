import asyncio
import math
import random
import time
import httpx
from datetime import datetime
from typing import Dict, List, Any

DEFAULT_UNIVERSE = {
    # ===== INDIAN INDICES =====
    "^NSEI": {"name": "NIFTY 50", "sector": "Index", "base_price": 24500.0, "prev_close": 24350.0, "avg_vol": 300000000, "sma50": 24000.0, "sma200": 22000.0, "atr": 250.0},
    "^BSESN": {"name": "SENSEX", "sector": "Index", "base_price": 80500.0, "prev_close": 80000.0, "avg_vol": 200000000, "sma50": 79000.0, "sma200": 74000.0, "atr": 800.0},

    # ===== INDIAN EQUITIES (Priority) =====
    "BHARTIARTL.NS": {"name": "Bharti Airtel", "sector": "Telecom", "base_price": 1680.0, "prev_close": 1660.0, "avg_vol": 5000000, "sma50": 1620.0, "sma200": 1400.0, "atr": 28.0, "high52": 1750.0, "low52": 1150.0},
    "SBIN.NS": {"name": "State Bank of India", "sector": "Banking", "base_price": 830.0, "prev_close": 820.0, "avg_vol": 20000000, "sma50": 800.0, "sma200": 720.0, "atr": 15.0, "high52": 870.0, "low52": 580.0},
    "LT.NS": {"name": "Larsen & Toubro", "sector": "Infrastructure", "base_price": 3600.0, "prev_close": 3550.0, "avg_vol": 3000000, "sma50": 3500.0, "sma200": 3200.0, "atr": 55.0, "high52": 3800.0, "low52": 2800.0},
    "WIPRO.NS": {"name": "Wipro Limited", "sector": "IT Services", "base_price": 580.0, "prev_close": 570.0, "avg_vol": 8000000, "sma50": 560.0, "sma200": 490.0, "atr": 12.0, "high52": 610.0, "low52": 400.0},
    "HCLTECH.NS": {"name": "HCL Technologies", "sector": "IT Services", "base_price": 1780.0, "prev_close": 1750.0, "avg_vol": 4000000, "sma50": 1720.0, "sma200": 1550.0, "atr": 30.0, "high52": 1850.0, "low52": 1250.0},
    "MARUTI.NS": {"name": "Maruti Suzuki", "sector": "Automobile", "base_price": 12800.0, "prev_close": 12650.0, "avg_vol": 1200000, "sma50": 12500.0, "sma200": 11000.0, "atr": 200.0, "high52": 13500.0, "low52": 9800.0},
    "SUNPHARMA.NS": {"name": "Sun Pharma", "sector": "Pharmaceuticals", "base_price": 1750.0, "prev_close": 1720.0, "avg_vol": 4500000, "sma50": 1700.0, "sma200": 1500.0, "atr": 32.0, "high52": 1850.0, "low52": 1200.0},
    "TATAMOTORS.NS": {"name": "Tata Motors", "sector": "Automobile", "base_price": 980.0, "prev_close": 960.0, "avg_vol": 12000000, "sma50": 940.0, "sma200": 850.0, "atr": 22.0, "high52": 1050.0, "low52": 620.0},
    "AXISBANK.NS": {"name": "Axis Bank", "sector": "Banking", "base_price": 1180.0, "prev_close": 1160.0, "avg_vol": 10000000, "sma50": 1150.0, "sma200": 1050.0, "atr": 20.0, "high52": 1250.0, "low52": 900.0},
    "BAJFINANCE.NS": {"name": "Bajaj Finance", "sector": "NBFC", "base_price": 7200.0, "prev_close": 7100.0, "avg_vol": 2500000, "sma50": 7000.0, "sma200": 6500.0, "atr": 120.0, "high52": 7800.0, "low52": 5600.0},
    "KOTAKBANK.NS": {"name": "Kotak Mahindra Bank", "sector": "Banking", "base_price": 1850.0, "prev_close": 1830.0, "avg_vol": 5000000, "sma50": 1800.0, "sma200": 1700.0, "atr": 28.0, "high52": 1950.0, "low52": 1500.0},
    "ADANIENT.NS": {"name": "Adani Enterprises", "sector": "Conglomerate", "base_price": 3100.0, "prev_close": 3050.0, "avg_vol": 6000000, "sma50": 3000.0, "sma200": 2700.0, "atr": 65.0, "high52": 3500.0, "low52": 2100.0},
    "TITAN.NS": {"name": "Titan Company", "sector": "Consumer Goods", "base_price": 3450.0, "prev_close": 3400.0, "avg_vol": 3000000, "sma50": 3350.0, "sma200": 3100.0, "atr": 50.0, "high52": 3600.0, "low52": 2800.0},
    "POWERGRID.NS": {"name": "Power Grid Corp", "sector": "Utilities", "base_price": 320.0, "prev_close": 315.0, "avg_vol": 15000000, "sma50": 310.0, "sma200": 280.0, "atr": 6.0, "high52": 340.0, "low52": 220.0},
    "NTPC.NS": {"name": "NTPC Limited", "sector": "Power", "base_price": 395.0, "prev_close": 390.0, "avg_vol": 12000000, "sma50": 385.0, "sma200": 340.0, "atr": 7.0, "high52": 420.0, "low52": 260.0},
    "ZOMATO.NS": {"name": "Zomato Limited", "sector": "Internet / Food Tech", "base_price": 265.0, "prev_close": 258.0, "avg_vol": 30000000, "sma50": 250.0, "sma200": 200.0, "atr": 8.0, "high52": 280.0, "low52": 115.0},
    "RELIANCE.NS": {"name": "Reliance Industries", "sector": "Conglomerate", "base_price": 2950.0, "prev_close": 2920.0, "avg_vol": 7000000, "sma50": 2900.0, "sma200": 2700.0, "atr": 45.0, "high52": 3200.0, "low52": 2200.0},
    "TCS.NS": {"name": "Tata Consultancy Services", "sector": "IT Services", "base_price": 4100.0, "prev_close": 4050.0, "avg_vol": 2500000, "sma50": 4000.0, "sma200": 3800.0, "atr": 60.0, "high52": 4250.0, "low52": 3100.0},
    "HDFCBANK.NS": {"name": "HDFC Bank", "sector": "Banking", "base_price": 1650.0, "prev_close": 1630.0, "avg_vol": 18000000, "sma50": 1600.0, "sma200": 1550.0, "atr": 25.0, "high52": 1750.0, "low52": 1350.0},
    "INFY.NS": {"name": "Infosys", "sector": "IT Services", "base_price": 1950.0, "prev_close": 1920.0, "avg_vol": 6000000, "sma50": 1900.0, "sma200": 1750.0, "atr": 35.0, "high52": 1980.0, "low52": 1350.0},
    "ICICIBANK.NS": {"name": "ICICI Bank", "sector": "Banking", "base_price": 1250.0, "prev_close": 1220.0, "avg_vol": 15000000, "sma50": 1200.0, "sma200": 1050.0, "atr": 20.0, "high52": 1280.0, "low52": 900.0},
    "ITC.NS": {"name": "ITC Limited", "sector": "Consumer Goods", "base_price": 505.0, "prev_close": 500.0, "avg_vol": 14000000, "sma50": 490.0, "sma200": 440.0, "atr": 6.5, "high52": 520.0, "low52": 399.0},
    "HINDUNILVR.NS": {"name": "Hindustan Unilever", "sector": "Consumer Goods", "base_price": 2780.0, "prev_close": 2750.0, "avg_vol": 2000000, "sma50": 2700.0, "sma200": 2500.0, "atr": 38.0, "high52": 2890.0, "low52": 2170.0},
    "TATASTEEL.NS": {"name": "Tata Steel", "sector": "Metals & Mining", "base_price": 155.0, "prev_close": 152.0, "avg_vol": 35000000, "sma50": 150.0, "sma200": 135.0, "atr": 3.2, "high52": 184.0, "low52": 114.0},
    "ASIANPAINT.NS": {"name": "Asian Paints", "sector": "Consumer Goods", "base_price": 3150.0, "prev_close": 3120.0, "avg_vol": 1500000, "sma50": 3050.0, "sma200": 2900.0, "atr": 48.0, "high52": 3400.0, "low52": 2670.0},
    "ULTRACEMCO.NS": {"name": "UltraTech Cement", "sector": "Materials", "base_price": 11400.0, "prev_close": 11250.0, "avg_vol": 450000, "sma50": 11000.0, "sma200": 9800.0, "atr": 180.0, "high52": 11900.0, "low52": 8200.0},
    "BAJAJFINSV.NS": {"name": "Bajaj Finserv", "sector": "Financial Services", "base_price": 1850.0, "prev_close": 1820.0, "avg_vol": 2200000, "sma50": 1780.0, "sma200": 1600.0, "atr": 32.0, "high52": 1950.0, "low52": 1420.0},
    "NESTLEIND.NS": {"name": "Nestle India", "sector": "Consumer Goods", "base_price": 2520.0, "prev_close": 2490.0, "avg_vol": 900000, "sma50": 2450.0, "sma200": 2350.0, "atr": 35.0, "high52": 2770.0, "low52": 2150.0},
    "COALINDIA.NS": {"name": "Coal India", "sector": "Energy & Mining", "base_price": 510.0, "prev_close": 502.0, "avg_vol": 12000000, "sma50": 490.0, "sma200": 420.0, "atr": 11.0, "high52": 543.0, "low52": 260.0},
    "ONGC.NS": {"name": "ONGC", "sector": "Energy", "base_price": 315.0, "prev_close": 310.0, "avg_vol": 18000000, "sma50": 305.0, "sma200": 260.0, "atr": 6.8, "high52": 344.0, "low52": 175.0},
    "M&M.NS": {"name": "Mahindra & Mahindra", "sector": "Automobile", "base_price": 2750.0, "prev_close": 2700.0, "avg_vol": 3500000, "sma50": 2650.0, "sma200": 2200.0, "atr": 52.0, "high52": 3014.0, "low52": 1450.0},
    "TECHM.NS": {"name": "Tech Mahindra", "sector": "IT Services", "base_price": 1620.0, "prev_close": 1590.0, "avg_vol": 2800000, "sma50": 1550.0, "sma200": 1300.0, "atr": 30.0, "high52": 1710.0, "low52": 1090.0},
    "JIOFIN.NS": {"name": "Jio Financial Services", "sector": "NBFC", "base_price": 345.0, "prev_close": 338.0, "avg_vol": 25000000, "sma50": 330.0, "sma200": 310.0, "atr": 7.5, "high52": 395.0, "low52": 205.0},
    "TATACONSUM.NS": {"name": "Tata Consumer Products", "sector": "Consumer Goods", "base_price": 1180.0, "prev_close": 1160.0, "avg_vol": 2000000, "sma50": 1150.0, "sma200": 1050.0, "atr": 20.0, "high52": 1269.0, "low52": 820.0},
    "GRASIM.NS": {"name": "Grasim Industries", "sector": "Materials", "base_price": 2680.0, "prev_close": 2640.0, "avg_vol": 1100000, "sma50": 2600.0, "sma200": 2250.0, "atr": 45.0, "high52": 2875.0, "low52": 1880.0},
    "HINDALCO.NS": {"name": "Hindalco Industries", "sector": "Metals & Mining", "base_price": 690.0, "prev_close": 675.0, "avg_vol": 8000000, "sma50": 660.0, "sma200": 580.0, "atr": 16.0, "high52": 715.0, "low52": 450.0},
    "CIPLA.NS": {"name": "Cipla Limited", "sector": "Pharmaceuticals", "base_price": 1620.0, "prev_close": 1600.0, "avg_vol": 2200000, "sma50": 1580.0, "sma200": 1400.0, "atr": 28.0, "high52": 1700.0, "low52": 1130.0},
    "DRREDDY.NS": {"name": "Dr. Reddy's Labs", "sector": "Pharmaceuticals", "base_price": 6650.0, "prev_close": 6580.0, "avg_vol": 750000, "sma50": 6500.0, "sma200": 6000.0, "atr": 110.0, "high52": 7100.0, "low52": 5200.0},
    "ADANIPORTS.NS": {"name": "Adani Ports & SEZ", "sector": "Infrastructure", "base_price": 1480.0, "prev_close": 1450.0, "avg_vol": 6000000, "sma50": 1420.0, "sma200": 1250.0, "atr": 32.0, "high52": 1620.0, "low52": 750.0},
    "APOLLOHOSP.NS": {"name": "Apollo Hospitals", "sector": "Healthcare", "base_price": 7150.0, "prev_close": 7050.0, "avg_vol": 650000, "sma50": 6900.0, "sma200": 6200.0, "atr": 125.0, "high52": 7450.0, "low52": 4750.0},
    "TRENT.NS": {"name": "Trent Limited", "sector": "Retail / Consumer", "base_price": 7100.0, "prev_close": 6950.0, "avg_vol": 2500000, "sma50": 6700.0, "sma200": 4800.0, "atr": 150.0, "high52": 7500.0, "low52": 2050.0},
    "BEL.NS": {"name": "Bharat Electronics", "sector": "Aerospace & Defence", "base_price": 295.0, "prev_close": 290.0, "avg_vol": 18000000, "sma50": 285.0, "sma200": 220.0, "atr": 7.2, "high52": 340.0, "low52": 125.0},
    "HAL.NS": {"name": "Hindustan Aeronautics", "sector": "Aerospace & Defence", "base_price": 4650.0, "prev_close": 4550.0, "avg_vol": 3000000, "sma50": 4500.0, "sma200": 3600.0, "atr": 110.0, "high52": 5675.0, "low52": 1900.0},
    "VBL.NS": {"name": "Varun Beverages", "sector": "Beverages", "base_price": 630.0, "prev_close": 618.0, "avg_vol": 5000000, "sma50": 610.0, "sma200": 520.0, "atr": 14.0, "high52": 680.0, "low52": 410.0},

    # ===== US EQUITIES =====
    "NVDA": {"name": "NVIDIA Corporation", "sector": "Semiconductors", "base_price": 124.50, "prev_close": 122.80, "avg_vol": 48500000, "sma50": 118.50, "sma200": 98.40, "atr": 4.20, "high52": 140.76, "low52": 45.0},
    "AAPL": {"name": "Apple Inc.", "sector": "Consumer Electronics", "base_price": 228.40, "prev_close": 226.10, "avg_vol": 42000000, "sma50": 220.30, "sma200": 195.60, "atr": 3.40, "high52": 237.23, "low52": 164.08},
    "TSLA": {"name": "Tesla, Inc.", "sector": "Auto & Energy", "base_price": 224.20, "prev_close": 220.50, "avg_vol": 68000000, "sma50": 215.10, "sma200": 190.80, "atr": 8.90, "high52": 271.0, "low52": 138.80},
    "MSFT": {"name": "Microsoft Corporation", "sector": "Cloud & Enterprise Software", "base_price": 425.60, "prev_close": 422.10, "avg_vol": 22000000, "sma50": 420.50, "sma200": 405.20, "atr": 5.90, "high52": 468.35, "low52": 309.45},
    "AMZN": {"name": "Amazon.com, Inc.", "sector": "E-Commerce & Cloud", "base_price": 182.50, "prev_close": 180.20, "avg_vol": 34000000, "sma50": 178.20, "sma200": 165.90, "atr": 3.80, "high52": 201.20, "low52": 118.35},
    "GOOGL": {"name": "Alphabet Inc.", "sector": "Internet & AI", "base_price": 164.80, "prev_close": 162.90, "avg_vol": 25000000, "sma50": 160.40, "sma200": 145.30, "atr": 3.20, "high52": 191.75, "low52": 120.21},
    "META": {"name": "Meta Platforms, Inc.", "sector": "Social Media & AI", "base_price": 530.20, "prev_close": 522.60, "avg_vol": 16000000, "sma50": 510.80, "sma200": 465.40, "atr": 10.40, "high52": 544.23, "low52": 279.40},
    "AMD": {"name": "Advanced Micro Devices", "sector": "Semiconductors", "base_price": 152.40, "prev_close": 149.80, "avg_vol": 42000000, "sma50": 145.20, "sma200": 150.40, "atr": 5.10, "high52": 227.30, "low52": 93.12},
    "PLTR": {"name": "Palantir Technologies", "sector": "Enterprise AI Software", "base_price": 32.50, "prev_close": 31.20, "avg_vol": 58000000, "sma50": 28.10, "sma200": 22.50, "atr": 1.40, "high52": 33.50, "low52": 14.48},
    "COIN": {"name": "Coinbase Global, Inc.", "sector": "Fintech & Crypto", "base_price": 178.50, "prev_close": 172.40, "avg_vol": 14000000, "sma50": 165.40, "sma200": 185.20, "atr": 9.20, "high52": 283.48, "low52": 70.12},
    "BRK-B": {"name": "Berkshire Hathaway", "sector": "Conglomerate", "base_price": 452.0, "prev_close": 448.50, "avg_vol": 3200000, "sma50": 440.0, "sma200": 410.0, "atr": 4.5, "high52": 460.0, "low52": 345.0},
    "LLY": {"name": "Eli Lilly and Company", "sector": "Pharmaceuticals", "base_price": 935.0, "prev_close": 920.0, "avg_vol": 3100000, "sma50": 900.0, "sma200": 760.0, "atr": 18.0, "high52": 972.0, "low52": 520.0},
    "AVGO": {"name": "Broadcom Inc.", "sector": "Semiconductors", "base_price": 158.0, "prev_close": 154.50, "avg_vol": 28000000, "sma50": 150.0, "sma200": 130.0, "atr": 4.8, "high52": 185.0, "low52": 80.0},
    "JPM": {"name": "JPMorgan Chase", "sector": "Banking", "base_price": 218.0, "prev_close": 215.0, "avg_vol": 9000000, "sma50": 210.0, "sma200": 190.0, "atr": 3.8, "high52": 225.0, "low52": 140.0},
    "NFLX": {"name": "Netflix, Inc.", "sector": "Entertainment", "base_price": 690.0, "prev_close": 680.0, "avg_vol": 3500000, "sma50": 660.0, "sma200": 580.0, "atr": 14.0, "high52": 711.0, "low52": 360.0},
    "SPY": {"name": "SPDR S&P 500 ETF Trust", "sector": "Broad Market ETF", "base_price": 558.20, "prev_close": 555.40, "avg_vol": 58000000, "sma50": 550.20, "sma200": 515.40, "atr": 4.50, "high52": 565.16, "low52": 410.0},
    "QQQ": {"name": "Invesco QQQ Trust", "sector": "Tech ETF", "base_price": 482.50, "prev_close": 479.20, "avg_vol": 46000000, "sma50": 475.10, "sma200": 435.80, "atr": 5.40, "high52": 503.52, "low52": 350.0},
}

class MarketFeedEngine:
    def __init__(self):
        self.stocks: Dict[str, Dict[str, Any]] = {}
        self.feed_mode = "LIVE"
        self.latency_ms = 38
        self.last_real_fetch_time = time.time()
        self.benchmark_pct = 0.85
        self.initialize_state()

    def initialize_state(self):
        for sym, data in DEFAULT_UNIVERSE.items():
            self._init_symbol(sym, data)

    def _init_symbol(self, sym: str, data: Dict[str, Any]):
        base = data["base_price"]
        prev = data["prev_close"]
        cur = round(base, 2)
        chg = round(cur - prev, 2)
        chg_pct = round((chg / prev) * 100.0, 2)

        sparkline = []
        for i in range(20):
            step = (cur - prev) * (i / 19.0) + (random.uniform(-0.25, 0.25) * data["atr"] * 0.2)
            sparkline.append(round(prev + step, 2))
        sparkline[-1] = cur

        vol = int(data["avg_vol"] * (0.85 + random.uniform(0.1, 0.6)))

        self.stocks[sym] = {
            "symbol": sym,
            "name": data["name"],
            "sector": data["sector"],
            "price": cur,
            "change": chg,
            "change_pct": chg_pct,
            "open": round(prev + (cur - prev) * 0.3, 2),
            "high": round(max(cur, prev) + random.uniform(0.5, 1.5), 2),
            "low": round(min(cur, prev) - random.uniform(0.5, 1.5), 2),
            "prev_close": prev,
            "volume": vol,
            "avg_volume_20d": data["avg_vol"],
            "volume_ratio": round(vol / max(data["avg_vol"], 1), 2),
            "atr": data["atr"],
            "sparkline": sparkline,
            "data_age_seconds": 0,
            "data_state": "fresh",
            "notes": None,
            "last_updated": datetime.utcnow()
        }


    async def fetch_real_market_quotes(self):
        try:
            symbols = list(self.stocks.keys())
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
            async with httpx.AsyncClient(timeout=4.0) as client:
                for sym in symbols:
                    try:
                        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=2m&range=1d"
                        r = await client.get(url, headers=headers)
                        if r.status_code == 200:
                            data = r.json()
                            meta = data["chart"]["result"][0]["meta"]
                            real_price = meta.get("regularMarketPrice")
                            prev_close = meta.get("previousClose")
                            if real_price and prev_close and sym in self.stocks:
                                st = self.stocks[sym]
                                st["price"] = round(real_price, 2)
                                st["prev_close"] = round(prev_close, 2)
                                st["change"] = round(real_price - prev_close, 2)
                                st["change_pct"] = round(((real_price - prev_close) / prev_close) * 100.0, 2)
                                if not st["sparkline"] or st["price"] != st["sparkline"][-1]:
                                    st["sparkline"].append(st["price"])
                                    if len(st["sparkline"]) > 25:
                                        st["sparkline"].pop(0)
                                st["data_state"] = "fresh"
                                st["last_updated"] = datetime.utcnow()
                    except Exception:
                        pass
            self.last_real_fetch_time = time.time()
        except Exception:
            pass

    def tick(self):
        if self.feed_mode == "STALE_OFFLINE":
            self.latency_ms = 5200
            return

        now = time.time()
        for sym, stock in self.stocks.items():
            volatility_step = (random.gauss(0, 0.0008) * stock["price"])
            new_price = round(max(0.5, stock["price"] + volatility_step), 2)
            prev = stock["prev_close"]
            chg = round(new_price - prev, 2)
            chg_pct = round((chg / prev) * 100.0, 2)
            
            stock["price"] = new_price
            stock["change"] = chg
            stock["change_pct"] = chg_pct
            stock["high"] = max(stock["high"], new_price)
            stock["low"] = min(stock["low"], new_price)
            stock["volume"] += random.randint(150, 900)
            stock["volume_ratio"] = round(stock["volume"] / max(stock["avg_volume_20d"], 1), 2)
            
            if random.random() < 0.3:
                stock["sparkline"].append(new_price)
                if len(stock["sparkline"]) > 25:
                    stock["sparkline"].pop(0)

            stock["last_updated"] = datetime.utcnow()
            
            stock["data_age_seconds"] = int(now - self.last_real_fetch_time)
            
            if self.feed_mode == "DELAYED_15M":
                stock["data_state"] = "delayed"
            elif self.feed_mode == "STALE_OFFLINE":
                stock["data_state"] = "stale"
            else:
                stock["data_state"] = "fresh" if stock["data_age_seconds"] < 300 else "delayed"

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        sym = symbol.upper()
        if sym not in self.stocks:
            self._init_symbol(sym, {"name": sym, "sector": "Equity", "base_price": 100.0, "prev_close": 100.0, "avg_vol": 1000000, "atr": 2.0})
            # Will be updated by fetch_real_market_quotes shortly
        return self.stocks.get(sym)

    def get_all_quotes(self) -> List[Dict[str, Any]]:
        return list(self.stocks.values())

    def get_breadth(self) -> Dict[str, Any]:
        adv = sum(1 for s in self.stocks.values() if s["change"] > 0)
        dec = sum(1 for s in self.stocks.values() if s["change"] < 0)
        
        nifty = self.stocks.get("^NSEI", {})
        sensex = self.stocks.get("^BSESN", {})
        spy = self.stocks.get("SPY", {})
        qqq = self.stocks.get("QQQ", {})

        return {
            "sp500_price": spy.get("price", 5748.20),
            "sp500_change_pct": spy.get("change_pct", 0.85),
            "nasdaq_price": qqq.get("price", 18210.40),
            "nasdaq_change_pct": qqq.get("change_pct", 1.15),
            "vix_price": 13.15,
            "vix_change_pct": -3.40,
            "nifty_price": nifty.get("price", 24500.0),
            "nifty_change_pct": nifty.get("change_pct", 0.0),
            "sensex_price": sensex.get("price", 80500.0),
            "sensex_change_pct": sensex.get("change_pct", 0.0),
            "us10y_yield": 4.185,
            "us10y_change_bp": 2.1,
            "advancers": adv,
            "decliners": dec,
            "market_phase": "REGULAR_OPEN",
            "data_feed_status": self.feed_mode,
            "latency_ms": self.latency_ms
        }

feed_engine = MarketFeedEngine()
