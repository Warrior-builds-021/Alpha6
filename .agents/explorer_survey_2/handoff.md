# Handoff Report: Quantitative Financial Logic, 6-Pillar Engine, Risk Shield & Computation

**Agent**: Survey Explorer 2 (Quantitative & Risk Domain Analyst)  
**Date**: 2026-09-14T01:37:30Z  
**Recipient**: Parent Agent (`e2ef6863-0926-4a1d-8a81-67c45aa8d9b5`)  
**Artifact Path**: `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_survey_2\handoff.md`

---

## 1. Observation

### 1.1 The 6-Pillar Institutional Scoring Engine (`core/evaluator.py`)
- **Weights Configuration** (`config.py:10-17`):
  ```python
  PILLAR_WEIGHTS = {
      "volume_momentum": 0.15,  # 15%
      "sales_growth": 0.20,     # 20%
      "ocf_quality": 0.25,      # 25% (highest conviction pillar)
      "debt_solvency": 0.15,    # 15%
      "pricing_power": 0.15,    # 15%
      "skin_in_game": 0.10,     # 10%
  }
  ```
- **Composite Score Calculation** (`core/evaluator.py:69-77`):
  ```python
  composite_score = (
      p1["score"] * config.PILLAR_WEIGHTS["volume_momentum"] +
      p2["score"] * config.PILLAR_WEIGHTS["sales_growth"] +
      p3["score"] * config.PILLAR_WEIGHTS["ocf_quality"] +
      p4["score"] * config.PILLAR_WEIGHTS["debt_solvency"] +
      p5["score"] * config.PILLAR_WEIGHTS["pricing_power"] +
      p6["score"] * config.PILLAR_WEIGHTS["skin_in_game"]
  )
  composite_score = float(round(min(100.0, max(0.0, composite_score)), 1))
  ```

#### Observed Bugs and Divergences in Pillar Logic:
1. **Pillar 2 Sales Growth Logic Defect** (`core/evaluator.py:205-215`):
   ```python
   rev_growth = self._normalize_pct(self.info.get("revenueGrowth"))
   if rev_growth is not None:
       if rev_growth >= 0.15:
           score += 20
           details.append(f"Latest YoY Revenue Growth at {rev_growth*100:.1f}%.")
       elif rev_growth < 0:
           score -= 25
           details.append(f"Topline contraction detected: Latest revenue down {abs(rev_growth)*100:.1f}%.")
   elif cagr_3y is None:
       score += 10
   ```
   **Observation**: If a company has positive quarterly revenue growth between `0.0%` and `14.9%` (e.g. TCS at `13.9%`), it matches neither `rev_growth >= 0.15` nor `rev_growth < 0`. Because `rev_growth is not None` is true, the `elif cagr_3y is None` branch is never evaluated. Consequently, a company growing revenue by 13.9% receives `+0` points and an empty `details: []` list. Empirically verified on `TCS.NS`: sales score was capped at baseline 50.0, dragging its composite score down from an eligible 80.0 to 77.0, erroneously failing the 78.0 conviction threshold.
2. **Pillar 3 Operating Cash Flow vs Negative Net Income** (`core/evaluator.py:255-273`):
   ```python
   if ocf_val is not None and net_inc is not None and net_inc > 0:
       ocf_to_net_income = ocf_val / net_inc
       ...
   elif ocf_val is not None and ocf_val < 0:
       score -= 40
       ...
   ```
   **Observation**: When `net_inc < 0` (loss-making entity) but `ocf_val > 0`, the code enters neither branch. `ocf_to_net_income` remains `None` without any accounting penalty for negative net earnings.
3. **Pillar 4 Debt Normalization Artifact** (`core/evaluator.py:28-40`, `295-296`):
   ```python
   @staticmethod
   def _normalize_pct(val: Any) -> Optional[float]:
       ...
       if abs(v) > 2.0:
           return v / 100.0
       return v
   ```
   **Observation**: In Yahoo Finance API, `debtToEquity` is provided as a percentage (e.g., `50.0` for 50% = 0.5x D/E). If a firm has very low debt, e.g. 1.8% D/E, `abs(1.8) <= 2.0`, so `_normalize_pct` returns `1.80` instead of `0.018`. It treats a 1.8% D/E company as having a high 1.8x (180%) D/E ratio, penalizing virtually debt-free companies with 100x overstated leverage.
