# Architectural Survey & Baseline Inventory Handoff Report

**Agent**: Survey Explorer 1 (Codebase & System Architect)  
**Date**: 2026-09-14  
**Target Project**: ALPHA6 Quantitative Equity Terminal (`c:\Users\asaik\OneDrive\Desktop\PROJECT1`)  
**Parent Conversation ID**: `e2ef6863-0926-4a1d-8a81-67c45aa8d9b5`  

---

## 1. Observation

### 1.1 Repository Structure & Inventory
The project at `c:\Users\asaik\OneDrive\Desktop\PROJECT1` contains 9 subdirectories and 9 root files:

| Path | Type / Size | Purpose & Architecture Role |
| :--- | :--- | :--- |
| `server.py` | Python (430 lines, 16.0 KB) | Primary FastAPI backend application; serves REST endpoints, mounts `/static`, serves `templates/index.html` at `/`, launches via Uvicorn on port 8000. |
| `app.py` | Python (645 lines, 26.9 KB) | Legacy Streamlit frontend (`streamlit run app.py` on port 8501); imports Plotly, pandas, and core modules. |
| `config.py` | Python (72 lines, 2.6 KB) | Configuration thresholds: `CONVICTION_THRESHOLD = 78.0`, `PILLAR_WEIGHTS` (Volume: 0.15, Sales: 0.20, OCF: 0.25, Debt: 0.15, Pricing: 0.15, Skin: 0.10), benchmark tickers. |
| `test_engine.py` | Python (120 lines, 4.3 KB) | Unit test suite using `unittest`. |
| `requirements.txt` | Text (7 lines, 95 B) | Lists `fastapi>=0.110.0`, `uvicorn>=0.29.0`, `yfinance>=0.2.38`, `pandas>=2.2.0`, `numpy>=1.26.0`, `requests>=2.31.0`. |
| `vercel.json` | JSON (9 lines, 102 B) | Serverless URL rewrite routing `/api/(.*)` to `/api/index.py`. |
| `api/index.py` | Python (10 lines, 274 B) | Vercel serverless entrypoint; configures `sys.path` and exports `app` from `server.py`. |
| `core/universe.py` | Python (217 lines, 17.1 KB) | Indian stock universes (`INDIAN_NIFTY_50`, `INDIAN_NIFTY_NEXT_50`, `INDIAN_COMMODITIES_METALS_ENERGY`, `INDIAN_MIDCAP_SMALLCAP_GROWTH`), `get_all_india_universe()`, and `format_ticker()`. |
| `core/data_fetcher.py` | Python (219 lines, 8.4 KB) | `StockDataFetcher` class; implements vectorized batch downloading (`get_batch_market_data`), screener fetcher (`get_screener_stock_data`), deep stock fetcher (`get_stock_data`), and `/tmp/py-yfinance` cache redirection. |
| `core/evaluator.py` | Python (541 lines, 24.3 KB) | `PillarEvaluator` class; evaluates the 6 pillars, calculates Piotroski F-score (0–9), Altman Z-score, valuation multiples, and detects red flags. |
| `core/backtester.py` | Python (142 lines, 6.3 KB) | `StockBacktester` class; calculates CAGR, Alpha, Beta, Sharpe ratio, Max Drawdown, and portfolio equity curve timeseries. |
| `core/risk_manager.py` | Python (92 lines, 4.6 KB) | `RiskManager` class; computes 14-period ATR, dynamic 2.0x ATR stop loss, 1:2 and 1:3.5 profit targets, and position sizing capped at 1.5% portfolio risk and 12% max allocation. |
| `templates/index.html` | HTML5 (407 lines, 26.1 KB) | Single Page Application shell; Tailwind CSS CDN, Chart.js CDN, Plotly.js CDN; contains 5 tabs (Screener, Audit, Technicals, Backtester, Risk). |
| `static/app.js` | JavaScript (839 lines, 37.8 KB) | Client-side SPA controller; handles lazy tab switching, Chart.js radar & equity curves, Plotly candlestick chart, 0ms autocomplete search, and API calls. |
| `public/index.html` | HTML5 (407 lines, 26.1 KB) | Exact binary mirror of `templates/index.html` (MD5: `b59943fa1781277cfe36304904cf4098`) for Vercel/Edge CDN deployments. |
| `public/static/app.js`| JavaScript (839 lines, 37.8 KB) | Exact binary mirror of `static/app.js` (MD5: `1908ff538efe66877f6f03f2a394d05a`) for Vercel/Edge CDN deployments. |
| `.streamlit/config.toml` | TOML (7 lines, 73 B) | Streamlit server config (`port = 8501`, `headless = true`, `gatherUsageStats = false`). |
| `README.md` | Markdown (68 lines, 3.2 KB) | Project documentation referencing Streamlit on port 8501 (outdated relative to FastAPI server). |
| `ORIGINAL_REQUEST.md` | Markdown (65 lines, 4.8 KB) | Target requirements for Investo.in dark aesthetic, institutional 6-pillar analysis, sub-second execution, and 10-suite regression verification. |

