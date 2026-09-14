"""
Risk Manager & Capital Preservation Engine.
Implements institutional position sizing, ATR-based stop loss calculation,
and exit triggers to ensure asymmetric upside while strictly capping downside.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class RiskManager:
    """
    Calculates disciplined risk-adjusted trade parameters to protect capital.
    """

    @staticmethod
    def calculate_trade_plan(
        stock_price: float,
        history: pd.DataFrame,
        total_portfolio_size: float = 100000.0,
        risk_per_trade_pct: float = 1.5,  # 1.5% max portfolio risk per position
        max_position_size_pct: float = 12.0  # Max 12% capital allocated to single stock
    ) -> Dict[str, Any]:
        """
        Computes dynamic ATR stop-loss, profit targets, and position sizing.
        """
        # Guard against zero or negative stock price
        if stock_price <= 0:
            return {
                "current_price": stock_price,
                "atr_14": 0.0,
                "stop_loss": 0.0,
                "stop_loss_pct": 0.0,
                "target_1": 0.0,
                "target_1_upside_pct": 0.0,
                "target_2": 0.0,
                "target_2_upside_pct": 0.0,
                "risk_reward_ratio": "N/A",
                "recommended_shares": 0,
                "total_investment": 0.0,
                "portfolio_weight_pct": 0.0,
                "max_risk_capital": 0.0,
                "potential_gain_t1": 0.0,
                "potential_gain_t2": 0.0,
                "sizing_alert": (
                    f"Invalid Price Guard: Unit share price ({stock_price}) must be positive (> 0) "
                    f"to calculate trade plan."
                ),
                "capital_preservation_rule": "Strict 2x ATR Trailing Stop Loss. Never risk more than 1.5% of total portfolio on any single trade."
            }

        clean_hist = history.dropna(subset=['High', 'Low', 'Close']) if not history.empty else pd.DataFrame()
        prec = 4 if stock_price < 1.0 else 2
        min_risk = 10 ** (-prec)

        if clean_hist.empty or len(clean_hist) < 14:
            # Fallback static percentage
            stop_loss = round(stock_price * 0.92, prec)  # 8% stop loss
            if stop_loss >= stock_price:
                stop_loss = round(stock_price * 0.90, prec)
            target_1 = round(stock_price * 1.16, prec)   # 1:2 R:R (16%)
            target_2 = round(stock_price * 1.25, prec)   # 1:3+ R:R (25%)
            if target_1 <= stock_price:
                target_1 = round(stock_price * 1.10, prec)
            if target_2 <= target_1:
                target_2 = round(target_1 * 1.05, prec)
            risk_per_share = max(min_risk, stock_price - stop_loss)
            atr_val = round(stock_price * 0.04, prec)
        else:
            # Calculate Average True Range (14-period ATR)
            high_low = clean_hist['High'] - clean_hist['Low']
            high_close = (clean_hist['High'] - clean_hist['Close'].shift()).abs()
            low_close = (clean_hist['Low'] - clean_hist['Close'].shift()).abs()
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1).dropna()
            
            rolling_atr = true_range.rolling(14).mean().dropna()
            atr_val = float(rolling_atr.iloc[-1]) if not rolling_atr.empty and not np.isnan(rolling_atr.iloc[-1]) else stock_price * 0.04
            
            # Dynamic Stop Loss: 2.0x ATR below current price (bounded to sensible minimum 3-15% buffer)
            atr_buffer = min(stock_price * 0.15, max(stock_price * 0.03, 2.0 * atr_val))
            # Relative floor ensures stop loss is strictly below entry price and positive
            stop_loss = round(max(stock_price * 0.50, stock_price - atr_buffer), prec)
            if stop_loss >= stock_price:
                stop_loss = round(stock_price * 0.92, prec)
            risk_per_share = max(min_risk, stock_price - stop_loss)
            
            # Asymmetric Risk-Reward: Target 1 (2x Risk), Target 2 (3.5x Risk)
            target_1 = round(stock_price + (2.0 * risk_per_share), prec)
            target_2 = round(stock_price + (3.5 * risk_per_share), prec)
            if target_1 <= stock_price:
                target_1 = round(stock_price + (2.0 * min_risk), prec)
            if target_2 <= target_1:
                target_2 = round(target_1 + min_risk, prec)

        # Money Management & Position Sizing
        max_capital_to_risk = total_portfolio_size * (risk_per_trade_pct / 100.0)
        
        # Quantity based on risk tolerance
        risk_based_shares = int(max_capital_to_risk / risk_per_share) if risk_per_share > 0 else 0
        
        # Hard cap on single stock position
        max_capital_cap = total_portfolio_size * (max_position_size_pct / 100.0)
        max_shares_cap = int(max_capital_cap / stock_price) if stock_price > 0 else 0
        
        sizing_alert = None
        if stock_price > max_capital_cap:
            recommended_shares = 0
            sizing_alert = (
                f"Capital Overrun Guard: Unit share price ({stock_price:,.2f}) exceeds maximum allowed "
                f"position allocation ({max_capital_cap:,.2f} = {max_position_size_pct}% of {total_portfolio_size:,.2f}). "
                f"Recommended shares set to 0 to prevent portfolio overrun."
            )
        else:
            recommended_shares = max(0, min(risk_based_shares, max_shares_cap))

        total_investment = round(recommended_shares * stock_price, 2)
        portfolio_weight = round((total_investment / total_portfolio_size) * 100, 1) if total_portfolio_size > 0 else 0.0

        risk_amount = round(recommended_shares * (stock_price - stop_loss), 2)
        potential_reward_t1 = round(recommended_shares * (target_1 - stock_price), 2)
        potential_reward_t2 = round(recommended_shares * (target_2 - stock_price), 2)

        return {
            "current_price": stock_price,
            "atr_14": round(atr_val, prec),
            "stop_loss": stop_loss,
            "stop_loss_pct": round(((stop_loss - stock_price) / stock_price) * 100, 2),
            "target_1": target_1,
            "target_1_upside_pct": round(((target_1 - stock_price) / stock_price) * 100, 2),
            "target_2": target_2,
            "target_2_upside_pct": round(((target_2 - stock_price) / stock_price) * 100, 2),
            "risk_reward_ratio": "1 : 2.0 (T1) / 1 : 3.5 (T2)",
            "recommended_shares": recommended_shares,
            "total_investment": total_investment,
            "portfolio_weight_pct": portfolio_weight,
            "max_risk_capital": risk_amount,
            "potential_gain_t1": potential_reward_t1,
            "potential_gain_t2": potential_reward_t2,
            "sizing_alert": sizing_alert,
            "capital_preservation_rule": "Strict 2x ATR Trailing Stop Loss. Never risk more than 1.5% of total portfolio on any single trade."
        }

    @classmethod
    def calculate_position_size(cls, *args, **kwargs) -> Dict[str, Any]:
        """Convenience alias for calculate_trade_plan."""
        return cls.calculate_trade_plan(*args, **kwargs)

