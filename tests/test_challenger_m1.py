"""
Challenger 1 Empirical Stress Test Suite for Milestone 1.
Tests Altman Z-Score, Piotroski F-Score, ATR Position Sizing, and Sales/OCF Scoring under extreme edge cases.
Empirically reproduces and verifies mathematical boundaries, edge cases, and failure modes.
"""

import unittest
import numpy as np
import pandas as pd
from typing import Dict, Any

from core.evaluator import PillarEvaluator
from core.risk_manager import RiskManager

class TestChallengerAltmanZScore(unittest.TestCase):
    """Stress-test Edward Altman's 5-ratio Z-Score formula with boundary & hostile inputs."""

    def _make_stock_data(self, bs_rows=None, inc_rows=None, info_dict=None, price=100.0, mcap=1000000000):
        bs = pd.DataFrame({"2024-03-31": list(bs_rows.values())}, index=list(bs_rows.keys())) if bs_rows else pd.DataFrame()
        inc = pd.DataFrame({"2024-03-31": list(inc_rows.values())}, index=list(inc_rows.keys())) if inc_rows else pd.DataFrame()
        return {
            "symbol": "STRESS.NS",
            "current_price": price,
            "market_cap": mcap,
            "info": info_dict or {},
            "history": pd.DataFrame(),
            "income_stmt": inc,
            "balance_sheet": bs,
            "cashflow": pd.DataFrame()
        }

    def test_zero_assets_graceful_handling(self):
        """Zero or negative Total Assets should not raise ZeroDivisionError and should return valid status."""
        stock_zero_ta = self._make_stock_data(
            bs_rows={"Total Assets": 0.0, "Working Capital": 100.0, "Retained Earnings": 50.0, "Total Liabilities": 20.0},
            info_dict={"totalAssets": 0.0}
        )
        ev = PillarEvaluator(stock_zero_ta)
        z, status = ev._calc_altman_z_score()
        self.assertIsInstance(z, float)
        self.assertFalse(np.isnan(z))
        self.assertFalse(np.isinf(z))
        self.assertIn(status, ["Safe Zone (Low Bankruptcy Risk)", "Grey Zone (Moderate Financial Health)", "Distress Zone (High Insolvent Risk)"])

    def test_zero_liabilities_graceful_handling(self):
        """Zero Total Liabilities should not cause division by zero in X4 (Mkt Cap / TL)."""
        stock_zero_tl = self._make_stock_data(
            bs_rows={"Total Assets": 1000000.0, "Working Capital": 200000.0, "Retained Earnings": 400000.0, "Total Liabilities": 0.0},
            info_dict={"totalDebt": 0.0, "debtToEquity": 0.0}
        )
        ev = PillarEvaluator(stock_zero_tl)
        z, status = ev._calc_altman_z_score()
        self.assertIsInstance(z, float)
        self.assertFalse(np.isnan(z))
        self.assertGreater(z, 0.0)

    def test_completely_empty_stock_data(self):
        """Completely empty stock data dictionary should gracefully use fallbacks without crashing."""
        ev = PillarEvaluator({})
        z, status = ev._calc_altman_z_score()
        self.assertIsInstance(z, float)
        self.assertEqual(z, 2.68)
        self.assertIn("Grey Zone", status)

    def test_financial_sector_short_circuit(self):
        """Financial firms (banks/NBFCs) should return safe baseline for Altman Z."""
        ev = PillarEvaluator({"sector": "Banking and Financial Services"})
        z, status = ev._calc_altman_z_score()
        self.assertEqual(z, 3.5)
        self.assertIn("Financial Institution", status)

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


