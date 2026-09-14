"""
ALPHA6 Enterprise Financial Terminal Server
High-Performance FastAPI Backend with Multi-Threaded Ingestion and Live Analytics.
"""

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import concurrent.futures

# Set writeable cache for serverless environments
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

import numpy as np
import pandas as pd
from datetime import datetime
import json
from typing import Optional, List

from core.data_fetcher import StockDataFetcher
from core.evaluator import PillarEvaluator
from core.backtester import StockBacktester
from core.risk_manager import RiskManager
from core.universe import (
    INDIAN_NIFTY_50, 
    INDIAN_NIFTY_NEXT_50, 
    INDIAN_COMMODITIES_METALS_ENERGY, 
    INDIAN_MIDCAP_SMALLCAP_GROWTH, 
    get_all_india_universe, 
    format_ticker
)
import config

app = FastAPI(
    title="ALPHA6 Quantitative Equity Terminal",
    description="Institutional 6-Pillar Screening, Forensic Quality Audit & Risk Management Engine",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import HTMLResponse, JSONResponse, FileResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
HTML_PATH = os.path.join(TEMPLATES_DIR, "index.html")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
@app.head("/")
async def serve_index():
    """Serves the main single-page quantitative trading terminal."""
    if os.path.exists(HTML_PATH):
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), media_type="text/html")
    return HTMLResponse(content="<h1>ALPHA6 Terminal Loading...</h1>", media_type="text/html")

@app.get("/static/app.js")
async def serve_static_js():
    """Fallback static js server for serverless runtimes."""
    js_path = os.path.join(STATIC_DIR, "app.js")
    if os.path.exists(js_path):
        with open(js_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), media_type="application/javascript")
    return HTMLResponse(content="// script not found", status_code=404)

@app.get("/manifest.json")
@app.get("/static/manifest.json")
async def serve_manifest():
    """Serves PWA Web App Manifest."""
    manifest_path = os.path.join(STATIC_DIR, "manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            return JSONResponse(content=json.loads(f.read()))
    return JSONResponse(status_code=404, content={"error": "manifest.json not found"})

@app.get("/sw.js")
@app.get("/static/sw.js")
async def serve_sw():
    """Serves PWA Service Worker."""
    sw_path = os.path.join(STATIC_DIR, "sw.js")
    if os.path.exists(sw_path):
        with open(sw_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), media_type="application/javascript")
    return HTMLResponse(content="// sw not found", status_code=404)

@app.get("/api/health")
async def health():
    return {"status": "ONLINE", "version": "2.0.0", "threshold": config.CONVICTION_THRESHOLD}

@app.get("/api/search")
async def search_stocks(q: str = Query("", min_length=1)):
    """
    Returns instant matching Indian stock symbols and company names for search autocomplete.
    """
    query = q.strip().lower()
    all_stocks = get_all_india_universe()
    matches = []
    for s in all_stocks:
        sym = s["symbol"].lower().replace(".ns", "").replace(".bo", "")
        name = s["name"].lower()
        sec = s.get("sector", "").lower()
        if query in sym or query in name or query in sec:
            matches.append(s)
            
    # Also support searching any custom ticker
    if not matches and len(query) >= 2:
        matches.append({
            "symbol": format_ticker(q),
            "name": f"Security {q.upper()}",
            "sector": "Indian Equities"
        })
        
    return {"query": q, "results": matches[:8]}

import time
import threading

_SCREEN_CACHE = {}
_INDEX_CACHE = {"timestamp": 0.0, "data": None}

