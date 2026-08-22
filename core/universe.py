"""
Universe of stocks across Indian (NSE/BSE) and Global (US/TradingView) markets.
Supports custom symbol resolution for both Indian (.NS, .BO) and US exchanges.
"""

INDIAN_NIFTY_50 = [
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy / Retail / Telecom"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "sector": "Information Technology"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "sector": "Financials / Banking"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Financials / Banking"},
    {"symbol": "INFY.NS", "name": "Infosys", "sector": "Information Technology"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel", "sector": "Telecommunications"},
    {"symbol": "ITC.NS", "name": "ITC Limited", "sector": "Consumer Goods (FMCG)"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever", "sector": "Consumer Goods (FMCG)"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro", "sector": "Engineering & Capital Goods"},
    {"symbol": "MM.NS", "name": "Mahindra & Mahindra", "sector": "Automobiles"},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharmaceutical", "sector": "Healthcare / Pharma"},
    {"symbol": "TITAN.NS", "name": "Titan Company", "sector": "Consumer Discretionary"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance", "sector": "Financial Services (NBFC)"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki", "sector": "Automobiles"},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints", "sector": "Consumer Paints"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies", "sector": "Information Technology"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "sector": "Financials / Banking"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank", "sector": "Financials / Banking"},
    {"symbol": "NTPC.NS", "name": "NTPC Limited", "sector": "Utilities / Power"},
    {"symbol": "ONGC.NS", "name": "Oil & Natural Gas Corp", "sector": "Energy"},
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement", "sector": "Materials / Cement"},
    {"symbol": "COALINDIA.NS", "name": "Coal India", "sector": "Energy / Mining"},
    {"symbol": "NESTLEIND.NS", "name": "Nestle India", "sector": "Consumer Goods (FMCG)"},
    {"symbol": "WIPRO.NS", "name": "Wipro", "sector": "Information Technology"},
    {"symbol": "POWERGRID.NS", "name": "Power Grid Corp", "sector": "Utilities / Power"},
]

INDIAN_QUALITY_GROWTH = [
    {"symbol": "HAL.NS", "name": "Hindustan Aeronautics", "sector": "Defense & Aerospace"},
    {"symbol": "BEL.NS", "name": "Bharat Electronics", "sector": "Defense Electronics"},
    {"symbol": "TRENT.NS", "name": "Trent Limited", "sector": "Retail (Tata Group)"},
    {"symbol": "VARUN.NS", "name": "Varun Beverages", "sector": "Consumer / Beverages"},
    {"symbol": "POLYCAB.NS", "name": "Polycab India", "sector": "Cables & Electricals"},
    {"symbol": "DIXON.NS", "name": "Dixon Technologies", "sector": "Electronics Manufacturing"},
    {"symbol": "SOLARINDS.NS", "name": "Solar Industries", "sector": "Industrial Explosives"},
    {"symbol": "KPITTECH.NS", "name": "KPIT Technologies", "sector": "Automotive Software"},
    {"symbol": "CHOLAFIN.NS", "name": "Cholamandalam Investment", "sector": "Financial Services"},
    {"symbol": "PERSISTENT.NS", "name": "Persistent Systems", "sector": "Information Technology"},
]

GLOBAL_US_MEGA_TECH = [
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Semiconductors & AI"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Cloud & Enterprise Software"},
    {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Consumer Tech & Ecosystem"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Search, Advertising & Cloud"},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "E-Commerce & AWS Cloud"},
    {"symbol": "META", "name": "Meta Platforms", "sector": "Social Media & AI"},
    {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "EVs, Energy & Robotics"},
    {"symbol": "AVGO", "name": "Broadcom Inc.", "sector": "Semiconductors & Infrastructure"},
    {"symbol": "LLY", "name": "Eli Lilly and Company", "sector": "Pharmaceuticals & Healthcare"},
    {"symbol": "V", "name": "Visa Inc.", "sector": "Payment Networks & Fintech"},
    {"symbol": "MA", "name": "Mastercard Inc.", "sector": "Payment Networks & Fintech"},
    {"symbol": "ASML", "name": "ASML Holding", "sector": "Semiconductor Lithography"},
]

def format_ticker(symbol: str, market: str = "AUTO") -> str:
    """
    Normalizes ticker symbols for Indian vs Global markets.
    TradingView / NSE inputs like 'RELIANCE', 'TCS' -> 'RELIANCE.NS'
    BSE inputs like '500325' -> '500325.BO'
    US inputs like 'AAPL', 'NVDA' -> 'AAPL', 'NVDA'
    """
    clean_sym = symbol.strip().upper()
    if clean_sym.endswith(".NS") or clean_sym.endswith(".BO"):
        return clean_sym
    
    if market == "INDIA" or (market == "AUTO" and any(s["symbol"].startswith(clean_sym + ".") for s in INDIAN_NIFTY_50 + INDIAN_QUALITY_GROWTH)):
        return f"{clean_sym}.NS"
        
    return clean_sym
