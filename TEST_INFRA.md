# E2E Test Infra: ALPHA6 Quantitative FinTech Platform

## Test Philosophy
- Opaque-box, requirement-driven testing based directly on `ORIGINAL_REQUEST.md`.
- No dependency on implementation internals; all tests interact via HTTP API endpoints, responses, data integrity, and static asset delivery.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial + Real-World Workload Testing.

## 10-Suite Regression Inventory
| Suite # | Suite Name | Scope & Coverage | Target Verification |
|---------|------------|------------------|---------------------|
| Suite 1 | Health & Configuration | `/api/health` status, version, conviction threshold (78.0) | HTTP 200, valid JSON schema |
| Suite 2 | Fast Search Autocomplete | `/api/search?q=...` instant suggestions, Indian NSE/BSE tickers | Response latency, fuzzy & exact matching, results formatting |
| Suite 3 | Quantitative Screener Engine | `/api/screen` custom & Nifty 50 universes, ranking matrix, disqualification | Valid response schema, capital risk flags, sorting by score |
| Suite 4 | Screener Caching & Latency | Warm cache latency test on `/api/screen?universe=nifty50` | Sub-20ms cache hit response time verification |
| Suite 5 | Forensic 6-Pillar Audit | `/api/audit/{symbol}` for Indian blue chips (TCS, RELIANCE, INFY) | 6 pillars breakdown, composite score (0-100), verdict, valuation multiples |
| Suite 6 | Altman Z-Score & Piotroski F-Score | Authentic 5-ratio Altman Z-score and 9-point Piotroski F-score with statements fallback | Z-score values vary accurately with financials; F-score reflects true balance sheet |
| Suite 7 | Live Candlestick Terminal | `/api/candles/{symbol}` for multiple periods (1mo, 3mo, 1y) | OHLCV candles, 20 EMA, 50 SMA, 200 SMA, volume, 14 RSI |
| Suite 8 | Strategy Backtester Engine | `/api/backtest?symbol=...&period=1y&capital=100000` | CAGR, Sharpe Ratio, Max Drawdown, Alpha, Beta, daily equity curve |
| Suite 9 | Risk Shield & Position Sizer | `/api/position-size?symbol=...&portfolio_size=100000&risk_pct=1.5` | 14 ATR, 2x ATR stop loss, target 1 & 2, cap guard (0 shares if price > max cap) |
| Suite 10 | Static Asset & PWA Serving | `/`, `/static/app.js`, `/static/manifest.json`, `/static/sw.js` | HTTP 200, valid HTML/JS/JSON, PWA headers, dual-runtime mirror parity |

## Test Architecture
- Test Runner: `python tests/test_e2e_suites.py`
- Framework: Python built-in `unittest` + `starlette.testclient.TestClient` / `requests` for zero external testing dependencies.
- Directory layout: `tests/test_e2e_suites.py`
- Pass/Fail Semantics: 100% test pass rate required (all 10 suites, 0 failures, 0 errors).