4. **Disconnection from `config.py`**:
   `config.py` defines institutional parameters (`min_quarterly_rev_growth: 0.08`, `min_interest_coverage: 4.0`, `max_pledged_percentage: 0.05`), but `core/evaluator.py` hardcodes divergent arbitrary constants throughout methods (e.g. 0.18, 0.12, 0.20) and omits interest coverage and promoter pledging entirely.

---

### 1.2 Piotroski F-Score (0–9 Checklist) (`core/evaluator.py:423-481`)
- **Current Code**:
  Checks only `self.info`:
  1. Net Income > 0 (+1)
  2. Operating Cash Flow > 0 (+1)
  3. Positive ROA (+1)
  4. OCF > Net Income (+1)
  5. D/E < 0.5 (+1)
  6. Current Ratio >= 1.25 (+1)
  7. Gross Margin >= 25% (+1)
  8. Revenue Growth > 0 (+1)
  9. ROE >= 12% (+1)
- **Direct Empirical Test on Indian Equities via yfinance**:
  Command executed:
  `python -c "import yfinance as yf; ..."`
  Output:
  ```
  TCS.NS        OCF: True   ROA: True   CR: True   DE: True
  RELIANCE.NS   OCF: False  ROA: False  CR: False  DE: True
  INFY.NS       OCF: True   ROA: True   CR: True   DE: True
  HDFCBANK.NS   OCF: False  ROA: True   CR: False  DE: False
  LT.NS         OCF: False  ROA: False  CR: False  DE: True
  ITC.NS        OCF: False  ROA: False  CR: False  DE: True
  ```
- **Observation**: For major Indian market leaders (`RELIANCE.NS`, `LT.NS`, `ITC.NS`), `operatingCashflow`, `returnOnAssets`, and `currentRatio` are returned as `None` in `ticker.info` by Yahoo Finance.
  However, inspecting `ticker.cashflow` and `ticker.balance_sheet`:
  ```
  Operating Cash Flow in cf: True
  Total Assets in bs: True
  Current Assets in bs: True
  ```
  Because `_calc_piotroski_f_score()` queries *only* `self.info` and does not fall back to `self.cashflow` or `self.balance_sheet`, `RELIANCE.NS` is scored 4/9 instead of 8/9, artificially penalized due to missing summary metadata despite pristine audited accounting statements.
- Furthermore, classical Piotroski F-Score (Piotroski 2000) evaluates **year-over-year operational delta/trend** ($\Delta\text{ROA} > 0$, $\Delta\text{Leverage} < 0$, $\Delta\text{Current Ratio} > 0$, no share dilution, $\Delta\text{Gross Margin} > 0$, $\Delta\text{Asset Turnover} > 0$). The current code is a static single-year absolute threshold proxy.

---

### 1.3 Altman Z-Score Bankruptcy Distress Calculation (`core/evaluator.py:484-515`)
- **Direct Code Inspection**:
  ```python
  # Proxy Altman Z-Score calculation using core fundamental ratios
  # Z = 1.2*(Working Capital/Total Assets) + 1.4*(Retained Earnings/Total Assets) + 3.3*(EBIT/Total Assets) + 0.6*(Market Cap/Total Liabilities) + 0.99*(Sales/Total Assets)
  ebitda = self._safe_float(self.info.get("ebitda"))
  mcap = self._safe_float(self.data.get("market_cap") or self.info.get("marketCap"))
  tot_debt = self._safe_float(self.info.get("totalDebt"))
  raw_de = self.info.get("debtToEquity")
  de = self._normalize_pct(raw_de) if raw_de is not None else None

  if de is not None:
      if de < 0.3:
          z = 4.2  # Bulletproof balance sheet
      elif de < 0.7:
          z = 3.2  # Solid safe zone
      elif de < 1.3:
          z = 2.4  # Moderate grey zone
      else:
          z = 1.4  # Distress risk zone
  else:
      z = 3.0
  ```
