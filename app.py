"""
ALPHA6 | Institutional Equity Intelligence Terminal
Designed for Institutional Precision, High-Contrast Readability & Capital Preservation.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# Import Core Analytical Engine
from core.data_fetcher import StockDataFetcher
from core.evaluator import PillarEvaluator
from core.backtester import StockBacktester
from core.risk_manager import RiskManager
from core.universe import (
    INDIAN_NIFTY_50, 
    INDIAN_QUALITY_GROWTH, 
    GLOBAL_US_MEGA_TECH, 
    format_ticker
)
import config

# Set Page Config
st.set_page_config(
    page_title="ALPHA6 | Equity Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inline Clean Vector Logo
LOGO_SVG = '<svg width="34" height="34" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" style="display:inline-block; vertical-align:middle;"><rect width="36" height="36" rx="8" fill="#0F172A" stroke="#334155" stroke-width="1.5"/><path d="M18 7L28 12.8V24.2L18 30L8 24.2V12.8L18 7Z" stroke="#38BDF8" stroke-width="2.2" stroke-linejoin="round"/><path d="M18 7V30M8 12.8L28 24.2M8 24.2L28 12.8" stroke="#38BDF8" stroke-width="1.2" stroke-opacity="0.4"/><circle cx="18" cy="18.5" r="3.2" fill="#10B981"/></svg>'

# Inject Global CSS via st.html
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

.stApp {
    background-color: #080C14;
    color: #F1F5F9;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 16px;
}

.brand-navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #0E1524;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 14px 20px;
    margin-bottom: 20px;
}

.brand-title-group {
    display: flex;
    align-items: center;
    gap: 14px;
}

.brand-name {
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #FFFFFF;
    line-height: 1.1;
}

.brand-subtitle {
    font-size: 0.9rem;
    color: #94A3B8;
    font-weight: 500;
    margin-top: 3px;
}

.status-badge-live {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.35);
    padding: 6px 14px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 700;
}

h1 { font-size: 1.8rem !important; font-weight: 800 !important; color: #FFFFFF !important; }
h2 { font-size: 1.5rem !important; font-weight: 700 !important; color: #FFFFFF !important; }
h3 { font-size: 1.25rem !important; font-weight: 700 !important; color: #F8FAFC !important; }
h4 { font-size: 1.05rem !important; font-weight: 600 !important; color: #F8FAFC !important; }

p, span, label {
    font-size: 0.95rem !important;
    color: #94A3B8;
}

div[data-testid="stMetric"] {
    background-color: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 14px 18px;
}

div[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
}

div[data-testid="stMetricLabel"] {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    color: #94A3B8 !important;
}

.terminal-card {
    background-color: #0F172A;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 18px;
    margin-bottom: 14px;
}

.badge-pass {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.4);
    padding: 3px 10px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
}

.badge-hold {
    background-color: rgba(245, 158, 11, 0.15);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.4);
    padding: 3px 10px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
}

.badge-risk {
    background-color: rgba(239, 68, 68, 0.15);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.4);
    padding: 3px 10px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    font-weight: 700;
}

section[data-testid="stSidebar"] {
    background-color: #05080E;
    border-right: 1px solid #1E293B;
}

.stTextInput input, .stSelectbox select, .stNumberInput input {
    background-color: #0F172A !important;
    color: #FFFFFF !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
    font-size: 1rem !important;
    padding: 8px 12px !important;
}

button[data-baseweb="tab"] {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #94A3B8 !important;
    padding: 10px 18px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #38BDF8 !important;
    border-bottom: 2px solid #38BDF8 !important;
}

button[kind="primary"] {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    padding: 8px 20px !important;
}

button[kind="primary"]:hover {
    background-color: #1D4ED8 !important;
}
</style>
""")

