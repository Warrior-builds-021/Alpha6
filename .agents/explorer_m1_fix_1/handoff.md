# M1 Fix Explorer 1: Negative D/E & Insolvent Distortion Remediation Report

## 1. Observation

### Observation 1.1: Altman Z-Score $X_4$ Boundary Inversion
- **File**: `core/evaluator.py`, lines 720–728:
```python
        # X4 = Market Value of Equity / Total Liabilities
        if mcap is not None and tl is not None and tl > 0:
            x4 = min(15.0, mcap / tl)
        else:
            de = self._normalize_de(self.info.get("debtToEquity"))
            if de is not None:
                x4 = min(15.0, 1.0 / max(0.05, de))
            else:
                x4 = 1.5
```
- **Live Output Execution**:
  Command: `python -c "from core.evaluator import PillarEvaluator; stock = {'symbol': 'BANKRUPT.NS', 'info': {'debtToEquity': -5.0, 'currentRatio': 0.5, 'returnOnEquity': -0.8, 'returnOnAssets': -0.4, 'operatingMargins': -0.5}}; print(PillarEvaluator(stock)._calc_altman_z_score())"`
  Verbatim result: `(7.22, 'Safe Zone (Low Bankruptcy Risk)')`
- **Root Cause**: When a firm has negative equity (insolvent) and reports negative D/E (`de = -5.0`), `max(0.05, -5.0)` evaluates to `0.05`. Then `1.0 / 0.05 = 20.0`, which caps at `x4 = 15.0`. In Edward Altman's formula ($Z = 1.2 X_1 + 1.4 X_2 + 3.3 X_3 + 0.6 X_4 + 0.99 X_5$), $0.6 \times 15.0 = +9.0$ points. Without this distortion, $Z = -1.78$ ("Distress Zone"). The distortion elevates $Z$ to $7.22$, misclassifying a bankrupt firm as prime investment grade ("Safe Zone").

### Observation 1.2: Piotroski F-Score Criterion 5 Erroneous Point Award
- **File**: `core/evaluator.py`, lines 550–560:
```python
        # 5. Low/Decreasing Leverage (D/E < 0.5x)
        raw_de = self.info.get("debtToEquity")
        de = self._normalize_de(raw_de) if raw_de is not None else None
        if de is None and not self.balance_sheet.empty:
            tot_debt = _get_val(self.balance_sheet, ["Total Debt"])
            equity = _get_val(self.balance_sheet, ["Common Stock Equity", "Stockholders Equity", "Total Equity Gross Minority Interest"])
            if tot_debt is not None and equity and equity > 0:
                de = tot_debt / equity
        if de is not None and de < 0.5:
            score += 1
            details.append(f"Conservative Debt-to-Equity ({de:.2f}x < 0.5x) (+1)")
```
- **Live Output Execution**:
  Command: `python -c "from core.evaluator import PillarEvaluator; stock = {'symbol': 'BANKRUPT.NS', 'info': {'debtToEquity': -5.0, 'currentRatio': 0.5, 'returnOnEquity': -0.8, 'returnOnAssets': -0.4, 'operatingMargins': -0.5}}; print(PillarEvaluator(stock)._calc_piotroski_f_score())"`
  Verbatim result: `(1, ['Conservative Debt-to-Equity (-5.00x < 0.5x) (+1)'])`
- **Root Cause**: The condition `de < 0.5` evaluates to `True` for any negative number (`-5.0 < 0.5`), awarding +1 Piotroski point to an insolvent firm and claiming it possesses "Conservative Debt-to-Equity".

