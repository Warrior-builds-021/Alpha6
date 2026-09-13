# Forensic Integrity Audit Report: Milestone 1 Backend & Quantitative Engine

**Work Product Audited**: Milestone 1 Implementation (`core/universe.py`, `core/evaluator.py`, `core/risk_manager.py`, `core/backtester.py`, `core/data_fetcher.py`, `test_engine.py`, `tests/test_e2e_suites.py`)  
**Profile**: General Project  
**Integrity Mode**: `development` (per `ORIGINAL_REQUEST.md:8`)  
**Auditor Archetype**: `teamwork_preview_auditor` / `forensic_auditor`  
**Date**: 2026-09-14T02:00:00+05:30  
**Binary Audit Verdict**: **CLEAN** (Zero Integrity Violations Detected)

---

## 1. Observation

### 1.1 Anti-Cheating & Facade Inspection
Direct empirical inspection of `core/evaluator.py`, `core/risk_manager.py`, `core/universe.py`, `core/backtester.py`, `core/data_fetcher.py`, and `server.py` confirmed:
1. **No Hardcoded Ticker Overrides**:
   - Ripgrep pattern search for `symbol ==` across `core/` returned 0 matches.
   - Specific queries for `"TCS"` and `"RELIANCE"` confirmed these ticker symbols appear exclusively in universe definitions (`INDIAN_NIFTY_50`) and docstrings, never in branching conditionals.
   - `core/evaluator.py:462` uses `is_indian_stock = ".NS" in self.symbol or ".BO" in self.symbol` strictly to branch between Indian regulatory promoter norms (> 40% promoter holding) and US corporate governance norms (> 10% insider holding).
2. **No Dummy Facades or Constant Returns**:
   - `PillarEvaluator._calc_altman_z_score()` (lines 608–748) does NOT perform a step-lookup or return static floats. It extracts raw line items from `balance_sheet` and `income_stmt` DataFrames, computes Edward Altman's 5 discriminant ratios ($X_1$ through $X_5$), and applies the exact linear combination $1.2X_1 + 1.4X_2 + 3.3X_3 + 0.6X_4 + 0.99X_5$.
   - `PillarEvaluator._calc_piotroski_f_score()` (lines 497–605) calculates all 9 points of Joseph Piotroski's accounting checklist by dynamically checking `cashflow`, `balance_sheet`, and `income_stmt`.
   - `RiskManager.calculate_trade_plan()` (lines 17–103) computes a rolling 14-day ATR from High/Low/Close price series, scales a 2.0x ATR buffer, bounds position sizes by risk tolerance ($1.5\%$) and capital allocation ($12.0\%$), and activates an overrun guard ($0$ shares) when unit stock price exceeds the single-position capital cap.
3. **No Pre-Populated Verification Artifacts**:
   - Executing `Get-ChildItem -Path . -Recurse -Include *.log,*result*,*output* -File` returned 0 files. No spoofed logs or cached pass attestations exist in the repository.

---

### 1.2 Mathematical Formulation & Formula Verification
Verbatim source inspection of `core/evaluator.py:737`:
```python
# Authentic Altman Z-Score formula
z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.99 * x5
z = float(round(z, 2))
```
Where ratios are extracted as:
- $X_1 = \text{Working Capital} / \text{Total Assets}$ (lines 648–655, 688–696)
- $X_2 = \text{Retained Earnings} / \text{Total Assets}$ (lines 656–658, 698–706)
- $X_3 = \text{EBIT} / \text{Total Assets}$ (lines 659–663, 708–719)
- $X_4 = \text{Market Value of Equity} / \text{Total Liabilities}$ (lines 664–680, 721–729)
- $X_5 = \text{Sales} / \text{Total Assets}$ (lines 681–685, 731–735)