# ----------------- SIDEBAR BRANDING & CONTROLS -----------------
with st.sidebar:
    st.html(f"""
    <div style="display:flex; align-items:center; gap:12px; padding-bottom:14px; border-bottom:1px solid #1E293B; margin-bottom:18px;">
        {LOGO_SVG}
        <div>
            <div style="font-size:1.25rem; font-weight:800; color:#FFFFFF; letter-spacing:-0.02em;">ALPHA6</div>
            <div style="font-size:0.75rem; color:#64748B; font-weight:600; text-transform:uppercase;">Equity Terminal</div>
        </div>
    </div>
    """)

    st.markdown("#### Screening Parameters")
    
    market_option = st.selectbox(
        "Market Universe",
        ["Indian Nifty 50", "Indian Quality Growth", "US Tech Leaders", "Custom Watchlist"],
        index=0
    )

    threshold = st.slider(
        "Conviction Threshold (%)",
        min_value=60,
        max_value=90,
        value=int(config.CONVICTION_THRESHOLD),
        step=1
    )

    st.markdown("---")
    st.markdown("#### Portfolio Risk Model")
    portfolio_capital = st.number_input(
        "Total Portfolio Capital",
        min_value=10000.0,
        max_value=100000000.0,
        value=100000.0,
        step=10000.0,
        format="%.0f"
    )
    risk_per_trade = st.slider(
        "Max Risk per Trade (%)",
        min_value=0.5,
        max_value=3.0,
        value=1.5,
        step=0.1
    )

# ----------------- TOP BRAND NAVBAR HEADER -----------------
st.html(f"""
<div class="brand-navbar">
    <div class="brand-title-group">
        {LOGO_SVG}
        <div>
            <div class="brand-name">ALPHA6 QUANTITATIVE TERMINAL</div>
            <div class="brand-subtitle">Institutional 6-Pillar Fundamental Screener & Downside Protection Engine</div>
        </div>
    </div>
    <div style="text-align: right;">
        <span class="status-badge-live">SYSTEM ONLINE</span>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #64748B; margin-top: 4px;">
            THRESHOLD: {threshold}%
        </div>
    </div>
</div>
""")

# ----------------- TABS -----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Universe Screener", 
    "Pillar Diagnostics", 
    "Backtest Simulation", 
    "Position Sizing & Risk"
])

