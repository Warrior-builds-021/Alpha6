# ⚡ 6-Pillar Stock Intelligence Terminal & AI Investment Agent

An institutional-grade stock screener, forensic quality auditor, backtester, and dynamic position-sizing terminal designed around the **6 Fundamental Pillars of Asymmetric Wealth Creation & Capital Preservation**.

Supports both **Indian Markets (NSE/BSE)** and **Global / US Markets (TradingView tickers)**.

---

## 🏛️ The 6 Core Pillars

| Pillar | Focus | What We Look For | Red Flag Trigger |
| :--- | :--- | :--- | :--- |
| **1. Volume & Momentum Growth** | Real Consumer Demand | Volume $> 50\text{-DMA}$ + YoY Quarterly Revenue $> 10\%$ | Volume dry-up + technical breakdown |
| **2. Sales Revenue Growth** | Topline Expansion | 3-5 Year Sales CAGR $\ge 12-15\%$ | Topline revenue contraction |
| **3. Operating Cash Flow (OCF)** | Quality of Earnings | $\frac{\text{OCF}}{\text{Net Income}} \ge 1.0$, Positive Free Cash Flow | Negative OCF, accrual manipulation |
| **4. Debt & Solvency Health** | Downside Shield | $\text{Debt-to-Equity} < 0.5$, Interest Coverage $> 4.0\text{x}$ | $\text{D/E} > 1.5\text{x}$, Current Ratio $< 1.0$ |
| **5. Pricing Power (Moat)** | Margin Protection | Gross Margins $> 30\%$, $\text{ROE} \ge 15\%$, High Pricing Power | Margin compression $> 300\text{ bps}$ |
| **6. Skin in the Game** | Alignment of Interests | Promoter holding $\ge 40\%$ (India) / High Insider Stake (US) | Pledged shares $> 10\%$, insider dumping |

---

## 🛡️ Senior Finance Manager Capital Preservation Philosophy

> **"Never Lose Money" Rule:**
> Over 80% of retail losses come from buying companies with high debt, negative cash flows, or fake accounting profits.
> 
> The system enforces:
> 1. **$\ge 78\%$ Conviction Threshold**: Only top-decile compounders qualify for buy signals.
> 2. **Hard Red-Flag Disqualification**: Instant rejection of high-debt, cash-burning, or pledged-share companies.
> 3. **Dynamic 2x ATR Stop-Loss & Position Sizing**: Caps total portfolio risk to $\le 1.5\%$ on any single trade.

---

## 🚀 Quickstart Guide

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Run Test Suite
```bash
python test_engine.py
```

### 3. Launch Interactive Financial Terminal Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 💻 Supported Markets & Ticker Formats

* **Indian Equities (NSE)**: `RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS`, `TATAMOTORS.NS`, `ITC.NS` (or simply `TCS`, `RELIANCE`)
* **Indian Equities (BSE)**: `500325.BO`
* **US Equities (NYSE / NASDAQ / TradingView)**: `NVDA`, `AAPL`, `MSFT`, `GOOGL`, `TSLA`, `AMZN`

---

## 📊 Features & Terminal Modules

1. **Daily Asymmetric Screener**: One-click batch scanning of Nifty 50, Indian Quality Midcaps, US Mega-Cap Tech, or custom watchlists.
2. **6-Pillar Forensic Deep-Dive**: Spider radar charts, 50-DMA/200-DMA momentum trends, and itemized pillar breakdown.
3. **Institutional Backtester**: Compares historical strategy equity curve vs Nifty 50 / S&P 500 benchmark (CAGR, Alpha, Beta, Sharpe Ratio, Underwater Drawdown).
4. **Position Sizing & Risk Plan**: Calculates exact shares to buy, dynamic stop loss, and 1:2 / 1:3.5 profit targets based on your portfolio size.
