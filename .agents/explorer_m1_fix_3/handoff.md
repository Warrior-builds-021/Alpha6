# M1 Fix Explorer 3 Investigation & Handoff Report
**Ticker Formatting, Index Caret Preservation, US Hyphenated Symbols, and Test Harness Unification**

- **Agent**: M1 Fix Explorer 3
- **Role**: Teamwork Explorer (Read-Only Investigation & Synthesis)
- **Target Files**: `core/universe.py`, `tests/test_challenger_m1.py`, `tests/test_challenger_m1_2.py`, `test_engine.py`
- **Working Directory**: `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_m1_fix_3`
- **Parent Conversation ID**: `e2ef6863-0926-4a1d-8a81-67c45aa8d9b5`
- **Date**: 2026-09-14T02:07:00+05:30

---

## Executive Summary
In Milestone 1 Gate Iteration 1, Challenger 1 and Challenger 2 identified critical edge cases in ticker normalization and test suite structure:
1. **Index Caret (`^`) Distortion**: `core/universe.py:format_ticker()` appends `.NS` to market index symbols beginning with `^` (e.g., `^NSEI` $\to$ `^NSEI.NS`), causing Yahoo Finance HTTP 404 Not Found errors on index candlestick and price queries.
2. **Hyphenated US Dual-Class Tickers**: `core/universe.py:US_TICKER_SYMBOLS` defined Berkshire Hathaway using dot notation (`BRK.A`, `BRK.B`), causing standard Yahoo Finance hyphenated symbols (`BRK-A`, `BRK-B`) to fall through to Indian NSE normalization (`BRK-A.NS`), returning HTTP 404.
3. **Challenger Reproduction Test Inversion**: `tests/test_challenger_m1.py` contains empirical defect reproduction tests asserting the *presence* of bugs (e.g., asserting $Z = 7.22$ for insolvent firms, stop loss > entry price for penny stocks, and `ZeroDivisionError`). Once Worker M1 implements the financial math and risk manager fixes, these tests will fail unless inverted into permanent regression assertions.
4. **Test Harness Fragmentation**: Unit tests (`test_engine.py` at repository root) and stress/e2e tests (`tests/`) are split, preventing unified boundary verification.

This report establishes the complete evidence chain and specifies exact code diffs and test unification plans for implementation.

---

## 1. Observation

### 1.1 Index Caret (`^`) Normalization & Yahoo Finance 404
- **Code Inspection**: `core/universe.py:240-258`:
  ```python
  240: def format_ticker(symbol: str, market: str = "AUTO") -> str:
  241:     """
  242:     Normalizes tickers for Indian (NSE: .NS, BSE: .BO) and US markets.
  243:     e.g. 'RELIANCE' -> 'RELIANCE.NS', '500325' -> '500325.BO', 'AAPL' -> 'AAPL'.
  244:     """
  245:     clean_sym = symbol.strip().upper()
  246:     if clean_sym.endswith(".NS") or clean_sym.endswith(".BO"):
  247:         return clean_sym
  248:     
  249:     # BSE Numeric scrip code check
  250:     if clean_sym.isdigit():
  251:         return f"{clean_sym}.BO"
  252: 
  253:     # Known US tickers or explicit US market
  254:     if market == "US" or clean_sym in US_TICKER_SYMBOLS:
  255:         return clean_sym
  256:         
  257:     return f"{clean_sym}.NS"
  ```
- **Empirical Execution**:
  Calling `format_ticker("^NSEI")` yields `"^NSEI.NS"`. Calling `format_ticker("^BSESN")` yields `"^BSESN.NS"`.
- **API Failure Empirical Verification**:
  Testing `server.py` candlestick endpoint with `^NSEI`:
  ```powershell
  python -c "from starlette.testclient import TestClient; import server; client = TestClient(server.app); print(client.get('/api/candles/%5ENSEI?period=1mo').status_code)"
  ```
  **Verbatim Output**:
  ```
  HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: ^NSEI.NS"}}}
  $^NSEI.NS: No data found, symbol may be delisted
  404
  ```