# =========================================================================
# TAB 1: UNIVERSE SCREENER
# =========================================================================
with tab1:
    if market_option == "Indian Nifty 50":
        tickers_to_scan = INDIAN_NIFTY_50
    elif market_option == "Indian Quality Growth":
        tickers_to_scan = INDIAN_QUALITY_GROWTH
    elif market_option == "US Tech Leaders":
        tickers_to_scan = GLOBAL_US_MEGA_TECH
    else:
        custom_input = st.text_input("Enter comma-separated tickers:", "TCS.NS, RELIANCE.NS, NVDA, AAPL, HAL.NS")
        tickers_to_scan = [{"symbol": s.strip(), "name": s.strip(), "sector": "Custom"} for s in custom_input.split(",") if s.strip()]

    col_btn, col_blank = st.columns([1, 4])
    with col_btn:
        scan_button = st.button("Run Quantitative Scan", type="primary")

    if scan_button or "scan_results" not in st.session_state:
        results = []
        progress_bar = st.progress(0.0)
        status_text = st.empty()

        for idx, item in enumerate(tickers_to_scan):
            sym = item["symbol"]
            status_text.text(f"Auditing {sym} ({idx+1}/{len(tickers_to_scan)})...")
            data = StockDataFetcher.get_stock_data(sym)
            if data:
                evaluator = PillarEvaluator(data)
                res = evaluator.evaluate_all()
                results.append({
                    "Symbol": sym,
                    "Name": res["short_name"],
                    "Sector": res["sector"],
                    "Price": f"{res['currency']} {res['current_price']:.2f}",
                    "Composite Score": res["composite_score"],
                    "Volume Growth": res["pillars"]["volume_momentum"]["score"],
                    "Sales CAGR": res["pillars"]["sales_growth"]["score"],
                    "OCF Quality": res["pillars"]["ocf_quality"]["score"],
                    "Debt Health": res["pillars"]["debt_solvency"]["score"],
                    "Pricing Power": res["pillars"]["pricing_power"]["score"],
                    "Insider Stake": res["pillars"]["skin_in_game"]["score"],
                    "Signal": res["signal"],
                    "Pass": res["is_recommended"] and res["composite_score"] >= threshold,
                    "Red Flags": len(res["red_flags"]),
                    "Raw": res,
                    "Data": data
                })
            progress_bar.progress((idx + 1) / len(tickers_to_scan))

        status_text.empty()
        progress_bar.empty()
        st.session_state.scan_results = results

    if "scan_results" in st.session_state and st.session_state.scan_results:
        res_list = st.session_state.scan_results
        df_results = pd.DataFrame(res_list)

        high_conviction = [r for r in res_list if r["Composite Score"] >= threshold and r["Red Flags"] == 0]
        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        
        with col_kpi1:
            st.metric("Total Equities Scanned", len(res_list))
        with col_kpi2:
            st.metric(f"High-Conviction (>={threshold}%)", len(high_conviction), delta=f"{len(high_conviction)/len(res_list)*100:.0f}% Pass Rate")
        with col_kpi3:
            avg_score = np.mean([r["Composite Score"] for r in res_list])
            st.metric("Universe Average Score", f"{avg_score:.1f}%")
        with col_kpi4:
            red_flag_count = sum(1 for r in res_list if r["Red Flags"] > 0)
            st.metric("Flagged Risk Securities", red_flag_count)

        if high_conviction:
            st.markdown("### Top Investment-Grade Selections")
            cols = st.columns(min(len(high_conviction), 3))
            for i, pick in enumerate(high_conviction[:3]):
                with cols[i]:
                    st.html(f"""
                    <div class="terminal-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <span style="font-size:1.2rem; font-weight:800; color:#FFFFFF;">{pick['Symbol']}</span>
                            <span class="badge-pass">{pick['Composite Score']}% SCORE</span>
                        </div>
                        <div style="font-size:0.85rem; color:#94A3B8; margin-bottom:10px;">{pick['Name']}</div>
                        <div style="font-family:'JetBrains Mono', monospace; font-size:1.3rem; font-weight:800; color:#FFFFFF; margin-bottom:8px;">{pick['Price']}</div>
                        <div style="font-size:0.8rem; color:#CBD5E1;">Operating Cash Flow: <b>{pick['OCF Quality']}/100</b></div>
                        <div style="font-size:0.8rem; color:#CBD5E1;">Debt & Solvency: <b>{pick['Debt Health']}/100</b></div>
                    </div>
                    """)

        st.markdown("### Universe Ranking Matrix")
        display_df = df_results[["Symbol", "Name", "Sector", "Price", "Composite Score", "Volume Growth", "Sales CAGR", "OCF Quality", "Debt Health", "Pricing Power", "Insider Stake", "Signal", "Red Flags"]].sort_values(by="Composite Score", ascending=False)
        st.dataframe(
            display_df,
            width="stretch",
            column_config={
                "Composite Score": st.column_config.ProgressColumn(
                    "Score",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
            }
        )

# =========================================================================
# TAB 2: PILLAR DIAGNOSTICS
# =========================================================================
with tab2:
    col_search, col_space = st.columns([2, 2])
    with col_search:
        selected_ticker = st.text_input("Inspect Security Ticker:", "RELIANCE.NS").strip().upper()
    
    if selected_ticker:
        norm_ticker = format_ticker(selected_ticker)
        with st.spinner(f"Executing deep audit on {norm_ticker}..."):
            stock_data = StockDataFetcher.get_stock_data(norm_ticker)

        if not stock_data:
            st.error(f"Data unavailable for symbol '{selected_ticker}'. Ensure correct suffix (e.g. .NS for NSE).")
        else:
            evaluator = PillarEvaluator(stock_data)
            eval_res = evaluator.evaluate_all()
            p = eval_res["pillars"]

            col_info1, col_info2, col_info3 = st.columns([2, 1, 1])
            with col_info1:
                st.markdown(f"## {eval_res['short_name']}")
                st.markdown(f"**Symbol:** `{eval_res['symbol']}` | **Sector:** `{eval_res['sector']}`")
            with col_info2:
                st.metric("Current Market Price", f"{eval_res['currency']} {eval_res['current_price']:.2f}")
            with col_info3:
                badge_class = "badge-pass" if eval_res["is_recommended"] else ("badge-risk" if eval_res["red_flags"] else "badge-hold")
                st.html(f"""
                <div style="text-align:right;">
                    <div style="font-size:0.75rem; text-transform:uppercase; color:#94A3B8; font-weight:600;">Composite Score</div>
                    <div style="font-family:'JetBrains Mono', monospace; font-size:1.8rem; font-weight:800; color:#FFFFFF;">{eval_res['composite_score']}%</div>
                    <span class="{badge_class}">{eval_res['signal']}</span>
                </div>
                """)

            if eval_res["red_flags"]:
                st.markdown("### Risk Shield Warnings")
                for rf in eval_res["red_flags"]:
                    st.html(f"<div style='background-color:rgba(239,68,68,0.12); border-left:4px solid #EF4444; padding:8px 14px; margin-bottom:6px; color:#FCA5A5; font-size:0.9rem; font-weight:600;'>{rf}</div>")

            col_radar, col_breakdown = st.columns([1, 1])

            with col_radar:
                st.markdown("### 6-Pillar Radar Fingerprint")
                categories = [
                    "Volume Growth", 
                    "Sales CAGR", 
                    "OCF Quality", 
                    "Debt Health", 
                    "Pricing Power", 
                    "Insider Stake"
                ]
                values = [
                    p["volume_momentum"]["score"],
                    p["sales_growth"]["score"],
                    p["ocf_quality"]["score"],
                    p["debt_solvency"]["score"],
                    p["pricing_power"]["score"],
                    p["skin_in_game"]["score"],
                ]
                values.append(values[0])
                categories.append(categories[0])

                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    fillcolor='rgba(56, 189, 248, 0.18)',
                    line=dict(color='#38BDF8', width=2),
                    name=eval_res['symbol']
                ))
                fig_radar.add_trace(go.Scatterpolar(
                    r=[78]*len(categories),
                    theta=categories,
                    mode='lines',
                    line=dict(color='#10B981', width=1.5, dash='dash'),
                    name='78% Conviction Benchmark'
                ))
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], color='#64748B', tickfont=dict(size=11, color='#94A3B8')),
                        bgcolor='#0F172A'
                    ),
                    paper_bgcolor='#080C14',
                    font=dict(color='#E2E8F0', size=12),
                    margin=dict(l=40, r=40, t=20, b=20),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_radar, width="stretch")

            with col_breakdown:
                st.markdown("### Itemized Pillar Scorecard")
                for key, name in [
                    ("volume_momentum", "1. Volume Growth & Momentum"),
                    ("sales_growth", "2. Sales Revenue CAGR"),
                    ("ocf_quality", "3. Operating Cash Flow Quality"),
                    ("debt_solvency", "4. Debt & Solvency Health"),
                    ("pricing_power", "5. Pricing Power & Moat"),
                    ("skin_in_game", "6. Insider & Promoter Stake"),
                ]:
                    item = p[key]
                    score_val = item["score"]
                    with st.expander(f"{name} — {score_val}/100", expanded=(score_val < 60 or score_val >= 80)):
                        for d in item.get("details", []):
                            st.markdown(f"- **{d}**")

            if not stock_data["history"].empty:
                st.markdown("### Technical Price Baseline & Moving Averages")
                hist = stock_data["history"]
                hist["SMA50"] = hist["Close"].rolling(50).mean()
                hist["SMA200"] = hist["Close"].rolling(200).mean()

                fig_price = go.Figure()
                fig_price.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Close Price", line=dict(color="#FFFFFF", width=2)))
                fig_price.add_trace(go.Scatter(x=hist.index, y=hist["SMA50"], name="50-DMA", line=dict(color="#38BDF8", width=1.5, dash="dot")))
                fig_price.add_trace(go.Scatter(x=hist.index, y=hist["SMA200"], name="200-DMA", line=dict(color="#F59E0B", width=1.5, dash="dash")))

                fig_price.update_layout(
                    paper_bgcolor='#080C14',
                    plot_bgcolor='#0F172A',
                    font=dict(color='#94A3B8', size=12),
                    xaxis=dict(gridcolor='#1E293B'),
                    yaxis=dict(gridcolor='#1E293B', title=f"Price ({eval_res['currency']})"),
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=300
                )
                st.plotly_chart(fig_price, width="stretch")

