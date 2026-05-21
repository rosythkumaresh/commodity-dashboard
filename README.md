# ⚡ CommodityOS — Global Markets Terminal

A professional-grade commodity markets dashboard built with Python and Streamlit. Designed to replicate the core functionality of institutional trading terminals — combining real-time price data, technical analysis, risk analytics, spread trading tools, and market education in one unified interface.

**Live Demo:** https://commodity-dashboard-p9nhek79a7dwtvsynn8qth.streamlit.app/

---

## 📸 Overview

CommodityOS tracks 16 instruments across four sectors — Energy, Metals, Agriculture, and Macro ETFs — and presents them through a Bloomberg-style dark terminal interface. All data is sourced live from Yahoo Finance and refreshes every 2 minutes.

---

## 🚀 Features

### 📈 Price & Technicals
- Candlestick, Line, and Area chart modes
- Bollinger Bands, MA20, and MA50 overlays
- RSI, MACD, and Volume panes synchronized on a single chart
- Multi-instrument overlay — normalize and compare up to 3 commodities side by side
- Algorithmic BUY / SELL / HOLD signal generated from RSI, MACD, and MA crossover rules

### 📊 Analytics
- Daily return distribution histogram with mean marker
- Rolling volatility chart (10D / 20D / 60D annualised)
- Monthly seasonality heatmap — identify historical return patterns by month and year
- Full statistics panel: Sharpe ratio, max drawdown, win rate, best/worst day

### 🌐 Market Scanner
- Scans all 16 instruments simultaneously for price, 1D change, RSI, and signal
- Overall market sentiment meter (Buy / Sell / Hold tally)
- Cross-commodity correlation matrix across 8 key instruments using 1-year return data

### ⚖️ Spread Analysis
- Four professional spreads with Z-score vs 1-year mean:
  - **Crack Spread** (Brent − WTI) — refining margin indicator
  - **Gold/Silver Ratio** — monetary metals relative value
  - **Copper/Gold Ratio** — global growth proxy
  - **Corn/Wheat Ratio** — grain substitution indicator
- Custom spread builder — select any two instruments, choose difference or ratio

### 📰 Market Intel
- Dynamic insights generated from live indicator readings (RSI zones, MACD crossovers, volatility regimes, MA crosses)
- Commodity education framework covering Energy, Metals, and Agriculture fundamentals
- **ATR-based position sizing calculator** — enter account size and risk percentage to get precise unit sizing and notional exposure

---

## 🛠 Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Streamlit | Web app framework |
| yfinance | Live market data |
| Plotly | Interactive charts |
| Pandas | Data manipulation |
| NumPy | Numerical calculations |

---

## 📦 Installation

**1. Clone the repository**
```bash
git clone https://github.com/rosythkumaresh/commodity-dashboard.git
cd commodity-dashboard
```

**2. Create a virtual environment (recommended)**
```bash
conda create -n commodity-dashboard python=3.11
conda activate commodity-dashboard
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the app**
```bash
streamlit run app.py
```

The dashboard will open automatically at `http://localhost:8501`

---

## 📊 Instruments Covered

| Sector | Instruments |
|---|---|
| ⚡ Energy | Crude Oil (WTI), Brent Crude, Natural Gas, Heating Oil |
| 🥇 Metals | Gold, Silver, Copper, Platinum |
| 🌾 Agriculture | Corn, Wheat, Soybeans, Coffee |
| 📊 Macro ETFs | S&P 500 (SPY), US Dollar (UUP), Commodities (DJP), Emerging Markets (EEM) |

---

## ⚠️ Disclaimer

This dashboard is built for **educational and research purposes only**. All signals and analytics are algorithmic and do not constitute financial or investment advice. Always do your own research before making any trading decisions.

---

## 👤 Author

**Thiagarajan Kumaresh** — built to demonstrate applied knowledge of commodity markets, quantitative analysis, and financial data engineering.

Feel free to connect on [LinkedIn](https://www.linkedin.com/in/thiagarajan-kumaresh-b7132421a/) or reach out via [GitHub](https://github.com/rosythkumaresh).
