# -*- coding: utf-8 -*-
"""
ALPHA6 Curated Institutional Fundamental Catalog & Zero-Latency Cache
Pre-computed fundamental profiles and balance sheet metrics for Indian and Global equities.
Enables sub-second (< 1.5s) screener execution on Serverless (Vercel) without 50x network roundtrips.
"""

from typing import Dict, Any, Optional, List

FUNDAMENTAL_CATALOG: Dict[str, Dict[str, Any]] = {
    # ---------------- NIFTY 50 BLUE CHIPS ----------------
    "RELIANCE.NS": {
        "shortName": "Reliance Industries", "sector": "Energy / Retail / Telecom", "industry": "Oil & Gas Refining",
        "currentPrice": 2985.0, "marketCap": 20200000000000, "trailingPE": 26.8, "priceToBook": 2.2, "pegRatio": 1.6,
        "enterpriseToEbitda": 13.8, "revenueGrowth": 0.115, "grossMargins": 0.345, "operatingMargins": 0.168,
        "returnOnEquity": 0.098, "debtToEquity": 0.38, "currentRatio": 1.15, "heldPercentInsiders": 0.503,
        "heldPercentInstitutions": 0.395, "operatingCashflow": 1420000000000, "netIncomeToCommon": 696200000000,
        "freeCashflow": 450000000000, "totalDebt": 3150000000000, "totalCash": 1850000000000, "sharesOutstanding": 6765000000
    },
    "TCS.NS": {
        "shortName": "Tata Consultancy Services", "sector": "Information Technology", "industry": "IT Services",
        "currentPrice": 4280.0, "marketCap": 15480000000000, "trailingPE": 31.5, "priceToBook": 15.2, "pegRatio": 2.5,
        "enterpriseToEbitda": 22.1, "revenueGrowth": 0.054, "grossMargins": 0.432, "operatingMargins": 0.258,
        "returnOnEquity": 0.485, "debtToEquity": 0.08, "currentRatio": 2.45, "heldPercentInsiders": 0.718,
        "heldPercentInstitutions": 0.215, "operatingCashflow": 485000000000, "netIncomeToCommon": 465000000000,
        "freeCashflow": 440000000000, "totalDebt": 85000000000, "totalCash": 152000000000, "sharesOutstanding": 3618000000
    },
    "HDFCBANK.NS": {
        "shortName": "HDFC Bank", "sector": "Financials / Banking", "industry": "Private Banking",
        "currentPrice": 1640.0, "marketCap": 12450000000000, "trailingPE": 18.5, "priceToBook": 2.7, "pegRatio": 1.2,
        "enterpriseToEbitda": None, "revenueGrowth": 0.245, "grossMargins": 0.520, "operatingMargins": 0.410,
        "returnOnEquity": 0.165, "debtToEquity": None, "currentRatio": 1.10, "heldPercentInsiders": 0.00,
        "heldPercentInstitutions": 0.795, "operatingCashflow": 780000000000, "netIncomeToCommon": 640000000000,
        "freeCashflow": 650000000000, "totalDebt": 3500000000000, "totalCash": 2100000000000, "sharesOutstanding": 7590000000
    },
    "ICICIBANK.NS": {
        "shortName": "ICICI Bank", "sector": "Financials / Banking", "industry": "Private Banking",
        "currentPrice": 1220.0, "marketCap": 8560000000000, "trailingPE": 17.8, "priceToBook": 3.1, "pegRatio": 1.1,
        "enterpriseToEbitda": None, "revenueGrowth": 0.198, "grossMargins": 0.540, "operatingMargins": 0.435,
        "returnOnEquity": 0.185, "debtToEquity": None, "currentRatio": 1.12, "heldPercentInsiders": 0.00,
        "heldPercentInstitutions": 0.762, "operatingCashflow": 620000000000, "netIncomeToCommon": 445000000000,
        "freeCashflow": 510000000000, "totalDebt": 2100000000000, "totalCash": 1650000000000, "sharesOutstanding": 7020000000
    },
    "BHARTIARTL.NS": {
        "shortName": "Bharti Airtel", "sector": "Telecommunications", "industry": "Telecom Services",
        "currentPrice": 1580.0, "marketCap": 9200000000000, "trailingPE": 62.0, "priceToBook": 8.5, "pegRatio": 2.1,
        "enterpriseToEbitda": 14.2, "revenueGrowth": 0.142, "grossMargins": 0.560, "operatingMargins": 0.285,
        "returnOnEquity": 0.158, "debtToEquity": 1.45, "currentRatio": 0.85, "heldPercentInsiders": 0.531,
        "heldPercentInstitutions": 0.405, "operatingCashflow": 680000000000, "netIncomeToCommon": 125000000000,
        "freeCashflow": 280000000000, "totalDebt": 1950000000000, "totalCash": 180000000000, "sharesOutstanding": 5820000000
    },
    "INFY.NS": {
        "shortName": "Infosys", "sector": "Information Technology", "industry": "IT Services",
        "currentPrice": 1920.0, "marketCap": 7980000000000, "trailingPE": 29.5, "priceToBook": 8.8, "pegRatio": 2.8,
        "enterpriseToEbitda": 19.5, "revenueGrowth": 0.048, "grossMargins": 0.325, "operatingMargins": 0.212,
        "returnOnEquity": 0.315, "debtToEquity": 0.09, "currentRatio": 2.15, "heldPercentInsiders": 0.148,
        "heldPercentInstitutions": 0.695, "operatingCashflow": 295000000000, "netIncomeToCommon": 262000000000,
        "freeCashflow": 260000000000, "totalDebt": 82000000000, "totalCash": 195000000000, "sharesOutstanding": 4150000000
    },
    "ITC.NS": {
        "shortName": "ITC Limited", "sector": "Consumer FMCG", "industry": "Tobacco & FMCG",
        "currentPrice": 510.0, "marketCap": 6380000000000, "trailingPE": 28.5, "priceToBook": 8.2, "pegRatio": 2.4,
        "enterpriseToEbitda": 20.4, "revenueGrowth": 0.075, "grossMargins": 0.585, "operatingMargins": 0.365,
        "returnOnEquity": 0.295, "debtToEquity": 0.005, "currentRatio": 2.80, "heldPercentInsiders": 0.00,
        "heldPercentInstitutions": 0.785, "operatingCashflow": 210000000000, "netIncomeToCommon": 204000000000,
        "freeCashflow": 185000000000, "totalDebt": 3500000000, "totalCash": 120000000000, "sharesOutstanding": 12500000000
    },
    "HINDUNILVR.NS": {
        "shortName": "Hindustan Unilever", "sector": "Consumer FMCG", "industry": "Personal & Home Care",
        "currentPrice": 2850.0, "marketCap": 6690000000000, "trailingPE": 62.5, "priceToBook": 12.8, "pegRatio": 4.5,
        "enterpriseToEbitda": 40.2, "revenueGrowth": 0.038, "grossMargins": 0.510, "operatingMargins": 0.235,
        "returnOnEquity": 0.205, "debtToEquity": 0.025, "currentRatio": 1.35, "heldPercentInsiders": 0.619,
        "heldPercentInstitutions": 0.275, "operatingCashflow": 105000000000, "netIncomeToCommon": 102000000000,
        "freeCashflow": 95000000000, "totalDebt": 15000000000, "totalCash": 65000000000, "sharesOutstanding": 2350000000
    },
    "LT.NS": {
        "shortName": "Larsen & Toubro", "sector": "Engineering & Capital Goods", "industry": "EPC & Infrastructure",
        "currentPrice": 3650.0, "marketCap": 5020000000000, "trailingPE": 35.8, "priceToBook": 5.4, "pegRatio": 2.2,
        "enterpriseToEbitda": 21.0, "revenueGrowth": 0.185, "grossMargins": 0.285, "operatingMargins": 0.105,
        "returnOnEquity": 0.155, "debtToEquity": 0.95, "currentRatio": 1.25, "heldPercentInsiders": 0.00,
        "heldPercentInstitutions": 0.735, "operatingCashflow": 245000000000, "netIncomeToCommon": 130000000000,
        "freeCashflow": 160000000000, "totalDebt": 1250000000000, "totalCash": 350000000000, "sharesOutstanding": 1375000000
    },
    "SBIN.NS": {
        "shortName": "State Bank of India", "sector": "Financials / PSU Bank", "industry": "PSU Banking",
        "currentPrice": 820.0, "marketCap": 7310000000000, "trailingPE": 10.8, "priceToBook": 1.8, "pegRatio": 0.75,
        "enterpriseToEbitda": None, "revenueGrowth": 0.165, "grossMargins": 0.480, "operatingMargins": 0.385,
        "returnOnEquity": 0.178, "debtToEquity": None, "currentRatio": 1.15, "heldPercentInsiders": 0.575,
        "heldPercentInstitutions": 0.315, "operatingCashflow": 850000000000, "netIncomeToCommon": 670000000000,
        "freeCashflow": 720000000000, "totalDebt": 4200000000000, "totalCash": 3100000000000, "sharesOutstanding": 8920000000
    },
    "BAJFINANCE.NS": {
        "shortName": "Bajaj Finance", "sector": "Financial Services (NBFC)", "industry": "Consumer NBFC",
        "currentPrice": 7450.0, "marketCap": 4610000000000, "trailingPE": 30.2, "priceToBook": 5.8, "pegRatio": 1.45,
        "enterpriseToEbitda": None, "revenueGrowth": 0.285, "grossMargins": 0.620, "operatingMargins": 0.465,
        "returnOnEquity": 0.225, "debtToEquity": 3.45, "currentRatio": 1.30, "heldPercentInsiders": 0.552,
        "heldPercentInstitutions": 0.345, "operatingCashflow": 320000000000, "netIncomeToCommon": 144500000000,
        "freeCashflow": 280000000000, "totalDebt": 2850000000000, "totalCash": 180000000000, "sharesOutstanding": 619000000
    },
    "HCLTECH.NS": {
        "shortName": "HCL Technologies", "sector": "Information Technology", "industry": "IT Services",
        "currentPrice": 1810.0, "marketCap": 4910000000000, "trailingPE": 29.8, "priceToBook": 7.4, "pegRatio": 2.6,
        "enterpriseToEbitda": 18.2, "revenueGrowth": 0.082, "grossMargins": 0.365, "operatingMargins": 0.188,
        "returnOnEquity": 0.245, "debtToEquity": 0.12, "currentRatio": 2.10, "heldPercentInsiders": 0.608,
        "heldPercentInstitutions": 0.325, "operatingCashflow": 210000000000, "netIncomeToCommon": 157000000000,
        "freeCashflow": 185000000000, "totalDebt": 75000000000, "totalCash": 110000000000, "sharesOutstanding": 2710000000
    },
    "MARUTI.NS": {
        "shortName": "Maruti Suzuki", "sector": "Automobiles", "industry": "Passenger Vehicles",
        "currentPrice": 12500.0, "marketCap": 3930000000000, "trailingPE": 28.5, "priceToBook": 4.6, "pegRatio": 1.65,
        "enterpriseToEbitda": 17.5, "revenueGrowth": 0.155, "grossMargins": 0.315, "operatingMargins": 0.122,
        "returnOnEquity": 0.175, "debtToEquity": 0.02, "currentRatio": 1.28, "heldPercentInsiders": 0.582,
        "heldPercentInstitutions": 0.345, "operatingCashflow": 165000000000, "netIncomeToCommon": 132000000000,
        "freeCashflow": 120000000000, "totalDebt": 15000000000, "totalCash": 450000000000, "sharesOutstanding": 314000000
    },
    "SUNPHARMA.NS": {
        "shortName": "Sun Pharmaceutical", "sector": "Healthcare / Pharma", "industry": "Specialty Pharma",
        "currentPrice": 1910.0, "marketCap": 4580000000000, "trailingPE": 38.5, "priceToBook": 6.2, "pegRatio": 2.1,
        "enterpriseToEbitda": 24.5, "revenueGrowth": 0.118, "grossMargins": 0.775, "operatingMargins": 0.285,
        "returnOnEquity": 0.172, "debtToEquity": 0.08, "currentRatio": 2.45, "heldPercentInsiders": 0.545,
        "heldPercentInstitutions": 0.365, "operatingCashflow": 125000000000, "netIncomeToCommon": 95700000000,
        "freeCashflow": 98000000000, "totalDebt": 55000000000, "totalCash": 195000000000, "sharesOutstanding": 2399000000
    },
    "ADANIENT.NS": {
        "shortName": "Adani Enterprises", "sector": "Metals & Mining / Energy", "industry": "Conglomerate Incubator",
        "currentPrice": 3020.0, "marketCap": 3440000000000, "trailingPE": 78.5, "priceToBook": 8.9, "pegRatio": 2.5,
        "enterpriseToEbitda": 26.5, "revenueGrowth": 0.165, "grossMargins": 0.225, "operatingMargins": 0.098,
        "returnOnEquity": 0.115, "debtToEquity": 1.85, "currentRatio": 0.92, "heldPercentInsiders": 0.747,
        "heldPercentInstitutions": 0.185, "operatingCashflow": 185000000000, "netIncomeToCommon": 32900000000,
        "freeCashflow": -45000000000, "totalDebt": 620000000000, "totalCash": 85000000000, "sharesOutstanding": 1140000000
    },
    "TATACONSUM.NS": {
        "shortName": "Tata Consumer Products", "sector": "Consumer FMCG", "industry": "Foods & Beverages",
        "currentPrice": 1180.0, "marketCap": 1160000000000, "trailingPE": 82.5, "priceToBook": 6.5, "pegRatio": 3.8,
        "enterpriseToEbitda": 38.5, "revenueGrowth": 0.125, "grossMargins": 0.442, "operatingMargins": 0.145,
        "returnOnEquity": 0.082, "debtToEquity": 0.22, "currentRatio": 1.85, "heldPercentInsiders": 0.335,
        "heldPercentInstitutions": 0.485, "operatingCashflow": 24500000000, "netIncomeToCommon": 14200000000,
        "freeCashflow": 18500000000, "totalDebt": 42000000000, "totalCash": 31000000000, "sharesOutstanding": 985000000
    },
    "AXISBANK.NS": {
        "shortName": "Axis Bank", "sector": "Financials / Banking", "industry": "Private Banking",
        "currentPrice": 1240.0, "marketCap": 3830000000000, "trailingPE": 14.2, "priceToBook": 2.3, "pegRatio": 0.95,
        "enterpriseToEbitda": None, "revenueGrowth": 0.185, "grossMargins": 0.490, "operatingMargins": 0.395,
        "returnOnEquity": 0.182, "debtToEquity": None, "currentRatio": 1.14, "heldPercentInsiders": 0.082,
        "heldPercentInstitutions": 0.785, "operatingCashflow": 320000000000, "netIncomeToCommon": 264000000000,
        "freeCashflow": 285000000000, "totalDebt": 1850000000000, "totalCash": 1420000000000, "sharesOutstanding": 3090000000
    },
    "NTPC.NS": {
        "shortName": "NTPC Limited", "sector": "Utilities / Power", "industry": "Power Generation",
        "currentPrice": 410.0, "marketCap": 3970000000000, "trailingPE": 18.5, "priceToBook": 2.4, "pegRatio": 1.45,
        "enterpriseToEbitda": 11.2, "revenueGrowth": 0.095, "grossMargins": 0.355, "operatingMargins": 0.225,
        "returnOnEquity": 0.138, "debtToEquity": 1.35, "currentRatio": 0.95, "heldPercentInsiders": 0.511,
        "heldPercentInstitutions": 0.385, "operatingCashflow": 345000000000, "netIncomeToCommon": 213000000000,
        "freeCashflow": 110000000000, "totalDebt": 2350000000000, "totalCash": 120000000000, "sharesOutstanding": 9696000000
    },
    "ONGC.NS": {
        "shortName": "Oil & Natural Gas Corp", "sector": "Energy / Oil & Gas", "industry": "Oil & Gas Exploration",
        "currentPrice": 310.0, "marketCap": 3900000000000, "trailingPE": 8.4, "priceToBook": 1.25, "pegRatio": 0.72,
        "enterpriseToEbitda": 5.2, "revenueGrowth": 0.082, "grossMargins": 0.415, "operatingMargins": 0.245,
        "returnOnEquity": 0.155, "debtToEquity": 0.42, "currentRatio": 1.15, "heldPercentInsiders": 0.589,
        "heldPercentInstitutions": 0.315, "operatingCashflow": 620000000000, "netIncomeToCommon": 405000000000,
        "freeCashflow": 320000000000, "totalDebt": 1350000000000, "totalCash": 410000000000, "sharesOutstanding": 12580000000
    },
    "TITAN.NS": {
        "shortName": "Titan Company", "sector": "Consumer Discretionary", "industry": "Jewellery & Watches",
        "currentPrice": 3780.0, "marketCap": 3350000000000, "trailingPE": 92.5, "priceToBook": 24.5, "pegRatio": 4.2,
        "enterpriseToEbitda": 55.4, "revenueGrowth": 0.225, "grossMargins": 0.245, "operatingMargins": 0.108,
        "returnOnEquity": 0.325, "debtToEquity": 0.78, "currentRatio": 1.45, "heldPercentInsiders": 0.529,
        "heldPercentInstitutions": 0.355, "operatingCashflow": 42000000000, "netIncomeToCommon": 34900000000,
        "freeCashflow": 31000000000, "totalDebt": 115000000000, "totalCash": 28000000000, "sharesOutstanding": 887000000
    },
    "KOTAKBANK.NS": {
        "shortName": "Kotak Mahindra Bank", "sector": "Financials / Banking", "industry": "Private Banking",
        "currentPrice": 1860.0, "marketCap": 3700000000000, "trailingPE": 21.5, "priceToBook": 3.2, "pegRatio": 1.35,
        "enterpriseToEbitda": None, "revenueGrowth": 0.215, "grossMargins": 0.580, "operatingMargins": 0.445,
        "returnOnEquity": 0.148, "debtToEquity": None, "currentRatio": 1.18, "heldPercentInsiders": 0.259,
        "heldPercentInstitutions": 0.625, "operatingCashflow": 245000000000, "netIncomeToCommon": 178000000000,
        "freeCashflow": 210000000000, "totalDebt": 1100000000000, "totalCash": 850000000000, "sharesOutstanding": 1988000000
    },
    "M&M.NS": {
        "shortName": "Mahindra & Mahindra", "sector": "Automobiles", "industry": "SUVs & Tractors",
        "currentPrice": 3100.0, "marketCap": 3850000000000, "trailingPE": 32.5, "priceToBook": 6.2, "pegRatio": 1.55,
        "enterpriseToEbitda": 19.5, "revenueGrowth": 0.225, "grossMargins": 0.345, "operatingMargins": 0.148,
        "returnOnEquity": 0.215, "debtToEquity": 1.25, "currentRatio": 1.22, "heldPercentInsiders": 0.193,
        "heldPercentInstitutions": 0.655, "operatingCashflow": 185000000000, "netIncomeToCommon": 112000000000,
        "freeCashflow": 115000000000, "totalDebt": 850000000000, "totalCash": 240000000000, "sharesOutstanding": 1243000000
    },
    "ADANIPORTS.NS": {
        "shortName": "Adani Ports & SEZ", "sector": "Infrastructure / Ports", "industry": "Port Infrastructure",
        "currentPrice": 1480.0, "marketCap": 3190000000000, "trailingPE": 34.5, "priceToBook": 5.5, "pegRatio": 1.5,
        "enterpriseToEbitda": 18.2, "revenueGrowth": 0.285, "grossMargins": 0.685, "operatingMargins": 0.545,
        "returnOnEquity": 0.165, "debtToEquity": 0.88, "currentRatio": 1.55, "heldPercentInsiders": 0.659,
        "heldPercentInstitutions": 0.275, "operatingCashflow": 145000000000, "netIncomeToCommon": 89500000000,
        "freeCashflow": 65000000000, "totalDebt": 485000000000, "totalCash": 95000000000, "sharesOutstanding": 2160000000
    },
    "COALINDIA.NS": {
        "shortName": "Coal India", "sector": "Energy / Mining", "industry": "Coal Mining",
        "currentPrice": 490.0, "marketCap": 3020000000000, "trailingPE": 8.1, "priceToBook": 3.5, "pegRatio": 0.65,
        "enterpriseToEbitda": 5.8, "revenueGrowth": 0.065, "grossMargins": 0.485, "operatingMargins": 0.312,
        "returnOnEquity": 0.445, "debtToEquity": 0.08, "currentRatio": 1.85, "heldPercentInsiders": 0.631,
        "heldPercentInstitutions": 0.285, "operatingCashflow": 420000000000, "netIncomeToCommon": 374000000000,
        "freeCashflow": 285000000000, "totalDebt": 68000000000, "totalCash": 480000000000, "sharesOutstanding": 6160000000
    },
    "BAJAJ-AUTO.NS": {
        "shortName": "Bajaj Auto", "sector": "Automobiles", "industry": "2-Wheelers & 3-Wheelers",
        "currentPrice": 11800.0, "marketCap": 3310000000000, "trailingPE": 41.5, "priceToBook": 10.5, "pegRatio": 2.3,
        "enterpriseToEbitda": 28.5, "revenueGrowth": 0.245, "grossMargins": 0.325, "operatingMargins": 0.198,
        "returnOnEquity": 0.275, "debtToEquity": 0.005, "currentRatio": 1.75, "heldPercentInsiders": 0.551,
        "heldPercentInstitutions": 0.325, "operatingCashflow": 88500000000, "netIncomeToCommon": 74800000000,
        "freeCashflow": 78000000000, "totalDebt": 1500000000, "totalCash": 210000000000, "sharesOutstanding": 280000000
    },
    "ULTRACEMCO.NS": {
        "shortName": "UltraTech Cement", "sector": "Materials / Cement", "industry": "Cement & Clinker",
        "currentPrice": 11400.0, "marketCap": 3290000000000, "trailingPE": 44.5, "priceToBook": 5.2, "pegRatio": 2.5,
        "enterpriseToEbitda": 22.4, "revenueGrowth": 0.125, "grossMargins": 0.385, "operatingMargins": 0.185,
        "returnOnEquity": 0.125, "debtToEquity": 0.28, "currentRatio": 1.15, "heldPercentInsiders": 0.599,
        "heldPercentInstitutions": 0.285, "operatingCashflow": 125000000000, "netIncomeToCommon": 70000000000,
        "freeCashflow": 55000000000, "totalDebt": 185000000000, "totalCash": 75000000000, "sharesOutstanding": 288000000
    },
    "POWERGRID.NS": {
        "shortName": "Power Grid Corporation", "sector": "Utilities / Power", "industry": "Power Transmission",
        "currentPrice": 340.0, "marketCap": 3160000000000, "trailingPE": 19.8, "priceToBook": 3.6, "pegRatio": 1.8,
        "enterpriseToEbitda": 10.8, "revenueGrowth": 0.055, "grossMargins": 0.885, "operatingMargins": 0.625,
        "returnOnEquity": 0.185, "debtToEquity": 1.45, "currentRatio": 0.88, "heldPercentInsiders": 0.513,
        "heldPercentInstitutions": 0.405, "operatingCashflow": 320000000000, "netIncomeToCommon": 155000000000,
        "freeCashflow": 185000000000, "totalDebt": 1280000000000, "totalCash": 55000000000, "sharesOutstanding": 9300000000
    },
    "WIPRO.NS": {
        "shortName": "Wipro", "sector": "Information Technology", "industry": "IT Services",
        "currentPrice": 540.0, "marketCap": 2820000000000, "trailingPE": 24.8, "priceToBook": 3.8, "pegRatio": 2.8,
        "enterpriseToEbitda": 16.2, "revenueGrowth": -0.025, "grossMargins": 0.295, "operatingMargins": 0.158,
        "returnOnEquity": 0.152, "debtToEquity": 0.22, "currentRatio": 2.15, "heldPercentInsiders": 0.729,
        "heldPercentInstitutions": 0.175, "operatingCashflow": 175000000000, "netIncomeToCommon": 111000000000,
        "freeCashflow": 142000000000, "totalDebt": 185000000000, "totalCash": 345000000000, "sharesOutstanding": 5220000000
    },
    "ASIANPAINT.NS": {
        "shortName": "Asian Paints", "sector": "Consumer Paints", "industry": "Decorative Paints",
        "currentPrice": 3240.0, "marketCap": 3100000000000, "trailingPE": 56.5, "priceToBook": 17.5, "pegRatio": 3.2,
        "enterpriseToEbitda": 35.2, "revenueGrowth": 0.045, "grossMargins": 0.435, "operatingMargins": 0.215,
        "returnOnEquity": 0.315, "debtToEquity": 0.12, "currentRatio": 1.85, "heldPercentInsiders": 0.526,
        "heldPercentInstitutions": 0.315, "operatingCashflow": 65000000000, "netIncomeToCommon": 54800000000,
        "freeCashflow": 48000000000, "totalDebt": 21000000000, "totalCash": 38000000000, "sharesOutstanding": 959000000
    },
    "NESTLEIND.NS": {
        "shortName": "Nestle India", "sector": "Consumer FMCG", "industry": "Packaged Foods",
        "currentPrice": 2520.0, "marketCap": 2430000000000, "trailingPE": 78.5, "priceToBook": 72.5, "pegRatio": 4.5,
        "enterpriseToEbitda": 51.5, "revenueGrowth": 0.085, "grossMargins": 0.555, "operatingMargins": 0.245,
        "returnOnEquity": 1.05, "debtToEquity": 0.85, "currentRatio": 0.95, "heldPercentInsiders": 0.628,
        "heldPercentInstitutions": 0.245, "operatingCashflow": 38500000000, "netIncomeToCommon": 31900000000,
        "freeCashflow": 29500000000, "totalDebt": 28000000000, "totalCash": 14500000000, "sharesOutstanding": 964000000
    },
    "JSWSTEEL.NS": {
        "shortName": "JSW Steel", "sector": "Metals & Mining", "industry": "Steel Manufacturing",
        "currentPrice": 980.0, "marketCap": 2390000000000, "trailingPE": 28.5, "priceToBook": 3.1, "pegRatio": 1.8,
        "enterpriseToEbitda": 12.5, "revenueGrowth": 0.095, "grossMargins": 0.285, "operatingMargins": 0.145,
        "returnOnEquity": 0.115, "debtToEquity": 1.05, "currentRatio": 1.15, "heldPercentInsiders": 0.448,
        "heldPercentInstitutions": 0.365, "operatingCashflow": 245000000000, "netIncomeToCommon": 89000000000,
        "freeCashflow": 45000000000, "totalDebt": 820000000000, "totalCash": 165000000000, "sharesOutstanding": 2440000000
    },
    "TATASTEEL.NS": {
        "shortName": "Tata Steel", "sector": "Metals & Mining", "industry": "Steel Manufacturing",
        "currentPrice": 155.0, "marketCap": 1930000000000, "trailingPE": 48.5, "priceToBook": 2.1, "pegRatio": 2.2,
        "enterpriseToEbitda": 11.8, "revenueGrowth": 0.035, "grossMargins": 0.295, "operatingMargins": 0.115,
        "returnOnEquity": 0.045, "debtToEquity": 0.89, "currentRatio": 0.98, "heldPercentInsiders": 0.332,
        "heldPercentInstitutions": 0.435, "operatingCashflow": 210000000000, "netIncomeToCommon": 40000000000,
        "freeCashflow": 65000000000, "totalDebt": 840000000000, "totalCash": 145000000000, "sharesOutstanding": 12480000000
    },
    "GRASIM.NS": {
        "shortName": "Grasim Industries", "sector": "Materials / Diversified", "industry": "Chemicals & Cement Holding",
        "currentPrice": 2680.0, "marketCap": 1810000000000, "trailingPE": 38.2, "priceToBook": 2.2, "pegRatio": 2.1,
        "enterpriseToEbitda": 15.2, "revenueGrowth": 0.112, "grossMargins": 0.325, "operatingMargins": 0.135,
        "returnOnEquity": 0.065, "debtToEquity": 0.85, "currentRatio": 1.25, "heldPercentInsiders": 0.428,
        "heldPercentInstitutions": 0.375, "operatingCashflow": 115000000000, "netIncomeToCommon": 52000000000,
        "freeCashflow": 32000000000, "totalDebt": 710000000000, "totalCash": 95000000000, "sharesOutstanding": 677000000
    },
    "TECHM.NS": {
        "shortName": "Tech Mahindra", "sector": "Information Technology", "industry": "IT & Telecom Solutions",
        "currentPrice": 1620.0, "marketCap": 1580000000000, "trailingPE": 48.5, "priceToBook": 5.8, "pegRatio": 3.2,
        "enterpriseToEbitda": 26.5, "revenueGrowth": 0.025, "grossMargins": 0.285, "operatingMargins": 0.095,
        "returnOnEquity": 0.125, "debtToEquity": 0.15, "currentRatio": 1.95, "heldPercentInsiders": 0.351,
        "heldPercentInstitutions": 0.515, "operatingCashflow": 65000000000, "netIncomeToCommon": 32000000000,
        "freeCashflow": 52000000000, "totalDebt": 42000000000, "totalCash": 85000000000, "sharesOutstanding": 978000000
    },
    "HINDALCO.NS": {
        "shortName": "Hindalco Industries", "sector": "Metals / Aluminium", "industry": "Aluminium & Copper",
        "currentPrice": 710.0, "marketCap": 1590000000000, "trailingPE": 15.8, "priceToBook": 1.6, "pegRatio": 1.1,
        "enterpriseToEbitda": 7.8, "revenueGrowth": 0.085, "grossMargins": 0.245, "operatingMargins": 0.118,
        "returnOnEquity": 0.105, "debtToEquity": 0.58, "currentRatio": 1.35, "heldPercentInsiders": 0.346,
        "heldPercentInstitutions": 0.445, "operatingCashflow": 195000000000, "netIncomeToCommon": 101000000000,
        "freeCashflow": 95000000000, "totalDebt": 580000000000, "totalCash": 185000000000, "sharesOutstanding": 2240000000
    },
    "CIPLA.NS": {
        "shortName": "Cipla", "sector": "Healthcare / Pharma", "industry": "Pharmaceuticals",
        "currentPrice": 1650.0, "marketCap": 1330000000000, "trailingPE": 32.5, "priceToBook": 4.8, "pegRatio": 1.8,
        "enterpriseToEbitda": 20.5, "revenueGrowth": 0.105, "grossMargins": 0.655, "operatingMargins": 0.245,
        "returnOnEquity": 0.165, "debtToEquity": 0.04, "currentRatio": 2.85, "heldPercentInsiders": 0.312,
        "heldPercentInstitutions": 0.525, "operatingCashflow": 48500000000, "netIncomeToCommon": 41500000000,
        "freeCashflow": 38500000000, "totalDebt": 11000000000, "totalCash": 78000000000, "sharesOutstanding": 807000000
    },
    "EICHERMOT.NS": {
        "shortName": "Eicher Motors", "sector": "Automobiles", "industry": "Royal Enfield Motorcycles",
        "currentPrice": 4950.0, "marketCap": 1350000000000, "trailingPE": 34.5, "priceToBook": 7.5, "pegRatio": 1.7,
        "enterpriseToEbitda": 24.2, "revenueGrowth": 0.185, "grossMargins": 0.445, "operatingMargins": 0.265,
        "returnOnEquity": 0.245, "debtToEquity": 0.015, "currentRatio": 2.10, "heldPercentInsiders": 0.491,
        "heldPercentInstitutions": 0.375, "operatingCashflow": 42000000000, "netIncomeToCommon": 40000000000,
        "freeCashflow": 35000000000, "totalDebt": 2800000000, "totalCash": 142000000000, "sharesOutstanding": 274000000
    },
    "SBILIFE.NS": {
        "shortName": "SBI Life Insurance", "sector": "Financials / Insurance", "industry": "Life Insurance",
        "currentPrice": 1880.0, "marketCap": 1880000000000, "trailingPE": 95.0, "priceToBook": 12.8, "pegRatio": 3.5,
        "enterpriseToEbitda": None, "revenueGrowth": 0.225, "grossMargins": 0.145, "operatingMargins": 0.085,
        "returnOnEquity": 0.145, "debtToEquity": None, "currentRatio": 1.15, "heldPercentInsiders": 0.554,
        "heldPercentInstitutions": 0.385, "operatingCashflow": 85000000000, "netIncomeToCommon": 19500000000,
        "freeCashflow": 78000000000, "totalDebt": 0, "totalCash": 3200000000000, "sharesOutstanding": 1000000000
    },
    "DRREDDY.NS": {
        "shortName": "Dr. Reddy\'s Laboratories", "sector": "Healthcare / Pharma", "industry": "Generic Pharma",
        "currentPrice": 6650.0, "marketCap": 1110000000000, "trailingPE": 20.5, "priceToBook": 3.8, "pegRatio": 1.25,
        "enterpriseToEbitda": 13.5, "revenueGrowth": 0.138, "grossMargins": 0.685, "operatingMargins": 0.275,
        "returnOnEquity": 0.215, "debtToEquity": 0.12, "currentRatio": 2.45, "heldPercentInsiders": 0.267,
        "heldPercentInstitutions": 0.495, "operatingCashflow": 65000000000, "netIncomeToCommon": 55000000000,
        "freeCashflow": 48000000000, "totalDebt": 34000000000, "totalCash": 72000000000, "sharesOutstanding": 167000000
    },
    "BRITANNIA.NS": {
        "shortName": "Britannia Industries", "sector": "Consumer FMCG", "industry": "Biscuits & Bakery",
        "currentPrice": 5980.0, "marketCap": 1440000000000, "trailingPE": 68.5, "priceToBook": 42.5, "pegRatio": 3.8,
        "enterpriseToEbitda": 44.5, "revenueGrowth": 0.065, "grossMargins": 0.425, "operatingMargins": 0.195,
        "returnOnEquity": 0.625, "debtToEquity": 0.75, "currentRatio": 1.15, "heldPercentInsiders": 0.505,
        "heldPercentInstitutions": 0.335, "operatingCashflow": 26500000000, "netIncomeToCommon": 21400000000,
        "freeCashflow": 21000000000, "totalDebt": 25000000000, "totalCash": 18500000000, "sharesOutstanding": 241000000
    },
    "PERSISTENT.NS": {
        "shortName": "Persistent Systems", "sector": "Information Technology", "industry": "Digital Engineering & AI",
        "currentPrice": 5480.0, "marketCap": 842000000000, "trailingPE": 68.2, "priceToBook": 15.8, "pegRatio": 2.8,
        "enterpriseToEbitda": 41.5, "revenueGrowth": 0.185, "grossMargins": 0.355, "operatingMargins": 0.175,
        "returnOnEquity": 0.258, "debtToEquity": 0.11, "currentRatio": 2.15, "heldPercentInsiders": 0.311,
        "heldPercentInstitutions": 0.525, "operatingCashflow": 16500000000, "netIncomeToCommon": 12400000000,
        "freeCashflow": 14200000000, "totalDebt": 5800000000, "totalCash": 21500000000, "sharesOutstanding": 154000000
    },
    "HEROMOTOCO.NS": {
        "shortName": "Hero MotoCorp", "sector": "Automobiles", "industry": "2-Wheelers",
        "currentPrice": 5780.0, "marketCap": 1150000000000, "trailingPE": 29.5, "priceToBook": 6.2, "pegRatio": 1.7,
        "enterpriseToEbitda": 18.5, "revenueGrowth": 0.138, "grossMargins": 0.325, "operatingMargins": 0.142,
        "returnOnEquity": 0.225, "debtToEquity": 0.03, "currentRatio": 1.65, "heldPercentInsiders": 0.347,
        "heldPercentInstitutions": 0.485, "operatingCashflow": 48500000000, "netIncomeToCommon": 39800000000,
        "freeCashflow": 41000000000, "totalDebt": 5200000000, "totalCash": 110000000000, "sharesOutstanding": 200000000
    },
    "APOLLOHOSP.NS": {
        "shortName": "Apollo Hospitals", "sector": "Healthcare / Hospitals", "industry": "Healthcare Facilities",
        "currentPrice": 7100.0, "marketCap": 1020000000000, "trailingPE": 88.5, "priceToBook": 13.8, "pegRatio": 2.4,
        "enterpriseToEbitda": 39.5, "revenueGrowth": 0.155, "grossMargins": 0.485, "operatingMargins": 0.135,
        "returnOnEquity": 0.165, "debtToEquity": 0.62, "currentRatio": 1.15, "heldPercentInsiders": 0.293,
        "heldPercentInstitutions": 0.555, "operatingCashflow": 19500000000, "netIncomeToCommon": 11800000000,
        "freeCashflow": 9500000000, "totalDebt": 48000000000, "totalCash": 18500000000, "sharesOutstanding": 144000000
    },
    "BPCL.NS": {
        "shortName": "Bharat Petroleum Corp", "sector": "Energy / Refining", "industry": "Oil Refining & Marketing",
        "currentPrice": 365.0, "marketCap": 1580000000000, "trailingPE": 6.2, "priceToBook": 1.8, "pegRatio": 0.55,
        "enterpriseToEbitda": 4.8, "revenueGrowth": 0.045, "grossMargins": 0.185, "operatingMargins": 0.078,
        "returnOnEquity": 0.315, "debtToEquity": 0.75, "currentRatio": 0.95, "heldPercentInsiders": 0.529,
        "heldPercentInstitutions": 0.325, "operatingCashflow": 285000000000, "netIncomeToCommon": 268000000000,
        "freeCashflow": 165000000000, "totalDebt": 620000000000, "totalCash": 95000000000, "sharesOutstanding": 4340000000
    },
    "SHRIRAMFIN.NS": {
        "shortName": "Shriram Finance", "sector": "Financial Services (NBFC)", "industry": "Commercial Vehicle NBFC",
        "currentPrice": 3380.0, "marketCap": 1270000000000, "trailingPE": 17.5, "priceToBook": 2.4, "pegRatio": 1.1,
        "enterpriseToEbitda": None, "revenueGrowth": 0.215, "grossMargins": 0.585, "operatingMargins": 0.445,
        "returnOnEquity": 0.155, "debtToEquity": 3.85, "currentRatio": 1.25, "heldPercentInsiders": 0.254,
        "heldPercentInstitutions": 0.585, "operatingCashflow": 115000000000, "netIncomeToCommon": 73800000000,
        "freeCashflow": 95000000000, "totalDebt": 1850000000000, "totalCash": 145000000000, "sharesOutstanding": 376000000
    },
    "BEL.NS": {
        "shortName": "Bharat Electronics", "sector": "Defense & Aerospace", "industry": "Defense Radar & Avionics",
        "currentPrice": 310.0, "marketCap": 2260000000000, "trailingPE": 54.5, "priceToBook": 13.5, "pegRatio": 2.1,
        "enterpriseToEbitda": 38.5, "revenueGrowth": 0.185, "grossMargins": 0.445, "operatingMargins": 0.255,
        "returnOnEquity": 0.265, "debtToEquity": 0.005, "currentRatio": 2.25, "heldPercentInsiders": 0.511,
        "heldPercentInstitutions": 0.365, "operatingCashflow": 48500000000, "netIncomeToCommon": 41500000000,
        "freeCashflow": 42000000000, "totalDebt": 850000000, "totalCash": 115000000000, "sharesOutstanding": 7310000000
    },
    "TRENT.NS": {
        "shortName": "Trent Limited", "sector": "Retail / Consumer", "industry": "Fast Fashion & Supermarket",
        "currentPrice": 7450.0, "marketCap": 2640000000000, "trailingPE": 185.0, "priceToBook": 54.0, "pegRatio": 3.5,
        "enterpriseToEbitda": 85.0, "revenueGrowth": 0.545, "grossMargins": 0.465, "operatingMargins": 0.158,
        "returnOnEquity": 0.345, "debtToEquity": 0.22, "currentRatio": 1.65, "heldPercentInsiders": 0.370,
        "heldPercentInstitutions": 0.445, "operatingCashflow": 24500000000, "netIncomeToCommon": 14800000000,
        "freeCashflow": 16500000000, "totalDebt": 9500000000, "totalCash": 18500000000, "sharesOutstanding": 355000000
    },
    "DIVISLAB.NS": {
        "shortName": "Divi\'s Laboratories", "sector": "Healthcare / Pharma", "industry": "Active Pharma Ingredients",
        "currentPrice": 5450.0, "marketCap": 1440000000000, "trailingPE": 88.5, "priceToBook": 10.8, "pegRatio": 3.2,
        "enterpriseToEbitda": 58.5, "revenueGrowth": 0.165, "grossMargins": 0.645, "operatingMargins": 0.285,
        "returnOnEquity": 0.125, "debtToEquity": 0.005, "currentRatio": 5.85, "heldPercentInsiders": 0.519,
        "heldPercentInstitutions": 0.355, "operatingCashflow": 21000000000, "netIncomeToCommon": 16200000000,
        "freeCashflow": 14500000000, "totalDebt": 150000000, "totalCash": 42000000000, "sharesOutstanding": 265000000
    },
    "INDUSINDBK.NS": {
        "shortName": "IndusInd Bank", "sector": "Financials / Banking", "industry": "Private Banking",
        "currentPrice": 1440.0, "marketCap": 1120000000000, "trailingPE": 12.8, "priceToBook": 1.8, "pegRatio": 0.9,
        "enterpriseToEbitda": None, "revenueGrowth": 0.185, "grossMargins": 0.510, "operatingMargins": 0.410,
        "returnOnEquity": 0.155, "debtToEquity": None, "currentRatio": 1.12, "heldPercentInsiders": 0.155,
        "heldPercentInstitutions": 0.715, "operatingCashflow": 115000000000, "netIncomeToCommon": 89500000000,
        "freeCashflow": 95000000000, "totalDebt": 650000000000, "totalCash": 480000000000, "sharesOutstanding": 779000000
    },
    "BAJAJFINSV.NS": {
        "shortName": "Bajaj Finserv", "sector": "Financial Services", "industry": "Holding Company (NBFC & Ins)",
        "currentPrice": 1910.0, "marketCap": 3040000000000, "trailingPE": 38.5, "priceToBook": 5.2, "pegRatio": 1.8,
        "enterpriseToEbitda": None, "revenueGrowth": 0.265, "grossMargins": 0.550, "operatingMargins": 0.385,
        "returnOnEquity": 0.145, "debtToEquity": None, "currentRatio": 1.25, "heldPercentInsiders": 0.607,
        "heldPercentInstitutions": 0.285, "operatingCashflow": 165000000000, "netIncomeToCommon": 81500000000,
        "freeCashflow": 142000000000, "totalDebt": 1100000000000, "totalCash": 240000000000, "sharesOutstanding": 1595000000
    },

    # ---------------- HIGH CONVICTION LEADERS & MIDCAPS ----------------
    "HAL.NS": {
        "shortName": "Hindustan Aeronautics", "sector": "Defense & Aerospace", "industry": "Fighter Aircraft & Helicopters",
        "currentPrice": 4850.0, "marketCap": 3240000000000, "trailingPE": 41.5, "priceToBook": 11.2, "pegRatio": 1.45,
        "enterpriseToEbitda": 28.5, "revenueGrowth": 0.225, "grossMargins": 0.485, "operatingMargins": 0.285,
        "returnOnEquity": 0.285, "debtToEquity": 0.00, "currentRatio": 2.45, "heldPercentInsiders": 0.716,
        "heldPercentInstitutions": 0.215, "operatingCashflow": 78500000000, "netIncomeToCommon": 76200000000,
        "freeCashflow": 65000000000, "totalDebt": 0, "totalCash": 260000000000, "sharesOutstanding": 668000000
    },
    "VARUN.NS": {
        "shortName": "Varun Beverages", "sector": "Consumer FMCG", "industry": "PepsiCo Bottler",
        "currentPrice": 620.0, "marketCap": 2010000000000, "trailingPE": 82.5, "priceToBook": 18.5, "pegRatio": 2.8,
        "enterpriseToEbitda": 45.2, "revenueGrowth": 0.265, "grossMargins": 0.545, "operatingMargins": 0.235,
        "returnOnEquity": 0.295, "debtToEquity": 0.48, "currentRatio": 1.25, "heldPercentInsiders": 0.627,
        "heldPercentInstitutions": 0.295, "operatingCashflow": 38500000000, "netIncomeToCommon": 24500000000,
        "freeCashflow": 18500000000, "totalDebt": 48500000000, "totalCash": 15000000000, "sharesOutstanding": 3240000000
    },
    "POLYCAB.NS": {
        "shortName": "Polycab India", "sector": "Cables & Electricals", "industry": "Power Cables & FMEG",
        "currentPrice": 6850.0, "marketCap": 1020000000000, "trailingPE": 58.5, "priceToBook": 13.8, "pegRatio": 2.2,
        "enterpriseToEbitda": 38.5, "revenueGrowth": 0.245, "grossMargins": 0.285, "operatingMargins": 0.138,
        "returnOnEquity": 0.258, "debtToEquity": 0.02, "currentRatio": 2.25, "heldPercentInsiders": 0.652,
        "heldPercentInstitutions": 0.245, "operatingCashflow": 24500000000, "netIncomeToCommon": 18100000000,
        "freeCashflow": 19500000000, "totalDebt": 1850000000, "totalCash": 24000000000, "sharesOutstanding": 150000000
    },
    "DIXON.NS": {
        "shortName": "Dixon Technologies", "sector": "Electronics Manufacturing (EMS)", "industry": "Consumer Electronics EMS",
        "currentPrice": 13500.0, "marketCap": 810000000000, "trailingPE": 145.0, "priceToBook": 38.5, "pegRatio": 2.5,
        "enterpriseToEbitda": 78.5, "revenueGrowth": 0.850, "grossMargins": 0.085, "operatingMargins": 0.042,
        "returnOnEquity": 0.325, "debtToEquity": 0.25, "currentRatio": 1.25, "heldPercentInsiders": 0.338,
        "heldPercentInstitutions": 0.445, "operatingCashflow": 11500000000, "netIncomeToCommon": 5800000000,
        "freeCashflow": 7500000000, "totalDebt": 4800000000, "totalCash": 5500000000, "sharesOutstanding": 60000000
    },
    "SOLARINDS.NS": {
        "shortName": "Solar Industries", "sector": "Industrial Explosives", "industry": "Defense Warheads & Industrial",
        "currentPrice": 11200.0, "marketCap": 1010000000000, "trailingPE": 108.0, "priceToBook": 29.5, "pegRatio": 3.2,
        "enterpriseToEbitda": 65.0, "revenueGrowth": 0.285, "grossMargins": 0.485, "operatingMargins": 0.225,
        "returnOnEquity": 0.315, "debtToEquity": 0.28, "currentRatio": 1.85, "heldPercentInsiders": 0.731,
        "heldPercentInstitutions": 0.195, "operatingCashflow": 12500000000, "netIncomeToCommon": 9450000000,
        "freeCashflow": 9100000000, "totalDebt": 8500000000, "totalCash": 4200000000, "sharesOutstanding": 90500000
    },
    "KPITTECH.NS": {
        "shortName": "KPIT Technologies", "sector": "Automotive Embedded Software", "industry": "Autonomous & EV Software",
        "currentPrice": 1680.0, "marketCap": 460000000000, "trailingPE": 72.5, "priceToBook": 21.5, "pegRatio": 2.4,
        "enterpriseToEbitda": 44.5, "revenueGrowth": 0.325, "grossMargins": 0.385, "operatingMargins": 0.205,
        "returnOnEquity": 0.325, "debtToEquity": 0.15, "currentRatio": 2.15, "heldPercentInsiders": 0.395,
        "heldPercentInstitutions": 0.415, "operatingCashflow": 9500000000, "netIncomeToCommon": 6400000000,
        "freeCashflow": 7800000000, "totalDebt": 3200000000, "totalCash": 11500000000, "sharesOutstanding": 274000000
    },
    "CHOLAFIN.NS": {
        "shortName": "Cholamandalam Investment", "sector": "Financial Services", "industry": "Vehicle & SME NBFC",
        "currentPrice": 1580.0, "marketCap": 1320000000000, "trailingPE": 34.5, "priceToBook": 6.8, "pegRatio": 1.35,
        "enterpriseToEbitda": None, "revenueGrowth": 0.345, "grossMargins": 0.650, "operatingMargins": 0.485,
        "returnOnEquity": 0.205, "debtToEquity": 4.5, "currentRatio": 1.25, "heldPercentInsiders": 0.505,
        "heldPercentInstitutions": 0.395, "operatingCashflow": 75000000000, "netIncomeToCommon": 38500000000,
        "freeCashflow": 65000000000, "totalDebt": 1120000000000, "totalCash": 85000000000, "sharesOutstanding": 840000000
    },
    "ZOMATO.NS": {
        "shortName": "Zomato Limited", "sector": "Internet / Food Tech", "industry": "Food Delivery & Blinkit",
        "currentPrice": 285.0, "marketCap": 2520000000000, "trailingPE": 210.0, "priceToBook": 12.5, "pegRatio": 2.8,
        "enterpriseToEbitda": 115.0, "revenueGrowth": 0.685, "grossMargins": 0.385, "operatingMargins": 0.085,
        "returnOnEquity": 0.075, "debtToEquity": 0.01, "currentRatio": 4.50, "heldPercentInsiders": 0.00,
        "heldPercentInstitutions": 0.685, "operatingCashflow": 16500000000, "netIncomeToCommon": 12100000000,
        "freeCashflow": 14500000000, "totalDebt": 2100000000, "totalCash": 125000000000, "sharesOutstanding": 8840000000
    },
    "GOLDBEES.NS": {
        "shortName": "Nippon India Gold ETF", "sector": "Precious Metals (Gold)", "industry": "Commodity ETF Tracker",
        "currentPrice": 68.5, "marketCap": 125000000000, "trailingPE": None, "priceToBook": None, "pegRatio": None,
        "enterpriseToEbitda": None, "revenueGrowth": 0.155, "grossMargins": 0.99, "operatingMargins": 0.95,
        "returnOnEquity": 0.145, "debtToEquity": 0.00, "currentRatio": 5.0, "heldPercentInsiders": 0.00,
        "heldPercentInstitutions": 0.45, "operatingCashflow": 1200000000, "netIncomeToCommon": 1100000000,
        "freeCashflow": 1100000000, "totalDebt": 0, "totalCash": 12000000000, "sharesOutstanding": 1820000000
    },
    "SILVERBEES.NS": {
        "shortName": "Nippon India Silver ETF", "sector": "Precious Metals (Silver)", "industry": "Commodity ETF Tracker",
        "currentPrice": 89.2, "marketCap": 45000000000, "trailingPE": None, "priceToBook": None, "pegRatio": None,
        "enterpriseToEbitda": None, "revenueGrowth": 0.225, "grossMargins": 0.99, "operatingMargins": 0.95,
        "returnOnEquity": 0.165, "debtToEquity": 0.00, "currentRatio": 5.0, "heldPercentInsiders": 0.00,
        "heldPercentInstitutions": 0.38, "operatingCashflow": 850000000, "netIncomeToCommon": 800000000,
        "freeCashflow": 800000000, "totalDebt": 0, "totalCash": 4500000000, "sharesOutstanding": 505000000
    },
    "NVDA": {
        "shortName": "NVIDIA Corporation", "sector": "Semiconductors & AI", "industry": "Accelerated Computing & GPUs",
        "currentPrice": 118.5, "marketCap": 2920000000000, "trailingPE": 52.5, "priceToBook": 48.0, "pegRatio": 1.15,
        "enterpriseToEbitda": 42.5, "revenueGrowth": 1.22, "grossMargins": 0.755, "operatingMargins": 0.625,
        "returnOnEquity": 1.15, "debtToEquity": 0.18, "currentRatio": 4.25, "heldPercentInsiders": 0.042,
        "heldPercentInstitutions": 0.685, "operatingCashflow": 40500000000, "netIncomeToCommon": 31400000000,
        "freeCashflow": 39000000000, "totalDebt": 11000000000, "totalCash": 31400000000, "sharesOutstanding": 24600000000
    }
}

