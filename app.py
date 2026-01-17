import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. पेज कॉन्फ़िगरेशन (Page Config) ---
st.set_page_config(
    page_title="Darvas Elite Scanner", 
    layout="wide", 
    page_icon="🦅",
    initial_sidebar_state="expanded"
)

# --- 2. कस्टम CSS (डिज़ाइन, लोगो और रंगों के लिए) ---
st.markdown("""
<style>
    /* मेन बैकग्राउंड हल्का सा डार्क ग्रे (Professional Look) */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* साइडबार का स्टाइल */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }

    /* मेट्रिक्स कार्ड्स (ऊपर के 3 डिब्बे) */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        text-align: center;
    }

    /* टिकर (चलती हुई पट्टी) का स्टाइल */
    .ticker-wrap-green {
        background: linear-gradient(90deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 12px;
        border-radius: 8px;
        border-left: 5px solid #28a745;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .ticker-wrap-red {
        background: linear-gradient(90deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 12px;
        border-radius: 8px;
        border-left: 5px solid #dc3545;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* बटन का स्टाइल */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(45deg, #2980b9, #6dd5fa);
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px;
        border-radius: 5px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background: linear-gradient(45deg, #1f618d, #2980b9);
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. पासवर्ड सुरक्षा ---
MY_PASSWORD = "Rituraj87" 

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        with st.sidebar:
            st.header("🔒 Login Required")
            pwd = st.text_input("Enter Password:", type="password")
            if st.button("Login"):
                if pwd == MY_PASSWORD:
                    st.session_state.password_correct = True
                    st.rerun()
                else:
                    st.error("Incorrect Password")
        return False
    return True

if not check_password():
    st.stop()

# --- 4. साइडबार (LOGO और कंट्रोल) ---
with st.sidebar:
    # --- LOGO AREA ---
    # आप यहाँ अपनी इमेज का लिंक डाल सकते हैं या GitHub पर इमेज अपलोड करके उसका लिंक दें
    # अभी मैं एक प्रोफेशनल इमोजी लोगो बना रहा हूँ
    st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <h1 style='font-size: 60px; margin:0;'>🦅</h1>
            <h2 style='color: #2c3e50; margin:0;'>DARVAS</h2>
            <h3 style='color: #e74c3c; margin:0;'>ELITE PRO</h3>
            <hr>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("Welcome to the premium Nifty 500 scanner.")
    
    # स्कैन बटन साइडबार में
    start_scan = st.button("🚀 SCAN MARKET NOW", type="primary")
    
    st.info("💡 **Tip:** Rotate phone to landscape mode for best view.")
    st.caption("v3.0 | 2026 Edition")

# --- स्टॉक लिस्ट (Top 150 Liquid Stocks for Fast Scan) ---
STOCKS = [
    "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "TCS.NS",
    "L&T.NS", "AXISBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS",
    "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS", "HCLTECH.NS", "TITAN.NS",
    "SUNPHARMA.NS", "ULTRACEMCO.NS", "TATAMOTORS.NS", "M&M.NS", "NTPC.NS",
    "POWERGRID.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "ADANIENT.NS", "HINDUNILVR.NS",
    "GRASIM.NS", "COALINDIA.NS", "ONGC.NS", "TECHM.NS", "HINDALCO.NS",
    "WIPRO.NS", "DIVISLAB.NS", "CIPLA.NS", "SBILIFE.NS", "DRREDDY.NS",
    "BAJAJFINSV.NS", "BPCL.NS", "BRITANNIA.NS", "EICHERMOT.NS", "HEROMOTOCO.NS",
    "TATACONSUM.NS", "INDUSINDBK.NS", "APOLLOHOSP.NS", "UPL.NS", "LICI.NS",
    "ADANIPORTS.NS", "DMART.NS", "ZOMATO.NS", "HAL.NS", "BEL.NS", "JIOFIN.NS",
    "VBL.NS", "TRENT.NS", "SIEMENS.NS", "IOC.NS", "DLF.NS", "BANKBARODA.NS",
    "CHOLAFIN.NS", "GAIL.NS", "RECLTD.NS", "SHRIRAMFIN.NS", "PFC.NS",
    "ADANIPOWER.NS", "ABB.NS", "HAVELLS.NS", "AMBUJACEM.NS", "CANBK.NS",
    "TVSMOTOR.NS", "DABUR.NS", "VEDL.NS", "PNB.NS", "INDIGO.NS", "NAUKRI.NS",
    "ICICIPRULI.NS", "PIDILITIND.NS", "SBICARD.NS", "LODHA.NS", "JINDALSTEL.NS",
    "POLYCAB.NS", "IRCTC.NS", "CUMMINSIND.NS", "BOSCHLTD.NS", "MCDOWELL-N.NS",
    "PERSISTENT.NS", "MUTHOOTFIN.NS", "ASHOKLEY.NS", "MRF.NS", "PIIND.NS",
    "IDFCFIRSTB.NS", "ASTRAL.NS", "TATACOMM.NS", "PHOENIXLTD.NS", "MPHASIS.NS",
    "SUPREMEIND.NS", "TIINDIA.NS", "LALPATHLAB.NS", "AUBANK.NS", "CONCOR.NS",
    "ABCAPITAL.NS", "TATACHEM.NS", "FEDERALBNK.NS", "OBEROIRLTY.NS", "LTTS.NS",
    "ATUL.NS", "COROMANDEL.NS", "GMRINFRA.NS", "WHIRLPOOL.NS", "ALKEM.NS",
    "COFORGE.NS", "BHEL.NS", "SAIL.NS", "NATIONALUM.NS", "BANDHANBNK.NS"
]

@st.cache_data(ttl=600)
def get_stock_data(symbol):
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if len(df) < 30: return None
        
        def get_val(series):
            return series.iloc[0] if isinstance(series, pd.Series) else series

        current_close = get_val(df['Close'].iloc[-1])
        past_data = df.iloc[:-1]
        
        box_high = get_val(past_data['High'].tail(20).max())
        box_low = get_val(past_data['Low'].tail(20).min())
        avg_vol = get_val(past_data['Volume'].tail(20).mean())
        current_vol = get_val(df['Volume'].iloc[-1])
        rvol = current_vol / avg_vol if avg_vol > 0 else 0

        return {"symbol": symbol.replace(".NS", ""), "close": current_close, "box_high": box_high, "box_low": box_low, "rvol": rvol}
    except:
        return None

# --- 5. मुख्य ऐप लॉजिक ---
st.title("📊 Market Dashboard")

if start_scan:
    # प्रोग्रेस बार ऊपर दिखाएं
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    valid_data = []
    entry_names = []
    exit_names = []
    
    for i, stock in enumerate(STOCKS):
        status_text.caption(f"Scanning {stock}...")
        data = get_stock_data(stock)
        progress_bar.progress((i + 1) / len(STOCKS))
        
        if data:
            cmp = data['close']
            entry = data['box_high']
            sl = data['box_low']
            rvol = data['rvol']
            
            is_above_box = cmp > entry
            volume_ok = rvol > 1.5 
            
            if is_above_box:
                risk = entry - sl
                target = entry + (risk * 2)
                pct_change = ((cmp - entry) / entry) * 100
                
                status = ""
                if cmp < sl:
                    status = "EXIT SIGNAL"
                    exit_names.append(data['symbol'])
                else:
                    status = "BUY SIGNAL"
                    entry_names.append(data['symbol'])

                tv_link = f"https://in.tradingview.com/chart/?symbol=NSE:{data['symbol']}"

                valid_data.append({
                    "Stock": data['symbol'],
                    "Chart": tv_link,
                    "CMP": cmp,
                    "Entry": entry,
                    "Target": target,
                    "Stop Loss": sl,
                    "% Gain": pct_change,
                    "Status": status
                })

    progress_bar.empty()
    status_text.empty()

    if valid_data:
        # --- 6. डैशबोर्ड मेट्रिक्स (Dashboard Metrics) ---
        # यह नया फीचर है: 3 बड़े बॉक्स
        total_found = len(valid_data)
        total_buy = len(entry_names)
        total_exit = len(exit_names)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Opportunities", value=total_found)
        with col2:
            st.metric(label="Bullish (Buy)", value=total_buy, delta="Strong")
        with col3:
            st.metric(label="Bearish (Exit)", value=total_exit, delta="-Weak", delta_color="inverse")
        
        st.write("---") # डिवाइडर लाइन

        # --- 7. टिकर (News Ticker) ---
        if entry_names:
            entry_str = " &nbsp; • &nbsp; ".join(entry_names)
            st.markdown(f"<div class='ticker-wrap-green'><marquee scrollamount='10'>🚀 <b>STRONG BUY:</b> {entry_str}</marquee></div>", unsafe_allow_html=True)
            
        if exit_names:
            exit_str = " &nbsp; • &nbsp; ".join(exit_names)
            st.markdown(f"<div class='ticker-wrap-red'><marquee scrollamount='10'>🛑 <b>EXIT ALERT:</b> {exit_str}</marquee></div>", unsafe_allow_html=True)

        # --- 8. फाइनल टेबल ---
        df_result = pd.DataFrame(valid_data)
        
        def color_status(val):
            if 'EXIT' in val: return 'background-color: #ffcccc; color: #b30000; font-weight: bold;'
            elif 'BUY' in val: return 'background-color: #d4edda; color: #155724; font-weight: bold;'
            return ''

        st.dataframe(
            df_result.style.map(color_status, subset=['Status']).format({
                "CMP": "{:.2f}", "Entry": "{:.2f}", "Target": "{:.2f}", 
                "Stop Loss": "{:.2f}", "% Gain": "{:.2f}%"
            }),
            column_config={
                "Stock": st.column_config.TextColumn("Symbol", help="Stock Name"),
                "Chart": st.column_config.LinkColumn("View", display_text="Open Chart"),
            },
            use_container_width=True,
            height=600,
            hide_index=True
        )
    else:
        st.warning("No high-probability setups found in current market.")

else:
    # जब स्कैन नहीं हो रहा हो, तब खाली स्क्रीन सुंदर दिखे
    st.info("👈 Please click 'SCAN MARKET NOW' from the sidebar to start.")
    st.image("https://images.unsplash.com/photo-1611974765270-ca1258634369?q=80&w=1000&auto=format&fit=crop", caption="Market Analytics", use_column_width=True)
