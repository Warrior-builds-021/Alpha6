# M1 Fix Explorer 2 Handoff Report: RiskManager Penny Stock & Zero Price Edge Cases

**Agent**: Explorer M1 Fix 2  
**Date**: 2026-09-14T02:06:30+05:30  
**Target File**: `core/risk_manager.py`  
**Associated Test Files**: `tests/test_challenger_m1.py`, `test_engine.py`, `tests/test_e2e_suites.py`  
**Parent Conversation ID**: `e2ef6863-0926-4a1d-8a81-67c45aa8d9b5`  
**Working Directory**: `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_m1_fix_2`  
**Status**: COMPLETE (Read-Only Investigation & Remediation Strategy Formulated)

---

## 1. Observation

Direct investigation of `core/risk_manager.py` and adversarial stress tests in `tests/test_challenger_m1.py` revealed two critical algorithmic defects in `RiskManager.calculate_trade_plan()`:

### 1.1 Defect 1: Penny Stock Stop Loss Floor Inversion (`core/risk_manager.py:48-54`)
In `core/risk_manager.py`, line 48–54 states:
```python
48:            atr_buffer = min(stock_price * 0.15, max(stock_price * 0.03, 2.0 * atr_val))
49:            stop_loss = round(max(0.1, stock_price - atr_buffer), 2)
50:            risk_per_share = max(0.01, stock_price - stop_loss)
51:            
52:            # Asymmetric Risk-Reward: Target 1 (2x Risk), Target 2 (3.5x Risk)
53:            target_1 = round(stock_price + (2.0 * risk_per_share), 2)
54:            target_2 = round(stock_price + (3.5 * risk_per_share), 2)
```

**Verbatim Reproduction Command**:
```powershell
python -c "import numpy as np, pandas as pd; from core.risk_manager import RiskManager; dates = pd.date_range(end=pd.Timestamp.now(), periods=50); hist = pd.DataFrame({'High': np.full(50, 0.06), 'Low': np.full(50, 0.04), 'Close': np.full(50, 0.05)}, index=dates); plan = RiskManager.calculate_trade_plan(0.05, hist, 100000.0); print('stop_loss:', plan['stop_loss'], 'stop_loss_pct:', plan['stop_loss_pct'], 'target_1:', plan['target_1'], 'max_risk_capital:', plan['max_risk_capital'])"
```
**Verbatim Output**:
```
stop_loss: 0.1 stop_loss_pct: 100.0 target_1: 0.07 max_risk_capital: -7500.0
```

**Direct Findings**:
1. When `stock_price < 0.10` (e.g. ₹0.05), `max(0.1, stock_price - atr_buffer)` forces `stop_loss` to ₹0.10.
2. For an entry at ₹0.05, `stop_loss` becomes ₹0.10 (+100.0% above entry price!).
3. Target 1 is calculated as ₹0.07, placing it **below** the stop loss (`target_1 < stop_loss`).
4. `max_risk_capital` evaluates to `-₹7,500.00`, a negative risk capital figure that completely breaks portfolio money management.
5. In the fallback branch (`clean_hist.empty or len(clean_hist) < 14`), line 31 calculates `stop_loss = round(stock_price * 0.92, 2)`. For `stock_price = 0.05`, `0.05 * 0.92 = 0.046`. Python's `round(0.046, 2)` rounds up to `0.05`, producing `stop_loss == stock_price` (0.0% stop loss) and `target_1 == target_2 == 0.06`.

### 1.2 Defect 2: Zero Stock Price Division by Zero (`core/risk_manager.py:29, 88-92`)
In `core/risk_manager.py`, line 29 lumps `stock_price <= 0` into the fallback calculation branch:
```python
29:        if clean_hist.empty or len(clean_hist) < 14 or stock_price <= 0:
30:            # Fallback static percentage
31:            stop_loss = round(stock_price * 0.92, 2)  # 8% stop loss
```
And lines 88, 90, 92 divide by `stock_price`:
```python
88:            "stop_loss_pct": round(((stop_loss - stock_price) / stock_price) * 100, 2),
89:            "target_1": target_1,
90:            "target_1_upside_pct": round(((target_1 - stock_price) / stock_price) * 100, 2),
91:            "target_2": target_2,
92:            "target_2_upside_pct": round(((target_2 - stock_price) / stock_price) * 100, 2),
```

**Verbatim Reproduction Command**:
```powershell
python -c "import pandas as pd; from core.risk_manager import RiskManager; RiskManager.calculate_trade_plan(0.0, pd.DataFrame())"
```
**Verbatim Crash Output**:
```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "C:\Users\asaik\OneDrive\Desktop\PROJECT1\core\risk_manager.py", line 88, in calculate_trade_plan
    "stop_loss_pct": round(((stop_loss - stock_price) / stock_price) * 100, 2),
                            ~~~~~~~~~~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~
ZeroDivisionError: division by zero
```

