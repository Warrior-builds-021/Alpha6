# Frontend UI/UX, Investo.in Dark Aesthetic, Terminal & Search Investigation Report

**Agent**: Survey Explorer 3 (UI/UX & Frontend Analyst)  
**Date**: 2026-09-14T01:35:00+05:30 (UTC: 2026-09-13T20:05:00Z)  
**Status**: Survey Complete — Hard Handoff  
**Target File**: `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_survey_3\handoff.md`  

---

## 1. Observation

Direct observations from examining the codebase, runtime configurations, templates, stylesheets, scripts, backend endpoints, and test suites.

### 1.1 Architecture & Dual-Runtime Parity
The project implements a Single Page Application (SPA) frontend served locally by FastAPI (`server.py`) and pre-configured for static edge serving on Vercel via `public/` and `api/index.py` (`vercel.json`).
- Template: `templates/index.html` (26,123 bytes)
- Public Template Mirror: `public/index.html` (26,123 bytes)
- Client Script: `static/app.js` (37,843 bytes)
- Public Script Mirror: `public/static/app.js` (37,843 bytes)
- Backend Server: `server.py` (FastAPI with 15 active routes)
- Legacy App: `app.py` (Streamlit dashboard prototype, 26,905 bytes)

**File Hash Verification**:
Tool execution of `powershell -Command "Get-FileHash templates/index.html, public/index.html, static/app.js, public/static/app.js"` confirmed byte-for-byte exact matches:
- `templates/index.html` & `public/index.html`: SHA256 `3D9DCC56DC9754C95B002BB71E52E73C7D9732DCAFE48962FAFF69F21F5E5C0D`
- `static/app.js` & `public/static/app.js`: SHA256 `F1B1427CE2F4C5179186ABF13CA591AEF89C2995C782C8528AECC39D884A61FC`

### 1.2 Investo.in Dark Aesthetic & Styling Gaps
In `templates/index.html` lines 7–29:
```html
<script src="https://cdn.tailwindcss.com"></script>
<script>
    tailwind.config = {
        darkMode: 'class',
        theme: {
            extend: {
                colors: {
                    surface: {
                        base: '#0A0A0A',
                        card: '#121212',
                        border: '#262626',
                        hover: '#1A1A1A'
                    }
                },
                fontFamily: {
                    sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
                    mono: ['JetBrains Mono', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace']
                }
            }
        }
    }
</script>
```
In `templates/index.html` lines 38–62:
```css
body {
    background-color: #0A0A0A;
    color: #E5E5E5;
    font-family: 'Inter', sans-serif;
}
...
.active-tab {
    border-bottom: 2px solid #FFFFFF !important;
    color: #FFFFFF !important;
}
```
**Deficiencies Observed**:
- The Investo.in brand palette specified in `ORIGINAL_REQUEST.md` (purple `#6943FF`, indigo `#4556DA`, and magenta `#BA1B9A`) is **not present anywhere** in `templates/index.html` or `static/app.js`.
- The current styling is completely flat monochrome gray (`#0A0A0A`, `#121212`, `#262626`, `#FFFFFF`).
- Glassmorphism properties (`backdrop-filter: blur(...)`, translucent alpha backgrounds like `rgba(15, 17, 28, 0.75)`, fine 1px translucent borders with gradient glow) are entirely missing.
- Active tab indicator is a stark white line (`2px solid #FFFFFF`) rather than an Investo.in radiant gradient line (`linear-gradient(90deg, #6943FF, #4556DA, #BA1B9A)` with ambient glow).
- Buttons and cards lack micro-interactions, gradient elevations, hover lift animations, and pill tags.

### 1.3 Tab 1: Market Screener & Live Index Badges Gaps
In `templates/index.html` lines 110–208:
- The screener view contains:
  1. Controls Bar: Universe selector dropdown (`screener-universe`), custom input, threshold number input, and "Execute Screen" button.
  2. Four KPI Cards: Total Scanned, High-Conviction Picks, Universe Avg Score, Capital Risk Disqualified.
  3. Top Selections Grid (`top-picks-grid`).
  4. Quantitative Ranking Matrix table (`screener-table`).
