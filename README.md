# ⚡ PulseWatch — Real-Time Intelligent Market Watchlist & AI Terminal

An institutional-grade, real-time stock market intelligence platform prioritizing the **Indian Stock Market (NSE/BSE)** and **US Equities**, featuring a quantitative **Significance Score Engine (ATR z-scores, volume surges, technical breakout detection)**, **AI-generated morning briefs**, **real-time WebSocket feeds**, and **interactive TradingView charts**.

---

## 🌟 Key Features

1. **🇮🇳 Indian-First Market Universe & Global Coverage**
   - **44+ Indian Equities** (Reliance, TCS, HDFC Bank, Infosys, ICICI Bank, Bharti Airtel, SBI, L&T, ITC, Hindustan Unilever, Axis Bank, Bajaj Finance, Maruti Suzuki, Sun Pharma, Tata Motors, Kotak Bank, Adani Enterprises, Titan, NTPC, Power Grid, Trent, BEL, HAL, Varun Beverages, Zomato, etc.).
   - **17+ US Tech & Broad Market Leaders** (NVIDIA, Apple, Microsoft, Amazon, Google, Meta, Tesla, Broadcom, Eli Lilly, Berkshire Hathaway, JPMorgan, AMD, Palantir, Coinbase, Netflix, SPY, QQQ).
   - Real-time market indices: **NIFTY 50**, **SENSEX**, and **S&P 500** with live sparklines.

2. **💡 Quantitative & Dynamic Recommendations**
   - Live AI recommendations placed directly with your active watchlist.
   - Calculates correlation with your portfolio, volume breakouts, and relative strength momentum.
   - Shows rationale tags (*Volume Breakout: 2.4x*, *Correlated with Core Holdings*, *Momentum Leader*) and match confidence.
   - One-click **"+ Add"** button to immediately save to any watchlist.

3. **🧠 AI Market Digest & Signal Feed**
   - Automated natural language **Morning Brief** that synthesizes live market breadth, index movements, top sector gainers, and anomaly alerts.
   - Statistical conviction classification (*high_signal* vs. *watch* vs. *noise*) preventing information overload.
   - One-click **"🔄 Refresh Live Analysis"** for instant on-demand AI market intelligence.

4. **⚡ Real-Time Streaming & Calm UI**
   - Sub-second WebSocket streaming updates across all 60+ equities and indices.
   - Micro-animations: real-time green/red price flash cells, responsive SVG sparklines, and active live indicators.
   - Instant full-screen **TradingView Advanced Real-Time Charts** with technical indicators.
   - Complete Light / Dark theme system with keyboard shortcuts (`Cmd+K` global stock search).

5. **🐳 Enterprise Docker Architecture**
   - Multi-container architecture: **PostgreSQL 15**, **Redis 7**, **FastAPI Python 3.12 Backend**, and **Nginx React 18 Production Frontend**.
   - One-command deployment with automated 10/10 integration verification suite.

---

## 🏗️ Architecture

```
                       ┌──────────────────────────────────────┐
                       │   React 18 + Tailwind SPA (Nginx)    │
                       │   Port: 3000 (Vite Production Build) │
                       └──────────────┬───────────────────────┘
                                      │ HTTP / WebSocket
                                      ▼
                       ┌──────────────────────────────────────┐
                       │      FastAPI Python 3.12 Backend     │
                       │             Port: 8000               │
                       └──────────────┬───────────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            │                         │                         │
            ▼                         ▼                         ▼
┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
│     PostgreSQL 15     │ │        Redis 7        │ │  Yahoo / AlphaVantage │
│  Multi-Watchlist DB   │ │   Cache & Event Queue │ │     Market Feeds      │
└───────────────────────┘ └───────────────────────┘ └───────────────────────┘
```

---

## 🚀 Quick Start & Deployment Instructions

### Prerequisites
- [Docker](https://www.docker.com/) & Docker Compose (or Python 3.11+ and Node.js 18+)

### Method 1: One-Command Enterprise Docker Deployment (Recommended)
Clone the repository and run the automated deployment script:
```bash
git clone https://github.com/Avniagarwal120/pulsewatch.git
cd pulsewatch
./deploy.sh
```

`deploy.sh` automatically:
1. Builds the production Docker containers for PostgreSQL, Redis, Backend, and Frontend.
2. Initializes the database schema and seeds 44 Indian stocks, 17 US stocks, and 20 core holdings.
3. Runs an automated 10-point end-to-end verification suite across all APIs and WebSockets.

**Live Application:** Open [http://localhost:3000](http://localhost:3000)  
**Interactive API Docs:** Open [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Method 2: Local Development Setup

#### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev -- --port 3000
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🛠️ Tech Stack

* **Frontend**: React 18, Vite, Tailwind CSS, Recharts, Lucide Icons, TradingView Technical Charts
* **Backend**: FastAPI (Python 3.12), SQLAlchemy, Uvicorn, WebSockets, Pydantic v2
* **Database & Cache**: PostgreSQL 15, Redis 7 (with SQLite automatic fallback for dev)
* **AI & Quant Layer**: Significance Score Engine (ATR z-scores, RVOL, 52-week level crossings), Claude / LLM Market Brief synthesis
* **DevOps**: Docker, Docker Compose, Nginx, Automated bash verification suite

---

## 👥 Author
Created with ❤️ by **Avni Agarwal** ([Avniagarwal120@gmail.com](mailto:Avniagarwal120@gmail.com))