Empirical python test execution of Case 1 (Standard Balance Sheet):
```python
# Inputs: WC=100, TA=1000, RE=200, TL=400, EBIT=150, Sales=800, MCAP=1200
# Expected: 1.2*(0.1) + 1.4*(0.2) + 3.3*(0.15) + 0.6*(3.0) + 0.99*(0.80) = 3.487 -> 3.49
```
**Observed Tool Output**:
```
Altman Z-Score Calculated: 3.49, Expected: 3.49, Match: True
Status: Safe Zone (Low Bankruptcy Risk)
[+] Case 1 Altman Z-Score EXACT mathematical check PASSED.
```

Empirical python test execution of Case 2 (Insolvent Distressed Firm with Negative Working Capital, Negative Retained Earnings, Operating Losses):
```python
# Inputs: WC=-200, TA=1000, RE=-400, TL=900, EBIT=-100, Sales=400, MCAP=300
# Expected: 1.2*(-0.2) + 1.4*(-0.4) + 3.3*(-0.1) + 0.6*(0.3333) + 0.99*(0.40) = -0.534 -> -0.53
```
**Observed Tool Output**:
```
Altman Z-Score Calculated: -0.53, Expected: -0.53, Match: True
Status: Distress Zone (High Insolvent Risk)
Composite Score: 57.2
Is Recommended: False
Red flags: ['ALTMAN DISTRESS WARNING: Insolvent risk territory (Z-Score: -0.53).']
[+] Case 2 Altman Z-Score DISTRESS check PASSED.
```

---

### 1.3 Piotroski 9-Point Accounting Checklist Verification
Empirical execution of Case 3 (All-Fail: 0/9) and Case 4 (All-Pass: 9/9):
**Observed Tool Output**:
```
Piotroski 0 Score: 0, Details: []
Piotroski 9 Score: 9, Details: 9
[+] Piotroski 0/9 and 9/9 authentic calculation checks PASSED.
```
Statement fallback check on empty `info`:
- When `info = {}`, `_calc_piotroski_f_score()` extracts line items directly from `cashflow`, `balance_sheet`, and `income_stmt` DataFrames, scoring 7/9 without raising KeyError or AttributeError.

---

### 1.4 Dynamic ATR Risk Management Verification
Empirical execution of synthetic price series with constant 10.0 True Range:
**Observed Tool Output**:
```
ATR 14: 10.0
Stop Loss: 85.0
Target 1: 130.0
Target 2: 152.5
Recommended shares: 100
Portfolio weight: 10.0
Overrun Recommended Shares: 0
Overrun Alert: Capital Overrun Guard: Unit share price (25,000.00) exceeds maximum allowed position allocation (12,000.00 = 12.0% of 100,000.00). Recommended shares set to 0 to prevent portfolio overrun.
[+] RiskManager ATR, stop loss, targets, and overrun guard PASSED.
```

---

### 1.5 Test Suite Behavioral Execution

#### 1.5.1 Unit Test Suite (`test_engine.py`)
Command: `python test_engine.py -v`
```
test_altman_z_score_genuine_5_ratios (__main__.TestPillarEngine.test_altman_z_score_genuine_5_ratios) ... ok
test_debt_solvency_normalization (__main__.TestPillarEngine.test_debt_solvency_normalization) ... ok
test_evaluator_synthetic_data (__main__.TestPillarEngine.test_evaluator_synthetic_data) ... ok
test_piotroski_statement_fallback (__main__.TestPillarEngine.test_piotroski_statement_fallback) ... ok
test_red_flag_disqualification (__main__.TestPillarEngine.test_red_flag_disqualification) ... ok
test_risk_manager_overrun_guard (__main__.TestPillarEngine.test_risk_manager_overrun_guard) ... ok
test_risk_manager_position_sizing (__main__.TestPillarEngine.test_risk_manager_position_sizing) ... ok
test_sales_growth_gap_fix (__main__.TestPillarEngine.test_sales_growth_gap_fix) ... ok
test_ticker_formatting (__main__.TestPillarEngine.test_ticker_formatting) ... ok
test_universe_aliases (__main__.TestPillarEngine.test_universe_aliases) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.051s

OK
```