---

### 1.2 Web Frameworks & Execution Architecture
Direct verification confirms two separate application entrypoints exist in the codebase:

1. **Production Primary: FastAPI + Uvicorn (`server.py`)**
   - Framework: FastAPI `0.141.1` on Starlette `1.6.0`, running on Uvicorn `0.52.1`.
   - Entrypoint command: `uvicorn server:app --host 0.0.0.0 --port 8000 --reload` (or `python server.py`).
   - Serverless Entrypoint: `api/index.py` for Vercel deployment.
   - Serving Mechanism: `server.py` mounts `/static` via `StaticFiles(directory=STATIC_DIR)` and provides explicit fallback GET routes for `/` (serving `templates/index.html`) and `/static/app.js`.
   - Startup Lifecycle: `server.py:227-238` implements `@app.on_event("startup")` launching a daemon background thread that pre-warms the Nifty 50 screener cache into `_SCREEN_CACHE["nifty50_None_78.0"]` with a 900-second TTL.

2. **Legacy / Secondary: Streamlit (`app.py`)**
   - Framework: Streamlit `1.62.0`.
   - Command: `streamlit run app.py` (port 8501).
   - **Current Status: BROKEN.** Execution fails on line 17–20 with:
     ```python
     ImportError: cannot import name 'INDIAN_QUALITY_GROWTH' from 'core.universe'
     ```
     because `core/universe.py` was refactored into `INDIAN_MIDCAP_SMALLCAP_GROWTH` and removed `GLOBAL_US_MEGA_TECH`.

---

### 1.3 REST API Endpoints Status & Latency
All 8 API endpoints in `server.py` were directly tested using `starlette.testclient.TestClient`:

| Endpoint | Method | Test Parameter | Status Code | Observed Latency | Observed Response |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/` | GET / HEAD | - | 200 OK | < 2 ms | Serves `templates/index.html` (26,119 bytes) |
| `/static/app.js` | GET | - | 200 OK | < 2 ms | Serves `static/app.js` (37,835 bytes) |
| `/api/health` | GET | - | 200 OK | < 1 ms | `{"status": "ONLINE", "version": "2.0.0", "threshold": 78.0}` |
| `/api/search` | GET | `?q=tcs` | 200 OK | < 3 ms | Returns matched security `TCS.NS` in `results` array |
| `/api/candles/{symbol}` | GET | `symbol=TCS.NS&period=1mo` | 200 OK | 980 ms | Returns OHLCV arrays, 20 EMA, 50 SMA, 200 SMA, and 14-period RSI |
| `/api/position-size` | GET | `symbol=TCS.NS` | 200 OK | 3,730 ms | Returns ATR 14, 2.0x stop loss, target 1 & 2, recommended shares, capital at risk |
| `/api/audit/{symbol}` | GET | `symbol=TCS.NS` | 200 OK | 5,020 ms | Returns complete 6 pillars breakdown, composite score (73.0), Piotroski (7/9), Altman (3.2), and risk plan |
| `/api/backtest` | GET | `symbol=TCS.NS&period=1y&capital=100000` | 200 OK | 490 ms | Returns CAGR, Sharpe ratio, Max Drawdown, Alpha, Beta, and daily timeseries |
| `/api/screen` (Custom) | GET | `universe=custom&custom_symbols=TCS.NS,INFY.NS&threshold=70` | 200 OK | 1,440 ms | Returns 2 audited securities |
| `/api/screen` (Cold Nifty 50) | GET | `universe=nifty50&threshold=78` | 200 OK | 8,040 ms | Scans all 50 securities via batch downloader + 8 worker threads |
| `/api/screen` (Cached Nifty 50) | GET | `universe=nifty50&threshold=78` | 200 OK | **10.72 ms** | In-memory cache hit (< 20 ms requirement satisfied) |

---

### 1.4 Test Suite Status
Running `python test_engine.py` in the root workspace exited with return code 1:
```
Traceback (most recent call last):
  File "C:\Users\asaik\OneDrive\Desktop\PROJECT1\test_engine.py", line 8, in <module>
    from core.universe import format_ticker, INDIAN_NIFTY_50, GLOBAL_US_MEGA_TECH