class TestChallengerPiotroskiFScore(unittest.TestCase):
    """Stress-test Piotroski F-Score bounds [0, 9] with empty, sparse, and extreme statements."""

    def test_completely_empty_data_returns_zero(self):
        """Empty data should return 0 and empty details list."""
        ev = PillarEvaluator({})
        score, details = ev._calc_piotroski_f_score()
        self.assertIsInstance(score, int)
        self.assertEqual(score, 0)
        self.assertEqual(len(details), 0)

    def test_perfect_data_returns_nine(self):
        """Stock satisfying all 9 criteria must receive exactly 9."""
        bs = pd.DataFrame({
            "2024-03-31": [5000000.0, 2000000.0, 10000000.0, 1000000.0, 8000000.0]
        }, index=["Current Assets", "Current Liabilities", "Total Assets", "Total Debt", "Common Stock Equity"])

        inc = pd.DataFrame({
            "2024-03-31": [1500000.0, 10000000.0, 4000000.0]
        }, index=["Net Income", "Total Revenue", "Gross Profit"])

        cf = pd.DataFrame({
            "2024-03-31": [2000000.0]
        }, index=["Operating Cash Flow"])

        stock = {
            "symbol": "PERFECT.NS",
            "info": {
                "netIncome": 1500000.0,
                "operatingCashflow": 2000000.0,
                "returnOnAssets": 0.15,
                "debtToEquity": 12.5,
                "currentRatio": 2.5,
                "grossMargins": 0.40,
                "revenueGrowth": 0.25,
                "returnOnEquity": 0.18
            },
            "balance_sheet": bs,
            "income_stmt": inc,
            "cashflow": cf
        }
        ev = PillarEvaluator(stock)
        score, details = ev._calc_piotroski_f_score()
        self.assertIsInstance(score, int)
        self.assertEqual(score, 9)
        self.assertEqual(len(details), 9)

    def test_all_failing_criteria_returns_zero(self):
        """Firm with negative earnings, negative cashflow, high debt, poor margins returns 0."""
        stock = {
            "symbol": "FAIL.NS",
            "info": {
                "netIncome": -500000.0,
                "operatingCashflow": -800000.0,
                "returnOnAssets": -0.10,
                "debtToEquity": 350.0,
                "currentRatio": 0.75,
                "grossMargins": 0.05,
                "revenueGrowth": -0.20,
                "returnOnEquity": -0.15
            }
        }
        ev = PillarEvaluator(stock)
        score, details = ev._calc_piotroski_f_score()
        self.assertIsInstance(score, int)
        self.assertEqual(score, 0)
        self.assertEqual(len(details), 0)

    def test_score_always_strictly_between_0_and_9(self):
        """Fuzz testing with random combinations of flags to ensure strict [0, 9] integer bound."""
        rng = np.random.default_rng(42)
        for _ in range(100):
            stock = {
                "symbol": "FUZZ.NS",
                "info": {
                    "netIncome": rng.uniform(-1e6, 1e6),
                    "operatingCashflow": rng.uniform(-1e6, 1e6),
                    "returnOnAssets": rng.uniform(-0.5, 0.5),
                    "debtToEquity": rng.uniform(0.0, 300.0),
                    "currentRatio": rng.uniform(0.1, 5.0),
                    "grossMargins": rng.uniform(-0.5, 0.9),
                    "revenueGrowth": rng.uniform(-0.5, 1.0),
                    "returnOnEquity": rng.uniform(-0.5, 0.5)
                }
            }
            ev = PillarEvaluator(stock)
            score, details = ev._calc_piotroski_f_score()
            self.assertIsInstance(score, int)
            self.assertTrue(0 <= score <= 9, f"Score {score} out of bounds [0, 9]")
            self.assertEqual(score, len(details))