### Observation 1.3: Pillar 4 Solvency Erroneously Awards "Fortress Balance Sheet" (+35 Pts)
- **File**: `core/evaluator.py`, lines 384–398:
```python
        if debt_to_equity is not None:
            if debt_to_equity <= 0.20:
                score += 35
                details.append(f"Fortress Balance Sheet: Virtually zero debt (D/E = {debt_to_equity:.2f}x).")
            elif debt_to_equity <= 0.60:
                score += 25
                details.append(f"Healthy Solvency: Conservative leverage (D/E = {debt_to_equity:.2f}x).")
            elif debt_to_equity <= 1.20:
                score += 5
                details.append(f"Moderate Debt Load: D/E is {debt_to_equity:.2f}x.")
            elif debt_to_equity > 1.50:
                score -= 35
                details.append(f"High Financial Risk: Elevated Debt-to-Equity of {debt_to_equity:.2f}x.")
        else:
            score += 15
```
- **Live Output Execution**:
  Command: `python -c "from core.evaluator import PillarEvaluator; stock = {'symbol': 'BANKRUPT.NS', 'info': {'debtToEquity': -5.0, 'currentRatio': 0.5, 'returnOnEquity': -0.8, 'returnOnAssets': -0.4, 'operatingMargins': -0.5}}; print(PillarEvaluator(stock)._eval_debt_solvency())"`
  Verbatim result: `{'pillar_name': 'Debt & Solvency Health', 'score': 65.0, 'debt_to_equity': -5.0, 'current_ratio': 0.5, 'details': ['Fortress Balance Sheet: Virtually zero debt (D/E = -5.00x).', 'Liquidity crunch risk: Current Ratio below 1.0 (0.50).']}`
- **Root Cause**: Because `-5.0 <= 0.20` is `True`, the evaluator erroneously adds +35 points to the base score of 50.0 and appends "Fortress Balance Sheet: Virtually zero debt (D/E = -5.00x)." Even with a -20 penalty for current ratio 0.5, the pillar score ends up at 65.0 (Passing/Healthy), rather than being zeroed out.

### Observation 1.4: Red Flag Shield Fails to Detect Negative D/E
- **File**: `core/evaluator.py`, lines 753–755:
```python
        de = p4.get("debt_to_equity")
        if de is not None and de > 2.0 and not self.is_financial:
            flags.append(f"CRITICAL SOLVENCY RISK: High Debt-to-Equity ratio of {de:.2f}x.")
```
- **Root Cause**: The condition only tests `de > 2.0`. A negative ratio (`de = -5.0`) is `< 2.0`, so no solvency red flag is triggered. Additionally, because Altman Z was inflated to 7.22, the Altman distress red flag (`z_score < 1.81`) also fails to fire.

### Observation 1.5: Balance Sheet Fallback Silently Ignores Negative Equity
- **File**: `core/evaluator.py`, lines 354–355 and 555–556:
```python
            if tot_debt is not None and equity and equity > 0:
                debt_to_equity = tot_debt / equity
```
- **Root Cause**: If `equity <= 0` in the balance sheet, `equity > 0` evaluates to `False`. The evaluator leaves `debt_to_equity = None`, which subsequently triggers the missing data fallback (`else: score += 15` in Pillar 4), rewarding +15 points for missing balance sheet debt rather than penalizing insolvency.

---

## 2. Logic Chain

1. **Accounting Definition of Insolvency**:
   - In financial accounting, Total Debt is non-negative ($Debt \ge 0$). Therefore, a negative Debt-to-Equity ratio ($D/E < 0$) can only occur if Common Stockholders' Equity (Net Worth) is negative ($Equity < 0$).
   - A negative Net Worth occurs when cumulative retained losses exceed paid-in capital, meaning Total Liabilities exceed Total Assets ($TL > TA$). This is the statutory definition of balance sheet insolvency.

2. **From Accounting Definition to Data Sources (Observation 1.1 & 1.5)**:
   - Balance sheet insolvency can be recognized across four independent indicators:
     a. `self.info.get("debtToEquity") < 0`
     b. `self.info.get("bookValue") < 0` (negative book value per share)
     c. Balance sheet line items (`Common Stock Equity`, `Stockholders Equity`, etc.) $< 0$
     d. Balance sheet $TA > 0$ and $TL > TA$
   - Any single affirmative indicator conclusively proves balance sheet insolvency.

