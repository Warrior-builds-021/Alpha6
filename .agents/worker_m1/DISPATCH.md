# M1 Worker Dispatch: Backend & Quantitative Financial Engine

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Assignment
Implement the core quantitative engine, 6-pillar analysis, authentic Altman Z-score, Piotroski F-score fallback, position sizing bounds, and universe fixes.

### Input Files to Study:
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\ORIGINAL_REQUEST.md`
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\PROJECT.md`
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_survey_1\handoff.md`
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_survey_2\handoff.md`

### Exclusive Write Ownership:
- `core/universe.py`
- `core/evaluator.py`
- `core/risk_manager.py`
- `core/backtester.py`
- `core/data_fetcher.py`
- `test_engine.py`
(Do NOT modify files in `templates/`, `static/`, or `public/` - those are owned by Milestone 3).

### Detailed Tasks:
1. **`core/universe.py`**:
   - Add backward-compatible aliases `GLOBAL_US_MEGA_TECH` and `INDIAN_QUALITY_GROWTH` to prevent import errors in `test_engine.py` and legacy prototypes.
   - Fix `format_ticker`: if a symbol does not contain a dot and is in standard US ticker format (e.g. `AAPL`, `MSFT`, `GOOGL`), do NOT append `.NS`. Keep `.NS` appending specifically for Indian NSE securities or numeric BSE codes.
2. **`core/evaluator.py`**:
   - **Pillar 2 (Sales Growth)**: Fix the 0% to 15% quarterly revenue growth scoring gap so compounders (like TCS at 13.9% growth) receive appropriate points (e.g., +10 to +15 points based on growth) and explanatory details instead of 0 points and empty details.
   - **Pillar 3 (OCF Quality)**: Correctly handle cases where Net Income is negative but OCF is positive (or vice versa), applying appropriate penalization for negative cash earnings.
   - **Pillar 4 (Debt & Solvency)**: Fix `_normalize_pct` for D/E so low debt (e.g. 1.8% D/E) is recognized as 0.018x rather than 1.8x.
   - **Authentic Altman Z-Score**: Replace the 4-tier step lookup with Edward Altman's 5-ratio formula:
     $Z = 1.2 X_1 + 1.4 X_2 + 3.3 X_3 + 0.6 X_4 + 0.99 X_5$
     where:
     - $X_1 = \text{Working Capital} / \text{Total Assets}$
     - $X_2 = \text{Retained Earnings} / \text{Total Assets}$
     - $X_3 = \text{EBIT} / \text{Total Assets}$
     - $X_4 = \text{Market Value of Equity} / \text{Total Liabilities}$
     - $X_5 = \text{Sales} / \text{Total Assets}$
     Extract balance sheet and income statement fields with robust fallback to financial ratios if specific balance sheet items are not reported. Categorize into Safe ($Z > 2.99$), Grey ($1.81 \le Z \le 2.99$), and Distress ($Z < 1.81$).
   - **Piotroski F-Score Fallback**: When `info` omits `operatingCashflow`, `returnOnAssets`, or `currentRatio` (common for Indian conglomerates like Reliance, L&T, ITC), extract them from `self.cashflow` and `self.balance_sheet` DataFrames available via `StockDataFetcher`.
   - **Capital Preservation Rule**: Ensure any stock with Altman distress flag ($Z < 1.8$) or revenue collapse (> 10% YoY contraction) or negative ROE is flagged with red flags and disqualified from recommendation (`is_recommended = False`).
3. **`core/risk_manager.py`**:
   - In `calculate_position_size`: when unit share price exceeds maximum single position capital allocation (`stock_price > max_capital_cap`), set `recommended_shares = 0` (do NOT force `max(1, ...)` which causes portfolio weight overrun) and provide a clear sizing alert explanation.
4. **`core/backtester.py`**:
   - Ensure `/tmp/py-yfinance` cache redirection is configured before importing yfinance to prevent serverless read-only filesystem exceptions.
5. **Verification**:
   - Run `python test_engine.py` and ensure all tests pass.
   - Test single-stock evaluation on `TCS.NS` and `RELIANCE.NS`.
   - Document all test commands and execution results in `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\worker_m1\handoff.md`.

## 2026-09-13T20:08:36Z
You are M1 Worker. Your role is Quantitative Engine & Backend Implementer.
Read your dispatch at `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\worker_m1\DISPATCH.md`.
Read `c:\Users\asaik\OneDrive\Desktop\PROJECT1\ORIGINAL_REQUEST.md`, `PROJECT.md`, and the survey reports at `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_survey_1\handoff.md` and `explorer_survey_2\handoff.md`.
Implement the core quantitative engine improvements:
1. Universe aliases and ticker formatting (`core/universe.py`).
2. Sales growth 0-15% handling, D/E normalization, genuine Edward Altman 5-ratio Z-score, Piotroski statement fallback, red flag triggers (`core/evaluator.py`).
3. Position sizing capital overrun guard (`core/risk_manager.py`).
4. Universal /tmp/py-yfinance cache redirection (`core/backtester.py`).
5. Fix `test_engine.py` and run tests to verify pass.
Write your complete handoff report to `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\worker_m1\handoff.md`.
Notify your parent via send_message when done with your test results and summary.

## 2026-09-13T20:20:11Z
**Context**: M1 Quantitative Engine Implementation Status Check
**Content**: Checking in on your progress with core/universe.py, core/evaluator.py, and test_engine.py. Please report current status and next steps.
**Action**: Reply with brief status update.
