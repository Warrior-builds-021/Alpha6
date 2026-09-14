# Project: ALPHA6 Institutional FinTech Platform Transformation

## Architecture
ALPHA6 is an institutional-grade quantitative equity analysis, screening, and execution terminal tailored for Indian (NSE/BSE) securities and commodities.
- **Backend**: High-performance FastAPI application (`server.py`) running on Uvicorn (port 8000), utilizing vectorized batch downloading via `yfinance`, multi-tier financial modeling, in-memory TTL caching, and serverless-safe `/tmp/py-yfinance` cache redirection.
- **Core Domain Engine**:
  - `core/universe.py`: Master Indian equities universe (Nifty 50, Nifty Next 50, Commodities, Midcaps) with backward-compatible ticker formatting.
  - `core/data_fetcher.py`: Vectorized batch downloading (`yf.download`) and deep stock profile fetcher with fallback to audited financial statements.
  - `core/evaluator.py`: Institutional 6-Pillar scoring engine (Volume 15%, Sales 20%, OCF 25%, Debt 15%, Moat 15%, Skin in Game 10%), authentic 5-ratio Edward Altman Z-Score, 9-point Piotroski F-Score with statement fallback, valuation multiples, and strict capital preservation red flag shield.
  - `core/risk_manager.py`: Dynamic 14-period ATR volatility modeling, strictly bounded 2.0x ATR stop loss, asymmetric 1:2 and 1:3.5 profit targets, and bounded position sizing.
  - `core/backtester.py`: Vectorized historical simulation engine computing CAGR, Sharpe Ratio, Max Drawdown, Alpha, and daily portfolio equity curves against Nifty 50.
- **Frontend SPA**:
  - Investo.in dark aesthetic: Obsidian black canvas (`#07080D` / `#080C14`), vibrant purple (`#6943FF`), indigo (`#4556DA`), and magenta (`#BA1B9A`) gradient accents, backdrop-blur glassmorphism (`.glass-card`), radiant active tab indicators, and stat counters.
  - 5 responsive tabs: Market Screener (with live Sensex/Nifty ribbon & sortable matrix), Forensic Audit (with radar chart & valuation multiples), Live Technical Terminal (Plotly candlestick, 20 EMA, 50 SMA, 200 SMA, volume, RSI), Strategy Backtester, and Risk Shield & Position Sizer.
  - Instant 0ms autocomplete search populated with all 150+ master Indian securities, accessible keyboard navigation with auto-scroll, and quick-action shortcuts.
  - Dual-runtime parity: Bit-for-bit mirroring between `templates/` + `static/` and `public/` + `public/static/` for local Uvicorn and Vercel edge deployment.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Universe & Ticker Handling | Complete master Indian universe (Nifty 50, Next 50, Commodities, Midcaps), backward compatibility (`GLOBAL_US_MEGA_TECH`, `INDIAN_QUALITY_GROWTH`), and clean US/Indian ticker parsing | M1 | Survey E1, E2 |