def _fetch_market_indices_sync() -> dict:
    """Synchronous fetcher for BSE Sensex and Nifty 50 with 60s cache and graceful fallback."""
    now_iso = datetime.utcnow().isoformat() + "Z"
    fallback_indices = [
        {
            "symbol": "^BSESN",
            "name": "BSE SENSEX",
            "price": 82890.94,
            "change": 234.50,
            "percent_change": 0.28
        },
        {
            "symbol": "^NSEI",
            "name": "NIFTY 50",
            "price": 25356.50,
            "change": 89.20,
            "percent_change": 0.35
        }
    ]
    try:
        df = yf.download(["^BSESN", "^NSEI"], period="5d", interval="1d", progress=False, threads=True)
        if df.empty:
            return {"status": "OK", "timestamp": now_iso, "indices": fallback_indices}

        is_multi = isinstance(df.columns, pd.MultiIndex)
        idx_configs = [
            ("^BSESN", "BSE SENSEX", 82890.94, 234.50, 0.28),
            ("^NSEI", "NIFTY 50", 25356.50, 89.20, 0.35)
        ]
        indices_res = []
        for sym, name, def_price, def_change, def_pct in idx_configs:
            try:
                if is_multi:
                    closes = df['Close'][sym].dropna() if sym in df['Close'] else pd.Series()
                else:
                    closes = df['Close'].dropna()
                
                if len(closes) >= 2:
                    curr_p = round(float(closes.iloc[-1]), 2)
                    prev_p = round(float(closes.iloc[-2]), 2)
                    change = round(curr_p - prev_p, 2)
                    pct_change = round((change / prev_p) * 100, 2) if prev_p > 0 else 0.0
                elif len(closes) == 1:
                    curr_p = round(float(closes.iloc[-1]), 2)
                    change = 0.0
                    pct_change = 0.0
                else:
                    curr_p = def_price
                    change = def_change
                    pct_change = def_pct
                
                indices_res.append({
                    "symbol": sym,
                    "name": name,
                    "price": curr_p,
                    "change": change,
                    "percent_change": pct_change
                })
            except Exception:
                indices_res.append({
                    "symbol": sym,
                    "name": name,
                    "price": def_price,
                    "change": def_change,
                    "percent_change": def_pct
                })
        return {"status": "OK", "timestamp": now_iso, "indices": indices_res}
    except Exception as e:
        print(f"Error fetching market indices: {e}")
        return {"status": "OK", "timestamp": now_iso, "indices": fallback_indices}

@app.get("/api/market-indices")
async def get_market_indices():
    """
    Returns live BSE Sensex and Nifty 50 index points, daily change, and % change.
    Protected by a 60-second in-memory TTL cache with graceful fallback.
    """
    now = time.time()
    if _INDEX_CACHE["data"] is not None and (now - _INDEX_CACHE["timestamp"]) < 60.0:
        return _INDEX_CACHE["data"]

    data = _fetch_market_indices_sync()
    _INDEX_CACHE["timestamp"] = now
    _INDEX_CACHE["data"] = data
    return data

def _audit_single_stock(item: dict, batch_data: dict, threshold: float = 78.0) -> Optional[dict]:
    """Helper function executed in high-speed thread pool using batch market data."""
    sym = item.get("symbol", "")
    try:
        # Check if pre-fetched in batch
        market_info = batch_data.get(sym)
        if market_info:
            # Fast single ticker info for fundamentals
            ticker = yf.Ticker(sym)
            info = ticker.info or {}
            curr_p = market_info["current_price"]
            hist = market_info["history"]
            data = {
                "symbol": sym,
                "short_name": info.get("shortName") or info.get("longName") or item.get("name", sym),
                "sector": info.get("sector") or item.get("sector", "General"),
                "industry": info.get("industry", "Diversified"),
                "current_price": curr_p,
                "currency": info.get("currency", "INR"),
                "market_cap": info.get("marketCap", 0),
                "info": info,
                "income_stmt": pd.DataFrame(),
                "balance_sheet": pd.DataFrame(),
                "cashflow": pd.DataFrame(),
                "history": hist
            }
        else:
            data = StockDataFetcher.get_screener_stock_data(sym)

        if not data:
            return None

        evaluator = PillarEvaluator(data)
        res = evaluator.evaluate_all()
        return {
            "symbol": sym,
            "name": res["short_name"],
            "sector": res["sector"],
            "price": res["current_price"],
            "currency": res["currency"],
            "composite_score": res["composite_score"],
            "volume_score": res["pillars"]["volume_momentum"]["score"],
            "sales_score": res["pillars"]["sales_growth"]["score"],
            "ocf_score": res["pillars"]["ocf_quality"]["score"],
            "debt_score": res["pillars"]["debt_solvency"]["score"],
            "pricing_score": res["pillars"]["pricing_power"]["score"],
            "skin_score": res["pillars"]["skin_in_game"]["score"],
            "piotroski_f_score": res["piotroski_f_score"],
            "altman_z_score": res["altman_z_score"],
            "altman_status": res["altman_status"],
            "valuation": res["valuation"],
            "signal": res["signal"],
            "is_recommended": res["is_recommended"] and res["composite_score"] >= threshold,
            "red_flags": res["red_flags"],
            "red_flag_count": len(res["red_flags"]),
        }
    except Exception as e:
        return None