ImportError: cannot import name 'GLOBAL_US_MEGA_TECH' from 'core.universe' (C:\Users\asaik\OneDrive\Desktop\PROJECT1\core\universe.py)
```
Inspecting `test_engine.py` line 8 revealed it attempts to import `GLOBAL_US_MEGA_TECH`, which is missing from `core/universe.py`. Furthermore:
- Line 17–18 of `test_engine.py` expects `format_ticker("AAPL") == "AAPL"`, but `core/universe.py:203-217` appends `.NS` to any non-numeric ticker that does not already end in `.NS` or `.BO`, causing `format_ticker("AAPL")` to return `"AAPL.NS"`.
- There is no automated test runner for the FastAPI API endpoints or the 10 verification suites specified in `ORIGINAL_REQUEST.md`.

---

### 1.5 Frontend Analysis vs. Requirements in ORIGINAL_REQUEST.md
Inspecting `templates/index.html` (lines 1–407) and `static/app.js` (lines 1–839):
1. **Design & Aesthetics**:
   - Current style is neutral monochrome dark (`#0A0A0A`, `#121212`, `#262626`).
   - Missing the Investo.in inspired dark aesthetic: obsidian dark background (`#080C14`), vibrant purple (`#6943FF`), indigo (`#4556DA`), and magenta (`#BA1B9A`) gradient accents, backdrop blur glassmorphism, and colored pill badges.
2. **Top Ribbon & Live Sensex/Nifty Badges**:
   - Current header has a static title and search bar.
   - Missing live Sensex/Nifty index ticker ribbons or status indicators requested in R1.
3. **PWA (Progressive Web App)**:
   - Missing `manifest.json`, service worker registration, PWA meta tags, and mobile app icons.
4. **Interactive Candlestick Terminal**:
   - Candlestick chart with 20 EMA, 50 SMA, 200 SMA, volume histogram, and RSI subplots is implemented using Plotly.js (`app.js:362-526`).
   - Bug identified: `app.js:46` attempts to resize `document.getElementById('native-candlestick-chart')`, but the element id defined in `index.html:303` is `live_candlestick_chart`.
5. **Redundant Duplicate Files**:
   - `public/index.html` and `public/static/app.js` are bit-for-bit duplicate copies of `templates/index.html` and `static/app.js`.

---

## 2. Logic Chain

```
[Observation 1.1, 1.2]: server.py defines 8 FastAPI routes, mounts static assets, serves index.html at '/', and runs on port 8000.
        ↓
[Inference 1]: FastAPI (server.py) is the primary intended production backend, while app.py is an abandoned/legacy Streamlit script.

[Observation 1.3]: Cold screen of 50 stocks takes 8.04s, but cached screen takes 10.72ms.
        ↓
[Inference 2]: The backend vectorized batch downloading (yf.download) and 15-minute in-memory TTL cache satisfy R3 (< 20ms cache hit requirement).

[Observation 1.4]: test_engine.py crashes with ImportError: cannot import name 'GLOBAL_US_MEGA_TECH'.
        ↓
[Inference 3]: core/universe.py was modified in commit a1d90c2/1da4b6c without updating test_engine.py or app.py.

[Observation 1.5]: templates/index.html uses neutral gray Tailwind classes (#0A0A0A, #121212) without gradient accents or live Sensex/Nifty badges; app.js has an ID mismatch on chart resize.
        ↓
[Inference 4]: The frontend requires a visual styling upgrade to match Investo.in dark/glassmorphic aesthetic (#6943FF, #4556DA, #BA1B9A), addition of index tickers, PWA assets, and bug fixes in app.js.
```