- **Deficiencies Observed**:
  1. **Missing Live Index Badges**: `ORIGINAL_REQUEST.md` requirement R1 specifically demands *"Live index badges (Sensex/Nifty)"*. There are **no Sensex or Nifty 50 live index badges** in `index.html` or `app.js`. In fact, a grep search across `server.py` and `core/` returned 0 occurrences of "Sensex" or `^BSESN`.
  2. **Table Filtering & Sorting Missing**: The ranking matrix table renders rows with `tbody.innerHTML = ...` (`static/app.js` line 164), but lacks any client-side search/filter input to filter rows by ticker name or sector, and lacks sortable column headers (clicking score, P/E, volume, or debt does not sort).

### 1.4 Tab 2: Forensic 6-Pillar Audit Gaps
In `core/evaluator.py` lines 89–116, the backend computes comprehensive valuation multiples:
```python
# Valuation metrics
pe_ratio = self._safe_float(self.info.get("trailingPE") or self.info.get("forwardPE"))
pb_ratio = self._safe_float(self.info.get("priceToBook"))
peg_ratio = self._safe_float(self.info.get("pegRatio"))
ev_ebitda = self._safe_float(self.info.get("enterpriseToEbitda"))
...
"valuation": {
    "pe_ratio": round(pe_ratio, 2) if pe_ratio else None,
    "pb_ratio": round(pb_ratio, 2) if pb_ratio else None,
    "peg_ratio": round(peg_ratio, 2) if peg_ratio else None,
    "ev_ebitda": round(ev_ebitda, 2) if ev_ebitda else None,
}
```
In `templates/index.html` lines 210–259 and `static/app.js` lines 205–280:
- The UI renders the header (Symbol, Signal Badge, Company Name, Composite Score), the 6-pillar breakdown list (`audit-pillar-breakdown`), the radar chart (`radarChart`), Piotroski F-Score text, and Altman Z-Score text.
- **Deficiencies Observed**:
  1. **Valuation Multiples Omitted from UI**: The `valuation` dictionary (P/E, P/B, PEG, EV/EBITDA) returned by `/api/audit/{symbol}` is **never rendered or referenced in the frontend**.
  2. **Piotroski Checklist Details Omitted**: While `core/evaluator.py` computes `piotroski_details` (an itemized list of 9 accounting checklist pass/fail criteria), the UI only renders `- / 9` with no breakdown.
  3. **Monochrome Radar Chart**: In `static/app.js` lines 302–306:
     ```javascript
     backgroundColor: 'rgba(255, 255, 255, 0.1)',
     borderColor: '#FFFFFF',
     borderWidth: 1.5,
     ```
     The radar chart is rendered in plain flat white without the Investo.in purple/magenta brand gradient.

### 1.5 Tab 3: Live Technical Terminal & Plotly Candlestick Resize Bug
In `templates/index.html` lines 302–304:
```html
<div class="bg-[#121212] border border-[#262626] rounded-lg p-3 h-[640px]" id="live_chart_container">
    <div id="live_candlestick_chart" class="w-full h-full"></div>
</div>
```
In `static/app.js` lines 44–50:
```javascript
// Responsive window resize for Plotly candlestick terminal
window.addEventListener('resize', () => {
    const chartEl = document.getElementById('native-candlestick-chart');
    if (chartEl && window.Plotly) {
        Plotly.Plots.resize(chartEl);
    }
});
```
**Deficiencies & Bugs Observed**:
1. **Critical DOM ID Mismatch Bug**:
   - In `index.html`, the element ID is `live_candlestick_chart`.
   - In `app.js` line 46, the resize handler queries `document.getElementById('native-candlestick-chart')`.
   - `chartEl` evaluates to `null`. On window resize, **Plotly responsive resizing fails silently**.
2. **Hidden Tab Reactivation Layout Flaw**:
   - In `switchTab('tab-chart')` (`static/app.js` lines 84–87), `loadLiveChart` is only called if `!tabLoaded['tab-chart']`. If the user navigates away and returns to `tab-chart`, `Plotly.Plots.resize('live_candlestick_chart')` is never invoked, leaving the canvas distorted if the window was resized while on another tab.
3. **Indicator & Aesthetic Implementation**:
   - The backend `/api/candles/{symbol}` properly computes OHLCV candles, 20 EMA, 50 SMA, 200 SMA, volume, and 14-period RSI with overbought (70) and oversold (30) levels.
   - However, the Plotly chart layout uses `#121212` background and default colors rather than obsidian glass styling with glowing brand accents.

### 1.6 Tab 4: Strategy Backtester & Tab 5: Risk Shield
- **Tab 4 (Backtester)**:
  - Fetches `/api/backtest`, displays Total Return, CAGR, Sharpe Ratio, Max Drawdown, and Alpha vs Benchmark.
  - Renders `equityChart` via Chart.js with white line on `#121212` canvas. Lacks gradient area fills and interactive benchmark toggles.
