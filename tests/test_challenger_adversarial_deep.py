"""
Deep Adversarial Stress Harness for Challenger M1 Gate 2
Probes the boundaries of:
1. Negative D/E / Insolvency in Altman Z & Piotroski F
2. Penny Stock Stop Loss & Pricing Limits
3. Non-positive & Hostile Price inputs (0, negative, NaN, Inf)
4. Ticker formatting edge cases (caret preservation, dual-class, punctuation)
"""

import os
import sys
import math
import unittest
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.evaluator import PillarEvaluator
from core.risk_manager import RiskManager
from core.universe import format_ticker


class TestBoundary1InsolvencyDeep(unittest.TestCase):
    def test_various_negative_de_values(self):
        """Test a spectrum of negative D/E ratios representing varying degrees of capital deficit."""
        for neg_de in [-0.001, -0.05, -0.5, -1.0, -5.0, -100.0, -1e6]:
            stock = {
                "symbol": "INSOLVENT.NS",
                "info": {
                    "debtToEquity": neg_de,
                    "currentRatio": 0.8,
                    "returnOnEquity": -0.2,
                    "operatingMargins": -0.1
                }
            }
            ev = PillarEvaluator(stock)
            z, status = ev._calc_altman_z_score()
            self.assertLessEqual(z, 1.80, f"Altman Z must be capped <= 1.80 for negative D/E {neg_de}, got {z}")
            self.assertEqual(status, "Distress Zone (High Insolvent Risk)")

            f_score, details = ev._calc_piotroski_f_score()
            self.assertFalse(any("Conservative Debt-to-Equity" in d for d in details),
                             f"Criterion 5 must NOT be awarded for negative D/E {neg_de}")

            p4 = ev._eval_debt_solvency()
            self.assertLessEqual(p4["score"], 50.0)
            self.assertTrue(any("Negative Equity" in d or "Insolvency" in d for d in p4["details"]))

    def test_balance_sheet_negative_equity_without_info_de(self):
        """When info has no debtToEquity but balance sheet shows common stock equity < 0."""
        bs = pd.DataFrame({
            "2024-03-31": [100000.0, -50000.0, 50000.0, 150000.0]
        }, index=["Total Assets", "Common Stock Equity", "Working Capital", "Total Liabilities"])

        stock = {
            "symbol": "BS_INSOLVENT.NS",
            "info": {},
            "balance_sheet": bs
        }
        ev = PillarEvaluator(stock)
        z, status = ev._calc_altman_z_score()
        self.assertLessEqual(z, 1.80)
        self.assertEqual(status, "Distress Zone (High Insolvent Risk)")

        f_score, details = ev._calc_piotroski_f_score()
        self.assertFalse(any("Conservative Debt-to-Equity" in d for d in details))


class TestBoundary2PennyStocksDeep(unittest.TestCase):
    def test_penny_stock_micro_prices(self):
        """Test micro-penny prices down to 0.01 and sub-rupee values."""
        for p in [0.01, 0.02, 0.05, 0.10, 0.25, 0.50, 0.75, 0.99]:
            plan = RiskManager.calculate_trade_plan(
                stock_price=p,
                history=pd.DataFrame(),
                total_portfolio_size=100000.0
            )
            self.assertLess(plan["stop_loss"], p, f"Stop loss must be strictly < price for p={p}")
            self.assertGreater(plan["stop_loss"], 0.0, f"Stop loss must be > 0 for p={p}")
            self.assertLess(plan["stop_loss_pct"], 0.0)
            self.assertGreater(plan["target_1"], p)
            self.assertGreater(plan["target_2"], plan["target_1"])
            self.assertGreaterEqual(plan["max_risk_capital"], 0.0)


class TestBoundary3ZeroNegativePricesDeep(unittest.TestCase):
    def test_zero_and_negative_prices(self):
        for bad_p in [0.0, -0.0001, -1.0, -100.0, -1e8]:
            plan = RiskManager.calculate_trade_plan(
                stock_price=bad_p,
                history=pd.DataFrame(),
                total_portfolio_size=100000.0
            )
            self.assertEqual(plan["recommended_shares"], 0)
            self.assertEqual(plan["total_investment"], 0.0)
            self.assertEqual(plan["max_risk_capital"], 0.0)
            self.assertIn("Invalid Price Guard", plan["sizing_alert"])


class TestBoundary4TickerFormattingDeep(unittest.TestCase):
    def test_caret_preservation_and_dual_class(self):
        test_cases = {
            "^NSEI": "^NSEI",
            "^BSESN": "^BSESN",
            "^GSPC": "^GSPC",
            "^DJI": "^DJI",
            "^IXIC": "^IXIC",
            "^VIX": "^VIX",
            "^RUT": "^RUT",
            "  ^NSEI  ": "^NSEI",
            "^NSEI.NS": "^NSEI",
            "^BSESN.BO": "^BSESN",
            "BRK.A": "BRK-A",
            "BRK.B": "BRK-B",
            "BRK-A": "BRK-A",
            "BRK-B": "BRK-B",
            "BF-A": "BF-A",
            "BF-B": "BF-B",
            "AAPL": "AAPL",
            "RELIANCE": "RELIANCE.NS",
            "500325": "500325.BO",
            "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
            "M&M": "M&M.NS",
        }
        for raw, exp in test_cases.items():
            self.assertEqual(format_ticker(raw), exp, f"Failed formatting '{raw}'")


if __name__ == "__main__":
    unittest.main()