- **Direct Yahoo Finance Inspection**:
  ```powershell
  python -c "import yfinance as yf; print('^NSEI:', len(yf.Ticker('^NSEI').history(period='1d'))); print('^NSEI.NS:', len(yf.Ticker('^NSEI.NS').history(period='1d')))"
  ```
  **Verbatim Output**:
  ```
  HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: ^NSEI.NS"}}}
  $^NSEI.NS: No data found, symbol may be delisted
  ^NSEI: 1
  ^NSEI.NS: 0
  ```
  Caret symbols (`^NSEI`, `^BSESN`, `^GSPC`, `^DJI`) are global index symbols in Yahoo Finance and never accept exchange suffixes.

### 1.2 Hyphenated US Dual-Class Tickers (`BRK-A`, `BRK-B`)
- **Code Inspection**: `core/universe.py:220-226`:
  ```python
  220: US_TICKER_SYMBOLS = {
  221:     s["symbol"] for s in GLOBAL_US_MEGA_TECH
  222: } | {
  223:     "SPY", "QQQ", "DIA", "IWM", "AMD", "INTC", "NFLX", "QCOM", "TXN", "ADBE",
  224:     "CRM", "ORCL", "CSCO", "IBM", "UBER", "PYPL", "ABNB", "COIN", "PLTR", "SNOW",
  225:     "BRK.A", "BRK.B", "JNJ", "JPM", "PG", "XOM", "CVX", "HD", "BAC", "WMT", "KO", "PEP"
  226: }
  ```
- **Empirical Execution**:
  Calling `format_ticker("BRK-A")` yields `"BRK-A.NS"` because `"BRK-A"` is not in `US_TICKER_SYMBOLS` (only `"BRK.A"` is present).
- **API Failure Empirical Verification**:
  ```powershell
  python -c "from starlette.testclient import TestClient; import server; client = TestClient(server.app); print(client.get('/api/candles/BRK-A?period=1mo').status_code)"
  ```
  **Verbatim Output**:
  ```
  HTTP Error 404: {"quoteSummary":{"result":null,"error":{"code":"Not Found","description":"Quote not found for symbol: BRK-A.NS"}}}
  $BRK-A.NS: No data found, symbol may be delisted
  404
  ```
- **Direct Yahoo Finance Inspection**:
  ```powershell
  python -c "import yfinance as yf; print('BRK-A:', len(yf.Ticker('BRK-A').history(period='1d'))); print('BRK.A:', len(yf.Ticker('BRK.A').history(period='1d')))"
  ```
  **Verbatim Output**:
  ```
  $BRK.A: No data found, symbol may be delisted
  BRK-A: 1
  BRK.A: 0
  ```
  Yahoo Finance convention strictly mandates hyphenation (`BRK-A`, `BRK-B`) for Berkshire Hathaway shares, rejecting dot notation (`BRK.A`).

### 1.3 Challenger 1 Test Suite Defect Reproduction Inversion Risk
- **Code Inspection**: `tests/test_challenger_m1.py`:
  1. Lines 72-97:
     ```python
     def test_reproduce_negative_equity_altman_distortion(self):
         ...
         self.assertEqual(z, 7.22, "Bug signature: negative D/E yields distorted Z=7.22")
         self.assertEqual(status, "Safe Zone (Low Bankruptcy Risk)", "Bug signature: classified as Safe Zone")
     ```
  2. Lines 236-265:
     ```python
     def test_reproduce_penny_stock_stop_loss_inversion(self):
         ...
         self.assertEqual(plan["stop_loss"], 0.1)
         self.assertGreater(plan["stop_loss"], plan["current_price"])
         self.assertEqual(plan["stop_loss_pct"], 100.0)
         self.assertLess(plan["target_1"], plan["stop_loss"])
         self.assertLess(plan["max_risk_capital"], 0.0)
     ```
  3. Lines 266-278:
     ```python
     def test_reproduce_zero_price_division_by_zero_crash(self):
         with self.assertRaises(ZeroDivisionError):
             RiskManager.calculate_trade_plan(stock_price=0.0, ...)
     ```