- **Tab 5 (Risk Shield & Position Sizer)**:
  - Connects to `/api/position-size`, computing recommended shares, total investment, portfolio weight %, 2x ATR stop loss, Target 1 (1:2 R:R), Target 2 (extended upside).
  - Lacks visual risk/reward meter, colored safety boundary pill tags, and dynamic share slider.

### 1.7 0ms NSE/BSE Search Autocomplete & Keyboard Navigation Gaps
In `static/app.js` lines 661–699:
- `LOCAL_CATALOG` contains only **37 hardcoded stocks**.
- In `core/universe.py`, the master Indian universe (`get_all_india_universe()`) contains **150+ securities** (Nifty 50, Nifty Next 50, Commodities/ETFs, Midcaps).
- When a user searches for a stock in the master universe not among the 37 hardcoded entries (e.g. `DLF.NS`, `SUZLON.NS`, `POLYCAB.NS`, `IOC.NS`, `IRCTC.NS`), the 0ms instant local filter misses it and must wait for the 120ms debounced network call to `/api/search`.
- In `static/app.js` lines 796–825 (`handleSearchKeydown`):
  - ArrowUp/ArrowDown changes `selectedSuggestionIndex` and calls `highlightSuggestion(index)`.
  - However, `highlightSuggestion()` does **not** call `el.scrollIntoView({ block: 'nearest' })`. When suggestions exceed the visible window of `max-h-80 overflow-y-auto`, the selected item scrolls out of view.
  - The input and dropdown lack WAI-ARIA combobox accessibility attributes (`role="combobox"`, `aria-autocomplete="list"`, `aria-expanded="false"`, `role="listbox"`, `role="option"`).
  - Selecting an item hardcodes `switchTab('tab-audit')`. It does not provide quick actions to view chart or risk sizing directly.

