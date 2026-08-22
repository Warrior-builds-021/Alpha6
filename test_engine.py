"""
Automated Test Suite for 6-Pillar Stock Intelligence Terminal
"""

import unittest
import pandas as pd
import numpy as np
from core.universe import format_ticker, INDIAN_NIFTY_50, GLOBAL_US_MEGA_TECH
from core.evaluator import PillarEvaluator
from core.risk_manager import RiskManager

class TestPillarEngine(unittest.TestCase):
    
    def test_ticker_formatting(self):
        self.assertEqual(format_ticker("TCS"), "TCS.NS")
        self.assertEqual(format_ticker("RELIANCE.NS"), "RELIANCE.NS")
        self.assertEqual(format_ticker("AAPL"), "AAPL")
        self.assertEqual(format_ticker("NVDA"), "NVDA")

    def test_evaluator_synthetic_data(self):
        # Mock high-conviction stock data
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
        mock_history = pd.DataFrame({
            "Open": np.linspace(100, 150, 100),
            "High": np.linspace(102, 155, 100),
            "Low": np.linspace(98, 148, 100),
            "Close": np.linspace(100, 150, 100),
            "Volume": np.full(100, 1000000)
        }, index=dates)

        mock_stock = {
            "symbol": "MOCK.NS",
            "short_name": "Mock Compounding Tech Ltd",
            "sector": "Information Technology",
            "current_price": 150.0,
            "currency": "INR",
            "info": {
                "revenueGrowth": 0.22,
                "operatingCashflow": 500000000,
                "netIncome": 400000000,
                "freeCashflow": 350000000,
                "debtToEquity": 0.05,
                "currentRatio": 2.5,
                "grossMargins": 0.48,
                "returnOnEquity": 0.28,
                "heldPercentInsiders": 0.62,
                "heldPercentInstitutions": 0.25
            },
            "history": mock_history,
            "income_stmt": pd.DataFrame(),
            "balance_sheet": pd.DataFrame(),
            "cashflow": pd.DataFrame()
        }

        evaluator = PillarEvaluator(mock_stock)
        res = evaluator.evaluate_all()

        self.assertGreaterEqual(res["composite_score"], 78.0)
        self.assertTrue(res["is_recommended"])
        self.assertEqual(len(res["red_flags"]), 0)
        self.assertEqual(res["signal"], "HIGH CONVICTION BUY")

    def test_red_flag_disqualification(self):
        # Mock dangerous debt-laden stock with negative cashflow
        mock_bad_stock = {
            "symbol": "RISK.NS",
            "short_name": "Debt Trap Corp",
            "sector": "Industrials",
            "current_price": 40.0,
            "currency": "INR",
            "info": {
                "revenueGrowth": -0.15,
                "operatingCashflow": -50000000,
                "netIncome": 10000000,
                "freeCashflow": -80000000,
                "debtToEquity": 3.5,  # Extreme debt
                "currentRatio": 0.6,
                "grossMargins": 0.08,
                "returnOnEquity": -0.05,
                "heldPercentInsiders": 0.05
            },
            "history": pd.DataFrame(),
            "income_stmt": pd.DataFrame(),
            "balance_sheet": pd.DataFrame(),
            "cashflow": pd.DataFrame()
        }

        evaluator = PillarEvaluator(mock_bad_stock)
        res = evaluator.evaluate_all()

        self.assertFalse(res["is_recommended"])
        self.assertGreater(len(res["red_flags"]), 0)
        self.assertIn("AVOID", res["signal"])

    def test_risk_manager_position_sizing(self):
        dates = pd.date_range(end=pd.Timestamp.now(), periods=50)
        mock_history = pd.DataFrame({
            "Open": np.full(50, 100.0),
            "High": np.full(50, 105.0),
            "Low": np.full(50, 95.0),
            "Close": np.full(50, 100.0),
            "Volume": np.full(50, 10000)
        }, index=dates)

        plan = RiskManager.calculate_trade_plan(
            stock_price=100.0,
            history=mock_history,
            total_portfolio_size=100000.0,
            risk_per_trade_pct=1.5,
            max_position_size_pct=10.0
        )

        self.assertLess(plan["stop_loss"], 100.0)
        self.assertGreater(plan["target_1"], 100.0)
        self.assertGreater(plan["target_2"], plan["target_1"])
        self.assertLessEqual(plan["portfolio_weight_pct"], 10.0)

if __name__ == "__main__":
    unittest.main()
