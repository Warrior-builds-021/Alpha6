"""
Core 6-Pillar Stock Screener and Investment Agent Package.
"""
from .data_fetcher import StockDataFetcher
from .evaluator import PillarEvaluator
from .backtester import StockBacktester
from .risk_manager import RiskManager
from .universe import (
    INDIAN_NIFTY_50,
    INDIAN_NIFTY_NEXT_50,
    INDIAN_COMMODITIES_METALS_ENERGY,
    INDIAN_MIDCAP_SMALLCAP_GROWTH,
    INDIAN_QUALITY_GROWTH,
    GLOBAL_US_MEGA_TECH,
    get_all_india_universe,
    format_ticker
)

__all__ = [
    "StockDataFetcher",
    "PillarEvaluator",
    "StockBacktester",
    "RiskManager",
    "INDIAN_NIFTY_50",
    "INDIAN_NIFTY_NEXT_50",
    "INDIAN_COMMODITIES_METALS_ENERGY",
    "INDIAN_MIDCAP_SMALLCAP_GROWTH",
    "INDIAN_QUALITY_GROWTH",
    "GLOBAL_US_MEGA_TECH",
    "get_all_india_universe",
    "format_ticker"
]