# =========================================================================
# TAB 3: BACKTEST SIMULATION
# =========================================================================
with tab3:
    col_bt_sym, col_bt_period, col_bt_cap = st.columns(3)
    with col_bt_sym:
        bt_ticker = st.text_input("Simulation Symbol:", "TCS.NS").strip().upper()
    with col_bt_period:
        bt_period = st.selectbox("Historical Lookback:", ["1y", "2y", "5y"], index=1)
    with col_bt_cap:
        bt_init_cap = st.number_input("Starting Capital:", value=100000.0, step=10000.0, format="%.0f")

    col_btn_bt, _ = st.columns([1, 4])
    with col_btn_bt:
        bt_run = st.button("Run Simulation Model", type="primary")

    if bt_run and bt_ticker:
        norm_bt_ticker = format_ticker(bt_ticker)
        with st.spinner(f"Simulating {norm_bt_ticker} vs Benchmark..."):
            backtester = StockBacktester(norm_bt_ticker)
            bt_results = backtester.run_backtest(period=bt_period, initial_capital=bt_init_cap)

        if not bt_results:
            st.error(f"Simulation failed for {norm_bt_ticker}.")
        else:
            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
            with col_m1:
                st.metric("Total Return", f"{bt_results['stock_total_return']}%", delta=f"{bt_results['stock_total_return'] - bt_results['benchmark_total_return']:.1f}% vs BM")
            with col_m2:
                st.metric("CAGR", f"{bt_results['stock_cagr']}%", delta=f"{bt_results['stock_cagr'] - bt_results['benchmark_cagr']:.1f}% vs BM")
            with col_m3:
                st.metric("Sharpe Ratio", f"{bt_results['sharpe_ratio']}")
            with col_m4:
                st.metric("Max Drawdown", f"{bt_results['max_drawdown_stock']}%", delta=f"BM: {bt_results['max_drawdown_bm']}%", delta_color="inverse")
            with col_m5:
                st.metric("Alpha", f"{bt_results['alpha']:.1f}%")

            st.markdown("### Portfolio Equity Trajectory")
            ts = bt_results["timeseries"]
            fig_eq = go.Figure()
            fig_eq.add_trace(go.Scatter(
                x=ts["Date"], 
                y=ts["Stock_Portfolio_Value"], 
                name=f"{norm_bt_ticker}", 
                line=dict(color="#34D399", width=2.5)
            ))
            fig_eq.add_trace(go.Scatter(
                x=ts["Date"], 
                y=ts["Benchmark_Portfolio_Value"], 
                name=f"Benchmark ({bt_results['benchmark_symbol']})", 
                line=dict(color="#64748B", width=1.5, dash="dash")
            ))
            fig_eq.update_layout(
                paper_bgcolor='#080C14',
                plot_bgcolor='#0F172A',
                font=dict(color='#94A3B8', size=12),
                xaxis=dict(gridcolor='#1E293B'),
                yaxis=dict(gridcolor='#1E293B', title="Portfolio Value"),
                margin=dict(l=10, r=10, t=10, b=10),
                height=320
            )
            st.plotly_chart(fig_eq, width="stretch")

            st.markdown("### Historical Drawdown Envelope")
            fig_dd = go.Figure()
            fig_dd.add_trace(go.Scatter(
                x=ts["Date"], 
                y=ts["Stock_Drawdown"] * 100, 
                name="Drawdown (%)", 
                fill='tozeroy',
                fillcolor='rgba(239, 68, 68, 0.15)',
                line=dict(color="#F87171", width=1.5)
            ))
            fig_dd.update_layout(
                paper_bgcolor='#080C14',
                plot_bgcolor='#0F172A',
                font=dict(color='#94A3B8', size=12),
                xaxis=dict(gridcolor='#1E293B'),
                yaxis=dict(gridcolor='#1E293B', title="Drawdown (%)"),
                margin=dict(l=10, r=10, t=10, b=10),
                height=220
            )
            st.plotly_chart(fig_dd, width="stretch")

