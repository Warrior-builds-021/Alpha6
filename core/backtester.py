"""
Backtesting Simulator Module:
Evaluates historical performance, risk-adjusted metrics, alpha, and drawdowns
for 6-pillar high-conviction stocks against benchmark indices (Nifty 50 or S&P 500).
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
from typing import Dict, Any, List, Optional
import config

class StockBacktester:
    """
    Simulates historical returns and calculates institutional risk metrics.
    """

    def __init__(self, ticker_symbol: str, benchmark_symbol: Optional[str] = None):
        self.symbol = ticker_symbol
        if benchmark_symbol:
            self.benchmark_symbol = benchmark_symbol
        else:
            self.benchmark_symbol = config.BENCHMARKS["INDIA"] if (".NS" in ticker_symbol or ".BO" in ticker_symbol) else config.BENCHMARKS["US"]

    def run_backtest(self, period: str = "2y", initial_capital: float = 100000.0) -> Optional[Dict[str, Any]]:
        """
        Runs backtest simulation against benchmark over specified period ('1y', '2y', '5y').
        """
        try:
            # Download stock and benchmark historical data
            stock = yf.Ticker(self.symbol)
            stock_df = stock.history(period=period)
            
            bm = yf.Ticker(self.benchmark_symbol)
            bm_df = bm.history(period=period)

            # Align timestamps across different exchange timezones (e.g. NSE Asia/Kolkata vs US America/New_York)
            stock_series = stock_df["Close"].dropna()
            bm_series = bm_df["Close"].dropna()

            # Strip timezones and normalize to date
            stock_series.index = pd.to_datetime(stock_series.index).tz_localize(None).normalize()
            bm_series.index = pd.to_datetime(bm_series.index).tz_localize(None).normalize()

            # Remove duplicate calendar dates if any
            stock_series = stock_series[~stock_series.index.duplicated(keep='last')]
            bm_series = bm_series[~bm_series.index.duplicated(keep='last')]

            # Create aligned DataFrame
            df = pd.DataFrame({
                "Stock_Close": stock_series,
                "Benchmark_Close": bm_series
            }).ffill().dropna()

            if len(df) < 15:
                return None

            # Daily Returns
            df["Stock_Return"] = df["Stock_Close"].pct_change().fillna(0)
            df["Benchmark_Return"] = df["Benchmark_Close"].pct_change().fillna(0)

            # Cumulative Multipliers
            df["Stock_Cum_Return"] = (1 + df["Stock_Return"]).cumprod()
            df["Benchmark_Cum_Return"] = (1 + df["Benchmark_Return"]).cumprod()

            # Portfolio Equity Curve
            df["Stock_Portfolio_Value"] = initial_capital * df["Stock_Cum_Return"]
            df["Benchmark_Portfolio_Value"] = initial_capital * df["Benchmark_Cum_Return"]

            # Drawdown series
            df["Stock_Peak"] = df["Stock_Portfolio_Value"].cummax()
            df["Stock_Drawdown"] = (df["Stock_Portfolio_Value"] - df["Stock_Peak"]) / df["Stock_Peak"]

            df["Benchmark_Peak"] = df["Benchmark_Portfolio_Value"].cummax()
            df["Benchmark_Drawdown"] = (df["Benchmark_Portfolio_Value"] - df["Benchmark_Peak"]) / df["Benchmark_Peak"]

            # Key Institutional Metrics
            total_days = (df.index[-1] - df.index[0]).days
            years = max(total_days / 365.25, 0.1)

            stock_total_return = (df["Stock_Cum_Return"].iloc[-1] - 1.0) * 100
            bm_total_return = (df["Benchmark_Cum_Return"].iloc[-1] - 1.0) * 100

            stock_cagr = (((df["Stock_Cum_Return"].iloc[-1]) ** (1.0 / years)) - 1.0) * 100
            bm_cagr = (((df["Benchmark_Cum_Return"].iloc[-1]) ** (1.0 / years)) - 1.0) * 100

            max_drawdown_stock = df["Stock_Drawdown"].min() * 100
            max_drawdown_bm = df["Benchmark_Drawdown"].min() * 100

            # Annualized Volatility
            stock_volatility = (df["Stock_Return"].std() * np.sqrt(252)) * 100
            bm_volatility = (df["Benchmark_Return"].std() * np.sqrt(252)) * 100

            # Sharpe Ratio (assuming 5% risk free rate)
            rf_daily = 0.05 / 252
            excess_return = df["Stock_Return"] - rf_daily
            ret_std = float(df["Stock_Return"].std())
            sharpe_ratio = float((excess_return.mean() / (ret_std + 1e-9)) * np.sqrt(252)) if ret_std > 0 else 0.0
            if np.isnan(sharpe_ratio):
                sharpe_ratio = 0.0

            # Beta & Alpha calculation
            try:
                covariance = float(np.cov(df["Stock_Return"], df["Benchmark_Return"])[0][1])
                bm_variance = float(np.var(df["Benchmark_Return"]))
                beta = covariance / bm_variance if bm_variance > 0 and not np.isnan(covariance) else 1.0
                if np.isnan(beta):
                    beta = 1.0
            except Exception:
                beta = 1.0

            alpha = stock_cagr - (5.0 + beta * (bm_cagr - 5.0))
            if np.isnan(alpha):
                alpha = 0.0

            # Win rate (% of trading days with positive returns)
            win_rate = float((df["Stock_Return"] > 0).sum() / len(df) * 100) if len(df) > 0 else 0.0

            return {
                "symbol": self.symbol,
                "benchmark_symbol": self.benchmark_symbol,
                "period": period,
                "initial_capital": initial_capital,
                "final_capital_stock": round(df["Stock_Portfolio_Value"].iloc[-1], 2),
                "final_capital_bm": round(df["Benchmark_Portfolio_Value"].iloc[-1], 2),
                "stock_total_return": round(stock_total_return, 2),
                "benchmark_total_return": round(bm_total_return, 2),
                "stock_cagr": round(stock_cagr, 2),
                "benchmark_cagr": round(bm_cagr, 2),
                "max_drawdown_stock": round(max_drawdown_stock, 2),
                "max_drawdown_bm": round(max_drawdown_bm, 2),
                "stock_volatility": round(stock_volatility, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "beta": round(beta, 2),
                "alpha": round(alpha, 2),
                "win_rate": round(win_rate, 2),
                "timeseries": df.reset_index()
            }
        except Exception as e:
            print(f"Backtest error for {self.symbol}: {e}")
            return None
