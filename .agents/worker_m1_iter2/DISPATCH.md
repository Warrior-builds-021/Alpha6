# Worker M1 Iteration 2 Dispatch: Boundary Defect Remediation

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Assignment
Implement the remediation diffs designed by Fix Explorers 1, 2, and 3:
1. `core/evaluator.py`:
   - Balance sheet insolvency detection (`de < 0`, `bookValue < 0`, negative equity lines).
   - Altman Z-Score: Set $X_4 = 0.0$ and cap $Z \le 1.80$ when equity/de is negative. Classify as Distress Zone ($Z < 1.81$).
   - Piotroski F-Score: Restrict Criterion 5 to $0.0 \le de < 0.5$ (negative D/E does NOT receive a point).
   - Pillar 4: Penalize negative D/E by -40 points with critical solvency log.
   - Red Flag Shield: Trigger `BALANCE SHEET INSOLVENCY` and `ALTMAN DISTRESS WARNING`, disqualifying the stock with `AVOID (RED FLAGS DETECTED)`.
2. `core/risk_manager.py`:
   - Relative stop-loss floor for penny stocks: ensure stop-loss is strictly below entry price for all positive prices.
   - Zero or negative stock price: guard `if stock_price <= 0:` returning zeroed plan without `ZeroDivisionError`.
3. `core/universe.py`:
   - Index caret preservation: `if clean_sym.startswith("^"): return clean_sym[:-3] if clean_sym.endswith((".NS", ".BO")) else clean_sym`.
   - Add `"BRK-A"`, `"BRK-B"`, `"BF-A"`, `"BF-B"` to `US_TICKER_SYMBOLS`.
4. Tests:
   - Invert reproduction tests in `tests/test_challenger_m1.py` so they assert the fixed behavior ($Z < 1.81$, stop loss < price, zero price handled).
   - Update `tests/test_challenger_m1_2.py` and `test_engine.py` with the new regression assertions.
   - Run `python test_engine.py`, `python tests/test_challenger_m1.py`, `python tests/test_challenger_m1_2.py`, and `python tests/test_e2e_suites.py`.

## Inputs to Study
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_m1_fix_1\handoff.md`
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_m1_fix_2\handoff.md`
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_m1_fix_3\handoff.md`
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\tests\test_challenger_m1.py`

Write your completion report to `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\worker_m1_iter2\handoff.md` and notify parent via `send_message`.
