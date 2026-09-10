"""
Complete Universe of Indian Equities (NSE/BSE) & Commodities.
Covers Nifty 50, Nifty Next 50, Midcap Compounders, and Commodities/Metals/Energy.
"""

from typing import List, Dict

# ==================== 1. FULL NIFTY 50 (50 BLUE CHIPS) ====================
INDIAN_NIFTY_50: List[Dict[str, str]] = [
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "sector": "Energy / Retail / Telecom"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "sector": "Information Technology"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "sector": "Financials / Banking"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "sector": "Financials / Banking"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel", "sector": "Telecommunications"},
    {"symbol": "INFY.NS", "name": "Infosys", "sector": "Information Technology"},
    {"symbol": "ITC.NS", "name": "ITC Limited", "sector": "Consumer FMCG"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever", "sector": "Consumer FMCG"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro", "sector": "Engineering & Capital Goods"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "sector": "Financials / PSU Bank"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance", "sector": "Financial Services (NBFC)"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies", "sector": "Information Technology"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki", "sector": "Automobiles"},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharmaceutical", "sector": "Healthcare / Pharma"},
    {"symbol": "ADANIENT.NS", "name": "Adani Enterprises", "sector": "Metals & Mining / Energy"},
    {"symbol": "TATACONSUM.NS", "name": "Tata Consumer Products", "sector": "Consumer FMCG"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank", "sector": "Financials / Banking"},
    {"symbol": "NTPC.NS", "name": "NTPC Limited", "sector": "Utilities / Power"},
    {"symbol": "ONGC.NS", "name": "Oil & Natural Gas Corp", "sector": "Energy / Oil & Gas"},
    {"symbol": "TITAN.NS", "name": "Titan Company", "sector": "Consumer Discretionary"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "sector": "Financials / Banking"},
    {"symbol": "M&M.NS", "name": "Mahindra & Mahindra", "sector": "Automobiles"},
    {"symbol": "ADANIPORTS.NS", "name": "Adani Ports & SEZ", "sector": "Infrastructure / Ports"},
    {"symbol": "COALINDIA.NS", "name": "Coal India", "sector": "Energy / Mining"},
    {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto", "sector": "Automobiles"},
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement", "sector": "Materials / Cement"},
    {"symbol": "POWERGRID.NS", "name": "Power Grid Corporation", "sector": "Utilities / Power"},
    {"symbol": "WIPRO.NS", "name": "Wipro", "sector": "Information Technology"},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints", "sector": "Consumer Paints"},
    {"symbol": "NESTLEIND.NS", "name": "Nestle India", "sector": "Consumer FMCG"},
    {"symbol": "JSWSTEEL.NS", "name": "JSW Steel", "sector": "Metals & Mining"},
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel", "sector": "Metals & Mining"},
    {"symbol": "GRASIM.NS", "name": "Grasim Industries", "sector": "Materials / Diversified"},
    {"symbol": "TECHM.NS", "name": "Tech Mahindra", "sector": "Information Technology"},
    {"symbol": "HINDALCO.NS", "name": "Hindalco Industries", "sector": "Metals / Aluminium"},
    {"symbol": "CIPLA.NS", "name": "Cipla", "sector": "Healthcare / Pharma"},
    {"symbol": "EICHERMOT.NS", "name": "Eicher Motors", "sector": "Automobiles"},
    {"symbol": "SBILIFE.NS", "name": "SBI Life Insurance", "sector": "Financials / Insurance"},
    {"symbol": "DRREDDY.NS", "name": "Dr. Reddy's Laboratories", "sector": "Healthcare / Pharma"},
    {"symbol": "BRITANNIA.NS", "name": "Britannia Industries", "sector": "Consumer FMCG"},
    {"symbol": "PERSISTENT.NS", "name": "Persistent Systems", "sector": "Information Technology"},
    {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp", "sector": "Automobiles"},
    {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals", "sector": "Healthcare / Hospitals"},
    {"symbol": "BPCL.NS", "name": "Bharat Petroleum Corp", "sector": "Energy / Refining"},
    {"symbol": "SHRIRAMFIN.NS", "name": "Shriram Finance", "sector": "Financial Services (NBFC)"},
    {"symbol": "BEL.NS", "name": "Bharat Electronics", "sector": "Defense & Aerospace"},
    {"symbol": "TRENT.NS", "name": "Trent Limited", "sector": "Retail / Consumer"},
    {"symbol": "DIVISLAB.NS", "name": "Divi's Laboratories", "sector": "Healthcare / Pharma"},
    {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank", "sector": "Financials / Banking"},
    {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv", "sector": "Financial Services"},
]

# ==================== 2. NIFTY NEXT 50 (50 LARGE / MIDCAPS) ====================
INDIAN_NIFTY_NEXT_50: List[Dict[str, str]] = [
    {"symbol": "HAL.NS", "name": "Hindustan Aeronautics", "sector": "Defense & Aerospace"},
    {"symbol": "VARUN.NS", "name": "Varun Beverages", "sector": "Consumer FMCG"},
    {"symbol": "ZOMATO.NS", "name": "Zomato Limited", "sector": "Internet / Food Tech"},
    {"symbol": "JIOFIN.NS", "name": "Jio Financial Services", "sector": "Financial Services"},
    {"symbol": "CHOLAFIN.NS", "name": "Cholamandalam Investment", "sector": "Financial Services"},
    {"symbol": "DLF.NS", "name": "DLF Limited", "sector": "Real Estate"},
    {"symbol": "GAIL.NS", "name": "GAIL India", "sector": "Energy / Natural Gas"},
    {"symbol": "GODREJCP.NS", "name": "Godrej Consumer Products", "sector": "Consumer FMCG"},
    {"symbol": "INDIGO.NS", "name": "InterGlobe Aviation (IndiGo)", "sector": "Aviation / Transport"},
    {"symbol": "IRCTC.NS", "name": "IRCTC Limited", "sector": "Railways / Tourism"},
    {"symbol": "MOTHERSON.NS", "name": "Samvardhana Motherson", "sector": "Auto Ancillary"},
    {"symbol": "PIDILITIND.NS", "name": "Pidilite Industries", "sector": "Specialty Chemicals"},
    {"symbol": "POLYCAB.NS", "name": "Polycab India", "sector": "Cables & Electricals"},
    {"symbol": "PNB.NS", "name": "Punjab National Bank", "sector": "Financials / PSU Bank"},
    {"symbol": "RECLTD.NS", "name": "REC Limited", "sector": "Financials / Power Finance"},
    {"symbol": "SIEMENS.NS", "name": "Siemens India", "sector": "Engineering & Capital Goods"},
    {"symbol": "TVSMOTOR.NS", "name": "TVS Motor Company", "sector": "Automobiles"},
    {"symbol": "VEDL.NS", "name": "Vedanta Limited", "sector": "Metals & Mining"},
    {"symbol": "BHEL.NS", "name": "Bharat Heavy Electricals", "sector": "Capital Goods"},
    {"symbol": "CANBK.NS", "name": "Canara Bank", "sector": "Financials / PSU Bank"},
    {"symbol": "DABUR.NS", "name": "Dabur India", "sector": "Consumer FMCG"},
    {"symbol": "HAVELLS.NS", "name": "Havells India", "sector": "Consumer Electricals"},
    {"symbol": "ICICIGI.NS", "name": "ICICI Lombard General Ins", "sector": "Financials / Insurance"},
    {"symbol": "ICICIPRULI.NS", "name": "ICICI Prudential Life", "sector": "Financials / Insurance"},
    {"symbol": "IOC.NS", "name": "Indian Oil Corporation", "sector": "Energy / Refining"},
    {"symbol": "NAUKRI.NS", "name": "Info Edge (Naukri)", "sector": "Internet / Recruitment"},
    {"symbol": "PFC.NS", "name": "Power Finance Corporation", "sector": "Financials / Power Finance"},
    {"symbol": "SRF.NS", "name": "SRF Limited", "sector": "Specialty Chemicals"},
    {"symbol": "TATAPOWER.NS", "name": "Tata Power Company", "sector": "Utilities / Power"},
    {"symbol": "ABB.NS", "name": "ABB India", "sector": "Capital Goods / Automation"},
    {"symbol": "ADANIGREEN.NS", "name": "Adani Green Energy", "sector": "Renewable Energy"},
    {"symbol": "ADANIPOWER.NS", "name": "Adani Power", "sector": "Utilities / Power"},
    {"symbol": "AMBUJACEM.NS", "name": "Ambuja Cements", "sector": "Materials / Cement"},
    {"symbol": "BANKBARODA.NS", "name": "Bank of Baroda", "sector": "Financials / PSU Bank"},
    {"symbol": "BOSCHLTD.NS", "name": "Bosch Limited", "sector": "Auto Ancillary"},
    {"symbol": "CGPOWER.NS", "name": "CG Power and Industrial", "sector": "Capital Goods / Electricals"},
    {"symbol": "COLPAL.NS", "name": "Colgate-Palmolive India", "sector": "Consumer FMCG"},
    {"symbol": "HDFCLIFE.NS", "name": "HDFC Life Insurance", "sector": "Financials / Insurance"},
    {"symbol": "LICI.NS", "name": "Life Insurance Corp (LIC)", "sector": "Financials / Insurance"},
    {"symbol": "MARICO.NS", "name": "Marico Limited", "sector": "Consumer FMCG"},
    {"symbol": "MAXHEALTH.NS", "name": "Max Healthcare Institute", "sector": "Healthcare / Hospitals"},
    {"symbol": "NHPC.NS", "name": "NHPC Limited", "sector": "Utilities / Hydro Power"},
    {"symbol": "SBICARD.NS", "name": "SBI Cards & Payment", "sector": "Financial Services"},
    {"symbol": "TORNTPOWER.NS", "name": "Torrent Power", "sector": "Utilities / Power"},
    {"symbol": "TORNTPHARM.NS", "name": "Torrent Pharmaceuticals", "sector": "Healthcare / Pharma"},
    {"symbol": "MCDOWELL-N.NS", "name": "United Spirits", "sector": "Consumer / Beverages"},
    {"symbol": "BERGEPAINT.NS", "name": "Berger Paints", "sector": "Consumer Paints"},
    {"symbol": "ZYDUSLIFE.NS", "name": "Zydus Lifesciences", "sector": "Healthcare / Pharma"},
    {"symbol": "SOLARINDS.NS", "name": "Solar Industries", "sector": "Industrial Explosives"},
    {"symbol": "PERSISTENT.NS", "name": "Persistent Systems", "sector": "Information Technology"},
]

# ==================== 3. INDIAN COMMODITIES, METALS & ENERGY ====================
INDIAN_COMMODITIES_METALS_ENERGY: List[Dict[str, str]] = [
    # Commodity ETFs & Direct Trackers
    {"symbol": "GOLDBEES.NS", "name": "Nippon Gold ETF", "sector": "Precious Metals (Gold)"},
    {"symbol": "SILVERBEES.NS", "name": "Nippon Silver ETF", "sector": "Precious Metals (Silver)"},
    {"symbol": "SETFGOLD.NS", "name": "SBI Gold ETF", "sector": "Precious Metals (Gold)"},
    {"symbol": "AXISGOLD.NS", "name": "Axis Gold ETF", "sector": "Precious Metals (Gold)"},
    # Base Metals & Mining
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel", "sector": "Base Metals (Steel)"},
    {"symbol": "JSWSTEEL.NS", "name": "JSW Steel", "sector": "Base Metals (Steel)"},
    {"symbol": "HINDALCO.NS", "name": "Hindalco Industries", "sector": "Base Metals (Aluminium/Copper)"},
    {"symbol": "VEDL.NS", "name": "Vedanta Limited", "sector": "Diversified Metals (Zinc/Alum/Oil)"},
    {"symbol": "NATIONALUM.NS", "name": "National Aluminium Co (NALCO)", "sector": "Base Metals (Aluminium)"},
    {"symbol": "JINDALSTEL.NS", "name": "Jindal Steel & Power", "sector": "Base Metals (Steel)"},
    {"symbol": "NMDC.NS", "name": "NMDC Limited", "sector": "Mining (Iron Ore)"},
    {"symbol": "SAIL.NS", "name": "Steel Authority of India", "sector": "Base Metals (Steel)"},
    {"symbol": "HINDZINC.NS", "name": "Hindustan Zinc", "sector": "Base Metals (Zinc/Lead/Silver)"},
    {"symbol": "MOIL.NS", "name": "MOIL Limited", "sector": "Mining (Manganese)"},
    # Energy, Oil, Gas & Coal
    {"symbol": "ONGC.NS", "name": "Oil & Natural Gas Corp", "sector": "Energy (Crude Oil & Gas)"},
    {"symbol": "COALINDIA.NS", "name": "Coal India", "sector": "Energy (Thermal Coal)"},
    {"symbol": "IOC.NS", "name": "Indian Oil Corporation", "sector": "Energy (Refining & Petroleum)"},
    {"symbol": "BPCL.NS", "name": "Bharat Petroleum Corp", "sector": "Energy (Refining & Fuels)"},
    {"symbol": "HPCL.NS", "name": "Hindustan Petroleum Corp", "sector": "Energy (Refining & Fuels)"},
    {"symbol": "GAIL.NS", "name": "GAIL India", "sector": "Energy (Natural Gas Grid)"},
    {"symbol": "OIL.NS", "name": "Oil India Limited", "sector": "Energy (Crude Oil Exploration)"},
    {"symbol": "PETRONET.NS", "name": "Petronet LNG", "sector": "Energy (LNG Terminal)"},
    {"symbol": "IGL.NS", "name": "Indraprastha Gas", "sector": "Energy (City Gas Distribution)"},
    {"symbol": "MGL.NS", "name": "Mahanagar Gas", "sector": "Energy (City Gas Distribution)"},
    {"symbol": "GUJGASLTD.NS", "name": "Gujarat Gas Limited", "sector": "Energy (Industrial Gas)"},
    # Agricultural Commodities, Fertilizers & Agrochem
    {"symbol": "COROMANDEL.NS", "name": "Coromandel International", "sector": "Agri (Fertilizers & Nutrients)"},
    {"symbol": "DEEPAKNTR.NS", "name": "Deepak Nitrite", "sector": "Chemicals / Commodity Intermediates"},
    {"symbol": "PIIND.NS", "name": "PI Industries", "sector": "Agri (Agrochem & CSM)"},
    {"symbol": "TATACHEM.NS", "name": "Tata Chemicals", "sector": "Chemicals (Soda Ash & Agri)"},
    {"symbol": "CHAMBLFERT.NS", "name": "Chambal Fertilisers", "sector": "Agri (Urea & Fertilizers)"},
    {"symbol": "GNFC.NS", "name": "Gujarat Narmada Valley Fert", "sector": "Agri (Fertilizers & Chemicals)"},
    {"symbol": "BALRAMCHIN.NS", "name": "Balrampur Chini Mills", "sector": "Agri (Sugar & Ethanol)"},
    {"symbol": "EIDPARRY.NS", "name": "E.I.D. Parry", "sector": "Agri (Sugar, Bio & Nutraceuticals)"},
]

# ==================== 4. HIGH-ROCE MIDCAP & SMALLCAP COMPOUNDERS ====================
INDIAN_MIDCAP_SMALLCAP_GROWTH: List[Dict[str, str]] = [
    {"symbol": "DIXON.NS", "name": "Dixon Technologies", "sector": "Electronics Manufacturing (EMS)"},
    {"symbol": "KAYNES.NS", "name": "Kaynes Technology", "sector": "Electronics Manufacturing (EMS)"},
    {"symbol": "KPITTECH.NS", "name": "KPIT Technologies", "sector": "Automotive Embedded Software"},
    {"symbol": "COFORGE.NS", "name": "Coforge Limited", "sector": "Information Technology"},
    {"symbol": "TATAELXSI.NS", "name": "Tata Elxsi", "sector": "Design & Technology Software"},
    {"symbol": "CYIENT.NS", "name": "Cyient Limited", "sector": "Engineering & Technology"},
    {"symbol": "SONACOMS.NS", "name": "Sona BLW Precision Forgings", "sector": "Auto Components / EV Driveline"},
    {"symbol": "SUZLON.NS", "name": "Suzlon Energy", "sector": "Renewable Wind Energy"},
    {"symbol": "MAZDOCK.NS", "name": "Mazagon Dock Shipbuilders", "sector": "Defense / Naval Shipbuilding"},
    {"symbol": "COCHINSHIP.NS", "name": "Cochin Shipyard", "sector": "Defense / Commercial Shipbuilding"},
    {"symbol": "BDL.NS", "name": "Bharat Dynamics", "sector": "Defense Missiles & Systems"},
    {"symbol": "ASTRAL.NS", "name": "Astral Limited", "sector": "Building Materials (Pipes/Adhesives)"},
    {"symbol": "SUPREMEIND.NS", "name": "Supreme Industries", "sector": "Plastic Products & Piping"},
    {"symbol": "KEI.NS", "name": "KEI Industries", "sector": "Cables & EPC"},
    {"symbol": "CDSL.NS", "name": "Central Depository Services", "sector": "Capital Markets Infrastructure"},
    {"symbol": "BSE.NS", "name": "BSE Limited", "sector": "Stock Exchange Infrastructure"},
    {"symbol": "ANGELONE.NS", "name": "Angel One Limited", "sector": "Retail Fintech & Brokerage"},
    {"symbol": "MCX.NS", "name": "Multi Commodity Exchange", "sector": "Commodity Exchange Infrastructure"},
    {"symbol": "CAMS.NS", "name": "Computer Age Management", "sector": "Mutual Fund Registrar & Transfer"},
    {"symbol": "KIMS.NS", "name": "Krishna Institute of Med Sci", "sector": "Healthcare / Hospitals"},
    {"symbol": "MEDANTA.NS", "name": "Global Health (Medanta)", "sector": "Healthcare / Super Specialty"},
    {"symbol": "JYOTHYLAB.NS", "name": "Jyothy Labs", "sector": "Consumer FMCG"},
    {"symbol": "RADICO.NS", "name": "Radico Khaitan", "sector": "Consumer / Alcoholic Beverages"},
    {"symbol": "BIKAJI.NS", "name": "Bikaji Foods International", "sector": "Packaged Foods & Snacks"},
    {"symbol": "AIAENG.NS", "name": "AIA Engineering", "sector": "Industrial Grinding Media"},
    {"symbol": "TIMKEN.NS", "name": "Timken India", "sector": "Industrial Bearings"},
    {"symbol": "SCHAEFFLER.NS", "name": "Schaeffler India", "sector": "Precision Bearings"},
    {"symbol": "APLAPOLLO.NS", "name": "APL Apollo Tubes", "sector": "Structural Steel Tubes"},
    {"symbol": "JUBLFOOD.NS", "name": "Jubilant FoodWorks", "sector": "Quick Service Restaurants"},
    {"symbol": "DEVYANI.NS", "name": "Devyani International", "sector": "Quick Service Restaurants"},
]

# ==================== 5. ALL INDIA UNIFIED NSE & BSE UNIVERSE ====================
def get_all_india_universe() -> List[Dict[str, str]]:
    """Combines all unique Indian equities, midcaps, and commodities into a single unified master universe."""
    seen = set()
    master = []
    for u in [INDIAN_NIFTY_50, INDIAN_NIFTY_NEXT_50, INDIAN_COMMODITIES_METALS_ENERGY, INDIAN_MIDCAP_SMALLCAP_GROWTH]:
        for item in u:
            if item["symbol"] not in seen:
                seen.add(item["symbol"])
                master.append(item)
    return master

def format_ticker(symbol: str) -> str:
    """
    Normalizes Indian tickers for NSE (.NS) and BSE (.BO).
    e.g. 'RELIANCE' -> 'RELIANCE.NS', '500325' -> '500325.BO'
    """
    clean_sym = symbol.strip().upper()
    if clean_sym.endswith(".NS") or clean_sym.endswith(".BO"):
        return clean_sym
    
    # BSE Numeric scrip code check
    if clean_sym.isdigit():
        return f"{clean_sym}.BO"
        
    return f"{clean_sym}.NS"