- **Observation**: These three tests assert the *buggy state*. When Explorers 1 and 2 remediate the evaluator and risk manager, running `tests/test_challenger_m1.py` will fail because the bugs will no longer reproduce. They must be inverted to assert the *correct behavior*.

### 1.4 Challenger 2 Investigation Test Lack of Assertions
- **Code Inspection**: `tests/test_challenger_m1_2.py:129-144`:
  ```python
  def test_special_symbols_investigation(self):
      index_nsei = format_ticker("^NSEI")
      index_bsesn = format_ticker("^BSESN")
      brk_a = format_ticker("BRK-A")
      print(f"DEBUG: format_ticker('^NSEI') = {index_nsei}")
      print(f"DEBUG: format_ticker('^BSESN') = {index_bsesn}")
      print(f"DEBUG: format_ticker('BRK-A') = {brk_a}")
  ```
- **Observation**: This test only prints debug strings without assertions (`self.assertEqual`). It does not fail when `format_ticker("^NSEI")` returns `"^NSEI.NS"`.

---

## 2. Logic Chain

```
[Observation 1.1]: format_ticker("^NSEI") appends .NS -> "^NSEI.NS". Yahoo Finance returns HTTP 404 for ^NSEI.NS, but returns valid data for ^NSEI.
        ↓
[Logic Step 1]: In Yahoo Finance, index tickers are globally prefixed with '^'. They do not represent stocks listed on NSE/BSE and must never receive .NS or .BO suffixes.
        ↓
[Remediation 1]: Add a caret check at the top of format_ticker:
                 if clean_sym.startswith("^"):
                     if clean_sym.endswith(".NS") or clean_sym.endswith(".BO"):
                         return clean_sym[:-3]
                     return clean_sym
                 This preserves ^NSEI, ^BSESN, ^GSPC, ^DJI, etc., and strips accidental suffixes.

[Observation 1.2]: format_ticker("BRK-A") appends .NS -> "BRK-A.NS" because "BRK-A" is missing from US_TICKER_SYMBOLS. Yahoo Finance returns HTTP 404 for BRK-A.NS and BRK.A, but succeeds for BRK-A.
        ↓
[Logic Step 2]: Yahoo Finance standard notation for dual-class US equities uses hyphens (BRK-A, BRK-B, BF-A, BF-B).
        ↓
[Remediation 2]: Add "BRK-A", "BRK-B", "BF-A", "BF-B" to US_TICKER_SYMBOLS, and normalize dot notation in format_ticker (e.g., BRK.A -> BRK-A).

[Observation 1.3]: tests/test_challenger_m1.py asserts bug signatures (Z=7.22 for insolvent, stop_loss=0.1 > price for penny stock, ZeroDivisionError).
        ↓
[Logic Step 3]: When bug fixes are applied by Worker M1, defect reproduction tests will fail because the bugs have been eliminated.
        ↓
[Remediation 3]: Invert reproduction assertions into permanent regression tests:
                 - test_negative_equity_altman_distress_classification: assert Z < 1.81 and 'Distress Zone'
                 - test_penny_stock_stop_loss_non_inversion: assert stop_loss < price and targets > price
                 - test_zero_or_negative_price_graceful_handling: assert no ZeroDivisionError and 0 shares returned

[Observation 1.4]: tests/test_challenger_m1_2.py contains an investigation method without assertions.
        ↓
[Logic Step 4]: Without assertions, regressions in index caret handling or hyphenated US tickers will not fail CI.
        ↓
[Remediation 4]: Replace test_special_symbols_investigation with test_special_symbols_and_indices_regression with strict assertEqual checks.

[Observation & Synthesis]: test_engine.py at root tests core engine functions but omits index/hyphen tickers and boundary edge cases.
        ↓
[Logic Step 5]: Incorporating boundary assertions into test_engine.py guarantees that local unit tests immediately verify all M1 fixes in < 0.1s.
```

---

## 3. Exact Remediation Strategy & Code Diffs

### 3.1 Proposed Changes to `core/universe.py`

