"""
Data Fetcher Module: Ingests fundamental and technical market data
for Indian (NSE/BSE) and Global (US/TradingView) stocks using yfinance.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class StockDataFetcher:
    """
    Fetches real-time, fundamental financial statements and historical data
    for equities across global exchanges (NSE, BSE, NYSE, NASDAQ).
    """

    @staticmethod
    def get_stock_data(ticker_symbol: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves complete dataset required for the 6-Pillar analysis.
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info or {}
            
            # Fast validation - if no price or empty info, return None
            current_price = (
                info.get("currentPrice") 
                or info.get("regularMarketPrice") 
                or info.get("previousClose")
            )
            
            if not current_price:
                # Try fetching latest price from 5d history
                hist = ticker.history(period="5d")
                if not hist.empty:
                    current_price = float(hist["Close"].iloc[-1])
                else:
                    return None

            # Financial statements
            try:
                income_stmt = ticker.financials  # Annual
                q_income_stmt = ticker.quarterly_financials  # Quarterly
            except Exception:
                income_stmt = pd.DataFrame()
                q_income_stmt = pd.DataFrame()

            try:
                balance_sheet = ticker.balance_sheet
                q_balance_sheet = ticker.quarterly_balance_sheet
            except Exception:
                balance_sheet = pd.DataFrame()
                q_balance_sheet = pd.DataFrame()

            try:
                cashflow = ticker.cashflow
                q_cashflow = ticker.quarterly_cashflow
            except Exception:
                cashflow = pd.DataFrame()
                q_cashflow = pd.DataFrame()

            # Technical history for volume, momentum, and backtesting (2 years)
            try:
                hist_2y = ticker.history(period="2y")
                if not hist_2y.empty:
                    hist_2y = hist_2y.dropna(subset=["Close", "High", "Low"])
            except Exception:
                hist_2y = pd.DataFrame()

            if not current_price and not hist_2y.empty:
                current_price = float(hist_2y["Close"].iloc[-1])

            # Ownership & Holders data
            major_holders = None
            try:
                major_holders = ticker.major_holders
            except Exception:
                pass

            return {
                "symbol": ticker_symbol,
                "info": info,
                "current_price": current_price,
                "currency": info.get("currency", "INR" if ".NS" in ticker_symbol or ".BO" in ticker_symbol else "USD"),
                "short_name": info.get("shortName") or info.get("longName") or ticker_symbol,
                "sector": info.get("sector", "General"),
                "industry": info.get("industry", "Diversified"),
                "market_cap": info.get("marketCap", 0),
                "income_stmt": income_stmt,
                "q_income_stmt": q_income_stmt,
                "balance_sheet": balance_sheet,
                "q_balance_sheet": q_balance_sheet,
                "cashflow": cashflow,
                "q_cashflow": q_cashflow,
                "history": hist_2y,
                "major_holders": major_holders,
                "fetched_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error fetching data for {ticker_symbol}: {e}")
            return None

    @staticmethod
    def get_benchmark_history(benchmark_symbol: str, period: str = "3y") -> pd.DataFrame:
        """
        Retrieves benchmark index history for backtesting comparisons (^NSEI or ^GSPC).
        """
        try:
            bm = yf.Ticker(benchmark_symbol)
            df = bm.history(period=period)
            return df
        except Exception:
            return pd.DataFrame()