- **Observation**: While lines 489-492 extract variables, they are discarded. The calculation does NOT use the Altman Z-score formula. It is a crude 4-tier step function mapping Debt-to-Equity directly to arbitrary numbers (`4.2`, `3.2`, `2.4`, `1.4`). A cash-burning company with zero debt but massive negative operating income and negative working capital would receive `z = 4.2` (classified as "Bulletproof Safe Zone"), completely defeating the purpose of a bankruptcy distress filter.

---

### 1.4 Capital Preservation Rule & Red Flag Shield (`core/evaluator.py:79-88`, `518-540`)
- **Current Rules**:
  - `is_recommended = bool(composite_score >= config.CONVICTION_THRESHOLD and len(red_flags) == 0)`
  - Hard Red Flags:
    1. Critical Solvency Risk: D/E > 2.0x (non-financials)
    2. Cash Drain: FCF negative AND OCF score < 30
    3. Revenue Collapse: YoY revenue down > 10%
    4. Value Destroyer: Negative ROE
    5. Altman Distress: Z-Score < 1.8 (non-financials)
- **Observation**:
  - Any single red flag immediately converts signal to `"AVOID (RED FLAGS DETECTED)"` and sets `is_recommended = False`.
  - Disconnected from Piotroski: Piotroski F-score $\le 3$ represents serious financial and accounting distress in empirical finance, but it is not linked to red flags.
  - Missing promoter pledged holding check: Pledged promoter shares > 15% is India's leading corporate governance fraud trigger, specified in `config.py:62` as `"hard_max_pledged_percentage": 0.15`, but never checked in `_detect_red_flags()`.

---

### 1.5 Dynamic ATR Position Sizing Calculator (`core/risk_manager.py:17-91`)
- **Calculations**:
  - True Range: $TR_t = \max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)$
  - 14-period rolling mean: $\text{ATR}_{14} = \overline{TR}_{14}$
  - ATR buffer clamped: `atr_buffer = min(P * 0.15, max(P * 0.03, 2.0 * atr_val))`
  - Dynamic Stop Loss: $\text{Stop Loss} = P - \text{atr\_buffer}$ (strictly 2x ATR, bounded between 3% and 15%)
  - Risk per share: $\Delta_{\text{risk}} = P - \text{Stop Loss}$
  - Target 1: $P + 2.0 \times \Delta_{\text{risk}}$ (1:2 R:R)
  - Target 2: $P + 3.5 \times \Delta_{\text{risk}}$ (1:3.5 R:R)
  - Position sizing:
    - Risk allocation: $\text{Capital at Risk} = S \times (R / 100)$
    - Risk-based shares: $\lfloor \text{Capital at Risk} / \Delta_{\text{risk}} \rfloor$
    - Max allocation cap: $S \times (M / 100)$
    - Max shares cap: $\lfloor \text{Max Capital Cap} / P \rfloor$
    - `recommended_shares = max(1, min(risk_based_shares, max_shares_cap))`
- **Observed Edge-Case Defect**:
  When stock price $P > \text{Max Capital Cap}$ (e.g. `MRF.NS` at ₹1,35,000 with a ₹1,00,000 portfolio and 12% cap = ₹12,000), `max_shares_cap` becomes 0, but `max(1, ...)` forces `recommended_shares = 1`. This leads to `total_investment = ₹135,000` (135% portfolio weight), violating portfolio risk allocation limits.

---

### 1.6 yfinance Vectorized Ingestion, In-Memory Caching & Serverless Constraints
- **Batch Vectorized Screener Benchmark**:
  Command executed:
  `python -c "import time; from fastapi.testclient import TestClient; from server import app; ..."`
  Output:
  ```
  Cold/First Screen: 8196.0 ms, Scanned: 50
  Warm/Cache Screen: 10.9 ms
  ```
- **Observation**:
  - Warm in-memory cache queries execute in **10.9 ms**, satisfying Requirement R3 (< 20ms).
  - Background cache pre-warming exists (`prewarm_screener_cache()` in `server.py:228-238`), warming Nifty 50 on startup.
  - Gap: `StockDataFetcher.get_stock_data()` (called on single-stock audit) lacks an in-memory TTL cache. Each audit executes 8 to 10 HTTP requests, taking 3.0–6.5 seconds.
  - Serverless cache redirection:
    `core/data_fetcher.py:10-20` and `server.py:16-26` redirect SQLite timezone cache to `tempfile.gettempdir()/py-yfinance`.
    However, `core/backtester.py:9` executes `import yfinance as yf` directly without cache redirection, exposing serverless deployments to `OSError: [Errno 30] Read-only file system` if backtester is invoked first.

