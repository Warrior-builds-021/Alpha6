# Progress Log - Explorer Survey 2 (Quantitative & Risk Domain Analyst)

- Last visited: 2026-09-14T01:36:40Z
- Status: Deep investigation in progress
- Completed findings:
  1. Identified import breakage in test_engine.py and app.py (`GLOBAL_US_MEGA_TECH` and `INDIAN_QUALITY_GROWTH` missing from core/universe.py).
  2. Identified format_ticker bug where non-Indian symbols like AAPL are incorrectly mangled to AAPL.NS.
  3. Identified severe limitation in Altman Z-Score implementation in `core/evaluator.py`: currently a 4-step dummy lookup on D/E ratio rather than true 5-variable formula (Z = 1.2X1 + 1.4X2 + 3.3X3 + 0.6X4 + 0.99X5).
  4. Identified bug in Pillar 2 Sales Growth: revenueGrowth between 0% and 15% receives zero points and empty details due to flawed if/elif structure.
  5. Identified data sparsity issue in yfinance `ticker.info` for major Indian scrips (RELIANCE.NS, LT.NS, ITC.NS missing operatingCashflow, returnOnAssets, currentRatio in info dict), causing severe artificial score penalties because `_calc_piotroski_f_score` does not fall back to `cashflow` and `balance_sheet` DataFrames.
  6. Verified dynamic ATR position sizing logic, 2x ATR stop loss bounds (3% to 15%), and identified edge cases when stock price exceeds max single position cap.
  7. Tested FastAPI endpoints: health, search, position-size, candles, backtest, audit.