**Direct Findings**:
1. When `stock_price == 0.0`, the function does not exit early; instead it falls through all position sizing logic down to percentage calculation where it divides `(stop_loss - 0.0) / 0.0`, throwing an unhandled `ZeroDivisionError`.
2. When `stock_price < 0` (e.g. -5.0), the function returns negative prices and inverted stop losses without validation.

---

## 2. Logic Chain

```
[Observation 1.1]: In core/risk_manager.py:49, stop_loss is floored with fixed constant 0.1:
                   stop_loss = round(max(0.1, stock_price - atr_buffer), 2)
        ↓
Whenever stock_price < 0.10 (penny equities, sub-dime securities):
stock_price - atr_buffer < 0.10, triggering the floor.
        ↓
stop_loss evaluates to 0.10, which strictly exceeds stock_price (0.10 > 0.05).
        ↓
risk_per_share becomes max(0.01, 0.05 - 0.10) = 0.01.
target_1 becomes 0.05 + 2 * 0.01 = 0.07.
        ↓
Trade plan geometry is inverted:
Stop Loss (0.10) > Target 1 (0.07) > Entry Price (0.05).
max_risk_capital = 150000 * (0.05 - 0.10) = -7500.0 (Negative risk allocation).
        ↓
Quantization Trap (Observation 1.1.5): Standard round(..., 2) quantizes in 0.01 increments.
For a ₹0.05 stock, 0.01 is 20% of the price; for ₹0.01 stock, 0.01 is 100% of the price.
In fallback branch, 0.05 * 0.92 = 0.046 rounds to 0.05 (0% stop loss).
        ↓
Conclusion 1: Stop loss floor MUST be relative to stock_price (e.g. stock_price * 0.50),
and precision MUST dynamically support 4 decimal places when stock_price < 1.0.

-------------------------------------------------------------------------------------

[Observation 1.2]: In core/risk_manager.py:29, stock_price <= 0 is treated as a fallback
                   condition rather than an invalid input:
                   if clean_hist.empty or len(clean_hist) < 14 or stock_price <= 0:
        ↓
Execution proceeds through fallback calculation with stock_price = 0.0.
        ↓
At line 88: "stop_loss_pct": round(((stop_loss - stock_price) / stock_price) * 100, 2)
The denominator stock_price is 0.0.
        ↓
Unhandled ZeroDivisionError crashes execution, violating acceptance criteria that all
endpoints return valid JSON with zero unhandled 500 exceptions.
        ↓
Conclusion 2: stock_price <= 0 MUST be guarded at method entry, immediately returning
a structured zeroed trade plan with sizing_alert describing the invalid price.
```

---

## 3. Caveats

1. **Read-Only Constraint**: Explorer 2 has strictly performed read-only analysis and mathematical verification. No modifications were made to `core/risk_manager.py`.
2. **Frontend UI Display Formatting**: In `static/app.js:634` and `app.py:627`, values are formatted via `toFixed(2)` and `:.2f`. For penny stocks under ₹1.00, while the backend plan accurately computes with 4 decimal places (e.g. ₹0.0425), standard currency formatters may render two decimals (`₹0.04`). The underlying API payload remains high-precision and mathematically sound.
3. **Portfolio Size Boundary**: When `total_portfolio_size <= 0`, lines 57–78 already handle zero portfolio size gracefully (`if total_portfolio_size > 0 else 0.0`).

---

## 4. Conclusion & Concrete Remediation Strategy

### 4.1 Remediation Architecture
`RiskManager.calculate_trade_plan()` requires three targeted enhancements:

1. **Entry Guard for Non-Positive Price (`stock_price <= 0`)**:
   Immediately return a structured, zeroed trade plan with:
   - `recommended_shares`: 0
   - `stop_loss`: 0.0, `stop_loss_pct`: 0.0
   - `target_1`: 0.0, `target_1_upside_pct`: 0.0
   - `target_2`: 0.0, `target_2_upside_pct`: 0.0
   - `total_investment`: 0.0, `portfolio_weight_pct`: 0.0, `max_risk_capital`: 0.0
   - `risk_reward_ratio`: `"N/A"`
   - `sizing_alert`: `"Invalid Price Guard: Unit share price ({stock_price}) must be positive (> 0) to calculate trade plan."`

