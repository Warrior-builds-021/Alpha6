"""
Data Fetcher Module: Ingests fundamental and technical market data
for Indian (NSE/BSE) and Global (US/TradingView) stocks using yfinance.
"""

import os
import tempfile

# Prevent read-only filesystem errors in Serverless environments (Vercel / AWS Lambda)
try:
    _tmp_cache = os.path.join(tempfile.gettempdir(), "py-yfinance")
    os.makedirs(_tmp_cache, exist_ok=True)
    os.environ["YFINANCE_CACHE_DIR"] = _tmp_cache
    import yfinance as yf
    try:
        yf.set_tz_cache_location(_tmp_cache)
    except Exception:
        pass
except Exception:
    import yfinance as yf

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

class StockDataFetcher:
    """
    Fetches real-time, fundamental financial statements and historical data
    for equities across global exchanges (NSE, BSE, NYSE, NASDAQ).
    """

    @staticmethod
    def get_batch_market_data(symbols: List[str], period: str = "3mo") -> Dict[str, Dict[str, Any]]:
        """
        High-performance vectorized batch market data downloader.
        Downloads prices, volumes, and moving averages for an entire universe in ONE HTTP roundtrip.
        """
        if not symbols:
            return {}
        try:
            df = yf.download(symbols, period=period, progress=False, threads=False)
            if df.empty:
                return {}

            results = {}
            is_multi = isinstance(df.columns, pd.MultiIndex)

            for sym in symbols:
                try:
                    if is_multi:
                        closes = df['Close'][sym].dropna() if sym in df['Close'] else pd.Series()
                        vols = df['Volume'][sym].dropna() if sym in df['Volume'] else pd.Series()
                    else:
                        closes = df['Close'].dropna()
                        vols = df['Volume'].dropna()

                    if len(closes) > 0:
                        curr_p = float(closes.iloc[-1])
                        sma50 = float(closes.tail(50).mean()) if len(closes) >= 10 else curr_p
                        avg_vol50 = float(vols.tail(50).mean()) if len(vols) >= 10 else 1.0
                        recent_vol = float(vols.tail(5).mean()) if len(vols) >= 5 else (float(vols.iloc[-1]) if len(vols) > 0 else 1.0)
                        vol_ratio = round(recent_vol / avg_vol50, 2) if avg_vol50 > 0 else 1.0

                        # Create synthetic history dataframe for downstream technical analysis
                        hist_df = pd.DataFrame({'Close': closes, 'Volume': vols})

                        results[sym] = {
                            "current_price": round(curr_p, 2),
                            "sma50": round(sma50, 2),
                            "price_above_sma50": curr_p >= sma50,
                            "vol_ratio": vol_ratio,
                            "history": hist_df
                        }
                except Exception:
                    continue

            return results
        except Exception as e:
            print(f"Batch market data error: {e}")
            return {}

    @staticmethod
    def get_screener_stock_data(ticker_symbol: str) -> Optional[Dict[str, Any]]:
        """
        Ultra-fast single-roundtrip data fetcher designed specifically for parallel index screening (< 150ms).
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info or {}
            
            current_price = (
                info.get("currentPrice") 
                or info.get("regularMarketPrice") 
                or info.get("previousClose")
            )
            
            hist = ticker.history(period="3mo")
            if not current_price and not hist.empty:
                current_price = float(hist["Close"].iloc[-1])
            elif not current_price:
                return None

            return {
                "symbol": ticker_symbol,
                "short_name": info.get("shortName") or info.get("longName") or ticker_symbol,
                "sector": info.get("sector", "General"),
                "industry": info.get("industry", "Diversified"),
                "current_price": float(current_price),
                "currency": info.get("currency", "INR"),
                "market_cap": info.get("marketCap", 0),
                "info": info,
                "income_stmt": pd.DataFrame(),
                "balance_sheet": pd.DataFrame(),
                "cashflow": pd.DataFrame(),
                "history": hist
            }
        except Exception:
            return None

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