| 2 | Institutional 6-Pillar Scoring | Weighted composite score (Volume 15%, Sales 20%, OCF 25%, Debt 15%, Moat 15%, Skin 10%), fixing 0-15% revenue gap, negative net income handling, and D/E normalization | M1 | Survey E2, ORIGINAL_REQUEST §R2 |
| 3 | Authentic Altman Z-Score | Edward Altman's 5-ratio formula ($1.2X_1 + 1.4X_2 + 3.3X_3 + 0.6X_4 + 0.99X_5$) replacing 4-tier step lookup | M1 | Survey E2, ORIGINAL_REQUEST §R2 |
| 4 | Piotroski F-Score Multi-Tier Fallback | 9-point checklist with fallback from `info` to `cashflow` and `balance_sheet` tables for Indian blue chips | M1 | Survey E2, ORIGINAL_REQUEST §R2 |
| 5 | Capital Preservation Defense | Strict disqualification on bankruptcy distress ($Z < 1.8$), revenue collapse (> 10%), negative ROE, or high debt | M1 | Survey E2, ORIGINAL_REQUEST §R2 |
| 6 | Dynamic ATR Position Sizer Guard | 14-period ATR, strictly bounded 2x ATR stop loss, asymmetric profit targets, and cap guard ($P > \text{Max Cap} \implies 0$ shares) | M1 | Survey E2, ORIGINAL_REQUEST §R2 |
| 7 | Vectorized Caching & Serverless Safety | Vectorized batch downloads, in-memory TTL caching (< 20ms cache hit), single-stock audit caching, and universal `/tmp/py-yfinance` cache redirection | M1 | Survey E1, E2, ORIGINAL_REQUEST §R3 |
| 8 | Live Market Indices Route & Ribbon | Backend `/api/market-indices` querying Sensex (`^BSESN`) and Nifty 50 (`^NSEI`) with 60s TTL cache | M2 | Survey E1, E3, ORIGINAL_REQUEST §R1 |
| 9 | 0ms Autocomplete Search Scale | Client-side `LOCAL_CATALOG` expanded to all 150+ stocks in universe, instant local matching, keyboard navigation with `scrollIntoView`, and ARIA accessibility | M2 | Survey E3, ORIGINAL_REQUEST §R1 |
| 10 | Investo.in Dark Aesthetic & Design Tokens | Obsidian theme (`#07080D`), purple (`#6943FF`), indigo (`#4556DA`), magenta (`#BA1B9A`) gradient accents, glassmorphic card elevations, radiant borders, and glowing active tab indicators | M3 | Survey E3, ORIGINAL_REQUEST §R1 |
| 11 | Tab 1 Screener Enhancements | Live Sensex & Nifty index ribbon, filterable search input on ranking table, and sortable table columns | M3 | Survey E3, ORIGINAL_REQUEST §R1 |
| 12 | Tab 2 Forensic Audit UI Upgrades | Valuation multiples card (P/E, P/B, PEG, EV/EBITDA), Piotroski 9-point criteria details list, and branded purple/magenta radar chart | M3 | Survey E3, ORIGINAL_REQUEST §R1 |
| 13 | Tab 3 Live Candlestick Terminal | Fix Plotly resize DOM ID mismatch (`live_candlestick_chart`), resize trigger on tab reactivation, branded EMA/SMA indicator colors, and obsidian styling | M3 | Survey E1, E3, ORIGINAL_REQUEST §R1 |
| 14 | Tab 4 & 5 Strategy & Risk UI | Strategy backtester equity curve gradient fills, interactive position sizing visual meter, and safety boundary tags | M3 | Survey E3, ORIGINAL_REQUEST §R1 |
| 15 | Performance & PWA Assets | Defer Plotly/Chart.js scripts for < 1s initial load, create `manifest.json`, `sw.js`, and mobile horizontal scroll tab strip | M3 | Survey E3, ORIGINAL_REQUEST §R1, R3 |
| 16 | Dual-Runtime Parity Sync | Ensure `templates/index.html` <-> `public/index.html` and `static/app.js` <-> `public/static/app.js` maintain exact parity | M3 | Survey E1, E3 |
| 17 | 10-Suite Automated Regression Suite | Comprehensive test suite covering health, search, screener, audit, candlesticks, backtest, position sizing, static assets, error handling, and performance | E2E Track | ORIGINAL_REQUEST §Verification Plan |
| 18 | Final E2E Test Suite Pass (100%) | Verify all test tiers (Tiers 1-4) achieve 100% pass rate with zero unhandled exceptions | M4 | Project Pattern |
| 19 | Adversarial Coverage Hardening (Tier 5) | White-box stress-testing, boundary edge cases, and forensic integrity audit | M5 | Project Pattern |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2E | E2E Testing Track | Design 10-suite regression verification test runner & test cases (Tiers 1-4) deriving from requirements; publish TEST_READY.md | none | IN_PROGRESS |
| M1 | Backend & Quantitative Engine | Fix universe imports, 6-pillar scoring, authentic Altman Z-score, Piotroski fallback, ATR position cap guard, `/tmp` cache redirection | none | DONE |
| M2 | Market Indices & Search Backend/Catalog | Add `/api/market-indices`, expand `LOCAL_CATALOG` to 150+ stocks, ARIA & keyboard navigation | M1 | PLANNED |
| M3 | Investo.in UI/UX & Terminal Transformation | Obsidian styling, purple/indigo/magenta gradients, glassmorphism, live index ribbon, valuation card, Plotly resize fix, PWA, script deferral, dual-runtime parity | M2 | PLANNED |
| M4 | Final E2E Test Suite Pass | Run and pass 100% of the E2E test suite (Tiers 1-4) across all endpoints and UI components | M3, E2E | PLANNED |
| M5 | Adversarial Hardening & Forensic Audit | Tier 5 adversarial stress testing and forensic integrity verification | M4 | PLANNED |

## Interface Contracts
### Market Indices API
- `GET /api/market-indices`
  - Response:
    ```json
    {
      "status": "OK",
      "timestamp": "2026-09-14T01:30:00Z",
      "indices": [
        {"symbol": "^BSESN", "name": "BSE SENSEX", "price": 82890.94, "change": 234.50, "percent_change": 0.28},
        {"symbol": "^NSEI", "name": "NIFTY 50", "price": 25356.50, "change": 89.20, "percent_change": 0.35}
      ]
    }
    ```

### Forensic Audit API
- `GET /api/audit/{symbol}`
  - Returns `composite_score`, `verdict`, `pillars` (1 to 6), `piotroski_f_score`, `piotroski_details`, `altman_z_score`, `altman_zone`, `valuation` (`pe_ratio`, `pb_ratio`, `peg_ratio`, `ev_ebitda`), and `red_flags`.

### Position Sizing API
- `GET /api/position-size?symbol={symbol}&portfolio_size={size}&risk_pct={risk}`
  - Returns `recommended_shares` (0 if unit price > max cap), `stop_loss`, `target_1`, `target_2`, `total_investment`, `risk_amount`, `portfolio_weight_pct`.

## Code Layout
- `server.py`: FastAPI server, REST API endpoints, static mounting.
- `core/`:
  - `universe.py`: Stock universes, ticker formatting, aliases.
  - `data_fetcher.py`: Batch market data, single stock financial statements, cache redirection.
  - `evaluator.py`: 6-Pillar evaluation, Altman Z-Score, Piotroski F-Score, red flags.
  - `risk_manager.py`: ATR 14, 2.0x stop loss, position sizing bounds.
  - `backtester.py`: Vectorized backtesting, benchmark comparison.
- `templates/index.html` & `public/index.html`: Investo.in dark SPA shell, glassmorphic layout.
- `static/app.js` & `public/static/app.js`: SPA frontend logic, tabs, Plotly charts, 0ms search.
- `static/manifest.json`: PWA manifest.
- `static/sw.js`: Service worker.
- `tests/test_e2e_suites.py`: 10-suite regression verification test runner.