# =========================================================================
# TAB 4: POSITION SIZING & RISK PLAN
# =========================================================================
with tab4:
    col_rk1, col_rk2 = st.columns(2)
    with col_rk1:
        plan_ticker = st.text_input("Select Security:", "RELIANCE.NS", key="ps_tick").strip().upper()
    with col_rk2:
        custom_price = st.number_input("Custom Entry Price (0 for Current Market Price):", value=0.0, step=10.0)

    if plan_ticker:
        norm_plan_ticker = format_ticker(plan_ticker)
        p_data = StockDataFetcher.get_stock_data(norm_plan_ticker)
        if p_data:
            curr_p = custom_price if custom_price > 0 else p_data["current_price"]
            trade_plan = RiskManager.calculate_trade_plan(
                stock_price=curr_p,
                history=p_data["history"],
                total_portfolio_size=portfolio_capital,
                risk_per_trade_pct=risk_per_trade,
                max_position_size_pct=12.0
            )

            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                st.metric("Entry Price", f"{p_data['currency']} {trade_plan['current_price']:.2f}")
                st.metric("Calculated Position Size", f"{trade_plan['recommended_shares']} Shares")
                st.metric("Capital Allocation", f"{p_data['currency']} {trade_plan['total_investment']:,.2f}", delta=f"{trade_plan['portfolio_weight_pct']}% Portfolio Weight")
            
            with col_p2:
                st.metric("Stop Loss (2x ATR)", f"{p_data['currency']} {trade_plan['stop_loss']:.2f}", delta=f"{trade_plan['stop_loss_pct']}%", delta_color="inverse")
                st.metric("Max Capital Risk", f"{p_data['currency']} {trade_plan['max_risk_capital']:,.2f}", delta=f"Capped at {risk_per_trade}%", delta_color="inverse")

            with col_p3:
                st.metric("Target 1 (1:2 R:R)", f"{p_data['currency']} {trade_plan['target_1']:.2f}", delta=f"+{trade_plan['target_1_upside_pct']}%")
                st.metric("Target 2 (1:3.5 R:R)", f"{p_data['currency']} {trade_plan['target_2']:.2f}", delta=f"+{trade_plan['target_2_upside_pct']}%")
                st.metric("Projected Gain (T2)", f"{p_data['currency']} {trade_plan['potential_gain_t2']:,.2f}")

            st.html(f"""
            <div class="terminal-card" style="margin-top:18px; border-left:4px solid #38BDF8;">
                <div style="font-size:1.05rem; font-weight:700; color:#FFFFFF; margin-bottom:8px;">Order Execution Directives</div>
                <div style="font-size:0.9rem; color:#CBD5E1; line-height:1.6;">
                    • <b>Portfolio Allocation:</b> Cap maximum allocation at <b>{trade_plan['portfolio_weight_pct']}%</b> ({p_data['currency']} {trade_plan['total_investment']:,.2f}) to prevent concentration risk.<br>
                    • <b>Strict Stop Loss:</b> Place hard stop at <b>{p_data['currency']} {trade_plan['stop_loss']:.2f}</b> ({trade_plan['stop_loss_pct']}%). Protects against downside tail risk.<br>
                    • <b>Profit Scaling:</b> Close 50% of position at Target 1 (<b>{p_data['currency']} {trade_plan['target_1']:.2f}</b>) and trail stop-loss to breakeven.
                </div>
            </div>
            """)