2. **Dynamic Precision & Relative Stop-Loss Flooring**:
   - Dynamic precision: `prec = 4 if stock_price < 1.0 else 2`
   - Minimum risk per share: `min_risk = 10 ** (-prec)` (0.01 for $\ge 1.0$, 0.0001 for $< 1.0$)
   - Relative stop loss floor in dynamic ATR:
     `stop_loss = round(max(stock_price * 0.50, stock_price - atr_buffer), prec)`
   - Relative stop loss floor in fallback:
     `stop_loss = round(stock_price * 0.92, prec)`

3. **Strict Monotonicity Invariants**:
   Under all market conditions, enforce:
   - `stop_loss < stock_price`: `if stop_loss >= stock_price: stop_loss = round(stock_price * 0.92, prec)`
   - `target_1 > stock_price`: `if target_1 <= stock_price: target_1 = round(stock_price + 2.0 * min_risk, prec)`
   - `target_2 > target_1`: `if target_2 <= target_1: target_2 = round(target_1 + min_risk, prec)`

---

### 4.2 Proposed Code Replacement for `core/risk_manager.py`

Replace lines 27–55 and lines 84–103 of `core/risk_manager.py`:

```python
<<<<
        clean_hist = history.dropna(subset=['High', 'Low', 'Close']) if not history.empty else pd.DataFrame()
        
        if clean_hist.empty or len(clean_hist) < 14 or stock_price <= 0:
            # Fallback static percentage
            stop_loss = round(stock_price * 0.92, 2)  # 8% stop loss
            target_1 = round(stock_price * 1.16, 2)   # 1:2 R:R (16%)
            target_2 = round(stock_price * 1.25, 2)   # 1:3+ R:R (25%)
            risk_per_share = max(0.01, stock_price - stop_loss)
            atr_val = stock_price * 0.04
        else:
            # Calculate Average True Range (14-period ATR)
            high_low = clean_hist['High'] - clean_hist['Low']
            high_close = (clean_hist['High'] - clean_hist['Close'].shift()).abs()
            low_close = (clean_hist['Low'] - clean_hist['Close'].shift()).abs()
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1).dropna()
            
            rolling_atr = true_range.rolling(14).mean().dropna()
            atr_val = float(rolling_atr.iloc[-1]) if not rolling_atr.empty and not np.isnan(rolling_atr.iloc[-1]) else stock_price * 0.04
            
            # Dynamic Stop Loss: 2.0x ATR below current price (bounded to sensible minimum 5-10% buffer)
            atr_buffer = min(stock_price * 0.15, max(stock_price * 0.03, 2.0 * atr_val))
            stop_loss = round(max(0.1, stock_price - atr_buffer), 2)
            risk_per_share = max(0.01, stock_price - stop_loss)
            
            # Asymmetric Risk-Reward: Target 1 (2x Risk), Target 2 (3.5x Risk)
            target_1 = round(stock_price + (2.0 * risk_per_share), 2)
            target_2 = round(stock_price + (3.5 * risk_per_share), 2)
====
        # Guard against zero or negative stock price
        if stock_price <= 0:
            return {
                "current_price": stock_price,
                "atr_14": 0.0,
                "stop_loss": 0.0,
                "stop_loss_pct": 0.0,
                "target_1": 0.0,
                "target_1_upside_pct": 0.0,
                "target_2": 0.0,
                "target_2_upside_pct": 0.0,
                "risk_reward_ratio": "N/A",
                "recommended_shares": 0,
                "total_investment": 0.0,
                "portfolio_weight_pct": 0.0,
                "max_risk_capital": 0.0,
                "potential_gain_t1": 0.0,
                "potential_gain_t2": 0.0,
                "sizing_alert": (
                    f"Invalid Price Guard: Unit share price ({stock_price}) must be positive (> 0) "
                    f"to calculate trade plan."
                ),
                "capital_preservation_rule": "Strict 2x ATR Trailing Stop Loss. Never risk more than 1.5% of total portfolio on any single trade."
            }

        clean_hist = history.dropna(subset=['High', 'Low', 'Close']) if not history.empty else pd.DataFrame()
        prec = 4 if stock_price < 1.0 else 2
        min_risk = 10 ** (-prec)

        if clean_hist.empty or len(clean_hist) < 14:
            # Fallback static percentage
            stop_loss = round(stock_price * 0.92, prec)  # 8% stop loss
            if stop_loss >= stock_price:
                stop_loss = round(stock_price * 0.90, prec)
            target_1 = round(stock_price * 1.16, prec)   # 1:2 R:R (16%)
            target_2 = round(stock_price * 1.25, prec)   # 1:3+ R:R (25%)
            if target_1 <= stock_price:
                target_1 = round(stock_price * 1.10, prec)
            if target_2 <= target_1:
                target_2 = round(target_1 * 1.05, prec)
            risk_per_share = max(min_risk, stock_price - stop_loss)
            atr_val = round(stock_price * 0.04, prec)
        else:
            # Calculate Average True Range (14-period ATR)
            high_low = clean_hist['High'] - clean_hist['Low']
            high_close = (clean_hist['High'] - clean_hist['Close'].shift()).abs()
            low_close = (clean_hist['Low'] - clean_hist['Close'].shift()).abs()
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1).dropna()
            
            rolling_atr = true_range.rolling(14).mean().dropna()
            atr_val = float(rolling_atr.iloc[-1]) if not rolling_atr.empty and not np.isnan(rolling_atr.iloc[-1]) else stock_price * 0.04
            
            # Dynamic Stop Loss: 2.0x ATR below current price (bounded to sensible minimum 3-15% buffer)
            atr_buffer = min(stock_price * 0.15, max(stock_price * 0.03, 2.0 * atr_val))
            # Relative floor ensures stop loss is strictly below entry price and positive
            stop_loss = round(max(stock_price * 0.50, stock_price - atr_buffer), prec)
            if stop_loss >= stock_price:
                stop_loss = round(stock_price * 0.92, prec)
            risk_per_share = max(min_risk, stock_price - stop_loss)
            
            # Asymmetric Risk-Reward: Target 1 (2x Risk), Target 2 (3.5x Risk)
            target_1 = round(stock_price + (2.0 * risk_per_share), prec)
            target_2 = round(stock_price + (3.5 * risk_per_share), prec)
            if target_1 <= stock_price:
                target_1 = round(stock_price + (2.0 * min_risk), prec)
            if target_2 <= target_1:
                target_2 = round(target_1 + min_risk, prec)
>>>>
```