#### A) Include Hyphenated US Tickers in `US_TICKER_SYMBOLS` (Lines 220–227)
```diff
--- a/core/universe.py
+++ b/core/universe.py
@@ -222,6 +222,7 @@ US_TICKER_SYMBOLS = {
 } | {
     "SPY", "QQQ", "DIA", "IWM", "AMD", "INTC", "NFLX", "QCOM", "TXN", "ADBE",
     "CRM", "ORCL", "CSCO", "IBM", "UBER", "PYPL", "ABNB", "COIN", "PLTR", "SNOW",
-    "BRK.A", "BRK.B", "JNJ", "JPM", "PG", "XOM", "CVX", "HD", "BAC", "WMT", "KO", "PEP"
+    "BRK.A", "BRK.B", "BRK-A", "BRK-B", "BF-A", "BF-B",
+    "JNJ", "JPM", "PG", "XOM", "CVX", "HD", "BAC", "WMT", "KO", "PEP"
 }
```

#### B) Preserve Index Caret (`^`) and Normalize US Tickers in `format_ticker` (Lines 240–258)
```diff
--- a/core/universe.py
+++ b/core/universe.py
@@ -240,16 +240,29 @@ def format_ticker(symbol: str, market: str = "AUTO") -> str:
     """
-    Normalizes tickers for Indian (NSE: .NS, BSE: .BO) and US markets.
-    e.g. 'RELIANCE' -> 'RELIANCE.NS', '500325' -> '500325.BO', 'AAPL' -> 'AAPL'.
+    Normalizes tickers for Indian (NSE: .NS, BSE: .BO), US markets, and global/domestic indices.
+    e.g. 'RELIANCE' -> 'RELIANCE.NS', '500325' -> '500325.BO', 'AAPL' -> 'AAPL', '^NSEI' -> '^NSEI'.
     """
     clean_sym = symbol.strip().upper()
+    
+    # 1. Market index preservation (e.g. ^NSEI, ^BSESN, ^GSPC, ^DJI)
+    # Yahoo Finance indices start with '^' and reject exchange suffixes (.NS/.BO).
+    if clean_sym.startswith("^"):
+        if clean_sym.endswith(".NS") or clean_sym.endswith(".BO"):
+            return clean_sym[:-3]
+        return clean_sym
+
+    # 2. Already formatted Indian exchange tickers
     if clean_sym.endswith(".NS") or clean_sym.endswith(".BO"):
         return clean_sym
     
-    # BSE Numeric scrip code check
+    # 3. BSE Numeric scrip code check
     if clean_sym.isdigit():
         return f"{clean_sym}.BO"
 
-    # Known US tickers or explicit US market
+    # 4. Normalize US dual-class shares with dot notation to hyphen (e.g. BRK.A -> BRK-A)
+    if clean_sym in {"BRK.A", "BRK.B"}:
+        clean_sym = clean_sym.replace(".", "-")
+
+    # 5. Known US tickers or explicit US market
     if market == "US" or clean_sym in US_TICKER_SYMBOLS:
         return clean_sym
         
     return f"{clean_sym}.NS"
```

---

### 3.2 Proposed Changes to `tests/test_challenger_m1.py`

Transform the 3 defect reproduction tests into permanent regression verification tests:

```diff
--- a/tests/test_challenger_m1.py
+++ b/tests/test_challenger_m1.py
@@ -72,27 +72,31 @@ class TestChallengerAltmanZScore(unittest.TestCase):
-    def test_reproduce_negative_equity_altman_distortion(self):
+    def test_negative_equity_altman_distress_classification(self):
         """
-        EMPERICAL DEFECT REPRODUCTION:
-        When a firm has negative equity (insolvent) and reports negative debtToEquity,
-        evaluator._calc_altman_z_score calculates x4 = 15.0 (maximum possible)
-        due to max(0.05, de) treating negative D/E as lower than 0.05.
-        This inflates Z by +9.0 points, classifying an insolvent company as 'Safe Zone'.
+        REGRESSION TEST: Negative Equity & Balance Sheet Insolvency.
+        When a firm has negative equity (insolvent) and reports negative debtToEquity,
+        Altman Z-Score must penalize X4 (not inflate it) and classify the firm into
+        Distress Zone (Z < 1.81). Pillar 4 must flag balance sheet insolvency.
         """
         stock_insolvent = {
             "symbol": "BANKRUPT.NS",
             "info": {
                 "debtToEquity": -5.0,  # Negative equity -> negative D/E
                 "currentRatio": 0.5,
                 "returnOnEquity": -0.8,
                 "returnOnAssets": -0.4,
                 "operatingMargins": -0.5
             }
         }
         ev = PillarEvaluator(stock_insolvent)
         z, status = ev._calc_altman_z_score()
-        # Empirically verify the bug exists:
-        # Expected correct behavior: z < 1.81 (Distress Zone)
-        # Actual buggy behavior: z = 7.22 (Safe Zone)
-        self.assertEqual(z, 7.22, "Bug signature: negative D/E yields distorted Z=7.22")
-        self.assertEqual(status, "Safe Zone (Low Bankruptcy Risk)", "Bug signature: classified as Safe Zone")
+        # Permanent regression assertion:
+        self.assertLess(z, 1.81, f"Insolvent firm must yield Z < 1.81 (Distress Zone), got {z}")
+        self.assertIn("Distress Zone", status)
+        
+        # Verify evaluator red flags
+        res = ev.evaluate_all()
+        self.assertFalse(res["is_recommended"])
+        self.assertIn("AVOID", res["signal"])
+        self.assertTrue(any("distress" in f.lower() or "insolven" in f.lower() or "equity" in f.lower() for f in res["red_flags"]))
@@ -236,32 +240,31 @@ class TestChallengerATRSizingLimits(unittest.TestCase):
-    def test_reproduce_penny_stock_stop_loss_inversion(self):
+    def test_penny_stock_stop_loss_non_inversion(self):
         """
-        EMPERICAL DEFECT REPRODUCTION:
-        In core/risk_manager.py:49, stop_loss = round(max(0.1, stock_price - atr_buffer), 2).
-        For stocks with price < 0.10, the stop loss is floored at 0.10, which is GREATER
-        than the entry price. This creates an inverted trade plan (stop loss > price, target1 < stop loss).
+        REGRESSION TEST: Sub-₹0.10 Penny Stock Stop Loss Bounds.
+        For penny stocks trading below ₹0.10, stop loss must be strictly BELOW
+        entry price, target 1 strictly above entry, and max risk capital non-negative.
         """
         dates = pd.date_range(end=pd.Timestamp.now(), periods=50)
         hist_penny = pd.DataFrame({
             "Open": np.full(50, 0.05),
             "High": np.full(50, 0.06),
             "Low": np.full(50, 0.04),
             "Close": np.full(50, 0.05),
             "Volume": np.full(50, 100000)
         }, index=dates)
 
         plan = RiskManager.calculate_trade_plan(
             stock_price=0.05,
             history=hist_penny,
             total_portfolio_size=100000.0,
             risk_per_trade_pct=1.5,
             max_position_size_pct=12.0
         )
-        # Verify the defect is present:
-        self.assertEqual(plan["stop_loss"], 0.1)
-        self.assertGreater(plan["stop_loss"], plan["current_price"])
-        self.assertEqual(plan["stop_loss_pct"], 100.0)
-        self.assertLess(plan["target_1"], plan["stop_loss"])
-        self.assertLess(plan["max_risk_capital"], 0.0)
+        # Permanent regression assertion:
+        self.assertLess(plan["stop_loss"], plan["current_price"], "Stop loss must be strictly below current entry price")
+        self.assertGreater(plan["target_1"], plan["current_price"], "Target 1 must be strictly above current entry price")
+        self.assertGreater(plan["target_2"], plan["target_1"], "Target 2 must be strictly above Target 1")
+        self.assertGreaterEqual(plan["max_risk_capital"], 0.0, "Risk capital must never be negative")
@@ -266,14 +269,21 @@ class TestChallengerATRSizingLimits(unittest.TestCase):
-    def test_reproduce_zero_price_division_by_zero_crash(self):
+    def test_zero_or_negative_price_graceful_handling(self):
         """
-        EMPERICAL DEFECT REPRODUCTION:
-        RiskManager.calculate_trade_plan() crashes with ZeroDivisionError when stock_price == 0.0
-        at line 88 ("stop_loss_pct": round(((stop_loss - stock_price) / stock_price) * 100, 2)).
+        REGRESSION TEST: Zero or Negative Stock Price Handling.
+        Must return a safe zeroed plan without raising ZeroDivisionError.
         """
-        with self.assertRaises(ZeroDivisionError):
-            RiskManager.calculate_trade_plan(
-                stock_price=0.0,
-                history=pd.DataFrame(),
-                total_portfolio_size=100000.0
-            )
+        plan_zero = RiskManager.calculate_trade_plan(
+            stock_price=0.0,
+            history=pd.DataFrame(),
+            total_portfolio_size=100000.0
+        )
+        self.assertEqual(plan_zero["recommended_shares"], 0)
+        self.assertEqual(plan_zero["total_investment"], 0.0)
+        self.assertIsNotNone(plan_zero["sizing_alert"])
+        
+        plan_neg = RiskManager.calculate_trade_plan(
+            stock_price=-5.0,
+            history=pd.DataFrame(),
+            total_portfolio_size=100000.0
+        )
+        self.assertEqual(plan_neg["recommended_shares"], 0)
+        self.assertIsNotNone(plan_neg["sizing_alert"])
```