---

## 3. Caveats
1. **Network Dependency for Yahoo Finance**: `yf.download` and `yf.Ticker` query Yahoo Finance servers. While cold queries complete in ~8s for 50 tickers, network flakiness or rate limits could cause delays if not cached. Prewarming on startup mitigates this for the primary universe.
2. **File Synchronization**: `public/` and `templates/` / `static/` must be kept in sync so that local Uvicorn serving (`templates/` and `static/`) and Vercel edge serving (`public/`) do not diverge.
3. **Python 3.14 Environment**: The runtime is Python 3.14 on Windows; `pytest` is not installed globally in this Python installation, but Python's built-in `unittest` is fully operational.

---

## 4. Conclusion & Actionable Recommendations

### 4.1 Reusability & Architectural Assessment
| Component | Status | Recommendation |
| :--- | :--- | :--- |
| `server.py` | **Keep & Re-use (Primary)** | Excellent architecture. Maintain as primary server; port 8000. |
| `core/evaluator.py` | **Keep & Re-use** | 100% implements 6-pillar logic, Piotroski F-score, Altman Z-score, and red flag defense. |
| `core/data_fetcher.py`| **Keep & Re-use** | High performance batch market data downloader with `/tmp` safe cache. |
| `core/risk_manager.py` | **Keep & Re-use** | Clean ATR and risk allocation logic. |
| `core/backtester.py` | **Keep & Re-use** | Accurate vectorized portfolio simulation. |
| `core/universe.py` | **Refactor (Minor)** | Add backward-compatible alias `GLOBAL_US_MEGA_TECH` and update `format_ticker` to support US tickers. |
| `test_engine.py` | **Refactor & Expand** | Fix broken import and create an end-to-end 10-suite regression test suite. |
| `templates/index.html`| **Refactor (Style & UI)** | Upgrade to Investo.in dark theme (purple `#6943FF`, indigo `#4556DA`, magenta `#BA1B9A`), add live Sensex/Nifty ribbon, add PWA manifest. |
| `static/app.js` | **Refactor (UI & Fixes)**| Fix `native-candlestick-chart` resize ID mismatch, integrate live index ribbon data, align with Investo.in micro-interactions. |
| `app.py` | **Deprecate / Secondary** | Streamlit is secondary; fix imports so it does not fail if executed, but direct users to FastAPI. |
| `README.md` | **Refactor** | Update quickstart instructions to `python server.py` on `http://localhost:8000`. |

---

## 5. Verification Method

To independently verify all findings and test current system behavior:

1. **Verify Backend Health & Endpoints**:
   ```bash
   python -c "from starlette.testclient import TestClient; from server import app; client = TestClient(app); print('Health:', client.get('/api/health').json())"
   ```
2. **Verify Screener Caching Speed**:
   ```bash
   python -c "import time; from starlette.testclient import TestClient; from server import app; c = TestClient(app); c.get('/api/screen?universe=nifty50&threshold=78'); t0 = time.time(); r = c.get('/api/screen?universe=nifty50&threshold=78'); print(f'Cached screener status: {r.status_code}, time: {(time.time()-t0)*1000:.2f}ms')"
   ```
3. **Verify Current Test Failure**:
   ```bash
   python test_engine.py
   ```
   *(Expected result: `ImportError: cannot import name 'GLOBAL_US_MEGA_TECH' from 'core.universe'`)*
4. **Verify File Duplication**:
   ```bash
   python -c "import hashlib; [print(p, hashlib.md5(open(p, 'rb').read()).hexdigest()) for p in ['templates/index.html', 'public/index.html', 'static/app.js', 'public/static/app.js']]"
   ```
