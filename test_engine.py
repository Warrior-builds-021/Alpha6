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
        self.assertEqual(format_ticker("500325"), "500325.BO")
        # Index carets and US dual-class tickers
        self.assertEqual(format_ticker("^NSEI"), "^NSEI")
        self.assertEqual(format_ticker("^BSESN"), "^BSESN")
        self.assertEqual(format_ticker("^GSPC"), "^GSPC")
        self.assertEqual(format_ticker("^NSEI.NS"), "^NSEI")
        self.assertEqual(format_ticker("BRK-A"), "BRK-A")
        self.assertEqual(format_ticker("BRK-B"), "BRK-B")
        self.assertEqual(format_ticker("BRK.A"), "BRK-A")

    def test_universe_aliases(self):
        from core.universe import INDIAN_QUALITY_GROWTH, GLOBAL_US_MEGA_TECH
        from core import INDIAN_QUALITY_GROWTH as IQG, GLOBAL_US_MEGA_TECH as GUMT
        self.assertGreater(len(INDIAN_QUALITY_GROWTH), 0)
        self.assertGreater(len(GLOBAL_US_MEGA_TECH), 0)
        self.assertEqual(len(INDIAN_QUALITY_GROWTH), len(IQG))
        self.assertEqual(len(GLOBAL_US_MEGA_TECH), len(GUMT))

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
                "debtToEquity": 3.5,  # Extreme debt (handled via normalization)
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

    def test_sales_growth_gap_fix(self):
        # Stock with 13.9% quarterly revenue growth (TCS case)
        mock_stock = {
            "symbol": "COMPOUNDER.NS",
            "current_price": 100.0,
            "info": {"revenueGrowth": 0.139},
            "history": pd.DataFrame(),
            "income_stmt": pd.DataFrame(),
            "balance_sheet": pd.DataFrame(),
            "cashflow": pd.DataFrame()
        }
        ev = PillarEvaluator(mock_stock)
        res = ev._eval_sales_growth()
        self.assertGreaterEqual(res["score"], 70.0)  # 50 base + 20 for >= 12%
        self.assertTrue(any("13.9%" in d for d in res["details"]))

    def test_debt_solvency_normalization(self):
        # 1.8% D/E reported as 1.8 by Yahoo Finance
        mock_stock = {
            "symbol": "LOWDEBT.NS",
            "current_price": 100.0,
            "info": {"debtToEquity": 1.8, "currentRatio": 2.0},
            "history": pd.DataFrame(),
            "income_stmt": pd.DataFrame(),
            "balance_sheet": pd.DataFrame(),
            "cashflow": pd.DataFrame()
        }
        ev = PillarEvaluator(mock_stock)
        res = ev._eval_debt_solvency()
        self.assertEqual(res["debt_to_equity"], 0.02)  # 0.018 rounded to 0.02
        self.assertGreaterEqual(res["score"], 85.0)    # Fortress balance sheet bonus

    def test_altman_z_score_genuine_5_ratios(self):
        # Test authentic Edward Altman 5-ratio calculation with balance sheet & financials
        bs = pd.DataFrame({
            "2024-03-31": [747910000000.0, 1823720000000.0, 998830000000.0, 738940000000.0]
        }, index=["Working Capital", "Total Assets", "Retained Earnings", "Total Liabilities Net Minority Interest"])

        inc = pd.DataFrame({
            "2024-03-31": [667140000000.0, 2670210000000.0]
        }, index=["EBIT", "Total Revenue"])

        mock_stock = {
            "symbol": "TEST.NS",
            "market_cap": 7962686914560,
            "current_price": 4000.0,
            "info": {"marketCap": 7962686914560},
            "history": pd.DataFrame(),
            "income_stmt": inc,
            "balance_sheet": bs,
            "cashflow": pd.DataFrame()
        }
        ev = PillarEvaluator(mock_stock)
        z, status = ev._calc_altman_z_score()
        self.assertGreater(z, 2.99)
        self.assertIn("Safe Zone", status)

    def test_piotroski_statement_fallback(self):
        # Stock where info omits OCF, ROA, Current Ratio, but balance sheet & cashflow provide them
        bs = pd.DataFrame({
            "2024-03-31": [1000000.0, 800000.0, 5000000.0, 200000.0, 4000000.0]
        }, index=["Current Assets", "Current Liabilities", "Total Assets", "Total Debt", "Common Stock Equity"])

        cf = pd.DataFrame({
            "2024-03-31": [600000.0]
        }, index=["Operating Cash Flow"])

        inc = pd.DataFrame({
            "2024-03-31": [400000.0, 3000000.0, 1000000.0]
        }, index=["Net Income", "Total Revenue", "Gross Profit"])

        mock_stock = {
            "symbol": "FALLBACK.NS",
            "current_price": 100.0,
            "info": {},  # Completely empty info!
            "history": pd.DataFrame(),
            "income_stmt": inc,
            "balance_sheet": bs,
            "cashflow": cf
        }
        ev = PillarEvaluator(mock_stock)
        score, details = ev._calc_piotroski_f_score()
        self.assertGreaterEqual(score, 7)  # Extracts net income, OCF, ROA, OCF>NI, D/E, CR, GM

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

    def test_risk_manager_overrun_guard(self):
        # Stock price ₹135,000 > ₹12,000 max capital cap (12% of 100k)
        plan = RiskManager.calculate_position_size(
            stock_price=135000.0,
            history=pd.DataFrame(),
            total_portfolio_size=100000.0,
            risk_per_trade_pct=1.5,
            max_position_size_pct=12.0
        )
        self.assertEqual(plan["recommended_shares"], 0)
        self.assertEqual(plan["portfolio_weight_pct"], 0.0)
        self.assertEqual(plan["total_investment"], 0.0)
        self.assertIsNotNone(plan["sizing_alert"])
        self.assertIn("Capital Overrun Guard", plan["sizing_alert"])

    def test_altman_z_score_negative_equity_distress(self):
        """Insolvent company with negative equity must be in Distress Zone, not Safe Zone."""
        mock_insolvent = {
            "symbol": "BANKRUPT.NS",
            "info": {
                "debtToEquity": -5.0,
                "currentRatio": 0.5,
                "returnOnEquity": -0.8,
                "returnOnAssets": -0.4,
                "operatingMargins": -0.5
            }
        }
        ev = PillarEvaluator(mock_insolvent)
        z, status = ev._calc_altman_z_score()
        self.assertLess(z, 1.81)
        self.assertIn("Distress Zone", status)
        
        res = ev.evaluate_all()
        self.assertFalse(res["is_recommended"])
        self.assertIn("AVOID", res["signal"])

    def test_risk_manager_penny_stock_bounds(self):
        """Sub-₹0.10 penny stocks must have stop loss strictly below entry price."""
        dates = pd.date_range(end=pd.Timestamp.now(), periods=50)
        hist = pd.DataFrame({
            "Open": np.full(50, 0.05),
            "High": np.full(50, 0.06),
            "Low": np.full(50, 0.04),
            "Close": np.full(50, 0.05),
            "Volume": np.full(50, 100000)
        }, index=dates)
        plan = RiskManager.calculate_trade_plan(
            stock_price=0.05,
            history=hist,
            total_portfolio_size=100000.0,
            risk_per_trade_pct=1.5,
            max_position_size_pct=12.0
        )
        self.assertLess(plan["stop_loss"], plan["current_price"])
        self.assertGreater(plan["target_1"], plan["current_price"])
        self.assertGreaterEqual(plan["max_risk_capital"], 0.0)

    def test_risk_manager_zero_price_guard(self):
        """Zero price input must not raise ZeroDivisionError."""
        plan = RiskManager.calculate_trade_plan(
            stock_price=0.0,
            history=pd.DataFrame(),
            total_portfolio_size=100000.0
        )
        self.assertEqual(plan["recommended_shares"], 0)
        self.assertEqual(plan["total_investment"], 0.0)
        self.assertIsNotNone(plan["sizing_alert"])

if __name__ == "__main__":
    unittest.main()

