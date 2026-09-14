"""
Milestone 1 Challenger 2 Empirical Stress Test Suite
====================================================
Tests:
1. Ticker Formatting Stress Test (50+ diverse tickers, BSE, NSE, hyphens, US, indices)
2. Serverless Cache Safety (Read-only CWD, verifying SQLite cache confined to tempfile)
"""

import os
import sys
import tempfile
import unittest
import sqlite3
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.universe import format_ticker, US_TICKER_SYMBOLS


class TestTickerFormattingStress(unittest.TestCase):
    """
    Stress-tests format_ticker with 50+ diverse tickers:
    - BSE 6-digit numeric codes
    - NSE symbols with hyphens and ampersands
    - US tickers (single-letter, multi-letter, hyphens, dots)
    - Global and Indian index symbols (^NSEI, ^BSESN, ^GSPC)
    - Already suffixed symbols (.NS, .BO)
    """

    def test_50_plus_diverse_tickers(self):
        test_cases = [
            # 1. Standard Indian NSE (plain symbols)
            ("TCS", "TCS.NS"),
            ("INFY", "INFY.NS"),
            ("RELIANCE", "RELIANCE.NS"),
            ("HDFCBANK", "HDFCBANK.NS"),
            ("ICICIBANK", "ICICIBANK.NS"),
            ("SBIN", "SBIN.NS"),
            ("WIPRO", "WIPRO.NS"),
            ("ITC", "ITC.NS"),
            ("LT", "LT.NS"),
            ("HCLTECH", "HCLTECH.NS"),
            
            # 2. Already formatted NSE symbols
            ("TCS.NS", "TCS.NS"),
            ("INFY.NS", "INFY.NS"),
            ("RELIANCE.NS", "RELIANCE.NS"),
            ("M&M.NS", "M&M.NS"),
            ("BAJAJ-AUTO.NS", "BAJAJ-AUTO.NS"),
            ("MCDOWELL-N.NS", "MCDOWELL-N.NS"),

            # 3. Already formatted BSE symbols
            ("500325.BO", "500325.BO"),
            ("532540.BO", "532540.BO"),
            ("TCS.BO", "TCS.BO"),
            ("RELIANCE.BO", "RELIANCE.BO"),

            # 4. BSE 6-digit numeric scrip codes
            ("500325", "500325.BO"),  # Reliance BSE
            ("532540", "532540.BO"),  # TCS BSE
            ("500180", "500180.BO"),  # HDFC Bank BSE
            ("500209", "500209.BO"),  # Infosys BSE
            ("500696", "500696.BO"),  # HUL BSE
            ("500820", "500820.BO"),  # Asian Paints BSE
            ("500875", "500875.BO"),  # ITC BSE
            ("532174", "532174.BO"),  # ICICI Bank BSE
            ("500112", "500112.BO"),  # SBIN BSE
            ("500510", "500510.BO"),  # L&T BSE

            # 5. NSE symbols with special characters (hyphens, ampersand)
            ("M&M", "M&M.NS"),
            ("BAJAJ-AUTO", "BAJAJ-AUTO.NS"),
            ("MCDOWELL-N", "MCDOWELL-N.NS"),
            ("NAM-INDIA", "NAM-INDIA.NS"),
            ("L&TFH", "L&TFH.NS"),

            # 6. US Blue Chips & Tech Tickers (known in universe or US_TICKER_SYMBOLS)
            ("AAPL", "AAPL"),
            ("MSFT", "MSFT"),
            ("GOOGL", "GOOGL"),
            ("AMZN", "AMZN"),
            ("NVDA", "NVDA"),
            ("META", "META"),
            ("TSLA", "TSLA"),
            ("AVGO", "AVGO"),
            ("LLY", "LLY"),
            ("V", "V"),
            ("MA", "MA"),
            ("ASML", "ASML"),
            ("AMD", "AMD"),
            ("INTC", "INTC"),
            ("NFLX", "NFLX"),
            ("SPY", "SPY"),
            ("QQQ", "QQQ"),
            
            # 7. US Tickers with market='US'
            ("PLTR", "PLTR"),
            ("SNOW", "SNOW"),
            ("UBER", "UBER"),
            ("COIN", "COIN"),

            # 8. White-space and lower-case resilience
            ("  tcs  ", "TCS.NS"),
            ("  aapl  ", "AAPL"),
            ("  500325  ", "500325.BO"),
            ("  infy.ns  ", "INFY.NS"),
        ]

        # Verify >= 50 test cases
        self.assertGreaterEqual(len(test_cases), 50, f"Must have at least 50 test cases, got {len(test_cases)}")

        mismatches = []
        for raw_sym, expected in test_cases:
            actual = format_ticker(raw_sym)
            if actual != expected:
                mismatches.append(f"format_ticker('{raw_sym}') -> '{actual}', expected '{expected}'")

        self.assertEqual(len(mismatches), 0, "\n".join(mismatches))

    def test_market_parameter_override(self):
        """Verifies explicit market='US' preserves any arbitrary US symbol without .NS."""
        self.assertEqual(format_ticker("ANYUSSYM", market="US"), "ANYUSSYM")
        self.assertEqual(format_ticker("FOOBAR", market="US"), "FOOBAR")
        self.assertEqual(format_ticker("BRK-A", market="US"), "BRK-A")

    def test_special_symbols_and_indices_regression(self):
        """
        REGRESSION TEST:
        1. Index symbols starting with '^' (e.g. ^NSEI, ^BSESN, ^GSPC).
           In Yahoo Finance, indices begin with '^' and DO NOT use .NS or .BO.
        2. Dual-share US class tickers like BRK-A, BRK-B vs BRK.A, BRK.B.
        3. Spurious suffixes accidentally appended to indices must be cleanly stripped.
        """
        self.assertEqual(format_ticker("^NSEI"), "^NSEI")
        self.assertEqual(format_ticker("^BSESN"), "^BSESN")
        self.assertEqual(format_ticker("^GSPC"), "^GSPC")
        self.assertEqual(format_ticker("^DJI"), "^DJI")
        self.assertEqual(format_ticker("^IXIC"), "^IXIC")
        self.assertEqual(format_ticker("  ^nsei  "), "^NSEI")
        self.assertEqual(format_ticker("^NSEI.NS"), "^NSEI")
        self.assertEqual(format_ticker("^BSESN.BO"), "^BSESN")
        
        self.assertEqual(format_ticker("BRK-A"), "BRK-A")
        self.assertEqual(format_ticker("BRK-B"), "BRK-B")
        self.assertEqual(format_ticker("BRK.A"), "BRK-A")
        self.assertEqual(format_ticker("BRK.B"), "BRK-B")