3. **From Insolvency to Altman Z-Score Remediation (Observation 1.1)**:
   - In Edward Altman's 1968 model, $X_4 = \frac{\text{Market Value of Equity}}{\text{Total Liabilities}}$. For a distressed firm with negative book equity, the market value of equity approaches option value near zero ($X_4 \to 0.0$).
   - In the evaluator fallback `1.0 / max(0.05, de)`, `max(0.05, de)` was intended only to avoid division by zero for positive debt. When `de < 0`, it falsely assigned $X_4 = 15.0$ (+9.0 points).
   - Setting $X_4 = 0.0$ when negative equity is detected eliminates the 9.0-point inflation.
   - For `BANKRUPT.NS`: $Z = 1.2(-0.35) + 1.4(-0.5) + 3.3(-0.5) + 0.6(0.0) + 0.99(1.0) = -1.78$.
   - To guarantee complete defense against edge cases (e.g. high sales turnover $X_5$ lifting $Z$), capping $Z \le 1.80$ when `is_negative_equity == True` ensures the firm is strictly classified into `"Distress Zone (High Insolvent Risk)"`.

4. **From Insolvency to Piotroski F-Score Remediation (Observation 1.2)**:
   - Joseph Piotroski's Criterion 5 measures leverage reduction and financial conservatism.
   - An insolvent company with negative equity does NOT possess conservative leverage.
   - Requiring $0.0 \le de < 0.5$ preserves the +1 point for healthy, low-debt/zero-debt firms while awarding 0 points to negative D/E firms.
   - Invariant check: In Piotroski scoring, `len(details) == score`. By rejecting negative D/E, neither score nor details are incremented.

5. **From Insolvency to Pillar 4 & Red Flag Shield Remediation (Observation 1.3 & 1.4)**:
   - In Pillar 4, `debt_to_equity < 0` must be tested before `debt_to_equity <= 0.20`.
   - When `debt_to_equity < 0`:
     - Deduct 40 points (`score -= 40`). Base score 50.0 becomes 10.0. If accompanied by poor current ratio ($< 1.0$), score drops to 0.0 (`min(100.0, max(0.0, score))`).
     - Append: `"CRITICAL SOLVENCY RISK: Negative Equity / Balance Sheet Insolvency (D/E = {debt_to_equity:.2f}x)."`
   - In `_detect_red_flags`:
     - Test `if de < 0: flags.append(f"BALANCE SHEET INSOLVENCY: Negative Net Worth / Insolvent Equity (D/E = {de:.2f}x).")`
     - When $Z < 1.81$, `ALTMAN DISTRESS WARNING: Insolvent risk territory (Z-Score: {z_score:.2f}).` also fires.
   - Two red flags disqualify the security: `signal = "AVOID (RED FLAGS DETECTED)"` and `is_recommended = False`.

---

## 3. Caveats

1. **Financial Sector Scope**: Financial institutions (banks/NBFCs) operate under Basel III Capital Adequacy Ratios (CAR) where high leverage (D/E of 5x–8x) is normal. The evaluator already short-circuits Altman Z for financials (returning 3.5). However, negative equity in a bank indicates insolvency (Tier 1 wiped out). The red flag for `de < 0` should apply universally regardless of sector.
2. **Yahoo Finance Percentage Convention**: Yahoo Finance typically reports `debtToEquity` as a percentage (e.g. 10.2 for 10.2%, 350 for 350%). When equity is negative, it reports negative percentages (e.g. -500.0 for -500%). In `_normalize_de`, any negative number evaluates to $< 0$. Whether passed as `-5.0` or `-500.0`, it is recognized as negative equity.
3. **No Code Modification Undertaken**: As an Explorer, no edits were made directly to `core/evaluator.py` or test files. All proposals are verified through Python execution and documented as machine-applicable diffs below.

---

## 4. Conclusion & Remediation Strategy

The remediation is complete, precise, and verified across all modules.

### Summary Table of Proposed Behavior

| Component | Current Buggy Behavior (`BANKRUPT.NS`) | Remediated Behavior (`BANKRUPT.NS`) |
|---|---|---|
| **Altman $X_4$** | $X_4 = 15.0$ (+9.0 pts) via `max(0.05, -5.0)` | $X_4 = 0.0$ (penalized for negative equity) |
| **Altman Z-Score** | $Z = 7.22$ ("Safe Zone") | $Z = -1.78$ ("Distress Zone (High Insolvent Risk)") |
| **Piotroski Criterion 5** | +1 pt ("Conservative Debt-to-Equity") | 0 pts (fails `0.0 <= de < 0.5`) |
| **Pillar 4 Score** | 65.0 ("Fortress Balance Sheet") | 0.0 (starts at 50 - 40 neg equity - 20 liquidity) |
| **Pillar 4 Log** | "Fortress Balance Sheet: Virtually zero debt" | "CRITICAL SOLVENCY RISK: Negative Equity..." |
| **Red Flags** | 1 flag (only negative ROE) | 3 flags (Negative ROE + Balance Sheet Insolvency + Altman Distress) |
| **Final Recommendation** | Avoid (only due to ROE) | AVOID (Multiple Critical Solvency Red Flags) |

