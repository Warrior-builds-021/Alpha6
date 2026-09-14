# Worker M2-M3 Dispatch: Investo.in Dark UI/UX, Market Indices, Live Terminal & PWA Transformation

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Assignment
Implement the complete Investo.in dark aesthetic, responsive app shell, live market indices route, 0ms autocomplete universe expansion, Plotly candlestick terminal resize fix, and PWA assets.

### Input Files to Study:
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\ORIGINAL_REQUEST.md`
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\PROJECT.md`
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_survey_3\handoff.md`
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\templates\index.html`
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\static\app.js`
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\server.py`

### Exclusive Write Ownership:
- `server.py`
- `templates/index.html`
- `static/app.js`
- `static/manifest.json`
- `static/sw.js`
- `public/index.html` (must mirror `templates/index.html` exactly)
- `public/static/app.js` (must mirror `static/app.js` exactly)
- `public/static/manifest.json` (must mirror `static/manifest.json` exactly)

### Detailed Implementation Tasks:

#### 1. Backend Route in `server.py`: `/api/market-indices`
- Add a new endpoint: `GET /api/market-indices`
- Queries BSE Sensex (`^BSESN`) and Nifty 50 (`^NSEI`) using `yf.download` or `StockDataFetcher` with a 60-second in-memory TTL cache (`_INDEX_CACHE`).
- Returns JSON:
  ```json
  {
    "status": "OK",
    "timestamp": "...",
    "indices": [
      {
        "symbol": "^BSESN",
        "name": "BSE SENSEX",
        "price": 82890.94,
        "change": 234.50,
        "percent_change": 0.28
      },
      {
        "symbol": "^NSEI",
        "name": "NIFTY 50",
        "price": 25356.50,
        "change": 89.20,
        "percent_change": 0.35
      }
    ]
  }
  ```
- If network/market data is momentarily unavailable, gracefully fall back to cached or last-known baseline values without crashing (HTTP 200 OK).

#### 2. Investo.in Dark UI/UX Transformation in `templates/index.html`:
- **Color Palette & Tokens**:
  - Obsidian dark foundation: background `#07080D` / `#080C14`, card surfaces `rgba(15, 20, 32, 0.75)` with `backdrop-filter: blur(16px)` glassmorphism, border `rgba(105, 67, 255, 0.18)` / `#1E2433`.
  - Vibrant brand gradients: purple (`#6943FF`), indigo (`#4556DA`), and magenta (`#BA1B9A`).
  - Radiant accents: buttons with `linear-gradient(135deg, #6943FF 0%, #4556DA 50%, #BA1B9A 100%)`, hover glow effects, micro-interaction lift animations.
  - Active tab indicator: gradient underline `linear-gradient(90deg, #6943FF, #4556DA, #BA1B9A)` with ambient purple glow.
  - Clean pill tags, stat counters, and live status pulses.
- **Top Bar / Navigation**:
  - Live Sensex & Nifty index ribbon in header/navbar with real-time points, daily change, % change badge (green/red), and live pulse indicator.
  - Responsive horizontally scrollable tab strip for mobile and tablet viewports (`overflow-x-auto no-scrollbar`).
- **Tab 1 (Market Screener)**:
  - Live index ribbon rendered at top.
  - Client-side search filter input on the ranking matrix table (filter by ticker/company name).
  - Sortable column headers (click on Score, Price, OCF, Debt, Moat to toggle sort ascending/descending).
- **Tab 2 (Forensic Audit)**:
  - Dedicated **Valuation Multiples** card displaying P/E, P/B, PEG, and EV/EBITDA ratios with contextual evaluation tags.
  - Itemized Piotroski 9-point criteria checklist accordion/breakdown.
  - Radar chart styled with Investo.in brand purple/magenta fill (`rgba(105, 67, 255, 0.25)` and `#6943FF` border with points in `#BA1B9A`).
- **Tab 3 (Live Technical Terminal)**:
  - Fix the Plotly resize bug in `static/app.js:46`: change `document.getElementById('native-candlestick-chart')` to `document.getElementById('live_candlestick_chart')`.
  - Add Plotly resize trigger in `switchTab('tab-chart')` when returning to the chart tab.
  - Style Plotly layout with obsidian dark canvas, clean gridlines, and branded indicator colors (20 EMA in purple `#6943FF`, 50 SMA in cyan/indigo `#4556DA`, 200 SMA in amber/magenta `#BA1B9A`, RSI in purple).
