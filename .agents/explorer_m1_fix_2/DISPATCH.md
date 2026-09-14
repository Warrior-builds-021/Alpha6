# M1 Fix Explorer 2: Risk Manager Penny Stock & Zero Price Edge Cases

## Context
Milestone 1 Gate Iteration 1 failed because Challenger 1 discovered:
1. In `core/risk_manager.py:49`:
   `stop_loss = round(max(0.1, stock_price - atr_buffer), 2)`
   For penny stocks priced below ₹0.10 (e.g. ₹0.05), flooring stop loss at 0.10 forces stop loss to be ABOVE entry price (+100% stop loss), causing target 1 to be below stop loss and calculating negative risk capital.
2. In `core/risk_manager.py:88`:
   Calling `RiskManager.calculate_trade_plan(0.0, ...)` crashes with `ZeroDivisionError: division by zero` in `"stop_loss_pct": round(((stop_loss - stock_price) / stock_price) * 100, 2)`.

## Assignment
Investigate and formulate the exact remediation strategy for `core/risk_manager.py`:
1. Proper stop-loss flooring: floor stop loss at a relative fraction (e.g. `max(0.01, stock_price * 0.85)` or `stock_price * (1 - buffer_pct)`) so that stop loss is strictly below entry price for all positive prices.
2. Zero or negative price handling: guard `if stock_price <= 0:` returning a zeroed plan with a clear error/alert message without raising ZeroDivisionError.
3. Provide exact code diffs and verification tests.

Write your report to `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_m1_fix_2\handoff.md` and notify parent via `send_message`.

## 2026-09-13T20:31:09Z
You are M1 Fix Explorer 2.
Read your dispatch at `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_m1_fix_2\DISPATCH.md`.
Read `c:\Users\asaik\OneDrive\Desktop\PROJECT1\core\risk_manager.py` and `tests\test_challenger_m1.py`.
Investigate the penny stock stop loss floor inversion and zero price division defects in RiskManager.
Formulate the exact remediation strategy. Do NOT implement changes directly.
Write your report to `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_m1_fix_2\handoff.md` and notify parent via send_message.