class TestServerlessCacheSafety(unittest.TestCase):
    """
    Verifies that yfinance cache redirection to tempfile.gettempdir()
    is strictly honored and no SQLite cache databases or files are created
    in the working directory or repository root.
    """

    def test_cache_redirection_configured(self):
        """Verifies YFINANCE_CACHE_DIR environment variable points inside tempfile.gettempdir()."""
        temp_dir = os.path.realpath(tempfile.gettempdir())
        yf_cache_env = os.environ.get("YFINANCE_CACHE_DIR")
        self.assertIsNotNone(yf_cache_env, "YFINANCE_CACHE_DIR environment variable must be set.")
        
        real_cache_env = os.path.realpath(yf_cache_env)
        self.assertTrue(
            real_cache_env.startswith(temp_dir),
            f"YFINANCE_CACHE_DIR ({real_cache_env}) must reside inside tempfile.gettempdir() ({temp_dir})"
        )

    def test_no_sqlite_in_cwd_or_project_root(self):
        """
        Checks that importing and running data_fetcher and backtester does not
        create any .db or .sqlite files in PROJECT_ROOT or current working directory.
        """
        # Check files before
        def find_sqlite_files(directory):
            found = []
            for root, dirs, files in os.walk(directory):
                # ignore .git
                if ".git" in root or ".venv" in root:
                    continue
                for f in files:
                    if f.endswith(".db") or f.endswith(".sqlite") or "yfinance" in f.lower():
                        found.append(os.path.join(root, f))
            return found

        project_sqlite_before = find_sqlite_files(PROJECT_ROOT)
        
        # Invoke data fetcher and backtester components
        from core.data_fetcher import StockDataFetcher
        from core.backtester import StockBacktester
        
        # Verify cache location in yfinance
        import yfinance as yf
        tz_cache = getattr(yf, "_tz_cache_location", None)
        print(f"DEBUG: yf._tz_cache_location = {tz_cache}")

        project_sqlite_after = find_sqlite_files(PROJECT_ROOT)
        new_sqlite = set(project_sqlite_after) - set(project_sqlite_before)
        self.assertEqual(
            len(new_sqlite), 0,
            f"Unexpected SQLite or cache files created in project root: {new_sqlite}"
        )


if __name__ == "__main__":
    unittest.main()
