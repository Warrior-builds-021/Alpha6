# M1 Fix Explorer 1: Negative D/E & Insolvent Distortion Remediation

## Context
Milestone 1 Gate Iteration 1 failed because Challenger 1 discovered:
In `core/evaluator.py:724-726`:
When an insolvent company has negative equity and reports negative D/E (e.g. `debtToEquity = -5.0`), `max(0.05, de)` evaluates to `0.05`, yielding maximum ratio $X_4 = 15.0$ (+9.0 points in Altman Z-Score).
This erroneously classifies an insolvent company as $Z = 7.22$ ("Safe Zone") and awards +1 Piotroski point (`de < 0.5`) and +35 points in Pillar 4!

## Assignment
Investigate and formulate the exact remediation strategy for `core/evaluator.py`:
1. How to identify negative equity / balance sheet insolvency (e.g. `de < 0`, negative common stock equity, or negative book value).
2. In `_calc_altman_z_score()`: when equity or D/E is negative, $X_4$ must be penalized (e.g. $X_4 = 0.0$ or negative) and Altman Z-score must classify into Distress Zone ($Z < 1.81$).
3. In `_calc_piotroski_f_score()`: criterion 5 (`de < 0.5`) must require $0.0 \le de < 0.5$ (negative D/E indicates negative equity / insolvency and must NOT receive a point).
4. In `_eval_debt_solvency()`: negative D/E must be penalized heavily (-40 points) and trigger a red flag for balance sheet insolvency / negative net worth.
5. Provide exact code diffs and verification tests.

Write your report to `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_m1_fix_1\handoff.md` and notify parent via `send_message`.
