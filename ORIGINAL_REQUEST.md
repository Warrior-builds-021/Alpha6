# Original User Request

## 2026-09-13T19:59:45Z

Transform ALPHA6 into an app-grade quantitative investing and financial analysis platform inspired by Investo.in's modern UI/UX, powered by the full 6-Pillar institutional discipline, real-time technical terminal, and automated capital preservation.

Working directory: c:\Users\asaik\OneDrive\Desktop\PROJECT1
Integrity mode: development

## Requirements

### R1. Modern Fintech App Shell UI/UX (Investo.in Inspired Dark Aesthetic)
Re-engineer the front-end into a modern, installable Progressive Web App (PWA) layout featuring:
- Obsidian dark theme with vibrant purple (#6943FF), indigo (#4556DA), and magenta (#BA1B9A) gradient accents inspired by Investo.in.
- App-grade card elevations, backdrop blur glassmorphism, fluid micro-interactions, clean pill tags, and stat counters.
- Responsive mobile & desktop ergonomics with seamless tab switching:
  1. **Market Screener**: Live index badges (Sensex/Nifty), top conviction cards, and filterable quantitative ranking matrix.
  2. **Forensic Audit**: 6-Pillar score radar, accounting quality checks, valuation multiples, and clear executive verdicts.
  3. **Live Technical Terminal**: Candlestick chart with 20 EMA, 50/200 SMA, 14-period RSI subplots, and multi-timeframe toggles (1M, 3M, 6M, 1Y, 2Y).
  4. **Strategy Backtester**: Equity growth curve, benchmark comparison, CAGR, and Sharpe ratio.
  5. **Risk Shield & Portfolio Sizer**: Dynamic ATR-based position sizing, strict 2x ATR stop loss, and asymmetric profit targets.
- 0ms instant search autocomplete dropdown for all Indian NSE/BSE securities and commodities.

### R2. Institutional 6-Pillar Analysis & Downside Protection Engine
Evaluate equities across the full 6 pillars with weighted composite scoring:
1. **Volume Growth & Demand** (15%): Institutional accumulation, volume surge vs. 50-day average, and price above 50-DMA.
2. **Sales Revenue Growth** (20%): 3-year topline CAGR and latest quarterly YoY demand expansion.
3. **Operating Cash Flow Quality** (25%): OCF-to-Net Income conversion ratio (> 1.0x cash earnings test) and free cash flow generation.
4. **Debt & Solvency Health** (15%): Conservative debt-to-equity (< 0.5x), current ratio, and leverage checks.
5. **Pricing Power & Moat** (15%): Gross margins (> 30%), operating margins, and return on equity (ROE).
6. **Promoter Skin in the Game** (10%): High promoter stake (> 50%) and institutional backing.
- Integrated **Piotroski F-Score (0–9)** accounting checklist and **Altman Z-Score** bankruptcy distress filter.
- Strict Capital Preservation Rule: Any stock with an Altman distress flag or revenue collapse is disqualified.

### R3. High-Performance Sub-Second Execution & Zero Lag
- Vectorized batch market data downloading via yf.download with in-memory TTL caching for instant (< 20ms) screener queries.
- Lazy-loaded tab architecture to eliminate startup waterfall bottlenecks.
- Safe serverless /tmp/py-yfinance cache redirection preventing read-only filesystem exceptions.

## Acceptance Criteria

### App Interface & User Experience
- [ ] UI reflects Investo.in dark mode aesthetic with purple/indigo gradient highlights and glassmorphic card elevations.
- [ ] App shell is fully responsive across mobile, tablet, and desktop viewports with app-like ergonomics.
- [ ] Global search input delivers instant (< 10ms) autocomplete suggestions for Indian stocks with full keyboard navigation (ArrowUp/ArrowDown/Enter).
- [ ] Plotly candlestick terminal renders OHLCV candles, 20 EMA, 50 SMA, 200 SMA, volume histogram, and RSI subplots with smooth timeframe switching.

### Financial Analysis & Risk Accuracy
- [ ] Each audited stock outputs scores for all 6 individual pillars, composite score (0–100%), and a definitive verdict (High Conviction Buy, Moderate Hold, Avoid/Red Flag).
- [ ] Piotroski F-Score (0-9) and Altman Z-Score are computed with clear plain-language rationale.
- [ ] Position sizing calculator computes exact share quantity and 2x ATR stop loss based on user portfolio size and risk tolerance.

### Performance & Stability
- [ ] Initial page load executes in < 1 second by lazy loading non-active tabs.
- [ ] Screener cache hits return in < 20ms without UI freezing or browser lag.
- [ ] 100% of API endpoints return valid JSON (HTTP 200 OK) with zero unhandled 500 crashes.

## Verification Plan

### Automated Test Suite
- Run automated 10-suite regression verification verifying health, search, screener, audit, candlesticks, backtest, position sizing, and static asset serving.

### Manual Verification
- Inspect the UI in the browser at http://localhost:8000 to verify Investo.in-inspired styling, responsive layout, smooth tab transitions, and real-time interactive charting.