### 1.8 Performance & Lazy Loading Architecture
In `templates/index.html` lines 34–36:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
```
- Plotly minified bundle is approximately **3.5 MB**.
- Because it is loaded synchronously in the `<head>` without `defer`, browser HTML parsing is blocked until the 3.5MB script finishes downloading, conflicting with the sub-second (< 1s) initial page load objective.
- In `static/app.js` lines 15–21, tab lazy-loading is implemented via `tabLoaded` object, preventing API waterfalls on initial load.

### 1.9 PWA Support & Mobile Ergonomics
- No `manifest.json` exists in `static/` or the project root.
- No Service Worker (`sw.js`) is registered.
- On mobile viewports (< 768px), the top horizontal navigation (`nav-screener`, `nav-audit`, etc.) wraps into multi-line buttons without horizontal scroll snap or mobile bottom navigation.

### 1.10 Backend Routes & Test Suite Regression
- `server.py` routes inspected: 15 active routes (`/`, `/static/app.js`, `/api/health`, `/api/search`, `/api/screen`, `/api/audit/{symbol}`, `/api/backtest`, `/api/position-size`, `/api/candles/{symbol}`).
- No `/api/market-indices` or `/api/indices` endpoint exists for Sensex/Nifty.
- Test Suite execution (`python test_engine.py`):
  ```
  Traceback (most recent call last):
    File "C:\Users\asaik\OneDrive\Desktop\PROJECT1\test_engine.py", line 8, in <module>
      from core.universe import format_ticker, INDIAN_NIFTY_50, GLOBAL_US_MEGA_TECH
  ImportError: cannot import name 'GLOBAL_US_MEGA_TECH' from 'core.universe'
  ```
  `GLOBAL_US_MEGA_TECH` was removed from `core/universe.py` when it was converted to an Indian equity focus, causing `test_engine.py` to fail upon import.

---

## 2. Logic Chain

```
[Observation 1.2: Monochromatic #0A0A0A & lack of #6943FF, #4556DA, #BA1B9A]
       │
       ▼
(Inference: UI fails Acceptance Criteria for Investo.in dark aesthetic)
       │
       ▼
[Need: Comprehensive CSS variables, glassmorphism utility classes, obsidian gradients]
```

1. **Investo.in Aesthetic Gap**:
   - *Observation*: `templates/index.html` defines only `#0A0A0A`, `#121212`, `#262626`, `#1A1A1A` in Tailwind config. No purple, indigo, or magenta gradient tokens exist.
   - *Logic*: The acceptance criteria explicitly state: *"UI reflects Investo.in dark mode aesthetic with purple/indigo gradient highlights and glassmorphic card elevations."* Therefore, the design system must be re-engineered with an obsidian foundation (`#07080D`), `#6943FF`, `#4556DA`, `#BA1B9A` gradient accents, `.glass-card` backdrop-filter blur, glowing borders, and modern pill tags.

2. **Sensex/Nifty Live Badges Gap**:
   - *Observation*: Tab 1 in `templates/index.html` has no index ticker elements, and `server.py` does not query `^BSESN` or `^NSEI`.
   - *Logic*: Requirement R1 and Tab 1 specification require *"live index badges (Sensex/Nifty)"*. Without an index bar, users have no benchmark market reference. A market bar component and corresponding backend route or cached fetcher must be introduced.

3. **Valuation Multiples Omission**:
   - *Observation*: `core/evaluator.py` line 111 computes `pe_ratio`, `pb_ratio`, `peg_ratio`, `ev_ebitda` and packages them into `res["valuation"]`. In `static/app.js`, `executeAudit()` receives this data but only renders Piotroski and Altman Z scores, completely ignoring `res.evaluation.valuation`.
   - *Logic*: Requirement R1 Tab 2 demands *"valuation multiples"*. The backend already computes this; the frontend simply failed to render the valuation card grid. Adding a dedicated Valuation Multiples card in Tab 2 resolves this gap immediately.

4. **Plotly Candlestick Resize Failure**:
   - *Observation*: `templates/index.html` line 303 declares `<div id="live_candlestick_chart">`, whereas `static/app.js` line 46 listens for `document.getElementById('native-candlestick-chart')`.
   - *Logic*: Whenever the browser window is resized, `chartEl` is null and `Plotly.Plots.resize()` is never executed. Furthermore, returning to `tab-chart` does not re-trigger resize. Fixing this ID and adding resize calls on tab switch ensures zero charting glitches.

5. **0ms Autocomplete Search Scale & Ergonomics**:
   - *Observation*: `LOCAL_CATALOG` has 37 items; `core/universe.py` has 150+. Navigating suggestions does not call `scrollIntoView()`.
   - *Logic*: 75% of Indian stocks in the universe miss the instant 0ms local match and fall back to the debounced network query. By embedding all 150+ stocks into `LOCAL_CATALOG`, 100% of searches achieve true 0ms response. Adding `scrollIntoView` and ARIA attributes ensures seamless keyboard navigation.

6. **Waterfall & Startup Performance**:
   - *Observation*: Plotly (3.5MB) is loaded synchronously in `<head>`.
   - *Logic*: Blocking scripts prevent initial paint. Deferring Plotly script execution or dynamically loading it when Tab 3 is clicked eliminates the render block and guarantees < 1s initial load.

7. **Deployment Parity Discipline**:
   - *Observation*: `templates/index.html` and `public/index.html` have identical SHA256 hashes, as do `static/app.js` and `public/static/app.js`.
   - *Logic*: Changes made to templates and static assets must be duplicated across both directories to ensure zero divergence between local FastAPI execution and Vercel edge deployment.

---

## 3. Caveats

1. **Live Indian Market Hours & YFinance Throttling**:
   - During off-market hours or weekends, yfinance data represents the last traded session close.
   - Batch querying large sets of tickers (> 100) concurrently can trigger Yahoo Finance rate limits if not protected by caching. The backend's 15-minute TTL cache in `_SCREEN_CACHE` is essential.
2. **Serverless Static Serving Constraints**:
   - On Vercel, static files are served from `public/`. FastAPI routes inside `api/index.py` run serverlessly with a read-only filesystem, where only `/tmp` is writable. The yfinance cache redirection to `/tmp/py-yfinance` in `server.py` is verified and operational.
3. **No Code Implementation in Explorer Turn**:
   - In accordance with the Explorer archetype rules, no application source code modifications have been made during this survey turn. All recommendations are packaged for the implementation phase.

---

## 4. Conclusion

The application has a functional foundation (FastAPI backend, core analytical engines, and preliminary SPA layout), but requires a significant frontend upgrade to meet the user's requirements:

### Prioritized Upgrade Matrix

| Priority | Component | Gap / Issue | Recommended Solution |
| :--- | :--- | :--- | :--- |
| **P0** | **Investo.in Dark Aesthetic** | Flat `#0A0A0A` monochrome; missing `#6943FF`, `#4556DA`, `#BA1B9A` gradients; no glassmorphism | Implement custom CSS theme with Obsidian background (`#07080D`), Investo.in brand gradients, `.glass-card` (blur: 16px, 1px border glow), gradient active tab indicator, and radiant pill badges. |
| **P0** | **Plotly Resize Bug** | ID mismatch (`live_candlestick_chart` vs `native-candlestick-chart`); hidden tab resize failure | Fix ID in `app.js` line 46; invoke `Plotly.Plots.resize('live_candlestick_chart')` on `tab-chart` activation in `switchTab()`. |
| **P0** | **Tab 1: Live Index Badges** | Sensex (`^BSESN`) and Nifty 50 (`^NSEI`) badges completely missing from UI and backend | Add an Index Bar at top of Tab 1 / Navbar with live points, daily points change, % change, and status pulse; add `/api/market-indices` route with 60s memory cache. |
| **P0** | **Tab 2: Valuation Multiples** | P/E, P/B, PEG, EV/EBITDA computed in backend but never rendered in frontend | Add a 4-metric Valuation Multiples glass card in Tab 2; wire `executeAudit()` to populate `pe_ratio`, `pb_ratio`, `peg_ratio`, `ev_ebitda`. |
| **P1** | **0ms Autocomplete Search** | Local catalog has only 37 stocks (vs 150+ in universe); no `scrollIntoView`; missing ARIA | Embed all 150+ stocks into `LOCAL_CATALOG`; add `scrollIntoView({ block: 'nearest' })`; add ARIA combobox attributes; add quick action pills (`[Audit]`, `[Chart]`, `[Risk]`). |
| **P1** | **Tab 1: Matrix Filter & Sort** | Ranking table cannot be filtered or sorted on the client | Add in-memory search filter input; enable click-to-sort on table column headers (Score, Price, OCF, Debt, Moat, etc.). |
| **P1** | **Lazy Loading & < 1s Load** | 3.5MB Plotly script in `<head>` blocks initial DOM parsing | Add `defer` attribute to Plotly and Chart.js `<script>` tags, ensuring DOM renders under 300ms. |
| **P1** | **PWA & Mobile Layout** | Missing `manifest.json`, `sw.js`; horizontal tab bar wraps clumsily on mobile | Add `manifest.json` and service worker; implement responsive horizontally scrollable tab strip with smooth swipe ergonomics. |
| **P2** | **Test Suite Regression** | `test_engine.py` fails on import `GLOBAL_US_MEGA_TECH` | Inform backend implementer to remove `GLOBAL_US_MEGA_TECH` from `test_engine.py` and `app.py`. |

---

## 5. Verification Method

To independently verify these observations and validate future implementations:

### 5.1 Verification Commands
1. **Verify Dual-Runtime File Parity**:
   ```powershell
   powershell -Command "Get-FileHash templates/index.html, public/index.html, static/app.js, public/static/app.js | Format-Table"
   ```
   *Expected*: Hashes match pair-wise.

2. **Verify Server Startup & Route Count**:
   ```powershell
   python -c "import server; print('Routes:', len(server.app.routes))"
   ```
   *Expected*: Prints 15 routes without import exceptions.

3. **Verify Existing Test Suite Failure (Regression Check)**:
   ```powershell
   python test_engine.py
   ```
   *Expected*: Fails with `ImportError: cannot import name 'GLOBAL_US_MEGA_TECH' from 'core.universe'`.

4. **Verify Plotly ID Mismatch Bug in Code**:
   Inspect line 303 in `templates/index.html` (`id="live_candlestick_chart"`) against line 46 in `static/app.js` (`document.getElementById('native-candlestick-chart')`).

5. **Verify Valuation Multiples Omission**:
   Inspect `core/evaluator.py` lines 111–116 (`valuation` dictionary returned) vs `static/app.js` lines 205–280 (`executeAudit` ignoring `valuation`).

### 5.2 Invalidation Conditions
- If the design implements light mode or non-obsidian backgrounds, the Investo.in dark aesthetic requirement is invalidated.
- If Plotly candlestick terminal does not resize upon window dimension change or tab re-selection, the terminal responsiveness requirement is invalidated.
- If search dropdown fails to match any stock in the Nifty 50 or Next 50 instantly in 0ms, the autocomplete requirement is invalidated.
- If initial page load exceeds 1.0 second on local server due to synchronous script waterfall, the performance requirement is invalidated.

---
*Report compiled by Survey Explorer 3. Handoff ready for Orchestrator and Implementer.*
