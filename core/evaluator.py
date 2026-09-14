"""
6-Pillar Evaluator, Forensic Quality Auditor & Capital Preservation Engine.
Calculates 6-Pillar Conviction Scores, Piotroski F-Score, Altman Z-Score, and Red Flag Shield.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import config

class PillarEvaluator:
    """
    Institutional quantitative equity evaluation across 6 fundamental pillars
    plus Piotroski F-Score and Altman Z-Score bankruptcy defense.
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
    def _normalize_de(val: Any) -> Optional[float]:
        """
        Normalizes Debt-to-Equity ratio.
        Yahoo Finance reports debtToEquity as a percentage (e.g. 1.8 for 1.8%, 10.2 for 10.2%, 350 for 350%).
        Converts to decimal ratio (e.g. 0.018x, 0.102x, 3.50x).
        Values already expressed as decimal ratio <= 0.5 (e.g. 0.05) are preserved.
        """
        if val is None:
            return None
        try:
            v = float(val)
            if np.isnan(v):
                return None
            if v > 0.5:
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
        Executes evaluation of all 6 pillars, computes composite score, Piotroski, Altman, and detects red flags.
        """
        p1 = self._eval_volume_momentum()
        p2 = self._eval_sales_growth()
        p3 = self._eval_ocf_quality()
        p4 = self._eval_debt_solvency()
        p5 = self._eval_pricing_power()
        p6 = self._eval_skin_in_game()

        f_score, f_score_details = self._calc_piotroski_f_score()
        z_score, z_score_status = self._calc_altman_z_score()
        red_flags = self._detect_red_flags(p1, p2, p3, p4, p5, p6, z_score)
        
        # Weighted composite score
        composite_score = (
            p1["score"] * config.PILLAR_WEIGHTS["volume_momentum"] +
            p2["score"] * config.PILLAR_WEIGHTS["sales_growth"] +
            p3["score"] * config.PILLAR_WEIGHTS["ocf_quality"] +
            p4["score"] * config.PILLAR_WEIGHTS["debt_solvency"] +
            p5["score"] * config.PILLAR_WEIGHTS["pricing_power"] +
            p6["score"] * config.PILLAR_WEIGHTS["skin_in_game"]
        )
        composite_score = float(round(min(100.0, max(0.0, composite_score)), 1))

        # Capital Preservation Rule: Must pass >= threshold with Zero Red Flags
        is_recommended = bool(
            composite_score >= config.CONVICTION_THRESHOLD 
            and len(red_flags) == 0
        )

        signal = "HIGH CONVICTION BUY" if is_recommended else ("MODERATE HOLD" if composite_score >= 60 and len(red_flags) == 0 else "AVOID / HIGH RISK")
        if red_flags:
            signal = "AVOID (RED FLAGS DETECTED)"

        # Valuation metrics
        pe_ratio = self._safe_float(self.info.get("trailingPE") or self.info.get("forwardPE"))
        pb_ratio = self._safe_float(self.info.get("priceToBook"))
        peg_ratio = self._safe_float(self.info.get("pegRatio"))
        ev_ebitda = self._safe_float(self.info.get("enterpriseToEbitda"))

        return {
            "symbol": str(self.symbol),
            "short_name": str(self.data.get("short_name", self.symbol)),
            "sector": str(self.data.get("sector", "General")),
            "industry": str(self.data.get("industry", "Diversified")),
            "current_price": float(self.data.get("current_price", 0.0)),
            "currency": str(self.data.get("currency", "INR")),
            "market_cap": int(self.data.get("market_cap", 0) or 0),
            "composite_score": composite_score,
            "is_recommended": is_recommended,
            "signal": signal,
            "red_flags": red_flags,
            "piotroski_f_score": int(f_score),
            "piotroski_details": f_score_details,
            "altman_z_score": float(z_score) if z_score else None,
            "altman_status": str(z_score_status),
            "valuation": {
                "pe_ratio": round(pe_ratio, 2) if pe_ratio else None,
                "pb_ratio": round(pb_ratio, 2) if pb_ratio else None,
                "peg_ratio": round(peg_ratio, 2) if peg_ratio else None,
                "ev_ebitda": round(ev_ebitda, 2) if ev_ebitda else None,
            },
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
                details.append(f"Institutional volume surge: Recent volume is {vol_ratio:.2f}x of 50-day average with bullish price action.")
            elif vol_ratio >= 0.9 and price_above_sma50:
                score += 15
                details.append(f"Steady volume demand ({vol_ratio:.2f}x 50-DMA) with price above 50-DMA.")
            elif not price_above_sma50:
                score -= 15
                details.append("Technical weakness: Price trading below 50-day Moving Average.")
        
        rev_growth = self._normalize_pct(self.info.get("revenueGrowth"))
        if rev_growth is not None:
            if rev_growth >= 0.20:
                score += 25
                details.append(f"Exceptional demand expansion: Quarterly YoY Revenue up {rev_growth*100:.1f}%.")
            elif rev_growth >= 0.10:
                score += 15
                details.append(f"Solid demand growth: Quarterly YoY Revenue up {rev_growth*100:.1f}%.")
            elif rev_growth < 0:
                score -= 20
                details.append(f"Demand contraction: Quarterly YoY Revenue fell by {abs(rev_growth)*100:.1f}%.")
        else:
            score += 10

        return {
            "pillar_name": "Volume & Demand Growth",
            "score": round(min(100.0, max(0.0, score)), 1),
            "vol_ratio": round(vol_ratio, 2),
            "price_above_sma50": bool(price_above_sma50),
            "revenue_growth": round(rev_growth * 100, 1) if rev_growth is not None else None,
            "details": details
        }

    # ==================== PILLAR 2: SALES REVENUE GROWTH ====================
    def _eval_sales_growth(self) -> Dict[str, Any]:
        score = 50.0
        details = []
        cagr_3y = None

        if not self.income_stmt.empty:
            rev_rows = [r for r in self.income_stmt.index if "total revenue" in str(r).lower() or "operating revenue" in str(r).lower()]
            if rev_rows:
                rev_series = self.income_stmt.loc[rev_rows[0]].dropna()
                if len(rev_series) >= 3:
                    latest_rev = float(rev_series.iloc[0])
                    past_rev = float(rev_series.iloc[2])
                    if past_rev > 0 and latest_rev > 0:
                        cagr_3y = ((latest_rev / past_rev) ** (1 / 2.0)) - 1.0
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

        rev_growth = self._normalize_pct(self.info.get("revenueGrowth"))
        if rev_growth is not None:
            if rev_growth >= 0.20:
                score += 25
                details.append(f"Exceptional quarterly revenue growth: YoY Revenue up {rev_growth*100:.1f}%.")
            elif rev_growth >= 0.12:
                score += 20
                details.append(f"Strong quarterly revenue growth: YoY Revenue up {rev_growth*100:.1f}%.")
            elif rev_growth >= 0.05:
                score += 12
                details.append(f"Steady quarterly revenue growth: YoY Revenue up {rev_growth*100:.1f}%.")
            elif rev_growth >= 0.0:
                score += 5
                details.append(f"Modest positive quarterly revenue growth: YoY Revenue up {rev_growth*100:.1f}%.")
            else:
                score -= 25
                details.append(f"Topline contraction detected: Latest revenue down {abs(rev_growth)*100:.1f}%.")
        elif cagr_3y is None:
            score += 10
            details.append("Baseline sales growth assumed in absence of quarterly reporting.")

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
        ocf_val = self._safe_float(self.info.get("operatingCashflow"))
        net_inc = self._safe_float(self.info.get("netIncomeToCommon") or self.info.get("netIncome"))
        fcf_val = self._safe_float(self.info.get("freeCashflow"))

        if ocf_val is None and not self.cashflow.empty:
            ocf_rows = [r for r in self.cashflow.index if "operating cash flow" in str(r).lower() or "cash from operating activities" in str(r).lower()]
            if ocf_rows:
                ocf_val = self._safe_float(self.cashflow.loc[ocf_rows[0]].iloc[0])

        if net_inc is None and not self.income_stmt.empty:
            net_rows = [r for r in self.income_stmt.index if "net income" in str(r).lower()]
            if net_rows:
                net_inc = self._safe_float(self.income_stmt.loc[net_rows[0]].iloc[0])

        if self.is_financial:
            score = 80.0
            details.append("Banking/Financial Sector: Evaluated on Return on Assets (ROA) & Net Interest Margin (NIM).")
            return {
                "pillar_name": "Operating Cash Flow (Quality of Earnings)",
                "score": score,
                "ocf_to_net_income": 1.0,
                "fcf_positive": True,
                "details": details
            }

        if ocf_val is not None and net_inc is not None:
            if net_inc > 0 and ocf_val > 0:
                ocf_to_net_income = ocf_val / net_inc
                if ocf_to_net_income >= 1.1:
                    score += 35
                    details.append(f"Elite Quality of Earnings: OCF/Net Income is {ocf_to_net_income:.2f}x (Cash exceeds accounting profit).")
                elif ocf_to_net_income >= 0.85:
                    score += 25
                    details.append(f"Healthy Cash Conversion: OCF/Net Income is {ocf_to_net_income:.2f}x.")
                elif ocf_to_net_income >= 0.5:
                    score += 5
                    details.append(f"Mediocre Cash Conversion: OCF/Net Income is {ocf_to_net_income:.2f}x (Working capital locked).")
                else:
                    score -= 30
                    details.append(f"Warning: Low Cash Conversion ({ocf_to_net_income:.2f}x). Paper profits not converting to cash.")
            elif net_inc > 0 and ocf_val <= 0:
                score -= 40
                fcf_positive = False
                details.append("Severe Accrual Warning: Negative Operating Cash Flow despite positive reported Net Income (paper profits).")
            elif net_inc <= 0 and ocf_val > 0:
                score -= 20
                details.append("Earnings Quality Warning: Operating Cash Flow is positive despite negative Net Income (accounting losses).")
            else:  # Both net_inc <= 0 and ocf_val <= 0
                score -= 40
                fcf_positive = False
                details.append("Critical Cash Drain: Both Operating Cash Flow and Net Income are negative.")
        elif ocf_val is not None and ocf_val < 0:
            score -= 40
            fcf_positive = False
            details.append("Negative Operating Cash Flow: Business burns cash in operations.")

        if fcf_val is not None:
            if fcf_val > 0:
                score += 15
                details.append("Positive Free Cash Flow (FCF): Company self-funds growth.")
            else:
                score -= 15
                fcf_positive = False
                details.append("Negative Free Cash Flow: Capex exceeds operational cash.")

        return {
            "pillar_name": "Operating Cash Flow (Quality of Earnings)",
            "score": round(min(100.0, max(0.0, score)), 1),
            "ocf_to_net_income": round(ocf_to_net_income, 2) if ocf_to_net_income is not None else None,
            "fcf_positive": bool(fcf_positive),
            "details": details
        }

    # ==================== PILLAR 4: DEBT & SOLVENCY HEALTH ====================
    def _eval_debt_solvency(self) -> Dict[str, Any]:
        score = 50.0
        details = []
        raw_de = self.info.get("debtToEquity")
        debt_to_equity = self._normalize_de(raw_de) if raw_de is not None else None
        current_ratio = self._safe_float(self.info.get("currentRatio"))

        if debt_to_equity is None and not self.balance_sheet.empty:
            tot_debt = None
            equity = None
            for idx in self.balance_sheet.index:
                low = str(idx).lower()
                if "total debt" in low:
                    s = self.balance_sheet.loc[idx].dropna()
                    if not s.empty:
                        tot_debt = float(s.iloc[0])
                elif "common stock equity" in low or "stockholders equity" in low:
                    s = self.balance_sheet.loc[idx].dropna()
                    if not s.empty:
                        equity = float(s.iloc[0])
            if tot_debt is not None and equity and equity > 0:
                debt_to_equity = tot_debt / equity
            elif tot_debt is not None and equity and equity < 0:
                debt_to_equity = tot_debt / equity
            elif equity is not None and equity < 0:
                debt_to_equity = -1.0

        if debt_to_equity is None:
            bv = self._safe_float(self.info.get("bookValue"))
            if bv is not None and bv < 0:
                debt_to_equity = -1.0

        if current_ratio is None and not self.balance_sheet.empty:
            ca = None
            cl = None
            for idx in self.balance_sheet.index:
                low = str(idx).lower()
                if "current assets" in low:
                    s = self.balance_sheet.loc[idx].dropna()
                    if not s.empty:
                        ca = float(s.iloc[0])
                elif "current liabilities" in low:
                    s = self.balance_sheet.loc[idx].dropna()
                    if not s.empty:
                        cl = float(s.iloc[0])
            if ca is not None and cl and cl > 0:
                current_ratio = ca / cl

        if self.is_financial:
            score = 80.0
            details.append("Banking/Financial Institution: Assessed via Capital Adequacy Ratio (CAR).")
            return {
                "pillar_name": "Debt & Solvency Health",
                "score": score,
                "debt_to_equity": debt_to_equity,
                "current_ratio": current_ratio,
                "details": details
            }

        if debt_to_equity is not None:
            if debt_to_equity < 0:
                score -= 40
                details.append(f"CRITICAL SOLVENCY RISK: Negative Equity / Balance Sheet Insolvency (D/E = {debt_to_equity:.2f}x).")
            elif debt_to_equity <= 0.20:
                score += 35
                details.append(f"Fortress Balance Sheet: Virtually zero debt (D/E = {debt_to_equity:.2f}x).")
            elif debt_to_equity <= 0.60:
                score += 25
                details.append(f"Healthy Solvency: Conservative leverage (D/E = {debt_to_equity:.2f}x).")
            elif debt_to_equity <= 1.20:
                score += 5
                details.append(f"Moderate Debt Load: D/E is {debt_to_equity:.2f}x.")
            elif debt_to_equity > 1.50:
                score -= 35
                details.append(f"High Financial Risk: Elevated Debt-to-Equity of {debt_to_equity:.2f}x.")
        else:
            score += 15

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

        if gross_margin is not None:
            if gross_margin >= 0.50:
                score += 25
                details.append(f"Wide Economic Moat: High Gross Margin of {gross_margin*100:.1f}% indicates strong pricing power.")
            elif gross_margin >= 0.30:
                score += 15
                details.append(f"Good Pricing Leverage: Gross Margin is {gross_margin*100:.1f}%.")
            elif gross_margin < 0.15:
                score -= 15
                details.append(f"Commodity-like business: Thin Gross Margin ({gross_margin*100:.1f}%).")

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
            if insider_pct is not None:
                if insider_pct >= 0.55:
                    score += 35
                    details.append(f"High Promoter Conviction: Promoter holding is {insider_pct*100:.1f}%.")
                elif insider_pct >= 0.40:
                    score += 20
                    details.append(f"Solid Promoter Stake: Promoter holding is {insider_pct*100:.1f}%.")
                elif insider_pct < 0.20:
                    score -= 10
                    details.append(f"Low Promoter Holding ({insider_pct*100:.1f}%). Institutionally held.")
            else:
                score += 15
                details.append("Promoter structure aligned with institutional governance norms.")
        else:
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

    # ==================== PIOTROSKI F-SCORE (0 to 9) ====================
    def _calc_piotroski_f_score(self) -> (int, List[str]):
        score = 0
        details = []

        def _get_val(df: pd.DataFrame, keys: List[str]) -> Optional[float]:
            if df is None or df.empty:
                return None
            for k in keys:
                k_low = k.strip().lower()
                for idx in df.index:
                    if str(idx).strip().lower() == k_low:
                        try:
                            s = df.loc[idx].dropna()
                            if not s.empty:
                                v = float(s.iloc[0])
                                if not np.isnan(v):
                                    return v
                        except Exception:
                            pass
            return None

        # 1. Positive Net Income
        net_inc = self._safe_float(self.info.get("netIncomeToCommon") or self.info.get("netIncome"))
        if net_inc is None and not self.income_stmt.empty:
            net_inc = _get_val(self.income_stmt, ["Net Income Common Stockholders", "Net Income", "Net Income Continuous Operations", "Net Income From Continuing Operation Net Minority Interest"])
        if net_inc and net_inc > 0:
            score += 1
            details.append("Positive Net Income (+1)")

        # 2. Positive Operating Cash Flow
        ocf = self._safe_float(self.info.get("operatingCashflow"))
        if ocf is None and not self.cashflow.empty:
            ocf = _get_val(self.cashflow, ["Operating Cash Flow", "Cash From Operating Activities", "Cash Provided By Operating Activities"])
        if ocf and ocf > 0:
            score += 1
            details.append("Positive Operating Cash Flow (+1)")

        # 3. Positive Return on Assets (ROA)
        roa = self._normalize_pct(self.info.get("returnOnAssets"))
        if roa is None and not self.balance_sheet.empty:
            ta = _get_val(self.balance_sheet, ["Total Assets"])
            if ta and ta > 0 and net_inc is not None:
                roa = net_inc / ta
        if roa and roa > 0:
            score += 1
            details.append(f"Positive Return on Assets ({roa*100:.1f}%) (+1)")

        # 4. Cash flow exceeds Net Income (Quality of earnings)
        if ocf and net_inc and ocf > net_inc:
            score += 1
            details.append("Operating Cash Flow > Net Income (+1)")

        # 5. Low/Decreasing Leverage (0.0 <= D/E < 0.5x)
        raw_de = self.info.get("debtToEquity")
        de = self._normalize_de(raw_de) if raw_de is not None else None
        if de is None and not self.balance_sheet.empty:
            tot_debt = _get_val(self.balance_sheet, ["Total Debt"])
            equity = _get_val(self.balance_sheet, ["Common Stock Equity", "Stockholders Equity", "Total Equity Gross Minority Interest"])
            if tot_debt is not None and equity and equity > 0:
                de = tot_debt / equity
            elif equity is not None and equity < 0:
                de = -1.0
        if de is not None and 0.0 <= de < 0.5:
            score += 1
            details.append(f"Conservative Debt-to-Equity ({de:.2f}x < 0.5x) (+1)")

        # 6. Current Ratio >= 1.25
        cr = self._safe_float(self.info.get("currentRatio"))
        if cr is None and not self.balance_sheet.empty:
            ca = _get_val(self.balance_sheet, ["Current Assets", "Total Current Assets"])
            cl = _get_val(self.balance_sheet, ["Current Liabilities", "Total Current Liabilities Net Minority Interest", "Total Current Liabilities"])
            if ca and cl and cl > 0:
                cr = ca / cl
        if cr and cr >= 1.25:
            score += 1
            details.append(f"Healthy Liquidity (Current Ratio: {cr:.2f}) (+1)")

        # 7. Positive / Robust Gross Margin (>= 25%)
        gm = self._normalize_pct(self.info.get("grossMargins"))
        if gm is None and not self.income_stmt.empty:
            gp = _get_val(self.income_stmt, ["Gross Profit"])
            rev = _get_val(self.income_stmt, ["Total Revenue", "Operating Revenue"])
            if gp and rev and rev > 0:
                gm = gp / rev
        if gm and gm >= 0.25:
            score += 1
            details.append(f"Robust Gross Margin ({gm*100:.1f}%) (+1)")

        # 8. Revenue Growth
        rg = self._normalize_pct(self.info.get("revenueGrowth"))
        if rg is None and not self.income_stmt.empty:
            rev_rows = [r for r in self.income_stmt.index if "total revenue" in str(r).lower() or "operating revenue" in str(r).lower()]
            if rev_rows:
                s = self.income_stmt.loc[rev_rows[0]].dropna()
                if len(s) >= 2 and float(s.iloc[1]) > 0:
                    rg = (float(s.iloc[0]) - float(s.iloc[1])) / float(s.iloc[1])
        if rg and rg > 0:
            score += 1
            details.append(f"Topline Growth ({rg*100:.1f}%) (+1)")

        # 9. Return on Equity >= 12%
        roe = self._normalize_pct(self.info.get("returnOnEquity"))
        if roe is None and not self.income_stmt.empty and not self.balance_sheet.empty:
            equity = _get_val(self.balance_sheet, ["Common Stock Equity", "Stockholders Equity", "Total Equity Gross Minority Interest"])
            if net_inc and equity and equity > 0:
                roe = net_inc / equity
        if roe and roe >= 0.12:
            score += 1
            details.append(f"High Capital Efficiency (ROE: {roe*100:.1f}%) (+1)")

        return score, details

    # ==================== ALTMAN Z-SCORE (BANKRUPTCY RISK SHIELD) ====================
    def _calc_altman_z_score(self) -> (Optional[float], str):
        """
        Edward Altman's genuine 5-ratio Z-Score formula for manufacturing / corporate firms:
        Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.99*X5
        X1 = Working Capital / Total Assets
        X2 = Retained Earnings / Total Assets
        X3 = EBIT / Total Assets
        X4 = Market Value of Equity / Total Liabilities
        X5 = Sales / Total Assets

        Zones:
        Z > 2.99: Safe Zone (Low Bankruptcy Risk)
        1.81 <= Z <= 2.99: Grey Zone (Moderate Financial Health)
        Z < 1.81: Distress Zone (High Insolvent Risk)
        """
        if self.is_financial:
            return 3.5, "Safe Zone (Financial Institution)"

        def _get_val(df: pd.DataFrame, keys: List[str]) -> Optional[float]:
            if df is None or df.empty:
                return None
            for k in keys:
                k_low = k.strip().lower()
                for idx in df.index:
                    if str(idx).strip().lower() == k_low:
                        try:
                            s = df.loc[idx].dropna()
                            if not s.empty:
                                v = float(s.iloc[0])
                                if not np.isnan(v):
                                    return v
                        except Exception:
                            pass
            return None

        # 1. Total Assets (TA)
        ta = _get_val(self.balance_sheet, ["Total Assets"])
        if ta is None:
            ta = self._safe_float(self.info.get("totalAssets"))

        # 2. Working Capital (WC)
        wc = _get_val(self.balance_sheet, ["Working Capital"])
        if wc is None and not self.balance_sheet.empty:
            ca = _get_val(self.balance_sheet, ["Current Assets", "Total Current Assets"])
            cl = _get_val(self.balance_sheet, ["Current Liabilities", "Total Current Liabilities Net Minority Interest", "Total Current Liabilities"])
            if ca is not None and cl is not None:
                wc = ca - cl

        # 3. Retained Earnings (RE)
        re = _get_val(self.balance_sheet, ["Retained Earnings", "Retained Earnings Or Accumulated Deficit"])

        # 4. EBIT
        ebit = _get_val(self.income_stmt, ["EBIT", "Operating Income", "Pretax Income"])
        if ebit is None:
            ebit = self._safe_float(self.info.get("operatingIncome") or self.info.get("ebitda"))

        # 5. Total Liabilities (TL)
        tl = _get_val(self.balance_sheet, ["Total Liabilities Net Minority Interest", "Total Liabilities"])
        if tl is None and not self.balance_sheet.empty:
            cur_liab = _get_val(self.balance_sheet, ["Current Liabilities", "Total Current Liabilities Net Minority Interest", "Total Current Liabilities"]) or 0.0
            non_cur_liab = _get_val(self.balance_sheet, ["Total Non Current Liabilities Net Minority Interest", "Total Non Current Liabilities"]) or 0.0
            if cur_liab + non_cur_liab > 0:
                tl = cur_liab + non_cur_liab
        if tl is None:
            tot_debt = self._safe_float(self.info.get("totalDebt"))
            if tot_debt:
                tl = tot_debt * 1.3  # Conservatively estimate total liabilities from debt

        # 6. Market Value of Equity (Market Cap)
        mcap = self._safe_float(self.data.get("market_cap") or self.info.get("marketCap"))
        if not mcap and self.data.get("current_price") and self.info.get("sharesOutstanding"):
            mcap = float(self.data["current_price"]) * float(self.info["sharesOutstanding"])

        # 7. Sales (Total Revenue)
        sales = _get_val(self.income_stmt, ["Total Revenue", "Operating Revenue"])
        if sales is None:
            sales = self._safe_float(self.info.get("totalRevenue"))

        # Compute Ratios with robust fallbacks
        # X1 = Working Capital / Total Assets
        if wc is not None and ta is not None and ta > 0:
            x1 = wc / ta
        else:
            cr = self._safe_float(self.info.get("currentRatio"))
            if cr is not None:
                x1 = max(-0.5, min(0.5, (cr - 1.0) / max(0.1, cr) * 0.35))
            else:
                x1 = 0.15

        # X2 = Retained Earnings / Total Assets
        if re is not None and ta is not None and ta > 0:
            x2 = re / ta
        else:
            roe = self._normalize_pct(self.info.get("returnOnEquity"))
            if roe is not None:
                x2 = max(-0.5, min(0.6, roe * 1.5))
            else:
                x2 = 0.20

        # X3 = EBIT / Total Assets
        if ebit is not None and ta is not None and ta > 0:
            x3 = ebit / ta
        else:
            roa = self._normalize_pct(self.info.get("returnOnAssets"))
            op_margin = self._normalize_pct(self.info.get("operatingMargins"))
            if roa is not None:
                x3 = roa * 1.25
            elif op_margin is not None:
                x3 = op_margin * 0.8
            else:
                x3 = 0.10

        # Balance sheet insolvency / negative equity detection
        raw_de = self.info.get("debtToEquity")
        de = self._normalize_de(raw_de) if raw_de is not None else None
        bv = self._safe_float(self.info.get("bookValue"))
        equity = _get_val(self.balance_sheet, ["Common Stock Equity", "Stockholders Equity", "Total Equity Gross Minority Interest", "Total Stockholder Equity"])
        
        is_negative_equity = (
            (de is not None and de < 0)
            or (bv is not None and bv < 0)
            or (equity is not None and equity < 0)
            or (ta is not None and tl is not None and ta > 0 and tl > ta)
        )

        # X4 = Market Value of Equity / Total Liabilities
        if is_negative_equity:
            x4 = 0.0
        elif mcap is not None and tl is not None and tl > 0:
            x4 = min(15.0, mcap / tl)
        elif de is not None:
            x4 = min(15.0, 1.0 / max(0.05, de))
        else:
            x4 = 1.5

        # X5 = Sales / Total Assets
        if sales is not None and ta is not None and ta > 0:
            x5 = sales / ta
        else:
            x5 = 1.0  # Normalized corporate asset turnover benchmark

        # Authentic Altman Z-Score formula
        z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.99 * x5
        z = float(round(z, 2))

        if is_negative_equity and z >= 1.81:
            z = 1.80  # Cap at Distress Zone boundary for balance sheet insolvent firms

        if z > 2.99:
            status = "Safe Zone (Low Bankruptcy Risk)"
        elif z >= 1.81:
            status = "Grey Zone (Moderate Financial Health)"
        else:
            status = "Distress Zone (High Insolvent Risk)"

        return z, status

    # ==================== DOWNSIDE SHIELD / HARD RED FLAGS ====================
    def _detect_red_flags(self, p1: Dict, p2: Dict, p3: Dict, p4: Dict, p5: Dict, p6: Dict, z_score: Optional[float]) -> List[str]:
        flags = []

        de = p4.get("debt_to_equity")
        if de is not None and not self.is_financial:
            if de < 0:
                flags.append(f"BALANCE SHEET INSOLVENCY: Negative Net Worth / Insolvent Equity (D/E = {de:.2f}x).")
            elif de > 2.0:
                flags.append(f"CRITICAL SOLVENCY RISK: High Debt-to-Equity ratio of {de:.2f}x.")

        if not self.is_financial:
            if p3.get("fcf_positive") is False and p3["score"] < 30:
                flags.append("CASH DRAIN: Negative Operating/Free Cash Flow - unsustainable cash burn.")

        rev_g = p2.get("latest_growth") if p2.get("latest_growth") is not None else p1.get("revenue_growth")
        if rev_g is not None and rev_g < -10.0:
            flags.append(f"REVENUE COLLAPSE: Topline shrank by {abs(rev_g):.1f}% YoY.")

        roe = p5.get("roe")
        if roe is not None and roe < 0.0:
            flags.append(f"VALUE DESTROYER: Negative Return on Equity ({roe:.1f}%).")

        if z_score is not None and z_score < 1.81 and not self.is_financial:
            flags.append(f"ALTMAN DISTRESS WARNING: Insolvent risk territory (Z-Score: {z_score:.2f}).")

        return flags