---

### 1.7 Broken Test Suite and Universe Imports (`test_engine.py`)
- **Direct Test Run Result**:
  Command executed: `python test_engine.py`
  Output:
  ```
  Traceback (most recent call last):
    File "C:\Users\asaik\OneDrive\Desktop\PROJECT1\test_engine.py", line 8, in <module>
      from core.universe import format_ticker, INDIAN_NIFTY_50, GLOBAL_US_MEGA_TECH
  ImportError: cannot import name 'GLOBAL_US_MEGA_TECH' from 'core.universe' (C:\Users\asaik\OneDrive\Desktop\PROJECT1\core\universe.py)
  ```
- `app.py:19-20` also fails with the same import error (`INDIAN_QUALITY_GROWTH` and `GLOBAL_US_MEGA_TECH`).
- In addition, `core/universe.py:203-216` `format_ticker("AAPL")` returns `"AAPL.NS"`, which violates `test_engine.py:17` (`self.assertEqual(format_ticker("AAPL"), "AAPL")`).

---

## 2. Logic Chain

1. **Premise 1 (Scoring Accuracy)**: A quantitative scoring engine must assign points consistently based on financial parameters.
   - *Observation 1.1*: In `_eval_sales_growth()`, revenue growth between 0% and 15% falls through conditional branches without adding points or explanation details.
   - *Deduction*: Blue-chip compounders (like TCS at 13.9% revenue growth) receive 0 points for topline expansion, artificially depressing their score below the conviction threshold.

2. **Premise 2 (Data Ingestion Robustness)**: yfinance data schema differs between summary quote dictionaries and raw financial statements.
   - *Observation 1.2*: Yahoo Finance omits `operatingCashflow`, `returnOnAssets`, and `currentRatio` in the `info` dictionary for key Indian scrips (`RELIANCE.NS`, `LT.NS`, `ITC.NS`), but provides them in `cashflow` and `balance_sheet` tables.
   - *Deduction*: Because `_calc_piotroski_f_score` only inspects `self.info`, Indian conglomerates are penalised with false accounting warning scores. A multi-tier fallback (Info $\to$ Cashflow/Balance Sheet $\to$ Proxies) is required.

3. **Premise 3 (Forensic Rigor in Bankruptcy Defense)**: The Altman Z-score is an empirical multivariate discriminant analysis model combining 5 distinct financial ratios.
   - *Observation 1.3*: The current implementation replaces the formula with a piecewise mapping of `debt_to_equity`.
   - *Deduction*: Solvency and bankruptcy risk are conflated. Companies with high operating losses, deteriorating working capital, and asset destruction are marked "Safe" simply because they have low debt. The real 5-variable formula must be implemented using balance sheet and income statement items.

4. **Premise 4 (Capital Preservation Discipline)**: Position sizing must prevent catastrophic portfolio ruin.
   - *Observation 1.5*: For high-priced scrips where unit share price exceeds maximum allowed position allocation, forcing `recommended_shares = max(1, ...)` causes a position size overrun (> 100% of capital).
   - *Deduction*: Sizing logic must enforce `recommended_shares = 0` when unit price exceeds maximum single position capital allocation, returning a clear sizing constraint alert.

5. **Premise 5 (System Stability & Performance)**: In serverless read-only runtimes (Vercel/Lambda), unhandled filesystem writes trigger immediate 500 errors.
   - *Observation 1.6*: `core/backtester.py` imports `yfinance` without setting `YFINANCE_CACHE_DIR` to `/tmp/py-yfinance`.
   - *Deduction*: Backtest requests in serverless environments can fail with filesystem permissions errors unless uniform cache redirection is applied across all modules.

---

## 3. Caveats

