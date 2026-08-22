"""
Configuration parameters for the 6-Pillar Stock Screener & AI Investment Agent.
Institutional-grade benchmarks for capital preservation and asymmetric alpha.
"""

# Minimum composite conviction score required to recommend an investment
CONVICTION_THRESHOLD = 78.0  # 78% as specified by user

# Pillar Weights in Composite Score Calculation (Total = 1.0)
PILLAR_WEIGHTS = {
    "volume_momentum": 0.15,
    "sales_growth": 0.20,
    "ocf_quality": 0.25,
    "debt_solvency": 0.15,
    "pricing_power": 0.15,
    "skin_in_game": 0.10,
}

# Benchmarks for Pillar 1: Volume & Demand Growth
VOLUME_MOMENTUM_RULES = {
    "min_volume_sma_ratio": 1.0,  # Volume > 50-day average
    "min_quarterly_rev_growth": 0.08,  # 8% YoY revenue/volume proxy
    "strong_rev_growth": 0.15,  # 15%+ YoY
}

# Benchmarks for Pillar 2: Sales Revenue Growth (Topline)
SALES_GROWTH_RULES = {
    "min_3y_cagr": 0.10,  # 10% 3-Year Sales CAGR minimum
    "strong_3y_cagr": 0.15,  # 15%+ 3-Year Sales CAGR strong
    "min_quarterly_growth": 0.08,  # 8% YoY latest quarter
}

# Benchmarks for Pillar 3: Operating Cash Flow (OCF) Quality
OCF_RULES = {
    "min_ocf_to_net_income": 0.80,  # OCF should be at least 80% of Net Income
    "strong_ocf_to_net_income": 1.05,  # OCF > Net Income indicates elite accounting quality
    "require_positive_fcf": True,  # Free cash flow (OCF - CapEx) > 0
}

# Benchmarks for Pillar 4: Debt & Solvency Health
DEBT_RULES = {
    "max_debt_to_equity": 0.60,  # D/E < 0.6 is healthy
    "hard_max_debt_to_equity": 1.50,  # D/E > 1.5 triggers penalty
    "min_interest_coverage": 4.0,  # EBIT / Interest > 4.0x
    "strong_interest_coverage": 8.0,  # 8x+ is bulletproof
    "min_current_ratio": 1.2,
}

# Benchmarks for Pillar 5: Pricing Power (Moat & Margins)
PRICING_POWER_RULES = {
    "min_gross_margin": 0.25,  # 25% minimum gross margin
    "strong_gross_margin": 0.45,  # 45%+ strong pricing leverage
    "min_roce_roe": 0.14,  # 14% ROCE / ROE minimum
    "strong_roce_roe": 0.20,  # 20%+ compounding machine
}

# Benchmarks for Pillar 6: Promoter / Insider Skin in the Game
SKIN_IN_GAME_RULES = {
    "min_promoter_holding_india": 0.40,  # 40%+ promoter holding in India
    "strong_promoter_holding_india": 0.55,  # 55%+
    "max_pledged_percentage": 0.05,  # Pledged shares must be < 5%
    "hard_max_pledged_percentage": 0.15,  # > 15% triggers instant red flag
    "min_insider_inst_us": 0.50,  # Combined insider + institutional ownership in US > 50%
}

# Benchmark Indices for Backtesting
BENCHMARKS = {
    "INDIA": "^NSEI",  # Nifty 50
    "US": "^GSPC",     # S&P 500
    "GLOBAL": "^IXIC"  # Nasdaq
}