class TestChallengerATRSizingLimits(unittest.TestCase):
    """Stress-test ATR position sizing boundaries across extreme prices, portfolio sizes, and volatility."""

    def test_mrf_extreme_price_in_modest_portfolio(self):
        """MRF at ₹150,000 in a ₹100,000 portfolio must yield 0 shares and 0% portfolio weight."""
        plan = RiskManager.calculate_trade_plan(
            stock_price=150000.0,
            history=pd.DataFrame(),
            total_portfolio_size=100000.0,
            risk_per_trade_pct=1.5,
            max_position_size_pct=12.0
        )
        self.assertEqual(plan["recommended_shares"], 0)
        self.assertEqual(plan["total_investment"], 0.0)
        self.assertEqual(plan["portfolio_weight_pct"], 0.0)
        self.assertIsNotNone(plan["sizing_alert"])
        self.assertIn("Capital Overrun Guard", plan["sizing_alert"])

    def test_mrf_extreme_price_in_ultra_hni_portfolio(self):
        """MRF at ₹150,000 in a ₹100,000,000 portfolio must respect the max 12% cap (₹12,000,000)."""
        plan = RiskManager.calculate_trade_plan(
            stock_price=150000.0,
            history=pd.DataFrame(),
            total_portfolio_size=100000000.0,
            risk_per_trade_pct=1.5,
            max_position_size_pct=12.0
        )
        self.assertGreater(plan["recommended_shares"], 0)
        self.assertLessEqual(plan["total_investment"], 12000000.0)
        self.assertLessEqual(plan["portfolio_weight_pct"], 12.0)
        self.assertLessEqual(plan["max_risk_capital"], 1500000.0)

    def test_tiny_portfolio_limits(self):
        """₹100 portfolio should never allocate more than ₹12 (12%) to any single stock."""
        plan = RiskManager.calculate_trade_plan(
            stock_price=50.0,
            history=pd.DataFrame(),
            total_portfolio_size=100.0,
            risk_per_trade_pct=1.5,
            max_position_size_pct=12.0
        )
        self.assertEqual(plan["recommended_shares"], 0)
        self.assertEqual(plan["total_investment"], 0.0)
        self.assertEqual(plan["portfolio_weight_pct"], 0.0)

    def test_reproduce_penny_stock_stop_loss_inversion(self):
        """
        EMPERICAL DEFECT REPRODUCTION:
        In core/risk_manager.py:49, stop_loss = round(max(0.1, stock_price - atr_buffer), 2).
        For stocks with price < 0.10, the stop loss is floored at 0.10, which is GREATER
        than the entry price. This creates an inverted trade plan (stop loss > price, target1 < stop loss).
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
        # Verify the defect is present:
        self.assertEqual(plan["stop_loss"], 0.1)
        self.assertGreater(plan["stop_loss"], plan["current_price"])
        self.assertEqual(plan["stop_loss_pct"], 100.0)
        self.assertLess(plan["target_1"], plan["stop_loss"])
        self.assertLess(plan["max_risk_capital"], 0.0)

    def test_reproduce_zero_price_division_by_zero_crash(self):
        """
        EMPERICAL DEFECT REPRODUCTION:
        RiskManager.calculate_trade_plan() crashes with ZeroDivisionError when stock_price == 0.0
        at line 88 ("stop_loss_pct": round(((stop_loss - stock_price) / stock_price) * 100, 2)).
        """
        with self.assertRaises(ZeroDivisionError):
            RiskManager.calculate_trade_plan(
                stock_price=0.0,
                history=pd.DataFrame(),
                total_portfolio_size=100000.0
            )


class TestChallengerSalesAndOCFScoring(unittest.TestCase):
    """Stress-test Sales Growth (-50% to +100%) and OCF Scoring for monotonic fairness."""

    def test_sales_growth_monotonicity(self):
        """Verify scores across full spectrum (-50% to +100% growth) are monotonically non-decreasing."""
        growth_rates = [-0.50, -0.20, -0.10, -0.05, -0.001, 0.0, 0.02, 0.05, 0.08, 0.12, 0.15, 0.20, 0.30, 0.50, 1.00]
        prev_score = -1.0
        for g in growth_rates:
            ev = PillarEvaluator({"info": {"revenueGrowth": g}})
            res = ev._eval_sales_growth()
            score = res["score"]
            self.assertTrue(0.0 <= score <= 100.0, f"Score {score} out of [0, 100]")
            self.assertGreaterEqual(score, prev_score, f"Monotonicity violation at growth {g*100}%: score {score} < prev {prev_score}")
            prev_score = score

    def test_ocf_quality_matrix(self):
        """Verify all branches of OCF quality matrix (NI vs OCF) behave predictably and stay within [0, 100]."""
        test_cases = [
            (1000.0, 1500.0, 500.0, 100.0, 80.0),
            (1000.0, 950.0, 200.0, 90.0, 75.0),
            (1000.0, 600.0, -100.0, 60.0, 40.0),
            (1000.0, 200.0, -500.0, 30.0, 5.0),
            (1000.0, -200.0, -500.0, 20.0, 0.0),
            (-500.0, 200.0, 100.0, 60.0, 30.0),
            (-500.0, -500.0, -800.0, 10.0, 0.0),
            (0.0, 0.0, None, 50.0, 0.0),
        ]

        for ni, ocf, fcf, exp_max, exp_min in test_cases:
            info = {"netIncome": ni, "operatingCashflow": ocf}
            if fcf is not None:
                info["freeCashflow"] = fcf
            ev = PillarEvaluator({"info": info})
            res = ev._eval_ocf_quality()
            score = res["score"]
            self.assertTrue(0.0 <= score <= 100.0, f"OCF score {score} out of [0, 100] for NI={ni}, OCF={ocf}")
            self.assertTrue(exp_min <= score <= exp_max, f"OCF score {score} outside [{exp_min}, {exp_max}] for NI={ni}, OCF={ocf}")

if __name__ == "__main__":
    unittest.main()