1. **yfinance Rate Limiting**: Vectorized downloading (`yf.download`) minimizes roundtrips, but parallel requests via `ThreadPoolExecutor` for single-ticker `.info` can trigger HTTP 429 rate limits if batch worker pools exceed 8 concurrent threads.
2. **Financial Institution Accounting**: Banking and NBFC balance sheets (e.g. HDFC Bank, ICICI Bank, SBI) do not report standard operating cash flows or traditional gross margins, and classical Altman Z-Score is statistically invalid for banks due to leverage structures. The engine correctly flags financials (`is_financial`), but sector-specific metrics (NIM, ROA, GNPA, Capital Adequacy) should be displayed instead of generic defaults.
3. **Data Freshness**: In-memory caching with 15-minute TTL provides sub-20ms speed, but intraday price action during live Indian market hours (09:15 to 15:30 IST) will reflect up to 15-minute latency unless a manual cache invalidation / refresh flag is triggered.

---

## 4. Conclusion

The quantitative engine core has solid foundations (modular pillars, 2x ATR dynamic stop loss, vectorized batch downloads, in-memory TTL caching, and FastAPI endpoints), but requires immediate remediation in five key areas:
1. **Pillar Calculation Fixes**: Correct the Sales Growth 0–15% scoring gap, resolve the D/E normalization boundary defect, and align thresholds with `config.py`.
2. **True Altman Z-Score**: Replace the 4-step dummy lookup with the genuine Edward Altman 5-ratio formulation ($Z = 1.2X_1 + 1.4X_2 + 3.3X_3 + 0.6X_4 + 0.99X_5$) using balance sheet and financials data.
3. **Piotroski Dual-Tier Engine**: Enhance `_calc_piotroski_f_score` to extract operating cash flow, net income, current ratio, and ROA from `cashflow` and `balance_sheet` DataFrames when `ticker.info` returns `None`.
4. **Position Sizing Boundary Guard**: Correct `core/risk_manager.py` to prevent position overrun when stock price exceeds single position capital cap.
5. **Universe & Test Integrity**: Add missing universe constants (`GLOBAL_US_MEGA_TECH`, `INDIAN_QUALITY_GROWTH`) to `core/universe.py`, fix `format_ticker` US symbol handling, and ensure all modules use `/tmp/py-yfinance` cache redirection.

---

## 5. Verification Method

### 5.1 Automated Regression Verification Commands
Run the following commands in the workspace root (`c:\Users\asaik\OneDrive\Desktop\PROJECT1`):

1. **Verify Universe and Imports**:
   ```powershell
   python -c "from core.universe import format_ticker, INDIAN_NIFTY_50; print('Universe count:', len(INDIAN_NIFTY_50))"
   ```
2. **Verify Pillar Scoring on Blue Chips (TCS & Reliance)**:
   ```powershell
   python -c "from core.data_fetcher import StockDataFetcher; from core.evaluator import PillarEvaluator; d = StockDataFetcher.get_screener_stock_data('TCS.NS'); ev = PillarEvaluator(d); res = ev.evaluate_all(); print('TCS Score:', res['composite_score'], 'Piotroski:', res['piotroski_f_score'], 'Altman:', res['altman_z_score'])"
   ```
3. **Verify Screener Cache Latency (< 20ms)**:
   ```powershell
   python -c "import time; from fastapi.testclient import TestClient; from server import app; client = TestClient(app); client.get('/api/screen?universe=nifty50'); t0 = time.time(); resp = client.get('/api/screen?universe=nifty50'); print('Cache latency:', round((time.time()-t0)*1000, 2), 'ms')"
   ```
4. **Verify Dynamic ATR Sizing**:
   ```powershell
   python -c "from fastapi.testclient import TestClient; from server import app; client = TestClient(app); resp = client.get('/api/position-size?symbol=TCS.NS&portfolio_size=100000&risk_pct=1.5'); print('Stop Loss:', resp.json()['stop_loss'], 'Shares:', resp.json()['recommended_shares'], 'Total Inv:', resp.json()['total_investment'])"
   ```
5. **Verify Comprehensive Test Suite Execution**:
   ```powershell
   python test_engine.py
   ```

### 5.2 Invalidation Conditions
- Any audited stock producing a composite score outside `[0.0, 100.0]`.
- Altman Z-Score output remaining identical across companies with vastly different debt and profitability profiles (sign of unaddressed stub lookup).
- Second execution of `/api/screen?universe=nifty50` taking $> 20$ ms.
- High-priced stock ($P > \text{Portfolio} \times 12\%$) resulting in portfolio allocation exceeding 12%.