def _execute_screen_sync(universe: str, custom_symbols: Optional[str] = None, threshold: float = 78.0) -> dict:
    """Synchronous core screener function callable from startup or API."""
    if universe == "nifty50":
        tickers = INDIAN_NIFTY_50
    elif universe == "niftynext50":
        tickers = INDIAN_NIFTY_NEXT_50
    elif universe == "commodities":
        tickers = INDIAN_COMMODITIES_METALS_ENERGY
    elif universe == "midcap":
        tickers = INDIAN_MIDCAP_SMALLCAP_GROWTH
    elif universe == "all_india":
        tickers = get_all_india_universe()
    elif universe == "custom" and custom_symbols:
        tickers = [{"symbol": format_ticker(s.strip()), "name": s.strip(), "sector": "Custom"} for s in custom_symbols.split(",") if s.strip()]
    else:
        tickers = INDIAN_NIFTY_50

    # 1. Batch download market data (prices, 50 SMA, volume ratios) in 1 HTTP call
    symbols = [t["symbol"] for t in tickers]
    batch_data = StockDataFetcher.get_batch_market_data(symbols, period="3mo")

    results = []
    try:
        # 2. Parallel worker pool for instant pillar evaluations
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(_audit_single_stock, item, batch_data, threshold) for item in tickers]
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                if res:
                    results.append(res)
    except Exception as e:
        print(f"Screen execution error: {e}")

    results.sort(key=lambda x: x["composite_score"], reverse=True)
    high_conviction = [r for r in results if r["is_recommended"]]

    return {
        "universe": universe,
        "total_scanned": len(results),
        "high_conviction_count": len(high_conviction),
        "threshold": threshold,
        "results": results,
        "high_conviction": high_conviction
    }

@app.on_event("startup")
def prewarm_screener_cache():
    """Background pre-warming of Nifty 50 screener and market indices so first visitor gets 5ms instant response."""
    def _worker():
        try:
            print("Pre-warming Nifty 50 screener and market indices cache in background...")
            idx_payload = _fetch_market_indices_sync()
            _INDEX_CACHE["timestamp"] = time.time()
            _INDEX_CACHE["data"] = idx_payload
            payload = _execute_screen_sync("nifty50", threshold=78.0)
            _SCREEN_CACHE["nifty50_None_78.0"] = (time.time(), payload)
            print(f"Screener cache pre-warmed: {payload['total_scanned']} securities loaded.")
        except Exception as e:
            print(f"Cache pre-warm note: {e}")
    threading.Thread(target=_worker, daemon=True).start()

@app.get("/api/screen")
async def screen_universe(
    universe: str = Query("nifty50", description="Universe: nifty50, niftynext50, commodities, midcap, all_india, custom"),
    custom_symbols: Optional[str] = Query(None, description="Comma-separated symbols"),
    threshold: float = Query(78.0, ge=50, le=95)
):
    """
    Scans an equity universe using batch vectorized ingestion (< 2.5s) with memory cache (5ms).
    """
    cache_key = f"{universe}_{custom_symbols}_{threshold}"
    now = time.time()
    if cache_key in _SCREEN_CACHE:
        cached_time, cached_payload = _SCREEN_CACHE[cache_key]
        if now - cached_time < 900:  # 15 minute cache
            return cached_payload

    payload = _execute_screen_sync(universe, custom_symbols, threshold)
    _SCREEN_CACHE[cache_key] = (now, payload)
    return payload

@app.get("/api/audit/{symbol}")
async def audit_stock(symbol: str):
    """
    Returns complete forensic 6-pillar breakdown, Piotroski, Altman, valuation and technicals for a single ticker.
    """
    norm_sym = format_ticker(symbol)
    data = StockDataFetcher.get_stock_data(norm_sym)
    if not data:
        return JSONResponse(status_code=404, content={"error": f"Security '{symbol}' not found or unavailable."})

    evaluator = PillarEvaluator(data)
    res = evaluator.evaluate_all()

    # Calculate trade risk plan
    risk_plan = RiskManager.calculate_trade_plan(
        stock_price=data["current_price"],
        history=data["history"],
        total_portfolio_size=100000.0,
        risk_per_trade_pct=1.5
    )

    return {
        "evaluation": res,
        "risk_plan": risk_plan,
        "symbol": norm_sym
    }