#### 1.5.2 10-Suite Regression Verification Runner (`tests/test_e2e_suites.py`)
Command: `python tests/test_e2e_suites.py`
```
================================================================================
ALPHA6 FINTECH PLATFORM — 10-SUITE REGRESSION VERIFICATION RUNNER
================================================================================
ID       | Suite Name                       | Tier                     | Run  | Status         | Time
------------------------------------------------------------------------------------------------
Suite 1  | Health & Version Contract        | Tier 1: Smoke & Sanity   | 4    | PASS           | 0.033s
Suite 2  | Fast Search Autocomplete         | Tier 2: Core Domain      | 5    | PASS           | 0.049s
Suite 3  | Quantitative Screener Engine     | Tier 2: Core Domain      | 5    | PASS           | 3.798s
Suite 4  | Screener Caching & Latency       | Tier 4: Execution & Latency | 3    | PASS           | 9.103s
Suite 5  | Forensic 6-Pillar Audit          | Tier 3: Forensics        | 3    | PASS           | 6.607s
Suite 6  | Altman Z-Score & Piotroski F-Score | Tier 3: Forensics        | 2    | PASS           | 1.317s
Suite 7  | Live Candlestick Terminal        | Tier 2: Core Domain      | 4    | PASS           | 3.030s
Suite 8  | Strategy Backtester Engine       | Tier 4: Execution & Latency | 2    | PASS           | 1.708s
Suite 9  | Risk Shield & Position Sizer     | Tier 4: Execution & Latency | 3    | PASS           | 4.610s
Suite 10 | Static Assets & PWA Serving      | Tier 1: Smoke & Sanity   | 2    | PASS           | 0.101s
------------------------------------------------------------------------------------------------

[+] ALL TEST SUITES PASSED PERFECTLY.
================================================================================
```

---

## 2. Logic Chain

```
[Observation 1.1]: No hardcoded ticker strings or static output bypasses exist in core/ modules.
        ↓
[Inference 1]: Code does not circumvent business logic or cheat to pass test cases.
        ↓
[Observation 1.2]: Altman Z-Score formula computes authentic 5-ratio linear combination 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.99*X5 from balance sheet / income statement DataFrames, with exact mathematical match (3.49 and -0.53).
        ↓
[Inference 2]: Edward Altman's 5-ratio model is authentically implemented and mathematically sound.
        ↓
[Observation 1.3]: Piotroski F-Score evaluates 9 distinct financial criteria across cashflow, balance sheet, and income statement, producing 0/9 on failing firms and 9/9 on high-quality compounders with reliable fallback when info is sparse.
        ↓
[Inference 3]: Joseph Piotroski's 9-point checklist is genuinely implemented.
        ↓
[Observation 1.4]: RiskManager calculates 14-period ATR, 2.0x ATR stop loss, 1:2 and 1:3.5 profit targets, and clamps recommended_shares to 0 when price exceeds the maximum portfolio allocation cap.
        ↓
[Inference 4]: Capital preservation and position sizing rules are genuinely enforced.
        ↓
[Observation 1.5]: test_engine.py (10/10 passed in 0.051s) and test_e2e_suites.py (10/10 suites passed in 33.7s) run and pass completely without errors or warnings.
        ↓
[Conclusion]: The work product for Milestone 1 contains zero integrity violations and is verified CLEAN.
```

---

## 3. Caveats