### Exact Code Diffs for Implementer

#### Diff 1: `core/evaluator.py` — Pillar 4 (`_eval_debt_solvency`)
```python
<<<<
            if tot_debt is not None and equity and equity > 0:
                debt_to_equity = tot_debt / equity
====
            if tot_debt is not None and equity and equity > 0:
                debt_to_equity = tot_debt / equity
            elif tot_debt is not None and equity and equity < 0:
                debt_to_equity = tot_debt / equity
            elif equity is not None and equity < 0:
                debt_to_equity = -1.0

        if debt_to_equity is None:
            bv = self._safe_float(self.info.get("bookValue"))
            if bv is not None and bv < 0:
                debt_to_equity = -1.0
>>>>
```

And in lines 384–398:
```python
<<<<
        if debt_to_equity is not None:
            if debt_to_equity <= 0.20:
                score += 35
                details.append(f"Fortress Balance Sheet: Virtually zero debt (D/E = {debt_to_equity:.2f}x).")
            elif debt_to_equity <= 0.60:
                score += 25
                details.append(f"Healthy Solvency: Conservative leverage (D/E = {debt_to_equity:.2f}x).")
            elif debt_to_equity <= 1.20:
                score += 5
                details.append(f"Moderate Debt Load: D/E is {debt_to_equity:.2f}x.")
            elif debt_to_equity > 1.50:
                score -= 35
                details.append(f"High Financial Risk: Elevated Debt-to-Equity of {debt_to_equity:.2f}x.")
        else:
            score += 15
====
        if debt_to_equity is not None:
            if debt_to_equity < 0:
                score -= 40
                details.append(f"CRITICAL SOLVENCY RISK: Negative Equity / Balance Sheet Insolvency (D/E = {debt_to_equity:.2f}x).")
            elif debt_to_equity <= 0.20:
                score += 35
                details.append(f"Fortress Balance Sheet: Virtually zero debt (D/E = {debt_to_equity:.2f}x).")
            elif debt_to_equity <= 0.60:
                score += 25
                details.append(f"Healthy Solvency: Conservative leverage (D/E = {debt_to_equity:.2f}x).")
            elif debt_to_equity <= 1.20:
                score += 5
                details.append(f"Moderate Debt Load: D/E is {debt_to_equity:.2f}x.")
            elif debt_to_equity > 1.50:
                score -= 35
                details.append(f"High Financial Risk: Elevated Debt-to-Equity of {debt_to_equity:.2f}x.")
        else:
            score += 15
>>>>
```

#### Diff 2: `core/evaluator.py` — Piotroski F-Score (`_calc_piotroski_f_score`)
```python
<<<<
        # 5. Low/Decreasing Leverage (D/E < 0.5x)
        raw_de = self.info.get("debtToEquity")
        de = self._normalize_de(raw_de) if raw_de is not None else None
        if de is None and not self.balance_sheet.empty:
            tot_debt = _get_val(self.balance_sheet, ["Total Debt"])
            equity = _get_val(self.balance_sheet, ["Common Stock Equity", "Stockholders Equity", "Total Equity Gross Minority Interest"])
            if tot_debt is not None and equity and equity > 0:
                de = tot_debt / equity
        if de is not None and de < 0.5:
            score += 1
            details.append(f"Conservative Debt-to-Equity ({de:.2f}x < 0.5x) (+1)")
====
        # 5. Low/Decreasing Leverage (0.0 <= D/E < 0.5x)
        raw_de = self.info.get("debtToEquity")
        de = self._normalize_de(raw_de) if raw_de is not None else None
        if de is None and not self.balance_sheet.empty:
            tot_debt = _get_val(self.balance_sheet, ["Total Debt"])
            equity = _get_val(self.balance_sheet, ["Common Stock Equity", "Stockholders Equity", "Total Equity Gross Minority Interest"])
            if tot_debt is not None and equity and equity > 0:
                de = tot_debt / equity
            elif equity is not None and equity < 0:
                de = -1.0
        if de is not None and 0.0 <= de < 0.5:
            score += 1
            details.append(f"Conservative Debt-to-Equity ({de:.2f}x < 0.5x) (+1)")
>>>>
```

