import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="CommodityOS — Global Markets Terminal",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

/* Global reset */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: #050b14;
    color: #c8d6e8;
}

/* Remove default Streamlit padding */
.block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 100% !important; }
[data-testid="stSidebar"] { background: #07101d !important; border-right: 1px solid #0d2035; }
[data-testid="stSidebar"] .block-container { padding: 1rem !important; }

/* Scanline overlay */
.main::before {
    content: '';
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px);
    pointer-events: none;
    z-index: 9999;
}

/* Header */
.terminal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 0 1.25rem 0;
    border-bottom: 1px solid #0d2035;
    margin-bottom: 1.5rem;
}
.terminal-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.4rem;
    font-weight: 600;
    color: #e8f4ff;
    letter-spacing: 0.05em;
}
.terminal-title span { color: #00d4ff; }
.terminal-status {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #3a5470;
}
.live-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #00ff88;
    margin-right: 6px;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* KPI Cards */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 1.5rem; }
.kpi-card {
    background: linear-gradient(135deg, #07101d 0%, #0a1825 100%);
    border: 1px solid #0d2035;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00d4ff, #0066ff);
}
.kpi-card.up::before { background: linear-gradient(90deg, #00ff88, #00cc66); }
.kpi-card.down::before { background: linear-gradient(90deg, #ff4466, #cc0033); }
.kpi-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #3a5470;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.55rem;
    font-weight: 600;
    color: #e8f4ff;
    line-height: 1;
    margin-bottom: 0.35rem;
}
.kpi-delta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
}
.kpi-delta.pos { color: #00ff88; }
.kpi-delta.neg { color: #ff4466; }
.kpi-delta.neu { color: #3a5470; }

/* Section titles */
.section-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #00d4ff;
    margin: 1.5rem 0 0.75rem 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #0d2035, transparent);
}

/* Signal badge */
.signal-badge {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 3px;
    letter-spacing: 0.08em;
}
.signal-buy { background: rgba(0,255,136,0.12); color: #00ff88; border: 1px solid rgba(0,255,136,0.3); }
.signal-sell { background: rgba(255,68,102,0.12); color: #ff4466; border: 1px solid rgba(255,68,102,0.3); }
.signal-hold { background: rgba(0,212,255,0.1); color: #00d4ff; border: 1px solid rgba(0,212,255,0.25); }

/* Tabs override */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: transparent;
    border-bottom: 1px solid #0d2035;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    color: #3a5470 !important;
    background: transparent !important;
    border: none !important;
    padding: 0.4rem 1rem;
}
.stTabs [aria-selected="true"] {
    color: #00d4ff !important;
    border-bottom: 2px solid #00d4ff !important;
}

/* Sidebar styling */
.sidebar-logo {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1rem;
    font-weight: 600;
    color: #e8f4ff;
    padding: 0.5rem 0 1rem 0;
    border-bottom: 1px solid #0d2035;
    margin-bottom: 1rem;
}
.sidebar-logo span { color: #00d4ff; }

/* Metric override */
[data-testid="stMetric"] { background: transparent; }
[data-testid="stMetricLabel"] { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: #3a5470; }
[data-testid="stMetricValue"] { font-family: 'IBM Plex Mono', monospace; color: #e8f4ff; }

/* Table styling */
.stDataFrame { border: 1px solid #0d2035 !important; border-radius: 6px; }

/* Alert / info boxes */
.stAlert { border-radius: 6px; font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem; }

/* Sidebar radio */
[data-testid="stRadio"] label { font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; color: #6a90b0; }
[data-testid="stSelectbox"] { font-family: 'IBM Plex Mono', monospace; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #050b14; }
::-webkit-scrollbar-thumb { background: #0d2035; border-radius: 2px; }

/* Correlation heatmap label */
.corr-title { font-size: 0.65rem; font-family: 'IBM Plex Mono'; color: #3a5470; text-align: center; }

/* Insight card */
.insight-card {
    background: #07101d;
    border: 1px solid #0d2035;
    border-left: 3px solid #00d4ff;
    border-radius: 6px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.82rem;
    line-height: 1.5;
}
.insight-card.warn { border-left-color: #ffaa00; }
.insight-card.bull { border-left-color: #00ff88; }
.insight-card.bear { border-left-color: #ff4466; }

/* Responsive grid */
@media (max-width: 900px) {
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
""", unsafe_allow_html=True)


# ─── COMMODITY UNIVERSE ───────────────────────────────────────────────────────
SECTORS = {
    "⚡ Energy": {
        "Crude Oil (WTI)":    {"ticker": "CL=F",  "unit": "USD/bbl",  "icon": "🛢"},
        "Natural Gas":        {"ticker": "NG=F",  "unit": "USD/MMBtu","icon": "🔥"},
        "Brent Crude":        {"ticker": "BZ=F",  "unit": "USD/bbl",  "icon": "🛢"},
        "Heating Oil":        {"ticker": "HO=F",  "unit": "USD/gal",  "icon": "🌡"},
    },
    "🥇 Metals": {
        "Gold":               {"ticker": "GC=F",  "unit": "USD/oz",   "icon": "🥇"},
        "Silver":             {"ticker": "SI=F",  "unit": "USD/oz",   "icon": "🥈"},
        "Copper":             {"ticker": "HG=F",  "unit": "USD/lb",   "icon": "🔶"},
        "Platinum":           {"ticker": "PL=F",  "unit": "USD/oz",   "icon": "⬜"},
    },
    "🌾 Agriculture": {
        "Corn":               {"ticker": "ZC=F",  "unit": "USc/bu",   "icon": "🌽"},
        "Wheat":              {"ticker": "ZW=F",  "unit": "USc/bu",   "icon": "🌾"},
        "Soybeans":           {"ticker": "ZS=F",  "unit": "USc/bu",   "icon": "🫘"},
        "Coffee":             {"ticker": "KC=F",  "unit": "USc/lb",   "icon": "☕"},
    },
    "📊 Macro ETFs": {
        "S&P 500 (SPY)":      {"ticker": "SPY",   "unit": "USD",      "icon": "📈"},
        "US Dollar (DXY)":    {"ticker": "UUP",   "unit": "USD",      "icon": "💵"},
        "Commodities (DJP)":  {"ticker": "DJP",   "unit": "USD",      "icon": "📦"},
        "Emerging Markets":   {"ticker": "EEM",   "unit": "USD",      "icon": "🌏"},
    }
}

ALL_TICKERS = {name: meta for sec in SECTORS.values() for name, meta in sec.items()}

PERIODS = {"1 Week": "5d", "1 Month": "1mo", "3 Months": "3mo",
           "6 Months": "6mo", "1 Year": "1y", "2 Years": "2y"}

COLORS = {
    "primary": "#00d4ff", "green": "#00ff88", "red": "#ff4466",
    "amber": "#ffaa00", "bg": "#050b14", "card": "#07101d",
    "border": "#0d2035", "text": "#e8f4ff", "muted": "#3a5470"
}

PLOTLY_TEMPLATE = dict(
    paper_bgcolor="#050b14", plot_bgcolor="#07101d",
    font=dict(family="IBM Plex Mono", color="#6a90b0", size=10),
    xaxis=dict(gridcolor="#0d2035", linecolor="#0d2035", tickfont=dict(size=9)),
    yaxis=dict(gridcolor="#0d2035", linecolor="#0d2035", tickfont=dict(size=9)),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9), orientation="v"),
    margin=dict(l=40, r=20, t=30, b=40),
)


# ─── DATA FUNCTIONS ───────────────────────────────────────────────────────────
@st.cache_data(ttl=120)
def fetch_history(ticker: str, period: str) -> pd.DataFrame:
    try:
        df = yf.Ticker(ticker).history(period=period)
        if df.empty:
            return pd.DataFrame()
        df.index = pd.to_datetime(df.index).tz_localize(None)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=120)
def fetch_quote(ticker: str) -> dict:
    try:
        info = yf.Ticker(ticker).fast_info
        return {"price": getattr(info, "last_price", None), "prev": getattr(info, "previous_close", None)}
    except Exception:
        return {"price": None, "prev": None}

def compute_technicals(df: pd.DataFrame) -> pd.DataFrame:
    c = df["Close"].copy()
    df["MA20"]   = c.rolling(20).mean()
    df["MA50"]   = c.rolling(50).mean()
    df["EMA12"]  = c.ewm(span=12, adjust=False).mean()
    df["EMA26"]  = c.ewm(span=26, adjust=False).mean()
    df["MACD"]   = df["EMA12"] - df["EMA26"]
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["Hist"]   = df["MACD"] - df["Signal"]
    # RSI
    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / (loss + 1e-9)
    df["RSI"] = 100 - 100 / (1 + rs)
    # Bollinger Bands
    df["BB_mid"]  = c.rolling(20).mean()
    df["BB_std"]  = c.rolling(20).std()
    df["BB_upper"]= df["BB_mid"] + 2 * df["BB_std"]
    df["BB_lower"]= df["BB_mid"] - 2 * df["BB_std"]
    # ATR
    hl  = df["High"] - df["Low"]
    hpc = (df["High"] - df["Close"].shift()).abs()
    lpc = (df["Low"]  - df["Close"].shift()).abs()
    df["ATR"] = pd.concat([hl, hpc, lpc], axis=1).max(axis=1).rolling(14).mean()
    # Returns
    df["Return1D"] = c.pct_change() * 100
    df["Return5D"] = c.pct_change(5) * 100
    df["Volatility20"] = df["Return1D"].rolling(20).std() * np.sqrt(252)
    return df

def generate_signal(df: pd.DataFrame) -> tuple[str, str]:
    """Simple rule-based signal for educational purposes."""
    if len(df) < 51:
        return "HOLD", "Insufficient data"
    latest = df.iloc[-1]
    score  = 0
    reasons = []
    rsi = latest.get("RSI", 50)
    if rsi < 35:   score += 1; reasons.append("RSI oversold")
    elif rsi > 65: score -= 1; reasons.append("RSI overbought")
    if latest.get("MACD", 0) > latest.get("Signal", 0): score += 1; reasons.append("MACD bullish")
    else: score -= 1; reasons.append("MACD bearish")
    if latest.get("MA20", 0) > latest.get("MA50", 0): score += 1; reasons.append("MA20 > MA50")
    else: score -= 1; reasons.append("MA20 < MA50")
    price = latest["Close"]
    if price > latest.get("BB_upper", price): score -= 1; reasons.append("Above upper BB")
    elif price < latest.get("BB_lower", price): score += 1; reasons.append("Below lower BB")
    sig = "BUY" if score >= 2 else ("SELL" if score <= -2 else "HOLD")
    return sig, " · ".join(reasons[:3])

def pct_delta(new, old):
    if old and old != 0:
        return (new - old) / abs(old) * 100
    return 0.0


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">⚡ Commodity<span>OS</span></div>', unsafe_allow_html=True)

    selected_sector = st.selectbox("Sector", list(SECTORS.keys()), key="sector_select")
    sector_items = SECTORS[selected_sector]
    selected_name = st.selectbox("Instrument", list(sector_items.keys()), key="instr_select")
    meta = sector_items[selected_name]

    st.markdown("---")
    period_label = st.select_slider("Time Horizon", options=list(PERIODS.keys()), value="6 Months")
    period = PERIODS[period_label]

    st.markdown("---")
    st.markdown('<div class="kpi-label">COMPARE INSTRUMENTS</div>', unsafe_allow_html=True)
    compare_options = [n for n in ALL_TICKERS if n != selected_name]
    compare_names   = st.multiselect("Add to overlay", compare_options, max_selections=3, key="compare_multi")

    st.markdown("---")
    show_vol   = st.toggle("Show Volume", value=True)
    show_bb    = st.toggle("Bollinger Bands", value=True)
    show_mas   = st.toggle("Moving Averages", value=True)
    chart_type = st.radio("Price Chart", ["Candlestick", "Line", "Area"], horizontal=False)

    st.markdown("---")
    st.markdown(f'<div class="kpi-label">DATA REFRESHES EVERY 2 MIN</div>', unsafe_allow_html=True)
    if st.button("⟳ Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ─── MAIN HEADER ──────────────────────────────────────────────────────────────
now_str = datetime.utcnow().strftime("%Y-%m-%d  %H:%M UTC")
st.markdown(f"""
<div class="terminal-header">
  <div class="terminal-title">⚡ Commodity<span>OS</span> — Global Markets Terminal ©Kumaresh 2026</div>
  <div class="terminal-status"><span class="live-dot"></span>LIVE  ·  {now_str}</div>
</div>
""", unsafe_allow_html=True)


# ─── LOAD PRIMARY DATA ────────────────────────────────────────────────────────
ticker = meta["ticker"]
df_raw = fetch_history(ticker, period)

if df_raw.empty:
    st.error(f"⚠ Could not retrieve data for **{selected_name}** ({ticker}). Markets may be closed.")
    st.stop()

df = compute_technicals(df_raw.copy())
latest = df.iloc[-1]
prev    = df.iloc[-2] if len(df) > 1 else df.iloc[-1]

price     = latest["Close"]
price_d1  = pct_delta(price, prev["Close"])
rsi_val   = latest.get("RSI", float("nan"))
atr_val   = latest.get("ATR", float("nan"))
vol_20    = latest.get("Volatility20", float("nan"))

signal, sig_reason = generate_signal(df)
sig_class = {"BUY": "signal-buy", "SELL": "signal-sell", "HOLD": "signal-hold"}[signal]


# ─── KPI STRIP ────────────────────────────────────────────────────────────────
high52 = df["High"].max()
low52  = df["Low"].min()
avg_vol = df["Volume"].tail(20).mean() if "Volume" in df.columns else 0

trend_cls = "up" if price_d1 >= 0 else "down"
delta_cls  = "pos" if price_d1 >= 0 else "neg"
delta_sym  = "▲" if price_d1 >= 0 else "▼"

vol_cls = "pos" if not np.isnan(vol_20) and vol_20 < 20 else ("neg" if not np.isnan(vol_20) and vol_20 > 40 else "neu")

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card {trend_cls}">
    <div class="kpi-label">LAST PRICE  ·  {meta['unit']}</div>
    <div class="kpi-value">{price:,.2f}</div>
    <div class="kpi-delta {delta_cls}">{delta_sym} {abs(price_d1):.2f}% (1D)</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">PERIOD HIGH / LOW</div>
    <div class="kpi-value" style="font-size:1.05rem;line-height:1.6">{high52:,.2f}<br>{low52:,.2f}</div>
    <div class="kpi-delta neu">Range: {((high52-low52)/low52*100):.1f}%</div>
  </div>
  <div class="kpi-card {'up' if rsi_val < 40 else ('down' if rsi_val > 60 else '')}">
    <div class="kpi-label">RSI (14)</div>
    <div class="kpi-value">{rsi_val:.1f}</div>
    <div class="kpi-delta {'pos' if rsi_val<40 else ('neg' if rsi_val>60 else 'neu')}">
      {'OVERSOLD — potential reversal' if rsi_val<30 else ('OVERBOUGHT — caution' if rsi_val>70 else ('Approaching overbought' if rsi_val>60 else ('Approaching oversold' if rsi_val<40 else 'NEUTRAL')))}
    </div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">SIGNAL  ·  ALGO</div>
    <div class="kpi-value" style="font-size:1.1rem;padding-top:4px">
      <span class="signal-badge {sig_class}">{signal}</span>
    </div>
    <div class="kpi-delta neu" style="margin-top:6px">{sig_reason[:45]}…</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── MAIN TABS ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈  PRICE & TECHNICALS",
    "📊  ANALYTICS",
    "🌐  MARKET SCANNER",
    "⚖️  SPREAD ANALYSIS",
    "📰  MARKET INTEL"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: PRICE & TECHNICALS
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f'<div class="section-title">PRICE CHART — {selected_name.upper()}</div>', unsafe_allow_html=True)

    rows   = 4 if show_vol else 3
    h_spec = [0.55, 0.18, 0.15, 0.12] if show_vol else [0.60, 0.22, 0.18]
    r_names = (["Price", "RSI", "MACD", "Volume"] if show_vol else ["Price", "RSI", "MACD"])[:rows]

    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        row_heights=h_spec[:rows], subplot_titles=["", "", "", ""][:rows])

    # ── Price pane ──
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
            name=selected_name,
            increasing_line_color=COLORS["green"], decreasing_line_color=COLORS["red"],
            increasing_fillcolor=COLORS["green"], decreasing_fillcolor=COLORS["red"]
        ), row=1, col=1)
    elif chart_type == "Area":
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"], fill="tozeroy",
            fillcolor="rgba(0,212,255,0.08)", line=dict(color=COLORS["primary"], width=1.5),
            name=selected_name
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"], line=dict(color=COLORS["primary"], width=1.5),
            name=selected_name
        ), row=1, col=1)

    if show_mas and len(df) >= 20:
        fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], line=dict(color="#ffaa00", width=1, dash="dot"),
                                 name="MA20"), row=1, col=1)
    if show_mas and len(df) >= 50:
        fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], line=dict(color="#9966ff", width=1, dash="dot"),
                                 name="MA50"), row=1, col=1)
    if show_bb and len(df) >= 20:
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], line=dict(color="rgba(0,212,255,0.35)", width=0.8),
                                 name="BB Upper", showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], fill="tonexty",
                                 fillcolor="rgba(0,212,255,0.04)", line=dict(color="rgba(0,212,255,0.35)", width=0.8),
                                 name="BB Bands"), row=1, col=1)

    # Compare overlays
    for cname in compare_names:
        cmeta = ALL_TICKERS[cname]
        cdf   = fetch_history(cmeta["ticker"], period)
        if not cdf.empty:
            norm = cdf["Close"] / cdf["Close"].iloc[0] * df["Close"].iloc[0]
            fig.add_trace(go.Scatter(x=cdf.index, y=norm, line=dict(width=1, dash="dot"),
                                     name=f"{cname} (norm)", opacity=0.7), row=1, col=1)

    # ── RSI pane ──
    fig.add_hline(y=70, line_color=COLORS["red"],   line_dash="dot", line_width=0.7, row=2, col=1)
    fig.add_hline(y=30, line_color=COLORS["green"], line_dash="dot", line_width=0.7, row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"],
                             fill="tozeroy", fillcolor="rgba(0,212,255,0.06)",
                             line=dict(color=COLORS["primary"], width=1.2), name="RSI"), row=2, col=1)

    # ── MACD pane ──
    colors_hist = [COLORS["green"] if v >= 0 else COLORS["red"] for v in df["Hist"].fillna(0)]
    fig.add_trace(go.Bar(x=df.index, y=df["Hist"], name="MACD Hist",
                         marker_color=colors_hist, opacity=0.7), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"],   line=dict(color=COLORS["primary"], width=1), name="MACD"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["Signal"], line=dict(color=COLORS["amber"], width=1, dash="dot"), name="Signal"), row=3, col=1)

    # ── Volume pane ──
    if show_vol and "Volume" in df.columns:
        vol_colors = [COLORS["green"] if df["Close"].iloc[i] >= df["Open"].iloc[i] else COLORS["red"]
                      for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume",
                             marker_color=vol_colors, opacity=0.6), row=4, col=1)

    fig.update_layout(**PLOTLY_TEMPLATE, height=680, showlegend=True)
    fig.update_layout(legend=dict(orientation="h", y=1.02, x=0, bgcolor="rgba(0,0,0,0)", font=dict(size=9)))
    fig.update_xaxes(rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # Technical summary table
    st.markdown('<div class="section-title">INDICATOR SUMMARY</div>', unsafe_allow_html=True)
    ind_data = {
        "Indicator":  ["RSI (14)", "MACD", "MA Cross", "Bollinger", "ATR (14)", "Volatility (20D Ann.)"],
        "Value":      [f"{rsi_val:.1f}", f"{latest['MACD']:.3f}" if not np.isnan(latest.get('MACD',float('nan'))) else "—",
                       f"{latest.get('MA20',0):.2f} / {latest.get('MA50',0):.2f}",
                       f"{latest.get('BB_lower',0):.2f} — {latest.get('BB_upper',0):.2f}",
                       f"{atr_val:.2f}" if not np.isnan(atr_val) else "—",
                       f"{vol_20:.1f}%" if not np.isnan(vol_20) else "—"],
        "Reading":    [
            "Oversold" if rsi_val<30 else ("Overbought" if rsi_val>70 else "Neutral"),
            "Bullish" if latest.get('MACD',0) > latest.get('Signal',0) else "Bearish",
            "Bullish" if latest.get('MA20',0) > latest.get('MA50',0) else "Bearish",
            "Overbought" if price > latest.get('BB_upper',price) else ("Oversold" if price < latest.get('BB_lower',price) else "Inside bands"),
            "High" if not np.isnan(atr_val) and atr_val > price*0.02 else "Normal",
            "High" if not np.isnan(vol_20) and vol_20>40 else ("Low" if not np.isnan(vol_20) and vol_20<15 else "Normal")
        ]
    }
    st.dataframe(pd.DataFrame(ind_data), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-title">RETURN DISTRIBUTION</div>', unsafe_allow_html=True)
        returns = df["Return1D"].dropna()
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=returns, nbinsx=40,
            marker_color=COLORS["primary"], opacity=0.8,
            name="Daily Returns %"
        ))
        mean_r = returns.mean()
        fig_hist.add_vline(x=mean_r, line_color=COLORS["amber"], line_dash="dot",
                           annotation_text=f"μ={mean_r:.2f}%", annotation_font_color=COLORS["amber"])
        fig_hist.update_layout(**PLOTLY_TEMPLATE, height=280, showlegend=False,
                               title=dict(text="Daily Return Distribution (%)", font=dict(size=10), x=0))
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-title">ROLLING VOLATILITY</div>', unsafe_allow_html=True)
        vol_10  = df["Return1D"].rolling(10).std()  * np.sqrt(252)
        vol_20_ = df["Return1D"].rolling(20).std()  * np.sqrt(252)
        vol_60  = df["Return1D"].rolling(60).std()  * np.sqrt(252)
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(x=df.index, y=vol_10,  line=dict(color=COLORS["red"],   width=1), name="10D Vol"))
        fig_vol.add_trace(go.Scatter(x=df.index, y=vol_20_, line=dict(color=COLORS["primary"],width=1.5), name="20D Vol"))
        fig_vol.add_trace(go.Scatter(x=df.index, y=vol_60,  line=dict(color=COLORS["amber"], width=1, dash="dot"), name="60D Vol"))
        fig_vol.update_layout(**PLOTLY_TEMPLATE, height=280,
                              title=dict(text="Annualised Volatility (%)", font=dict(size=10), x=0))
        st.plotly_chart(fig_vol, use_container_width=True)

    # Seasonal pattern
    st.markdown('<div class="section-title">MONTHLY SEASONALITY HEATMAP</div>', unsafe_allow_html=True)
    df_seas = df_raw.copy()
    df_seas["Year"]  = df_seas.index.year
    df_seas["Month"] = df_seas.index.month
    df_seas["Ret"]   = df_seas["Close"].pct_change() * 100
    monthly = df_seas.groupby(["Year","Month"])["Ret"].sum().unstack("Month")
    monthly.columns = [pd.Timestamp(2000, m, 1).strftime("%b") for m in monthly.columns]
    if not monthly.empty:
        fig_heat = go.Figure(go.Heatmap(
            z=monthly.values, x=monthly.columns.tolist(), y=monthly.index.tolist(),
            colorscale=[[0,"#cc0033"],[0.5,"#07101d"],[1,"#00cc66"]],
            zmid=0, colorbar=dict(thickness=8, len=0.8, tickfont=dict(size=8)),
            text=[[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in monthly.values],
            texttemplate="%{text}", hovertemplate="%{y} %{x}: %{z:.1f}%<extra></extra>"
        ))
        fig_heat.update_layout(**PLOTLY_TEMPLATE, height=260,
                               title=dict(text="Monthly Return % by Year", font=dict(size=10), x=0))
        st.plotly_chart(fig_heat, use_container_width=True)

    # Stats table
    st.markdown('<div class="section-title">STATISTICS</div>', unsafe_allow_html=True)
    r = df["Return1D"].dropna()
    neg_days = (r < 0).sum(); pos_days = (r >= 0).sum()
    sharpe = (r.mean() / r.std() * np.sqrt(252)) if r.std() > 0 else 0
    max_dd_series = (df["Close"] / df["Close"].cummax() - 1) * 100
    max_dd = max_dd_series.min()
    stat_df = pd.DataFrame({
        "Metric":    ["Mean Daily Return","Std Dev (Daily)","Sharpe Ratio (Ann.)","Max Drawdown","Best Day","Worst Day","% Positive Days"],
        "Value":     [f"{r.mean():.3f}%", f"{r.std():.3f}%", f"{sharpe:.2f}",
                      f"{max_dd:.2f}%", f"{r.max():.2f}%", f"{r.min():.2f}%",
                      f"{pos_days/(pos_days+neg_days)*100:.1f}%"]
    })
    st.dataframe(stat_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: MARKET SCANNER
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">LIVE MARKET SCANNER — ALL INSTRUMENTS</div>', unsafe_allow_html=True)
    st.caption("Scanning all tracked instruments. RSI & signal generated from 6-month data.")

    scanner_rows = []
    with st.spinner("Scanning markets…"):
        for name, m in ALL_TICKERS.items():
            sd = fetch_history(m["ticker"], "6mo")
            if sd.empty or len(sd) < 10:
                continue
            sd = compute_technicals(sd)
            lat = sd.iloc[-1]
            pr  = lat["Close"]
            d1  = pct_delta(pr, sd.iloc[-2]["Close"]) if len(sd) > 1 else 0
            rsi = lat.get("RSI", float("nan"))
            sig, _ = generate_signal(sd)
            high_ = sd["Close"].max(); low_ = sd["Close"].min()
            pos_pct = (pr - low_) / (high_ - low_) * 100 if high_ != low_ else 50
            scanner_rows.append({
                "Instrument": name,
                "Price":      round(pr, 2),
                "1D %":       round(d1, 2),
                "RSI":        round(rsi, 1) if not np.isnan(rsi) else None,
                "Signal":     sig,
                "Pos in Range": round(pos_pct, 1),
                "Unit":       m["unit"]
            })

    if scanner_rows:
        scan_df = pd.DataFrame(scanner_rows)

        def style_signal(val):
            if val == "BUY":  return "color: #00ff88; font-weight:600"
            if val == "SELL": return "color: #ff4466; font-weight:600"
            return "color: #00d4ff"

        def style_delta(val):
            return "color: #00ff88" if val >= 0 else "color: #ff4466"

        styled = scan_df.style\
            .map(style_signal, subset=["Signal"])\
            .map(style_delta, subset=["1D %"])\
            .format({"Price": "{:,.2f}", "1D %": "{:+.2f}%", "RSI": "{:.1f}", "Pos in Range": "{:.1f}%"})

        st.dataframe(styled, use_container_width=True, hide_index=True, height=420)

        # Quick bar — buy/sell/hold counts
        sig_counts = scan_df["Signal"].value_counts()
        b = sig_counts.get("BUY", 0); s = sig_counts.get("SELL", 0); h = sig_counts.get("HOLD", 0)
        total = b + s + h
        st.markdown(f"""
        <div style="display:flex;gap:20px;margin-top:12px;font-family:'IBM Plex Mono';font-size:0.78rem">
          <span style="color:#00ff88">▲ BUY: {b} ({b/total*100:.0f}%)</span>
          <span style="color:#ff4466">▼ SELL: {s} ({s/total*100:.0f}%)</span>
          <span style="color:#00d4ff">◆ HOLD: {h} ({h/total*100:.0f}%)</span>
          <span style="color:#3a5470">Market Sentiment: {'Risk-On 🟢' if b>s else ('Risk-Off 🔴' if s>b else 'Neutral ⚪')}</span>
        </div>
        """, unsafe_allow_html=True)

    # Correlation heatmap
    st.markdown('<div class="section-title">CROSS-COMMODITY CORRELATION MATRIX</div>', unsafe_allow_html=True)
    corr_names = ["Crude Oil (WTI)", "Gold", "Silver", "Copper", "Corn", "Wheat", "Natural Gas", "S&P 500 (SPY)"]
    corr_data  = {}
    for n in corr_names:
        cd = fetch_history(ALL_TICKERS[n]["ticker"], "1y")
        if not cd.empty:
            corr_data[n] = cd["Close"].pct_change().dropna()
    if len(corr_data) >= 3:
        corr_df  = pd.DataFrame(corr_data).dropna()
        corr_mat = corr_df.corr()
        fig_corr = go.Figure(go.Heatmap(
            z=corr_mat.values,
            x=corr_mat.columns.tolist(),
            y=corr_mat.index.tolist(),
            colorscale=[[0,"#cc0033"],[0.5,"#07101d"],[1,"#00cc66"]],
            zmid=0, zmin=-1, zmax=1,
            text=[[f"{v:.2f}" for v in row] for row in corr_mat.values],
            texttemplate="%{text}",
            colorbar=dict(thickness=8, tickfont=dict(size=8))
        ))
        fig_corr.update_layout(**PLOTLY_TEMPLATE, height=380,
                               title=dict(text="1-Year Rolling Return Correlations", font=dict(size=10), x=0))
        fig_corr.update_xaxes(tickangle=-35, tickfont=dict(size=8))
        st.plotly_chart(fig_corr, use_container_width=True)
        st.caption("Correlation of 1 = perfect positive co-movement. Use for diversification analysis.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: SPREAD ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">COMMODITY SPREAD CALCULATOR</div>', unsafe_allow_html=True)
    st.caption("Spreads are key tools for relative value trading and supply-demand analysis.")

    SPREADS = {
        "Crack Spread (Brent − WTI)":        ("BZ=F", "CL=F",  "Energy arb between Brent and WTI crude"),
        "Gold/Silver Ratio (×)":             ("GC=F", "SI=F",  "Monetary metals relative value (higher = gold rich vs silver)"),
        "Corn/Wheat Ratio (×)":              ("ZC=F", "ZW=F",  "Grain substitution ratio — feed market indicator"),
        "Copper/Gold Ratio (×)":             ("HG=F", "GC=F",  "Economic growth proxy — rising = risk-on"),
    }

    col1, col2 = st.columns(2)
    for i, (spread_name, (t1, t2, desc)) in enumerate(SPREADS.items()):
        d1_ = fetch_history(t1, "1y")
        d2_ = fetch_history(t2, "1y")
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            if d1_.empty or d2_.empty:
                st.warning(f"No data for {spread_name}")
                continue
            aligned = pd.concat([d1_["Close"].rename("A"), d2_["Close"].rename("B")], axis=1).dropna()
            if "Ratio" in spread_name:
                spread_series = aligned["A"] / aligned["B"]
                y_label = "Ratio"
            else:
                spread_series = aligned["A"] - aligned["B"]
                y_label = "Spread (USD)"

            current_spread = spread_series.iloc[-1]
            mean_spread    = spread_series.mean()
            std_spread     = spread_series.std()
            z_score        = (current_spread - mean_spread) / std_spread if std_spread > 0 else 0

            fig_sp = go.Figure()
            fig_sp.add_trace(go.Scatter(x=spread_series.index, y=spread_series,
                                        fill="tozeroy", fillcolor="rgba(0,212,255,0.06)",
                                        line=dict(color=COLORS["primary"], width=1.5), name=y_label))
            fig_sp.add_hline(y=mean_spread, line_color=COLORS["amber"], line_dash="dot",
                             annotation_text=f"Mean: {mean_spread:.2f}")
            fig_sp.add_hline(y=mean_spread + std_spread, line_color=COLORS["red"], line_dash="dot", line_width=0.7)
            fig_sp.add_hline(y=mean_spread - std_spread, line_color=COLORS["green"], line_dash="dot", line_width=0.7)
            fig_sp.update_layout(**PLOTLY_TEMPLATE, height=230,
                                 title=dict(text=spread_name, font=dict(size=9, color=COLORS["primary"]), x=0))
            st.plotly_chart(fig_sp, use_container_width=True)
            z_cls = "pos" if z_score < -1 else ("neg" if z_score > 1 else "neu")
            st.markdown(f"""
            <div style="font-family:'IBM Plex Mono';font-size:0.72rem;color:#3a5470;margin:-8px 0 14px 0">
              Current: <span style="color:#e8f4ff">{current_spread:.3f}</span> &nbsp;|&nbsp;
              Z-Score: <span class="kpi-delta {z_cls}">{z_score:+.2f}σ</span> &nbsp;|&nbsp;
              {desc}
            </div>
            """, unsafe_allow_html=True)

    # Custom spread builder
    st.markdown('<div class="section-title">CUSTOM SPREAD BUILDER</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    leg1 = c1.selectbox("Long Leg", list(ALL_TICKERS.keys()), key="leg1")
    leg2 = c2.selectbox("Short Leg", list(ALL_TICKERS.keys()), index=1, key="leg2")
    sp_type = c3.radio("Spread Type", ["Difference", "Ratio"], horizontal=True)

    if leg1 != leg2:
        csd1 = fetch_history(ALL_TICKERS[leg1]["ticker"], "1y")
        csd2 = fetch_history(ALL_TICKERS[leg2]["ticker"], "1y")
        if not csd1.empty and not csd2.empty:
            cal = pd.concat([csd1["Close"].rename("L1"), csd2["Close"].rename("L2")], axis=1).dropna()
            cs  = cal["L1"] / cal["L2"] if sp_type == "Ratio" else cal["L1"] - cal["L2"]
            fig_cs = go.Figure(go.Scatter(x=cs.index, y=cs, line=dict(color=COLORS["amber"], width=1.5),
                                          fill="tozeroy", fillcolor="rgba(255,170,0,0.06)"))
            fig_cs.update_layout(**PLOTLY_TEMPLATE, height=220,
                                 title=dict(text=f"{leg1} / {leg2} — {sp_type}", font=dict(size=10), x=0))
            st.plotly_chart(fig_cs, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: MARKET INTEL
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">MARKET FRAMEWORK & INSIGHTS</div>', unsafe_allow_html=True)

    # Dynamic insights from data
    insights = []
    if not np.isnan(rsi_val):
        if rsi_val < 30:
            insights.append(("bull", f"⚡ {selected_name} RSI at {rsi_val:.1f} — deep oversold territory. Historical mean-reversion probability elevated. Watch for volume confirmation before entry."))
        elif rsi_val > 70:
            insights.append(("bear", f"⚠ {selected_name} RSI at {rsi_val:.1f} — overbought. Risk of short-term pullback. Consider trailing stops or partial profit-taking."))
    if latest.get("MA20", 0) > latest.get("MA50", 0):
        insights.append(("bull", f"📈 Golden cross pattern on {selected_name}: MA20 ({latest['MA20']:.2f}) trading above MA50 ({latest['MA50']:.2f}). Medium-term uptrend intact."))
    else:
        insights.append(("bear", f"📉 Death cross on {selected_name}: MA20 below MA50. Medium-term trend remains bearish. Selling rallies may be preferred strategy."))
    if not np.isnan(vol_20):
        if vol_20 > 40:
            insights.append(("warn", f"🌊 Elevated annualised volatility ({vol_20:.1f}%) on {selected_name}. Consider position sizing carefully; risk per trade may need reduction."))
        elif vol_20 < 12:
            insights.append(("warn", f"😴 Compressed volatility ({vol_20:.1f}%) on {selected_name}. Low-vol regimes often precede breakouts — watch range boundaries closely."))
    macd_val = latest.get("MACD", 0); sig_val = latest.get("Signal", 0)
    if not np.isnan(macd_val) and not np.isnan(sig_val):
        if macd_val > sig_val:
            insights.append(("bull", f"🔀 MACD ({macd_val:.3f}) above signal line ({sig_val:.3f}) — momentum is bullish. Histogram expansion would confirm acceleration."))
        else:
            insights.append(("bear", f"🔀 MACD ({macd_val:.3f}) below signal line ({sig_val:.3f}) — bearish momentum divergence. Watch for histogram contraction as potential reversal clue."))

    for cls, text in insights:
        st.markdown(f'<div class="insight-card {cls}">{text}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">COMMODITY TRADING FUNDAMENTALS</div>', unsafe_allow_html=True)

    topics = {
        "🛢 Energy Markets": {
            "WTI vs Brent":        "WTI (West Texas Intermediate) is the US benchmark; Brent is the global benchmark. The spread reflects transport costs, quality differentials and geopolitical risk.",
            "Crack Spread":        "The refining margin: crack spread = refined product price − crude price. A widening crack spread signals strong refinery demand and usually supports crude.",
            "Contango vs Backwardation": "Contango (futures > spot) = oversupply or weak near-term demand. Backwardation (spot > futures) = tight supply or strong demand — bullish for physical holders.",
        },
        "🥇 Metals Markets": {
            "Gold as Safe Haven":  "Gold is inversely correlated with real interest rates and USD strength. Rising inflation expectations without rising nominal rates = tailwind for gold.",
            "Copper as Barometer": "Copper's industrial demand makes it a leading economic indicator. A rising copper/gold ratio signals improving global growth expectations.",
            "Silver Dual Role":    "Silver has both monetary (safe-haven) and industrial (solar, EVs) demand. High gold/silver ratio = silver relatively cheap historically.",
        },
        "🌾 Agriculture Markets": {
            "Weather & Crop Cycles": "Grain prices are highly seasonal. El Niño/La Niña patterns drive supply shocks. Planting intentions (USDA reports) are key catalysts.",
            "Corn-Soy Ratio":      "Farmers switch between corn and soy based on relative prices. A ratio above ~2.5 incentivises more corn planting, which eventually pressures corn prices.",
            "Carry & Storage":     "Physical commodities incur storage and financing costs ('carry'). Backwardated markets may discourage storage, tightening nearby supply.",
        }
    }

    for section, items in topics.items():
        with st.expander(section, expanded=False):
            for concept, explanation in items.items():
                st.markdown(f"**{concept}**")
                st.markdown(f"<div style='font-size:0.83rem;color:#8aafcc;line-height:1.6;margin-bottom:10px'>{explanation}</div>", unsafe_allow_html=True)

    # Position sizing calculator
    st.markdown('<div class="section-title">POSITION SIZING CALCULATOR</div>', unsafe_allow_html=True)
    st.caption("Risk-based position sizing using ATR — a standard professional approach.")

    ps_col1, ps_col2, ps_col3 = st.columns(3)
    account_size  = ps_col1.number_input("Account Size (USD)", value=100_000, step=10_000)
    risk_pct      = ps_col2.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    atr_mult      = ps_col3.slider("ATR Stop Multiplier", 1.0, 4.0, 2.0, 0.5)

    if not np.isnan(atr_val) and atr_val > 0 and price > 0:
        risk_usd   = account_size * risk_pct / 100
        stop_dist  = atr_val * atr_mult
        pos_size   = risk_usd / stop_dist
        notional   = pos_size * price
        pct_of_acc = notional / account_size * 100

        ps_col1.metric("Risk Amount (USD)", f"${risk_usd:,.0f}")
        ps_col2.metric("Stop Distance", f"{stop_dist:.2f} ({stop_dist/price*100:.1f}%)")
        ps_col3.metric("Units to Trade", f"{pos_size:.2f}")
        st.info(f"Notional Exposure: **${notional:,.0f}** ({pct_of_acc:.1f}% of account) | Entry: {price:.2f} | Stop: {price - stop_dist:.2f}")
        st.caption("⚠ For educational purposes only. Not financial advice.")
    else:
        st.warning("Insufficient ATR data for position sizing. Select a longer time horizon.")


# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding-top:1rem;border-top:1px solid #0d2035;
            font-family:'IBM Plex Mono';font-size:0.65rem;color:#1e3a55;text-align:center">
  CommodityOS · Data via Yahoo Finance · For educational & research purposes only ·
  Not financial advice · Signals are algorithmic and do not constitute investment recommendations
</div>
""", unsafe_allow_html=True)