And in the return dictionary (line 86):
```python
<<<<
            "atr_14": round(atr_val, 2),
====
            "atr_14": round(atr_val, prec),
>>>>
```

---

## 5. Verification Method

### 5.1 Test Updates for `tests/test_challenger_m1.py`
Replace lines 236–278 in `tests/test_challenger_m1.py` with positive verification methods:

```python
    def test_penny_stock_stop_loss_flooring_validity(self):
        """
        Positive verification: For penny stocks trading below ₹0.10 (e.g. ₹0.05),
        stop loss is strictly below entry price, targets are above entry price,
        and max risk capital is non-negative.
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
        self.assertLess(plan["stop_loss"], plan["current_price"])
        self.assertGreater(plan["stop_loss"], 0.0)
        self.assertLess(plan["stop_loss_pct"], 0.0)
        self.assertGreater(plan["target_1"], plan["current_price"])
        self.assertGreater(plan["target_2"], plan["target_1"])
        self.assertGreaterEqual(plan["max_risk_capital"], 0.0)
        self.assertGreater(plan["recommended_shares"], 0)

    def test_zero_or_negative_price_graceful_handling(self):
        """
        Positive verification: calculate_trade_plan() gracefully handles stock_price <= 0.0
        by returning a zeroed plan with an alert rather than crashing with ZeroDivisionError.
        """
        for bad_price in [0.0, -5.0]:
            plan = RiskManager.calculate_trade_plan(
                stock_price=bad_price,
                history=pd.DataFrame(),
                total_portfolio_size=100000.0
            )
            self.assertEqual(plan["recommended_shares"], 0)
            self.assertEqual(plan["stop_loss"], 0.0)
            self.assertEqual(plan["stop_loss_pct"], 0.0)
            self.assertEqual(plan["total_investment"], 0.0)
            self.assertEqual(plan["portfolio_weight_pct"], 0.0)
            self.assertEqual(plan["max_risk_capital"], 0.0)
            self.assertIsNotNone(plan["sizing_alert"])
            self.assertIn("Invalid Price Guard", plan["sizing_alert"])
```

### 5.2 Verification Commands
After implementing the changes, independently verify with:
```powershell
python -m unittest tests/test_challenger_m1.py -v
python test_engine.py -v
python -m unittest tests/test_e2e_suites.py -v
```

### 5.3 Invalidation Conditions
The fix is invalid if:
1. Any stock price $P > 0$ yields $\text{stop\_loss} \ge P$.
2. Calling `calculate_trade_plan(0.0, ...)` or `calculate_trade_plan(-1.0, ...)` raises `ZeroDivisionError` or any uncaught exception.
3. Any trade plan yields $\text{max\_risk\_capital} < 0.0$.
4. Target 1 is less than or equal to entry price, or Target 2 is less than or equal to Target 1.