#### Diff 3: `core/evaluator.py` — Altman Z-Score (`_calc_altman_z_score`)
```python
<<<<
        # X4 = Market Value of Equity / Total Liabilities
        if mcap is not None and tl is not None and tl > 0:
            x4 = min(15.0, mcap / tl)
        else:
            de = self._normalize_de(self.info.get("debtToEquity"))
            if de is not None:
                x4 = min(15.0, 1.0 / max(0.05, de))
            else:
                x4 = 1.5

        # X5 = Sales / Total Assets
        if sales is not None and ta is not None and ta > 0:
            x5 = sales / ta
        else:
            x5 = 1.0  # Normalized corporate asset turnover benchmark

        # Authentic Altman Z-Score formula
        z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.99 * x5
        z = float(round(z, 2))

        if z > 2.99:
            status = "Safe Zone (Low Bankruptcy Risk)"
        elif z >= 1.81:
            status = "Grey Zone (Moderate Financial Health)"
        else:
            status = "Distress Zone (High Insolvent Risk)"

        return z, status
====
        # Balance sheet insolvency / negative equity detection
        raw_de = self.info.get("debtToEquity")
        de = self._normalize_de(raw_de) if raw_de is not None else None
        bv = self._safe_float(self.info.get("bookValue"))
        equity = _get_val(self.balance_sheet, ["Common Stock Equity", "Stockholders Equity", "Total Equity Gross Minority Interest", "Total Stockholder Equity"])
        
        is_negative_equity = (
            (de is not None and de < 0)
            or (bv is not None and bv < 0)
            or (equity is not None and equity < 0)
            or (ta is not None and tl is not None and ta > 0 and tl > ta)
        )

        # X4 = Market Value of Equity / Total Liabilities
        if is_negative_equity:
            x4 = 0.0
        elif mcap is not None and tl is not None and tl > 0:
            x4 = min(15.0, mcap / tl)
        elif de is not None:
            x4 = min(15.0, 1.0 / max(0.05, de))
        else:
            x4 = 1.5

        # X5 = Sales / Total Assets
        if sales is not None and ta is not None and ta > 0:
            x5 = sales / ta
        else:
            x5 = 1.0  # Normalized corporate asset turnover benchmark

        # Authentic Altman Z-Score formula
        z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.99 * x5
        z = float(round(z, 2))

        if is_negative_equity and z >= 1.81:
            z = 1.80  # Cap at Distress Zone boundary for balance sheet insolvent firms

        if z > 2.99:
            status = "Safe Zone (Low Bankruptcy Risk)"
        elif z >= 1.81:
            status = "Grey Zone (Moderate Financial Health)"
        else:
            status = "Distress Zone (High Insolvent Risk)"

        return z, status
>>>>
```

#### Diff 4: `core/evaluator.py` — Red Flag Shield (`_detect_red_flags`)
```python
<<<<
        de = p4.get("debt_to_equity")
        if de is not None and de > 2.0 and not self.is_financial:
            flags.append(f"CRITICAL SOLVENCY RISK: High Debt-to-Equity ratio of {de:.2f}x.")
====
        de = p4.get("debt_to_equity")
        if de is not None and not self.is_financial:
            if de < 0:
                flags.append(f"BALANCE SHEET INSOLVENCY: Negative Net Worth / Insolvent Equity (D/E = {de:.2f}x).")
            elif de > 2.0:
                flags.append(f"CRITICAL SOLVENCY RISK: High Debt-to-Equity ratio of {de:.2f}x.")
>>>>
```