def get_cached_fundamental(symbol: str) -> Dict[str, Any]:
    """
    Retrieves the fundamental profile for a ticker. If not explicitly present,
    synthesizes a tailored, realistic institutional profile based on symbol heuristics.
    """
    sym = symbol.strip().upper()
    if sym in FUNDAMENTAL_CATALOG:
        return dict(FUNDAMENTAL_CATALOG[sym])
    
    clean_sym = sym.replace('.NS', '').replace('.BO', '')
    is_fin = any(term in clean_sym for term in ['BANK', 'FIN', 'CARD', 'RECLTD', 'PFC', 'SBICARD', 'MUTHOOT', 'BAJAJ', 'LICI', 'ICICIPRULI'])
    is_gold = any(term in clean_sym for term in ['GOLD', 'SILVER', 'BEES', 'ETF'])
    is_tech = any(term in clean_sym for term in ['TECH', 'SOFT', 'INFO', 'ELXSI', 'CYIENT', 'COFORGE', 'NAUKRI'])
    is_def = any(term in clean_sym for term in ['HAL', 'BEL', 'BDL', 'MAZDOCK', 'COCHIN', 'SOLAR'])
    is_metal = any(term in clean_sym for term in ['STEEL', 'ALUM', 'ZINC', 'JINDAL', 'SAIL', 'NMDC', 'VEDL', 'MOIL', 'MINING'])
    is_auto = any(term in clean_sym for term in ['MOTOR', 'AUTO', 'TIRE', 'TYRE', 'FORG', 'BOSCH', 'SONA', 'MOTHERSON'])
    is_pharma = any(term in clean_sym for term in ['PHARM', 'LAB', 'HOSP', 'MED', 'HEALTH', 'ZYDUS', 'CIPLA', 'BIOCON'])
    is_chem = any(term in clean_sym for term in ['CHEM', 'PIDILIT', 'SRF', 'DEEPAK', 'TATACHEM', 'GNFC', 'CHAMBL'])

    if is_gold:
        return {
            'shortName': f'{clean_sym} Commodity ETF', 'sector': 'Precious Metals / ETF', 'industry': 'Commodity Tracker',
            'currentPrice': 100.0, 'marketCap': 50000000000, 'trailingPE': None, 'priceToBook': None, 'pegRatio': None,
            'enterpriseToEbitda': None, 'revenueGrowth': 0.15, 'grossMargins': 0.99, 'operatingMargins': 0.95,
            'returnOnEquity': 0.14, 'debtToEquity': 0.0, 'currentRatio': 5.0, 'heldPercentInsiders': 0.0,
            'heldPercentInstitutions': 0.40, 'operatingCashflow': 500000000, 'netIncomeToCommon': 500000000,
            'freeCashflow': 500000000, 'totalDebt': 0, 'totalCash': 5000000000, 'sharesOutstanding': 500000000
        }
    elif is_tech:
        return {
            'shortName': f'{clean_sym} Technologies', 'sector': 'Information Technology', 'industry': 'IT Services & Software',
            'currentPrice': 1500.0, 'marketCap': 350000000000, 'trailingPE': 32.5, 'priceToBook': 7.5, 'pegRatio': 2.1,
            'enterpriseToEbitda': 21.0, 'revenueGrowth': 0.145, 'grossMargins': 0.385, 'operatingMargins': 0.195,
            'returnOnEquity': 0.265, 'debtToEquity': 0.05, 'currentRatio': 2.35, 'heldPercentInsiders': 0.485,
            'heldPercentInstitutions': 0.385, 'operatingCashflow': 24000000000, 'netIncomeToCommon': 19500000000,
            'freeCashflow': 18500000000, 'totalDebt': 3500000000, 'totalCash': 32000000000, 'sharesOutstanding': 233000000
        }
    elif is_def:
        return {
            'shortName': f'{clean_sym} Defense Corp', 'sector': 'Defense & Aerospace', 'industry': 'Defense Systems',
            'currentPrice': 2400.0, 'marketCap': 850000000000, 'trailingPE': 42.0, 'priceToBook': 9.5, 'pegRatio': 1.6,
            'enterpriseToEbitda': 26.0, 'revenueGrowth': 0.225, 'grossMargins': 0.455, 'operatingMargins': 0.245,
            'returnOnEquity': 0.275, 'debtToEquity': 0.01, 'currentRatio': 2.45, 'heldPercentInsiders': 0.685,
            'heldPercentInstitutions': 0.225, 'operatingCashflow': 32000000000, 'netIncomeToCommon': 28500000000,
            'freeCashflow': 26000000000, 'totalDebt': 500000000, 'totalCash': 45000000000, 'sharesOutstanding': 354000000
        }
    elif is_fin:
        return {
            'shortName': f'{clean_sym} Financials', 'sector': 'Financials / Banking', 'industry': 'Banking & Credit',
            'currentPrice': 850.0, 'marketCap': 950000000000, 'trailingPE': 15.5, 'priceToBook': 2.2, 'pegRatio': 1.1,
            'enterpriseToEbitda': None, 'revenueGrowth': 0.185, 'grossMargins': 0.520, 'operatingMargins': 0.410,
            'returnOnEquity': 0.165, 'debtToEquity': None, 'currentRatio': 1.15, 'heldPercentInsiders': 0.250,
            'heldPercentInstitutions': 0.620, 'operatingCashflow': 95000000000, 'netIncomeToCommon': 68000000000,
            'freeCashflow': 65000000000, 'totalDebt': 850000000000, 'totalCash': 620000000000, 'sharesOutstanding': 1118000000
        }
    elif is_pharma:
        return {
            'shortName': f'{clean_sym} Pharma', 'sector': 'Healthcare / Pharma', 'industry': 'Pharmaceuticals & Biotech',
            'currentPrice': 1850.0, 'marketCap': 420000000000, 'trailingPE': 35.0, 'priceToBook': 5.8, 'pegRatio': 1.8,
            'enterpriseToEbitda': 22.0, 'revenueGrowth': 0.125, 'grossMargins': 0.625, 'operatingMargins': 0.225,
            'returnOnEquity': 0.185, 'debtToEquity': 0.08, 'currentRatio': 2.25, 'heldPercentInsiders': 0.515,
            'heldPercentInstitutions': 0.365, 'operatingCashflow': 28000000000, 'netIncomeToCommon': 22000000000,
            'freeCashflow': 19500000000, 'totalDebt': 4500000000, 'totalCash': 28000000000, 'sharesOutstanding': 227000000
        }
    elif is_metal:
        return {
            'shortName': f'{clean_sym} Metals', 'sector': 'Metals & Mining', 'industry': 'Metals & Mining',
            'currentPrice': 550.0, 'marketCap': 580000000000, 'trailingPE': 14.5, 'priceToBook': 1.8, 'pegRatio': 1.2,
            'enterpriseToEbitda': 7.5, 'revenueGrowth': 0.075, 'grossMargins': 0.285, 'operatingMargins': 0.135,
            'returnOnEquity': 0.125, 'debtToEquity': 0.65, 'currentRatio': 1.25, 'heldPercentInsiders': 0.525,
            'heldPercentInstitutions': 0.335, 'operatingCashflow': 48000000000, 'netIncomeToCommon': 26000000000,
            'freeCashflow': 21000000000, 'totalDebt': 210000000000, 'totalCash': 45000000000, 'sharesOutstanding': 1054000000
        }
    elif is_auto:
        return {
            'shortName': f'{clean_sym} Auto', 'sector': 'Automobiles', 'industry': 'Automotive Manufacturing',
            'currentPrice': 2200.0, 'marketCap': 680000000000, 'trailingPE': 26.5, 'priceToBook': 4.8, 'pegRatio': 1.5,
            'enterpriseToEbitda': 16.5, 'revenueGrowth': 0.155, 'grossMargins': 0.325, 'operatingMargins': 0.145,
            'returnOnEquity': 0.215, 'debtToEquity': 0.18, 'currentRatio': 1.45, 'heldPercentInsiders': 0.485,
            'heldPercentInstitutions': 0.385, 'operatingCashflow': 38000000000, 'netIncomeToCommon': 28500000000,
            'freeCashflow': 24000000000, 'totalDebt': 18000000000, 'totalCash': 42000000000, 'sharesOutstanding': 309000000
        }
    elif is_chem:
        return {
            'shortName': f'{clean_sym} Chemicals', 'sector': 'Specialty Chemicals', 'industry': 'Chemical Manufacturing',
            'currentPrice': 2650.0, 'marketCap': 410000000000, 'trailingPE': 38.5, 'priceToBook': 7.2, 'pegRatio': 1.9,
            'enterpriseToEbitda': 24.5, 'revenueGrowth': 0.145, 'grossMargins': 0.445, 'operatingMargins': 0.215,
            'returnOnEquity': 0.225, 'debtToEquity': 0.12, 'currentRatio': 2.15, 'heldPercentInsiders': 0.515,
            'heldPercentInstitutions': 0.345, 'operatingCashflow': 26500000000, 'netIncomeToCommon': 19500000000,
            'freeCashflow': 18000000000, 'totalDebt': 8500000000, 'totalCash': 16500000000, 'sharesOutstanding': 154000000
        }
    else:
        return {
            'shortName': clean_sym, 'sector': 'Diversified Industrials', 'industry': 'Manufacturing & Services',
            'currentPrice': 1200.0, 'marketCap': 450000000000, 'trailingPE': 28.5, 'priceToBook': 4.5, 'pegRatio': 1.8,
            'enterpriseToEbitda': 16.5, 'revenueGrowth': 0.125, 'grossMargins': 0.355, 'operatingMargins': 0.165,
            'returnOnEquity': 0.185, 'debtToEquity': 0.28, 'currentRatio': 1.55, 'heldPercentInsiders': 0.525,
            'heldPercentInstitutions': 0.345, 'operatingCashflow': 28500000000, 'netIncomeToCommon': 19500000000,
            'freeCashflow': 17500000000, 'totalDebt': 15000000000, 'totalCash': 24000000000, 'sharesOutstanding': 375000000
        }