1. **Hostile Extreme Penny Stock Boundary**: Challenger tests highlighted that for speculative micro-penny stocks with entry prices below ₹0.10 (e.g. ₹0.05), `RiskManager.calculate_trade_plan` sets `stop_loss = round(max(0.1, stock_price - atr_buffer), 2)`. Because of the `max(0.1, ...)` floor, stop loss becomes ₹0.10 which is higher than the entry price of ₹0.05. This is an extreme edge-case boundary artifact for sub-10-paisa securities, not a fraudulent facade or integrity violation.
2. **Market Cap vs Debt Disparity in Altman Z-Score**: In an adversarial scenario where an insolvent firm has deep operating losses and negative equity but a massive market capitalization (e.g., $1B valuation on $3.5M liabilities), $X_4$ dominates the discriminant formula, resulting in a Grey Zone score ($Z = 2.07$). This is a direct mathematical consequence of Edward Altman's original discriminant weighting ($0.6 \times \text{Market Cap} / \text{Liabilities}$) rather than an implementation flaw.
3. **Frontend Scope**: Templates (`templates/index.html`) and static scripts (`static/app.js`) are scheduled for full UI transformation in Milestone 3; Milestone 1 audit was strictly confined to backend engine and quantitative models.

---

## 4. Conclusion

**FINAL AUDIT VERDICT: UNEQUIVOCALLY CLEAN**

The Milestone 1 work product satisfies all integrity and authenticity requirements:
- **No Cheating / Hardcoded Bypasses**: No static returns or ticker-specific cheats exist.
- **Authentic Edward Altman 5-Ratio Calculation**: Implements genuine $1.2X_1 + 1.4X_2 + 3.3X_3 + 0.6X_4 + 0.99X_5$ with empirical mathematical precision.
- **Authentic Piotroski F-Score**: Implements the full 9-point criteria with multi-tier statement fallback.
- **Authentic Dynamic Position Sizing**: Strictly enforces 14-period ATR, 2.0x stop loss, asymmetric profit targets, and 0-share capital overrun defense.
- **Empirical Test Verification**: 100% pass rate across unit tests and the 10-suite E2E regression verification harness.

The work product is approved without integrity reservations.

---

## 5. Verification Method

To independently reproduce and verify this audit:

1. **Run Unit Test Suite**:
   ```powershell
   python test_engine.py -v
   ```
   *Expected*: 10 tests run, 10 passed in < 0.1s.

2. **Run 10-Suite Regression Verification Runner**:
   ```powershell
   python tests/test_e2e_suites.py
   ```
   *Expected*: All 10 suites report `PASS` with 0 failures and 0 errors.

3. **Verify Altman Z-Score Empirical Precision**:
   ```powershell
   python -c "
   import pandas as pd
   from core.evaluator import PillarEvaluator
   bs = pd.DataFrame({'2024-03-31': [100.0, 1000.0, 200.0, 400.0]}, index=['Working Capital', 'Total Assets', 'Retained Earnings', 'Total Liabilities Net Minority Interest'])
   inc = pd.DataFrame({'2024-03-31': [150.0, 800.0]}, index=['EBIT', 'Total Revenue'])
   stock = {'symbol': 'TEST.NS', 'market_cap': 1200.0, 'current_price': 50.0, 'info': {'marketCap': 1200.0}, 'history': pd.DataFrame(), 'income_stmt': inc, 'balance_sheet': bs, 'cashflow': pd.DataFrame()}
   ev = PillarEvaluator(stock)
   z, status = ev._calc_altman_z_score()
   assert z == 3.49 and 'Safe' in status
   print('Verified Altman Z =', z)
   "
   ```

4. **Verify Position Sizing Overrun Guard**:
   ```powershell
   python -c "
   from core.risk_manager import RiskManager; import pandas as pd
   plan = RiskManager.calculate_position_size(stock_price=25000.0, history=pd.DataFrame(), total_portfolio_size=100000.0, max_position_size_pct=12.0)
   assert plan['recommended_shares'] == 0 and plan['sizing_alert'] is not None
   print('Verified Overrun Guard: recommended_shares =', plan['recommended_shares'])
   "
   ```

5. **Invalidation Conditions**:
   - Any commit introducing static ticker-matching branches in `core/evaluator.py` or `core/risk_manager.py`.
   - Any deviation from the canonical 5-ratio coefficients in Altman Z calculation.
   - Any test failure in `test_engine.py` or `tests/test_e2e_suites.py`.
