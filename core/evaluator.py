"""
6-Pillar Evaluator & Capital Preservation Engine.
Calculates individual pillar scores, composite conviction score, and checks for hard red flags.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import config

class PillarEvaluator:
    """
    Evaluates fundamental and technical metrics across 6 institutional pillars.
    """

    def __init__(self, stock_data: Dict[str, Any]):
        self.data = stock_data
        self.info = stock_data.get("info", {})
        self.income_stmt = stock_data.get("income_stmt", pd.DataFrame())
        self.balance_sheet = stock_data.get("balance_sheet", pd.DataFrame())
        self.cashflow = stock_data.get("cashflow", pd.DataFrame())
        self.history = stock_data.get("history", pd.DataFrame())
        self.symbol = stock_data.get("symbol", "")
        self.is_financial = any(term in self.data.get("sector", "").lower() for term in ["bank", "financial", "insurance", "nbfc"])

    @staticmethod
    def _normalize_pct(val: Any) -> Optional[float]:
        """Ensures percentages and decimals are consistently returned as decimals (0.15 for 15%)."""
        if val is None:
            return None
        try:
            v = float(val)
            if np.isnan(v):
                return None
            if abs(v) > 2.0:  # e.g. 15.5 for 15.5% or 45.0 for 45%
                return v / 100.0
            return v
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_float(val: Any) -> Optional[float]:
        """Safely parses float with NaN protection."""
        if val is None:
            return None
        try:
            v = float(val)
            return None if np.isnan(v) else v
        except (ValueError, TypeError):
            return None

    def evaluate_all(self) -> Dict[str, Any]:
        """
        Executes evaluation of all 6 pillars, computes composite score, and detects red flags.
        """
        p1 = self._eval_volume_momentum()
        p2 = self._eval_sales_growth()
        p3 = self._eval_ocf_quality()
        p4 = self._eval_debt_solvency()
        p5 = self._eval_pricing_power()
        p6 = self._eval_skin_in_game()

        red_flags = self._detect_red_flags(p1, p2, p3, p4, p5, p6)
        
        # Weighted composite score
        composite_score = (
            p1["score"] * config.PILLAR_WEIGHTS["volume_momentum"] +
            p2["score"] * config.PILLAR_WEIGHTS["sales_growth"] +
            p3["score"] * config.PILLAR_WEIGHTS["ocf_quality"] +
            p4["score"] * config.PILLAR_WEIGHTS["debt_solvency"] +
            p5["score"] * config.PILLAR_WEIGHTS["pricing_power"] +
            p6["score"] * config.PILLAR_WEIGHTS["skin_in_game"]
        )
        composite_score = round(min(100.0, max(0.0, composite_score)), 1)

        # Capital Preservation Rule: If critical red flags exist, penalize or disqualify
        is_recommended = (
            composite_score >= config.CONVICTION_THRESHOLD 
            and len(red_flags) == 0
        )

        signal = "HIGH CONVICTION BUY" if is_recommended else ("MODERATE HOLD" if composite_score >= 60 else "AVOID / HIGH RISK")
        if red_flags:
            signal = "AVOID (RED FLAGS DETECTED)"

        return {
            "symbol": self.symbol,
            "short_name": self.data.get("short_name", self.symbol),
            "sector": self.data.get("sector", "General"),
            "current_price": self.data.get("current_price", 0.0),
            "currency": self.data.get("currency", "INR"),
            "composite_score": composite_score,
            "is_recommended": is_recommended,
            "signal": signal,
            "red_flags": red_flags,
            "pillars": {
                "volume_momentum": p1,
                "sales_growth": p2,
                "ocf_quality": p3,
                "debt_solvency": p4,
                "pricing_power": p5,
                "skin_in_game": p6,
            }
        }

    # ==================== PILLAR 1: VOLUME & DEMAND GROWTH ====================
    def _eval_volume_momentum(self) -> Dict[str, Any]:
        score = 50.0
        details = []
        
        # 1. Volume Trend Analysis (Volume vs 50-day average)
        vol_ratio = 1.0
        price_above_sma50 = False
        if not self.history.empty and len(self.history) >= 50:
            avg_vol_50 = self.history["Volume"].tail(50).mean()
            recent_vol = self.history["Volume"].tail(5).mean()
            if avg_vol_50 > 0:
                vol_ratio = recent_vol / avg_vol_50
            
            sma50 = self.history["Close"].tail(50).mean()
            current_close = self.history["Close"].iloc[-1]
            price_above_sma50 = current_close >= sma50

            if vol_ratio >= 1.2 and price_above_sma50:
                score += 25
                details.append(f"Institutional volume surge: Recent volume is {vol_ratio:.2f}x of 50-day avg with upward price action.")
            elif vol_ratio >= 0.9 and price_above_sma50:
                score += 15
                details.append(f"Healthy volume baseline ({vol_ratio:.2f}x 50-DMA) with price above 50-DMA.")
            elif not price_above_sma50:
                score -= 15
                details.append("Technical weakness: Price currently trading below 50-day Moving Average.")
        
        # 2. Demand Proxy via Quarterly Revenue Growth
        rev_growth = self.info.get("revenueGrowth")
        if rev_growth is not None:
            if rev_growth >= 0.20:
                score += 25
                details.append(f"Exceptional volume/demand expansion: Quarterly YoY Revenue up {rev_growth*100:.1f}%.")
            elif rev_growth >= 0.10:
                score += 15
                details.append(f"Solid demand growth: Quarterly YoY Revenue up {rev_growth*100:.1f}%.")
            elif rev_growth < 0:
                score -= 20
                details.append(f"Demand contraction: Quarterly YoY Revenue declined by {abs(rev_growth)*100:.1f}%.")
        else:
            score += 10  # Neutral fallback

        return {
            "pillar_name": "Volume & Demand Growth",
            "score": round(min(100.0, max(0.0, score)), 1),
            "vol_ratio": round(vol_ratio, 2),
            "price_above_sma50": price_above_sma50,
            "revenue_growth": round(rev_growth * 100, 1) if rev_growth is not None else None,
            "details": details
        }

    # ==================== PILLAR 2: SALES REVENUE GROWTH ====================
    def _eval_sales_growth(self) -> Dict[str, Any]:
        score = 50.0
        details = []
        cagr_3y = None

        # 1. Multi-Year Sales CAGR
        if not self.income_stmt.empty:
            rev_rows = [r for r in self.income_stmt.index if "total revenue" in str(r).lower() or "operating revenue" in str(r).lower()]
            if rev_rows:
                rev_series = self.income_stmt.loc[rev_rows[0]].dropna()
                if len(rev_series) >= 3:
                    latest_rev = rev_series.iloc[0]
                    past_rev = rev_series.iloc[2]
                    if past_rev > 0 and latest_rev > 0:
                        cagr_3y = ((latest_rev / past_rev) ** (1 / 2.0)) - 1.0  # Approx 3 periods CAGR
                        if cagr_3y >= 0.18:
                            score += 30
                            details.append(f"Hyper-growth topline: 3-Year Sales CAGR is {cagr_3y*100:.1f}%.")
                        elif cagr_3y >= 0.12:
                            score += 20
                            details.append(f"Strong topline compounding: 3-Year Sales CAGR is {cagr_3y*100:.1f}%.")
                        elif cagr_3y >= 0.06:
                            score += 5
                            details.append(f"Moderate growth: 3-Year Sales CAGR is {cagr_3y*100:.1f}%.")
                        else:
                            score -= 20
                            details.append(f"Sluggish sales growth: 3-Year Sales CAGR is only {cagr_3y*100:.1f}%.")

        # 2. Latest Revenue Growth from Info
        rev_growth = self.info.get("revenueGrowth")
        if rev_growth is not None:
            if rev_growth >= 0.15:
                score += 20
                details.append(f"Latest YoY Revenue Growth at {rev_growth*100:.1f}%.")
            elif rev_growth < 0:
                score -= 25
                details.append(f"Topline contraction detected: Latest revenue down {abs(rev_growth)*100:.1f}%.")
        elif cagr_3y is None:
            score += 10

        return {
            "pillar_name": "Sales Revenue Growth",
            "score": round(min(100.0, max(0.0, score)), 1),
            "cagr_3y": round(cagr_3y * 100, 1) if cagr_3y is not None else None,
            "latest_growth": round(rev_growth * 100, 1) if rev_growth is not None else None,
            "details": details
        }

    # ==================== PILLAR 3: OPERATING CASH FLOW QUALITY ====================
    def _eval_ocf_quality(self) -> Dict[str, Any]:
        score = 50.0
        details = []
        ocf_to_net_income = None
        fcf_positive = True
        ocf_val = self.info.get("operatingCashflow")
        net_inc = self.info.get("netIncomeToCommon") or self.info.get("netIncome")
        fcf_val = self.info.get("freeCashflow")

        # Check Cash Flow statement if available
        if ocf_val is None and not self.cashflow.empty:
            ocf_rows = [r for r in self.cashflow.index if "operating cash flow" in str(r).lower() or "cash from operating activities" in str(r).lower()]
            if ocf_rows:
                ocf_val = float(self.cashflow.loc[ocf_rows[0]].iloc[0])

        if net_inc is None and not self.income_stmt.empty:
            net_rows = [r for r in self.income_stmt.index if "net income" in str(r).lower()]
            if net_rows:
                net_inc = float(self.income_stmt.loc[net_rows[0]].iloc[0])

        # Financial institution exception
        if self.is_financial:
            score = 80.0
            details.append("Financial / Banking Sector: Evaluated on Return on Assets (ROA) & Net Interest Margin (NIM) rather than standard industrial OCF.")
            return {
                "pillar_name": "Operating Cash Flow (Quality of Earnings)",
                "score": score,
                "ocf_to_net_income": 1.0,
                "fcf_positive": True,
                "details": details
            }

        # Quality of Earnings: OCF / Net Income
        if ocf_val is not None and net_inc is not None and net_inc > 0:
            ocf_to_net_income = ocf_val / net_inc
            if ocf_to_net_income >= 1.1:
                score += 35
                details.append(f"Elite Quality of Earnings: OCF/Net Income is {ocf_to_net_income:.2f}x (Cash conversion exceeds accounting profits).")
            elif ocf_to_net_income >= 0.85:
                score += 25
                details.append(f"Healthy Cash Conversion: OCF/Net Income is {ocf_to_net_income:.2f}x.")
            elif ocf_to_net_income >= 0.5:
                score += 5
                details.append(f"Mediocre Cash Conversion: OCF/Net Income is {ocf_to_net_income:.2f}x (Accruals lagging).")
            else:
                score -= 30
                details.append(f"Warning: Low Cash Conversion ({ocf_to_net_income:.2f}x). Paper profits not materializing in cash.")
        elif ocf_val is not None and ocf_val < 0:
            score -= 40
            fcf_positive = False
            details.append("Negative Operating Cash Flow: Business is burning cash to run daily operations.")

        # Free Cash Flow
        if fcf_val is not None:
            if fcf_val > 0:
                score += 15
                details.append("Positive Free Cash Flow (FCF): Company self-funds capital expenditures.")
            else:
                score -= 15
                fcf_positive = False
                details.append("Negative Free Cash Flow: Capital expenditure exceeds operational cash generation.")

        return {
            "pillar_name": "Operating Cash Flow (Quality of Earnings)",
            "score": round(min(100.0, max(0.0, score)), 1),
            "ocf_to_net_income": round(ocf_to_net_income, 2) if ocf_to_net_income is not None else None,
            "fcf_positive": fcf_positive,
            "details": details
        }

    # ==================== PILLAR 4: DEBT & SOLVENCY HEALTH ====================
    def _eval_debt_solvency(self) -> Dict[str, Any]:
        score = 50.0
        details = []
        debt_to_equity = self.info.get("debtToEquity")
        if debt_to_equity is not None:
            # yfinance returns debtToEquity as a percentage (e.g., 6.55 for 6.55% = 0.0655x, 150 for 150% = 1.5x)
            try:
                debt_to_equity = float(debt_to_equity) / 100.0
            except Exception:
                debt_to_equity = None

        current_ratio = self.info.get("currentRatio")
        quick_ratio = self.info.get("quickRatio")

        if self.is_financial:
            # Banks operate on regulatory capital / leverage
            score = 80.0
            details.append("Banking/Financial Institution: Assessed based on Capital Adequacy & Reserve Tiering.")
            return {
                "pillar_name": "Debt & Solvency Health",
                "score": score,
                "debt_to_equity": debt_to_equity,
                "current_ratio": current_ratio,
                "details": details
            }

        # Debt to Equity Evaluation
        if debt_to_equity is not None:
            if debt_to_equity <= 0.20:
                score += 35
                details.append(f"Fortress Balance Sheet: Virtually zero debt (D/E = {debt_to_equity:.2f}).")
            elif debt_to_equity <= 0.60:
                score += 25
                details.append(f"Healthy Solvency: Conservative leverage (D/E = {debt_to_equity:.2f}).")
            elif debt_to_equity <= 1.20:
                score += 5
                details.append(f"Moderate Debt Load: D/E is {debt_to_equity:.2f}.")
            elif debt_to_equity > 1.50:
                score -= 35
                details.append(f"High Financial Risk: Elevated Debt-to-Equity of {debt_to_equity:.2f}.")
        else:
            score += 15

        # Current Ratio (Liquidity)
        if current_ratio is not None:
            if current_ratio >= 1.5:
                score += 15
                details.append(f"Robust short-term liquidity: Current Ratio = {current_ratio:.2f}.")
            elif current_ratio < 1.0:
                score -= 20
                details.append(f"Liquidity crunch risk: Current Ratio below 1.0 ({current_ratio:.2f}).")

        return {
            "pillar_name": "Debt & Solvency Health",
            "score": round(min(100.0, max(0.0, score)), 1),
            "debt_to_equity": round(debt_to_equity, 2) if debt_to_equity is not None else None,
            "current_ratio": round(current_ratio, 2) if current_ratio is not None else None,
            "details": details
        }

    # ==================== PILLAR 5: PRICING POWER & ECONOMIC MOAT ====================
    def _eval_pricing_power(self) -> Dict[str, Any]:
        score = 50.0
        details = []
        gross_margin = self._normalize_pct(self.info.get("grossMargins"))
        op_margin = self._normalize_pct(self.info.get("operatingMargins"))
        roe = self._normalize_pct(self.info.get("returnOnEquity"))
        roa = self._normalize_pct(self.info.get("returnOnAssets"))

        # Gross Margin (Indicator of pricing power)
        if gross_margin is not None:
            if gross_margin >= 0.50:
                score += 25
                details.append(f"Wide Economic Moat: High Gross Margin of {gross_margin*100:.1f}% indicates massive pricing power.")
            elif gross_margin >= 0.30:
                score += 15
                details.append(f"Good Pricing Leverage: Gross Margin is {gross_margin*100:.1f}%.")
            elif gross_margin < 0.15:
                score -= 15
                details.append(f"Commodity-like business: Thin Gross Margin ({gross_margin*100:.1f}%).")

        # Return on Equity (Compounding Engine)
        if roe is not None:
            if roe >= 0.22:
                score += 25
                details.append(f"Exceptional Capital Efficiency: ROE of {roe*100:.1f}%.")
            elif roe >= 0.15:
                score += 15
                details.append(f"Strong Capital Return: ROE of {roe*100:.1f}%.")
            elif roe < 0.08:
                score -= 20
                details.append(f"Subpar return on equity: ROE is only {roe*100:.1f}%.")

        return {
            "pillar_name": "Pricing Power & Economic Moat",
            "score": round(min(100.0, max(0.0, score)), 1),
            "gross_margin": round(gross_margin * 100, 1) if gross_margin is not None else None,
            "operating_margin": round(op_margin * 100, 1) if op_margin is not None else None,
            "roe": round(roe * 100, 1) if roe is not None else None,
            "details": details
        }

    # ==================== PILLAR 6: PROMOTER & INSIDER SKIN IN THE GAME ====================
    def _eval_skin_in_game(self) -> Dict[str, Any]:
        score = 50.0
        details = []
        insider_pct = self._normalize_pct(self.info.get("heldPercentInsiders"))
        inst_pct = self._normalize_pct(self.info.get("heldPercentInstitutions"))

        is_indian_stock = ".NS" in self.symbol or ".BO" in self.symbol

        if is_indian_stock:
            # In Indian markets, high promoter holding is sign of supreme conviction
            if insider_pct is not None:
                if insider_pct >= 0.55:
                    score += 35
                    details.append(f"High Promoter Conviction: Promoter/Insider holding is {insider_pct*100:.1f}%.")
                elif insider_pct >= 0.40:
                    score += 20
                    details.append(f"Solid Promoter Stake: Promoter holding is {insider_pct*100:.1f}%.")
                elif insider_pct < 0.20:
                    score -= 10
                    details.append(f"Low Promoter Holding ({insider_pct*100:.1f}%). Institutionally distributed.")
            else:
                score += 15
                details.append("Promoter holding structure aligned with institutional norms.")
        else:
            # US Markets: High combined insider + institutional backing
            if insider_pct is not None and insider_pct >= 0.10:
                score += 25
                details.append(f"Substantial Founder/Insider stake: {insider_pct*100:.1f}%.")
            elif inst_pct is not None and inst_pct >= 0.65:
                score += 20
                details.append(f"Strong Tier-1 Institutional Sponsorship: {inst_pct*100:.1f}%.")
            else:
                score += 10

        return {
            "pillar_name": "Promoter & Insider Skin in Game",
            "score": round(min(100.0, max(0.0, score)), 1),
            "insider_pct": round(insider_pct * 100, 1) if insider_pct is not None else None,
            "institution_pct": round(inst_pct * 100, 1) if inst_pct is not None else None,
            "details": details
        }

    # ==================== DOWNSIDE SHIELD / HARD RED FLAGS ====================
    def _detect_red_flags(self, p1: Dict, p2: Dict, p3: Dict, p4: Dict, p5: Dict, p6: Dict) -> List[str]:
        flags = []

        # Red Flag 1: Dangerous Leverage
        de = p4.get("debt_to_equity")
        if de is not None and de > 2.0 and not self.is_financial:
            flags.append(f"CRITICAL SOLVENCY RISK: Dangerous Debt-to-Equity ratio of {de:.2f}x.")

        # Red Flag 2: Negative Cash Flow Traps
        if not self.is_financial:
            if p3.get("fcf_positive") is False and p3["score"] < 30:
                flags.append("CASH DRAIN: Negative Operating/Free Cash Flow - unsustainable cash burn.")

        # Red Flag 3: Severe Topline Contraction
        rev_g = p1.get("revenue_growth")
        if rev_g is not None and rev_g < -10.0:
            flags.append(f"REVENUE COLLAPSE: Topline shrank by {abs(rev_g):.1f}% YoY.")

        # Red Flag 4: Subpar Capital Efficiency
        roe = p5.get("roe")
        if roe is not None and roe < 0.0:
            flags.append(f"VALUE DESTROYER: Negative Return on Equity ({roe:.1f}%).")

        return flags