---

### 3.3 Proposed Changes to `tests/test_challenger_m1_2.py`

Convert `test_special_symbols_investigation` into an assertion-backed regression test:

```diff
--- a/tests/test_challenger_m1_2.py
+++ b/tests/test_challenger_m1_2.py
@@ -129,15 +129,19 @@ class TestTickerFormattingStress(unittest.TestCase):
-    def test_special_symbols_investigation(self):
+    def test_special_symbols_and_indices_regression(self):
         """
-        Adversarial edge cases:
+        REGRESSION TEST:
         1. Index symbols starting with '^' (e.g. ^NSEI, ^BSESN, ^GSPC).
            In Yahoo Finance, indices begin with '^' and DO NOT use .NS or .BO.
         2. Dual-share US class tickers like BRK-A, BRK-B vs BRK.A, BRK.B.
+        3. Spurious suffixes accidentally appended to indices must be cleanly stripped.
         """
-        # Let's inspect the behavior of format_ticker on these edge cases
-        index_nsei = format_ticker("^NSEI")
-        index_bsesn = format_ticker("^BSESN")
-        brk_a = format_ticker("BRK-A")
-        
-        print(f"DEBUG: format_ticker('^NSEI') = {index_nsei}")
-        print(f"DEBUG: format_ticker('^BSESN') = {index_bsesn}")
-        print(f"DEBUG: format_ticker('BRK-A') = {brk_a}")
+        self.assertEqual(format_ticker("^NSEI"), "^NSEI")
+        self.assertEqual(format_ticker("^BSESN"), "^BSESN")
+        self.assertEqual(format_ticker("^GSPC"), "^GSPC")
+        self.assertEqual(format_ticker("^DJI"), "^DJI")
+        self.assertEqual(format_ticker("^IXIC"), "^IXIC")
+        self.assertEqual(format_ticker("  ^nsei  "), "^NSEI")
+        self.assertEqual(format_ticker("^NSEI.NS"), "^NSEI")
+        self.assertEqual(format_ticker("^BSESN.BO"), "^BSESN")
+        
+        self.assertEqual(format_ticker("BRK-A"), "BRK-A")
+        self.assertEqual(format_ticker("BRK-B"), "BRK-B")
+        self.assertEqual(format_ticker("BRK.A"), "BRK-A")
+        self.assertEqual(format_ticker("BRK.B"), "BRK-B")
```

---

### 3.4 Proposed Changes to `test_engine.py`

Update `test_engine.py` to directly verify index carets, hyphenated US symbols, and boundary fixes in the standard unit test run:

```diff
--- a/test_engine.py
+++ b/test_engine.py
@@ -18,3 +18,12 @@ class TestPillarEngine(unittest.TestCase):
         self.assertEqual(format_ticker("NVDA"), "NVDA")
         self.assertEqual(format_ticker("500325"), "500325.BO")
+        # Index carets and US dual-class tickers
+        self.assertEqual(format_ticker("^NSEI"), "^NSEI")
+        self.assertEqual(format_ticker("^BSESN"), "^BSESN")
+        self.assertEqual(format_ticker("^GSPC"), "^GSPC")
+        self.assertEqual(format_ticker("^NSEI.NS"), "^NSEI")
+        self.assertEqual(format_ticker("BRK-A"), "BRK-A")
+        self.assertEqual(format_ticker("BRK-B"), "BRK-B")
+        self.assertEqual(format_ticker("BRK.A"), "BRK-A")
@@ -226,0 +235,53 @@ class TestPillarEngine(unittest.TestCase):
+    def test_altman_z_score_negative_equity_distress(self):
+        """Insolvent company with negative equity must be in Distress Zone, not Safe Zone."""
+        mock_insolvent = {
+            "symbol": "BANKRUPT.NS",
+            "info": {
+                "debtToEquity": -5.0,
+                "currentRatio": 0.5,
+                "returnOnEquity": -0.8,
+                "returnOnAssets": -0.4,
+                "operatingMargins": -0.5
+            }
+        }
+        ev = PillarEvaluator(mock_insolvent)
+        z, status = ev._calc_altman_z_score()
+        self.assertLess(z, 1.81)
+        self.assertIn("Distress Zone", status)
+        
+        res = ev.evaluate_all()
+        self.assertFalse(res["is_recommended"])
+        self.assertIn("AVOID", res["signal"])
+
+    def test_risk_manager_penny_stock_bounds(self):
+        """Sub-₹0.10 penny stocks must have stop loss strictly below entry price."""
+        dates = pd.date_range(end=pd.Timestamp.now(), periods=50)
+        hist = pd.DataFrame({
+            "Open": np.full(50, 0.05),
+            "High": np.full(50, 0.06),
+            "Low": np.full(50, 0.04),
+            "Close": np.full(50, 0.05),
+            "Volume": np.full(50, 100000)
+        }, index=dates)
+        plan = RiskManager.calculate_trade_plan(
+            stock_price=0.05,
+            history=hist,
+            total_portfolio_size=100000.0,
+            risk_per_trade_pct=1.5,
+            max_position_size_pct=12.0
+        )
+        self.assertLess(plan["stop_loss"], plan["current_price"])
+        self.assertGreater(plan["target_1"], plan["current_price"])
+        self.assertGreaterEqual(plan["max_risk_capital"], 0.0)
+
+    def test_risk_manager_zero_price_guard(self):
+        """Zero price input must not raise ZeroDivisionError."""
+        plan = RiskManager.calculate_trade_plan(
+            stock_price=0.0,
+            history=pd.DataFrame(),
+            total_portfolio_size=100000.0
+        )
+        self.assertEqual(plan["recommended_shares"], 0)
+        self.assertEqual(plan["total_investment"], 0.0)
+        self.assertIsNotNone(plan["sizing_alert"])
```

---

## 4. Caveats

1. **Read-Only Mandate Strictly Respected**: In compliance with the Teamwork Explorer contract, zero edits were made directly to `core/universe.py`, `core/evaluator.py`, `core/risk_manager.py`, `test_engine.py`, or any files in `tests/`. All changes are formulated as exact diffs and proposals for Worker M1.
2. **Yahoo Finance Index Availability**: Caret index symbols (`^NSEI`, `^BSESN`, `^GSPC`, `^DJI`) are available for historical OHLCV data through `yf.Ticker(norm_sym).history()`. However, some index tickers may not return fundamental balance sheet ratios or valuation multiples (`info` or `quarterly_financials`) because indices are baskets, not corporate entities. This is normal and expected behaviour for index securities.
3. **NSE Ticker Collisions**: NSE ticker symbols containing hyphens (`BAJAJ-AUTO`, `MCDOWELL-N`, `NAM-INDIA`) remain correctly classified as NSE equities (`.NS`) because they are not in `US_TICKER_SYMBOLS` and `market` is not set to `"US"`.

