import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import requests
import io
import plotly.graph_objects as go

# --- 1. पेज सेटअप (सबसे पहले) ---
st.set_page_config(
    page_title="Pro Trader AI Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CRITICAL FIX: Initialization (KeyError रोकने के लिए) ---
# यह कोड सबसे ऊपर रहना चाहिए ताकि App को खाली डिब्बे पहले से मिल जाएं
if 'scan_df' not in st.session_state:
    st.session_state['scan_df'] = pd.DataFrame()

if 'buy_list' not in st.session_state:
    st.session_state['buy_list'] = []

if 'sell_list' not in st.session_state:
    st.session_state['sell_list'] = []

if 'password_correct' not in st.session_state:
    st.session_state['password_correct'] = False

# --- 3. Advance CSS (3D Cards + Day/Night Visibility) ---
st.markdown("""
<style>
    /* 3D Glassmorphism Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }
    
    /* Day Mode Specifics */
    @media (prefers-color-scheme: light) {
        .metric-card {
            background: linear-gradient(145deg, #ffffff, #e6e6e6);
            box-shadow: 5px 5px 10px #d9d9d9, -5px -5px 10px #ffffff;
            color: #333;
        }
        .stock-list { color: #555; }
    }

    /* Night Mode Specifics */
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background: linear-gradient(145deg, #1e1e1e, #2d2d2d);
            box-shadow: 5px 5px 15px #121212, -5px -5px 15px #383838;
            color: #e0e0e0;
        }
        .stock-list { color: #ccc; }
    }

    /* Text Styles */
    .card-title { font-size: 1.1rem; font-weight: bold; margin-bottom: 5px; opacity: 0.8; }
    .card-count { font-size: 2.5rem; font-weight: 900; margin: 0; }
    .stock-list { font-size: 0.85rem; margin-top: 10px; font-family: monospace; overflow-wrap: break-word; }
    .green-text { color: #00e676; }
    .red-text { color: #ff5252; }

    /* Button Style */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 55px;
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Advisor Note */
    .advisor-note {
        padding: 20px;
        border-left: 5px solid #ff9800;
        background-color: rgba(255, 152, 0, 0.1);
        border-radius: 5px;
        margin-bottom: 25px;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. Authentication ---
def check_password():
    if not st.session_state["password_correct"]:
        st.markdown("<br><br><h2 style='text-align: center;'>🔐 QUANTUM TRADER ACCESS</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            pwd = st.text_input("ENTER SECURITY PROTOCOL", type="password")
            if st.button("AUTHENTICATE SYSTEM"):
                if pwd == "Raipur@2026":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("ACCESS DENIED")
        return False
    return True

# --- 5. Logic Helper Functions ---
def calculate_technicals(df):
    try:
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df.ta.vwap(append=True) # VWAP column name varies
        return df
    except:
        return df

@st.cache_data
def get_nifty_tickers():
    try:
        url = "https://www.niftyindices.com/IndexConstituent/ind_nifty100list.csv"
        headers = {'User-Agent': 'Mozilla/5.0'}
        s = requests.get(url, headers=headers).content
        df = pd.read_csv(io.StringIO(s.decode('utf-8')))
        return [f"{x}.NS" for x in df['Symbol'].tolist()]
    except:
        return ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'SBIN.NS']

# --- MAIN APP LOGIC ---
if check_password():
    
    # Advisor Note
    st.markdown("""
    <div class="advisor-note">
        <strong>⚠️ FINANCIAL ADVISOR ALERT:</strong> <br>
        यह टूल केवल एनालिसिस के लिए है। 'Buy' या 'Sell' सिग्नल मिलने पर तुरंत ट्रेड न लें।
        चार्ट देखें, ट्रेंड समझें और हमेशा <strong>Stop Loss</strong> का उपयोग करें।
    </div>
    """, unsafe_allow_html=True)

    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1: st.title("📊 Pro Intraday Scanner")
    with col_h2: timeframe = st.selectbox("Timeframe", ["15m", "5m", "30m", "1h"])

    # --- SCANNER BUTTON ---
    col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
    with col_b2:
        scan_btn = st.button("🔍 START DEEP SCAN (Live)")

    if scan_btn:
        tickers = get_nifty_tickers()
        rows = []
        buy_names = []
        sell_names = []
        
        my_bar = st.progress(0, text="Initializing Quantum Scan...")
        limit = 30 # Limit for speed
        
        for i, ticker in enumerate(tickers[:limit]):
            try:
                df = yf.download(ticker, period="5d", interval=timeframe, progress=False)
                if len(df) > 20:
                    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                    df = calculate_technicals(df)
                    
                    curr = df.iloc[-1]
                    o, h, l, c = curr['Open'], curr['High'], curr['Low'], curr['Close']
                    rsi = curr.get('RSI', 50)
                    # VWAP Check (name adjustment)
                    vwap_col = [col for col in df.columns if 'VWAP' in col]
                    vwap = curr[vwap_col[0]] if vwap_col else c
                    
                    signal = "AVOID ⚪"
                    entry, target, sl = 0.0, 0.0, 0.0
                    
                    # Buy Logic
                    if abs(o - l) <= (o * 0.001):
                        strength = "WEAK"
                        if rsi > 55 and c > vwap: strength = "STRONG 🚀"
                        signal = f"BUY ({strength})"
                        entry, sl, target = o, o*0.99, o*1.015
                        if "STRONG" in strength: buy_names.append(ticker.replace('.NS',''))
                        
                    # Sell Logic
                    elif abs(o - h) <= (o * 0.001):
                        strength = "WEAK"
                        if rsi < 45 and c < vwap: strength = "STRONG 🩸"
                        signal = f"SELL ({strength})"
                        entry, sl, target = o, o*1.01, o*0.985
                        if "STRONG" in strength: sell_names.append(ticker.replace('.NS',''))

                    rows.append({
                        "Stock": ticker.replace('.NS', ''),
                        "Signal": signal,
                        "Entry Price": entry if entry > 0 else None,
                        "Target": target if target > 0 else None,
                        "Stop Loss": sl if sl > 0 else None,
                        "CMP": c,
                        "RSI": rsi
                    })
            except: pass
            my_bar.progress((i+1)/limit)
        
        my_bar.empty()
        st.session_state['scan_df'] = pd.DataFrame(rows)
        st.session_state['buy_list'] = buy_names
        st.session_state['sell_list'] = sell_names

    # --- RESULTS DISPLAY ---
    
    # 3D Cards
    st.write("### Market Momentum")
    c1, c2 = st.columns(2)
    b_str = ", ".join(st.session_state['buy_list']) if st.session_state['buy_list'] else "None"
    s_str = ", ".join(st.session_state['sell_list']) if st.session_state['sell_list'] else "None"

    with c1:
        st.markdown(f"""<div class="metric-card"><div class="card-title green-text">BULLISH RADAR</div>
        <div class="card-count green-text">{len(st.session_state['buy_list'])}</div><div class="stock-list">{b_str}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card"><div class="card-title red-text">BEARISH RADAR</div>
        <div class="card-count red-text">{len(st.session_state['sell_list'])}</div><div class="stock-list">{s_str}</div></div>""", unsafe_allow_html=True)

    # Table
    if not st.session_state['scan_df'].empty:
        df_display = st.session_state['scan_df'].copy()
        df_display.set_index("Stock", inplace=True)
        
        def highlight(val):
            if 'STRONG 🚀' in str(val): return 'background-color: #e8f5e9; color: green; font-weight: bold'
            if 'STRONG 🩸' in str(val): return 'background-color: #ffebee; color: red; font-weight: bold'
            if 'AVOID' in str(val): return 'color: #ff9800'
            return ''

        st.dataframe(
            df_display.style.map(highlight, subset=['Signal']),
            height=600,
            use_container_width=True,
            column_config={
                "Stock": st.column_config.TextColumn("Stock Name", pinned=True),
                "Signal": st.column_config.TextColumn("Status"),
                "Entry Price": st.column_config.NumberColumn("Entry ₹", format="%.2f"),
                "Target": st.column_config.NumberColumn("Target ₹", format="%.2f"),
                "Stop Loss": st.column_config.NumberColumn("SL ₹", format="%.2f"),
                "CMP": st.column_config.NumberColumn("Current ₹", format="%.2f"),
                "RSI": st.column_config.NumberColumn("RSI", format="%.1f"),
            }
        )
        
        # --- CHART SECTION (New Feature) ---
        st.write("---")
        st.subheader("📈 Visual Analysis (Tap to Open)")
        for idx, row in st.session_state['scan_df'].iterrows():
            if "STRONG" in row['Signal']:
                with st.expander(f"Show Chart: {idx} ({row['Signal']})"):
                    try:
                        data = yf.download(idx + ".NS", period="5d", interval=timeframe, progress=False)
                        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
                        fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])])
                        fig.update_layout(height=400, xaxis_rangeslider_visible=False, template="plotly_dark")
                        st.plotly_chart(fig, use_container_width=True)
                    except: st.error("Chart loading failed.")
    
    elif scan_btn:
        st.info("Market data processed. No signals found yet.")
