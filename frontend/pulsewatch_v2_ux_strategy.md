# PulseWatch V2: Product & UX Strategy

PulseWatch started as a smart "Market Inbox" that respects the user's time by only showing meaningful changes since their last visit. 

To evolve PulseWatch into a world-class, sticky financial application (drawing inspiration from industry leaders like Groww, Angel One, and Robinhood), we need to focus on **Data Density**, **Micro-interactions**, and **Proactive Workflows**.

Here is a comprehensive roadmap for making the app incredibly smooth, deeply engaging, and highly functional.

---

## 1. Information Architecture & Workflow

Currently, the user lands on a unified dashboard. We can make the workflow smarter.

### The "Morning Briefing" Mode
**Concept**: If the user hasn't opened the app in >8 hours, they don't want to immediately see individual stock rows. They want to know "What happened while I slept?"
**Execution**:
- When the app detects a large time gap, it opens a modal overlay called the "Morning Briefing".
- It shows a 3-sentence AI-generated (or dynamically formatted) summary of global markets (e.g., *“US Markets closed in the green led by Tech. SGX Nifty indicates a gap-up opening for Indian markets.”*)
- **Smooth UX**: The user clicks "Let's Go" and the modal swoops away to reveal their specific watchlist.

### Multi-Workspace Layout
**Concept**: Right now, watchlists are tabs. As users add more stocks, horizontal scrolling becomes tedious.
**Execution**:
- Move watchlists to a sleek left-hand sidebar (collapsible).
- The main view is dedicated entirely to the selected watchlist, allowing for much wider, data-dense tables.

---

## 2. Presenting Data (The Visual Layer)

Tables are functional, but heatmaps and smart groupings are visual.

### Visual Heatmap Mode (Treemaps)
- **Concept**: Add a toggle next to the watchlist tabs: [ Table View | Heatmap View ].
- **Execution**: The Heatmap view represents the entire watchlist as interconnected colored blocks. 
- **Smooth UX**: Block size = Market Cap (or Volume). Block color = % Change (Deep Red to Bright Green). The user can instantly spot the most critical movement without reading a single number.

### Smart Sector Grouping
- **Concept**: Flat lists are hard to parse.
- **Execution**: Automatically group rows in the table by Sector (e.g., *Technology, Financials, Consumer Goods*). 
- **Smooth UX**: The table headers sticky-scroll as the user scrolls down, keeping context.

### Richer Detail Drawer (Groww / Angel One style)
- We just added the "Market Depth" grid (Open, High, Low, Volume). To go further:
- **Technical Dials**: A visual speedometer dial showing "Bearish / Neutral / Bullish" based on simple moving averages (SMA50/SMA200).
- **Recent News Feed**: A small infinite-scroll section pulling real Yahoo Finance news headlines for the clicked stock.

---

## 3. "Smoothness" & The Extra Polish

The difference between a good app and a great app is micro-interactions.

### Real-Time Price Flash (Blink)
- **Concept**: When a WebSocket tick arrives with a new price, the user shouldn't have to hunt for what changed.
- **Execution**: If the price went up, the table cell background flashes soft green for 300ms. If down, it flashes soft red. 
- **Why**: This gives the entire dashboard a "living, breathing" feel.

### Skeleton Loaders
- **Concept**: Avoid text like "Loading details...".
- **Execution**: When opening the Stock Detail Drawer, instantly render a "Skeleton" version of the drawer (shimmering grey boxes where the chart and numbers will be). 
- **Why**: It makes the app feel infinitely faster because the UI structure loads instantly while the data is fetched.

### Power-User Keyboard Navigation
- **Execution**: We just added `Cmd + K` to open search. We should also add:
    - `Up / Down Arrows`: Navigate up and down the watchlist table rows.
    - `Enter`: Open the drawer for the selected row.
    - `Escape`: Close the drawer.
- **Why**: Traders hate using their mouse when analyzing lists.

### Dynamic Favicon & Tab Title
- **Concept**: The user has the app open in a background tab while working.
- **Execution**: The browser tab's favicon dynamically changes to a green arrow or red arrow based on the NIFTY 50 / S&P 500 trend. The tab `<title>` updates to show the index price.
- **Why**: They don't even have to open the tab to know the market sentiment.

---

## What We Build Next?

We just successfully implemented the **Groww-style Market Depth Drawer** and the **Search / Bookmark toggle flow**. I have also just added the **Cmd+K** keyboard shortcut to make searching instantly accessible.

If you want to implement the next major UI upgrade, I highly recommend we choose between:
1. **The Visual Heatmap Mode** (A completely new way to visualize the watchlist)
2. **Real-time Price Flash Animations** (To make the data feel alive)
3. **Skeleton Loaders** (To make the UX feel 100x smoother)