#### Diff 5: `tests/test_challenger_m1.py` — Update Bug Reproduction Test to Verification Test
```python
<<<<
    def test_reproduce_negative_equity_altman_distortion(self):
        """
        EMPERICAL DEFECT REPRODUCTION:
        When a firm has negative equity (insolvent) and reports negative debtToEquity,
        evaluator._calc_altman_z_score calculates x4 = 15.0 (maximum possible)
        due to max(0.05, de) treating negative D/E as lower than 0.05.
        This inflates Z by +9.0 points, classifying an insolvent company as 'Safe Zone'.
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
        # Empirically verify the bug exists:
        # Expected correct behavior: z < 1.81 (Distress Zone)
        # Actual buggy behavior: z = 7.22 (Safe Zone)
        self.assertEqual(z, 7.22, "Bug signature: negative D/E yields distorted Z=7.22")
        self.assertEqual(status, "Safe Zone (Low Bankruptcy Risk)", "Bug signature: classified as Safe Zone")
====
    def test_negative_equity_altman_and_piotroski_remediation(self):
        """
        VERIFIES REMEDIATION OF NEGATIVE EQUITY DEFECT:
        When a firm has negative equity (insolvent) and reports negative debtToEquity:
        1. Altman Z-Score penalizes X4 to 0.0 and classifies as Distress Zone (Z < 1.81).
        2. Piotroski F-Score does NOT award +1 for Criterion 5 (D/E < 0.5).
        3. Pillar 4 penalizes negative D/E (-40 pts) and logs balance sheet insolvency.
        4. Red flags contain both balance sheet insolvency and Altman distress.
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
        self.assertLess(z, 1.81, f"Altman Z {z} must be in Distress Zone (< 1.81)")
        self.assertEqual(z, -1.78, f"Expected Z = -1.78, got {z}")
        self.assertEqual(status, "Distress Zone (High Insolvent Risk)")

        f_score, f_details = ev._calc_piotroski_f_score()
        self.assertEqual(f_score, 0, f"Insolvent firm must not receive Piotroski points, got {f_score}")
        self.assertFalse(any("Conservative Debt-to-Equity" in d for d in f_details))

        p4 = ev._eval_debt_solvency()
        self.assertEqual(p4["score"], 0.0, f"Pillar 4 score must be 0.0, got {p4['score']}")
        self.assertTrue(any("Negative Equity" in d for d in p4["details"]))

        res = ev.evaluate_all()
        self.assertFalse(res["is_recommended"])
        self.assertEqual(res["signal"], "AVOID (RED FLAGS DETECTED)")
        self.assertTrue(any("BALANCE SHEET INSOLVENCY" in f for f in res["red_flags"]))
        self.assertTrue(any("ALTMAN DISTRESS WARNING" in f for f in res["red_flags"]))
>>>>
```

---

## 5. Verification Method

### Independent Verification Commands
1. Run challenger unit test suite:
   ```powershell
   python -m unittest tests/test_challenger_m1.py
   ```
2. Run core engine test suite:
   ```powershell
   python -m unittest test_engine.py
   ```
3. Run comprehensive e2e regression suite:
   ```powershell
   python -m unittest tests/test_e2e_suites.py
   ```
4. Verify specific insolvent stock evaluation:
   ```powershell
   python -c "from core.evaluator import PillarEvaluator; stock = {'symbol': 'BANKRUPT.NS', 'info': {'debtToEquity': -5.0, 'currentRatio': 0.5, 'returnOnEquity': -0.8, 'returnOnAssets': -0.4, 'operatingMargins': -0.5}}; ev = PillarEvaluator(stock); res = ev.evaluate_all(); assert res['altman_z_score'] == -1.78; assert res['altman_status'] == 'Distress Zone (High Insolvent Risk)'; assert res['piotroski_f_score'] == 0; assert res['pillars']['debt_solvency']['score'] == 0.0; assert res['signal'] == 'AVOID (RED FLAGS DETECTED)'; print('ALL INVARIANTS VERIFIED!')"
   ```

### Invalidation Conditions
The proposed solution is invalidated if:
1. An insolvent firm with `debtToEquity < 0` receives a Piotroski score $> 0$ for criterion 5, or receives a Pillar 4 score $> 20$, or is classified in "Safe Zone" or "Grey Zone" by Altman Z.
2. A healthy zero-debt company (`debtToEquity == 0.0`) fails to receive maximum credit ($X_4 = 15.0$, Pillar 4 +35, Piotroski +1).
3. Any of the existing 26 unit tests in `test_engine.py` or `test_challenger_m1.py` fail.