---

## 5. Conclusion

- **Defect 1 Root Cause**: `format_ticker` lacked a guard for caret-prefixed symbols (`clean_sym.startswith("^")`), erroneously suffixing `.NS` onto index symbols (`^NSEI.NS`), triggering Yahoo Finance 404s.
- **Defect 2 Root Cause**: `US_TICKER_SYMBOLS` omitted `"BRK-A"` and `"BRK-B"`, causing standard Yahoo Finance dual-class share queries to be treated as NSE equities (`BRK-A.NS`), triggering Yahoo Finance 404s.
- **Defect 3 Root Cause**: Challenger 1 test suite asserted defect signatures that will invert upon remediation.
- **Action Plan for Worker M1**:
  1. Apply diff to `core/universe.py` (add caret check, add `"BRK-A"`, `"BRK-B"` to `US_TICKER_SYMBOLS`, add dot-to-hyphen normalization).
  2. Apply diff to `tests/test_challenger_m1.py` (invert defect reproduction assertions to regression assertions).
  3. Apply diff to `tests/test_challenger_m1_2.py` (convert investigation prints into regression assertions).
  4. Apply diff to `test_engine.py` (add index, hyphen, and boundary test cases).

---

## 6. Verification Method

To independently verify the defects before fix and the resolutions after fix:

### 6.1 Pre-Fix Defect Verification (Reproduce Now)
```powershell
# Verify ^NSEI returns HTTP 404 on API
python -c "from starlette.testclient import TestClient; import server; client = TestClient(server.app); res = client.get('/api/candles/%5ENSEI?period=1mo'); print('Status:', res.status_code); print('Response:', res.json())"

# Verify BRK-A returns HTTP 404 on API
python -c "from starlette.testclient import TestClient; import server; client = TestClient(server.app); res = client.get('/api/candles/BRK-A?period=1mo'); print('Status:', res.status_code); print('Response:', res.json())"
```
**Expected Pre-Fix Result**: Both return HTTP 404 with message `Quote not found for symbol: ^NSEI.NS` and `Quote not found for symbol: BRK-A.NS`.

### 6.2 Post-Fix Verification (Run After Worker Applies Diffs)

```powershell
# 1. Run Unit Engine Tests (all fast unit tests + boundary checks)
python test_engine.py -v

# 2. Run Challenger 1 Math & Boundary Suite
python -m unittest tests/test_challenger_m1.py -v

# 3. Run Challenger 2 50+ Ticker & Cache Safety Suite
python -m unittest tests/test_challenger_m1_2.py -v

# 4. Run Full 10-Suite Regression Verification Runner
python tests/test_e2e_suites.py

# 5. Verify Index & BRK-A API Endpoints Return 200 OK
python -c "from starlette.testclient import TestClient; import server; client = TestClient(server.app); res_idx = client.get('/api/candles/%5ENSEI?period=1mo'); res_brk = client.get('/api/candles/BRK-A?period=1mo'); print('Index status:', res_idx.status_code); print('BRK status:', res_brk.status_code)"
```
**Expected Post-Fix Result**:
- `test_engine.py`: 13/13 tests pass in < 0.1s.
- `test_challenger_m1.py`: 16/16 tests pass in < 0.2s.
- `test_challenger_m1_2.py`: 5/5 tests pass in < 0.2s.
- `test_e2e_suites.py`: All 10 suites pass with 0 failures, 0 errors.
- Index status: 200 OK, BRK status: 200 OK.

### 6.3 Invalidation Conditions
- Any occurrence of `^NSEI.NS` or `^BSESN.NS` output from `format_ticker`.
- Any occurrence of `BRK-A.NS` output from `format_ticker`.
- Failure of `test_challenger_m1.py` or `test_challenger_m1_2.py`.
- Regression in `tests/test_e2e_suites.py`.
