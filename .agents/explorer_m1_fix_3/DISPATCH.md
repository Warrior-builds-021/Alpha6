# M1 Fix Explorer 3: Ticker Formatting & Test Harness Unification

## Context
Milestone 1 Gate Iteration 1 highlighted:
1. In `core/universe.py:format_ticker()`:
   Index symbols starting with `^` (e.g. `^NSEI`, `^BSESN`) get appended with `.NS` (e.g. `^NSEI.NS`), causing Yahoo Finance 404 errors for index price lookups.
   Hyphenated US tickers like `BRK-A`, `BRK-B` should be included in `US_TICKER_SYMBOLS`.
2. `tests/test_challenger_m1.py` contains empirical reproduction tests written by Challenger 1.
   Explore how to cleanly incorporate these boundary test cases into `test_engine.py` or regression suites so that passing tests prove all edge cases are permanently fixed.

## Assignment
Investigate and formulate the exact remediation strategy for `core/universe.py` and test suite unification.
Provide exact code diffs and verification tests.

Write your report to `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_m1_fix_3\handoff.md` and notify parent via `send_message`.

## 2026-09-13T20:31:09Z
You are M1 Fix Explorer 3.
Read your dispatch at `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_m1_fix_3\DISPATCH.md`.
Read `c:\Users\asaik\OneDrive\Desktop\PROJECT1\core\universe.py`, `tests\test_challenger_m1.py`, and `tests\test_challenger_m1_2.py`.
Investigate the index caret (^) preservation in `format_ticker`, hyphenated US symbols, and test suite integration.
Formulate the exact remediation strategy. Do NOT implement changes directly.
Write your report to `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_m1_fix_3\handoff.md` and notify parent via send_message.

