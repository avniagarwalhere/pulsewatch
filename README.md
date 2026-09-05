# ⚡ PulseWatch — Real-Time Intelligent Market Watchlist & AI Terminal

> **Live Public URL (Cloudflare):** [https://brain-complications-conversation-operation.trycloudflare.com](https://brain-complications-conversation-operation.trycloudflare.com)  
> *Click above to explore the live running platform on any device without installing anything!*

---

## 👋 Hey there! Welcome to PulseWatch

Most financial dashboards and trading apps are either too noisy or too sluggish. You open a finance app and get bombarded with dozens of flashing push notifications, half of which are tiny 0.2% price wiggles. Or worse, if you trade Indian markets, the tools feel outdated and lack institutional-grade signal detection.

I built **PulseWatch** to fix that. It's a calm, fast, and thoughtful market terminal built for both **Indian equities (NSE/BSE)** and **US markets**. Instead of treating every tick as an emergency, PulseWatch only raises an eyebrow when a move is statistically abnormal.

---

## ✨ What Makes PulseWatch Different

- **🇮🇳 Built for Indian Markets First**: We track 44+ top Indian companies (Reliance, TCS, HDFC Bank, Infosys, Zomato, Tata Motors, L&T, etc.) along with NIFTY 50 and SENSEX with sub-second live price updates, ₹ currency formatting, and live sparkline graphs.
- **🇺🇸 Seamless US Market Tracking**: One-click toggle over to 17+ US tech and broad market leaders (NVIDIA, Apple, Microsoft, Tesla, Amazon, Google, S&P 500, QQQ).
- **💡 Smart, Quiet Recommendations**: Right underneath your watchlist table, PulseWatch highlights the top 3 high-conviction breakout stocks. It analyzes live volume surges, portfolio correlation, and momentum so you discover opportunities without hunting for them.
- **🧠 Morning Brief that Actually Makes Sense**: An automated AI summary that explains *why* the market moved in plain English—no robotic jargon or fluff.
- **📈 Real-Time TradingView Charts**: Click any stock to pull up live interactive candlestick charts with volume bars, technical indicators, and sector breakdown.
- **🌓 Calm UI Design**: Handcrafted light and dark themes, keyboard shortcut navigation (`Cmd+K`), and smooth micro-animations.

---

## 🏗️ How It's Built

- **Frontend**: React 18 with Vite, styled with Tailwind CSS, Recharts for lightweight SVG sparklines, and TradingView for interactive technical charting.
- **Backend**: FastAPI (Python 3.12) running asynchronous WebSockets for sub-second quote delivery.
- **Data Engine**: A statistical Significance Score engine calculating ATR z-scores, volume surges (RVOL), and 52-week level crossings.
- **Database & Queue**: PostgreSQL 15 for multi-watchlist persistence and Redis 7 for high-speed caching.
- **Deployment**: Docker Compose with Nginx reverse proxy, globally served through Cloudflare.

---

## 🚀 How to Run It Yourself

### Option 1: Just click the live link!
No setup needed. Just visit:  
👉 **[https://brain-complications-conversation-operation.trycloudflare.com](https://brain-complications-conversation-operation.trycloudflare.com)**

---

### Option 2: 1-Command Docker Deployment (Local)
If you have Docker Desktop running, clone and launch:
```bash
git clone https://github.com/Avniagarwal120/pulsewatch.git
cd pulsewatch
./deploy.sh
```
`./deploy.sh` automatically spins up the database, cache, backend, and frontend containers, seeds 44 Indian and 17 US stocks, and runs a 10-point test suite to confirm everything is healthy.

- App: [http://localhost:3000](http://localhost:3000)
- Interactive API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option 3: Manual Local Development

1. **Backend**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev -- --port 3000
   ```
   Visit [http://localhost:3000](http://localhost:3000) in your browser!

---

## 👩‍💻 Created By
**Avni Agarwal**  
Email: [Avniagarwal120@gmail.com](mailto:Avniagarwal120@gmail.com)  
GitHub: [https://github.com/Avniagarwal120](https://github.com/Avniagarwal120)