- **Tab 4 & Tab 5**:
  - Strategy Backtester: Chart.js equity curve with purple gradient fill and benchmark comparison toggle.
  - Risk Shield: Visual risk-reward meter, colored safety boundary pill tags, and dynamic ATR position calculator.
- **Performance & Lazy Loading**:
  - Add `defer` attribute to Plotly (`plotly-2.35.2.min.js`) and Chart.js `<script>` tags in `<head>` so HTML parses immediately (< 1s load).
- **PWA Assets**:
  - Create `static/manifest.json` (and `public/static/manifest.json`) with PWA metadata (name: "ALPHA6 Quantitative FinTech", short_name: "ALPHA6", theme_color: "#07080D", background_color: "#07080D", display: "standalone").
  - Create `static/sw.js` (and `public/static/sw.js`) with service worker caching for static assets.
  - Link `manifest.json` and register `sw.js` in `templates/index.html`.

#### 3. 0ms Autocomplete Search Universe Expansion in `static/app.js`:
- Expand `LOCAL_CATALOG` from 37 items to include all 150+ stocks from `core/universe.py` (`INDIAN_NIFTY_50`, `INDIAN_NIFTY_NEXT_50`, `INDIAN_COMMODITIES_METALS_ENERGY`, `INDIAN_MIDCAP_SMALLCAP_GROWTH`).
- Ensure 0ms instant local filtering without waiting for network debouncing.
- Improve keyboard navigation: call `suggestionElement.scrollIntoView({ block: 'nearest' })` when ArrowUp/ArrowDown is pressed so highlighted suggestions stay visible.
- Add WAI-ARIA combobox accessibility attributes (`role="combobox"`, `aria-autocomplete="list"`, `aria-expanded="false"`, `role="listbox"`, `role="option"`).

#### 4. Dual-Runtime Parity Sync:
- Ensure byte-for-byte exact copies between:
  - `templates/index.html` -> `public/index.html`
  - `static/app.js` -> `public/static/app.js`
  - `static/manifest.json` -> `public/static/manifest.json`
  - `static/sw.js` -> `public/static/sw.js`

### Verification Requirements:
1. Run `python tests/test_e2e_suites.py` - all 10 suites MUST pass (including Suite 10 for static assets & manifest).
2. Test `/api/market-indices` endpoint:
   `python -c "from starlette.testclient import TestClient; import server; c = TestClient(server.app); r = c.get('/api/market-indices'); print(r.status_code, r.json())"`
3. Verify file hashes between `templates/` and `public/`, and `static/` and `public/static/` match.
4. Write comprehensive handoff report to `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\worker_m2_m3\handoff.md` and notify parent via `send_message`.

## 2026-09-13T20:50:50Z
You are Worker M2-M3. Your role is Frontend UI/UX & API Implementer.
Read your dispatch at `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\worker_m2_m3\DISPATCH.md`.
Read `c:\Users\asaik\OneDrive\Desktop\PROJECT1\ORIGINAL_REQUEST.md`, `PROJECT.md`, and the survey report at `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_survey_3\handoff.md`.
Implement all requirements:
1. Backend `/api/market-indices` route in `server.py` with 60s TTL cache.
2. Investo.in dark aesthetic in `templates/index.html`: obsidian background, purple/indigo/magenta gradients, glassmorphic cards, live index ribbon, valuation multiples card, Plotly resize bug fix, script deferral, PWA manifest and service worker.
3. 0ms autocomplete search in `static/app.js`: expand `LOCAL_CATALOG` to 150+ stocks, keyboard navigation with `scrollIntoView`, ARIA attributes.
4. Dual-runtime parity: mirror `templates/` and `static/` to `public/` and `public/static/`.
Run test suites:
- `python tests/test_e2e_suites.py`
- Test `/api/market-indices`
Write your complete handoff report to `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\worker_m2_m3\handoff.md`.
Notify parent via send_message.