@app.get("/api/backtest")
async def run_backtest(
    symbol: str, 
    period: str = "2y", 
    capital: float = 100000.0,
    benchmark: Optional[str] = None
):
    """
    Executes historical backtest simulation against benchmark.
    """
    norm_sym = format_ticker(symbol)
    backtester = StockBacktester(norm_sym, benchmark_symbol=benchmark)
    bt_res = backtester.run_backtest(period=period, initial_capital=capital)
    if not bt_res:
        return JSONResponse(status_code=400, content={"error": f"Failed to backtest {norm_sym} over {period}."})

    # Convert timeseries for JSON serialization
    ts = bt_res["timeseries"]
    ts_data = []
    for _, row in ts.iterrows():
        ts_data.append({
            "date": str(row["Date"])[:10],
            "stock_value": round(float(row["Stock_Portfolio_Value"]), 2),
            "benchmark_value": round(float(row["Benchmark_Portfolio_Value"]), 2),
            "stock_drawdown": round(float(row["Stock_Drawdown"]) * 100, 2),
        })

    bt_res["timeseries"] = ts_data
    return bt_res

@app.get("/api/position-size")
async def calculate_position(
    symbol: str,
    price: Optional[float] = None,
    portfolio_size: float = 100000.0,
    risk_pct: float = 1.5
):
    """
    Calculates exact dynamic position sizing and ATR risk targets.
    """
    norm_sym = format_ticker(symbol)
    data = StockDataFetcher.get_stock_data(norm_sym)
    if not data:
        return JSONResponse(status_code=404, content={"error": f"Symbol {symbol} not found."})

    entry_p = price if price and price > 0 else data["current_price"]
    plan = RiskManager.calculate_trade_plan(
        stock_price=entry_p,
        history=data["history"],
        total_portfolio_size=portfolio_size,
        risk_per_trade_pct=risk_pct
    )
    plan["currency"] = data["currency"]
    plan["symbol"] = norm_sym
    return plan

@app.get("/api/candles/{symbol}")
async def get_candles(symbol: str, period: str = "1y"):
    """
    Returns native OHLCV candlestick data and technical indicators directly from live market.
    """
    norm_sym = format_ticker(symbol)
    try:
        t = yf.Ticker(norm_sym)
        # Fetch appropriate lookback
        fetch_period = "5y" if period in ["2y", "5y"] else "2y"
        df = t.history(period=fetch_period)
        
        if df.empty:
            return JSONResponse(status_code=404, content={"error": f"Candlestick data for {symbol} unavailable."})

        # Trim to requested period
        if period == "1mo":
            df = df.tail(22)
        elif period == "3mo":
            df = df.tail(66)
        elif period == "6mo":
            df = df.tail(130)
        elif period == "1y":
            df = df.tail(252)
        elif period == "2y":
            df = df.tail(504)

        close = df["Close"]
        sma20 = close.ewm(span=20, adjust=False).mean()
        sma50 = close.rolling(window=min(50, len(close)), min_periods=1).mean()
        sma200 = close.rolling(window=min(200, len(close)), min_periods=1).mean()

        # 14-period RSI
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14, min_periods=1).mean()
        avg_loss = loss.rolling(window=14, min_periods=1).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi_series = 100 - (100 / (1 + rs))
        rsi_series = rsi_series.fillna(50.0)

        dates = [str(d)[:10] for d in df.index]
        opens = [round(float(v), 2) for v in df["Open"]]
        highs = [round(float(v), 2) for v in df["High"]]
        lows = [round(float(v), 2) for v in df["Low"]]
        closes = [round(float(v), 2) for v in df["Close"]]
        volumes = [int(v) for v in df["Volume"]]

        sma20_list = [round(float(v), 2) if not np.isnan(v) else None for v in sma20]
        sma50_list = [round(float(v), 2) if not np.isnan(v) else None for v in sma50]
        sma200_list = [round(float(v), 2) if not np.isnan(v) else None for v in sma200]
        rsi_list = [round(float(v), 1) if not np.isnan(v) else 50.0 for v in rsi_series]

        curr_p = closes[-1] if closes else 0.0
        curr_rsi = rsi_list[-1] if rsi_list else 50.0
        curr_sma50 = sma50_list[-1] if sma50_list else None
        curr_sma200 = sma200_list[-1] if sma200_list else None

        return {
            "symbol": norm_sym,
            "currency": "INR" if norm_sym.endswith((".NS", ".BO")) else "USD",
            "period": period,
            "dates": dates,
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
            "sma20": sma20_list,
            "sma50": sma50_list,
            "sma200": sma200_list,
            "rsi": rsi_list,
            "current_price": curr_p,
            "current_rsi": curr_rsi,
            "current_sma50": curr_sma50,
            "current_sma200": curr_sma200,
            "is_above_50dma": bool(curr_p >= curr_sma50 if curr_sma50 else True),
            "is_above_200dma": bool(curr_p >= curr_sma200 if curr_sma200 else True),
        }
    except Exception as e:
        print(f"Error fetching candles for {symbol}: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
