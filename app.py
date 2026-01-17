import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. पेज कॉन्फ़िगरेशन ---
st.set_page_config(
    page_title="Darvas Elite 300", 
    layout="wide", 
    page_icon="🦅",
    initial_sidebar_state="collapsed" # मोबाइल पर साइडबार बंद रहेगा ताकि स्क्रीन बड़ी दिखे
)

# --- 2. स्मार्ट CSS (Auto Dark/Light Mode Support) ---
st.markdown("""
<style>
    /* नोट: हमने बैकग्राउंड कलर हटा दिया है ताकि 
       यह आपके फोन की सेटिंग (Dark/Light) के हिसाब से अपने आप सेट हो जाए 
    */
    
    /* मेट्रिक्स कार्ड्स (Stats) */
    div[data-testid="metric-container"] {
        border: 1px solid #444; /* डार्क बॉर्डर ताकि ब्लैक थीम में भी दिखे */
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }

    /* टिकर (News Ticker) - यह हमेशा हाईलाइटेड रहेगा */
    .ticker-wrap-green {
        background: linear-gradient(90deg, #155724 0%, #1e8e3e 100%); /* डार्क ग्रीन */
        color: white; /* वाइट टेक्स्ट */
        padding: 12px;
        border-radius: 8px;
        border-left: 5px solid #2ecc71;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .ticker-wrap-red {
        background: linear-gradient(90deg, #721c24 0%, #c0392b 100%); /* डार्क रेड */
        color: white;
        padding: 12px;
        border-radius: 8px;
        border-left: 5px solid #e74c3c;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    /* बटन स्टाइल (Blue Gradient) */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(45deg, #2980b9, #6dd5fa);
        color: white;
        font-weight: bold;
        border: none;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. पासवर्ड सुरक्षा ---
MY_PASSWORD = "Rituraj87" 

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        st.header("🔒 Secure Login")
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

# --- 4. साइडबार (लोगो और कंट्रोल) ---
with st.sidebar:
    st.markdown("""
        <div style='text-align: center;'>
            <h1>🦅</h1>
            <h3>DARVAS ELITE</h3>
            <p>Scanning 300 Stocks</p>
            <hr>
        </div>
    """, unsafe_allow_html=True)
    
    # स्कैन बटन
    start_scan = st.button("🚀 START SCAN (300)", type="primary")
    
    st.info("System Theme: Auto (Black/White)")
    st.caption("v4.0 | 300 Stocks Edition")

# --- 5. NIFTY 500 LIST (Expanded to 300 Stocks) ---
STOCKS = [
    # --- Top Giants (50) ---
    "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "TCS.NS",
    "L&T.NS", "AXISBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS",
    "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS", "HCLTECH.NS", "TITAN.NS",
    "SUNPHARMA.NS", "ULTRACEMCO.NS", "TATAMOTORS.NS", "M&M.NS", "NTPC.NS",
    "POWERGRID.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "ADANIENT.NS", "HINDUNILVR.NS",
    "GRASIM.NS", "COALINDIA.NS", "ONGC.NS", "TECHM.NS", "HINDALCO.NS",
    "WIPRO.NS", "DIVISLAB.NS", "CIPLA.NS", "SBILIFE.NS", "DRREDDY.NS",
    "BAJAJFINSV.NS", "BPCL.NS", "BRITANNIA.NS", "EICHERMOT.NS", "HEROMOTOCO.NS",
    "TATACONSUM.NS", "INDUSINDBK.NS", "APOLLOHOSP.NS", "UPL.NS", "LICI.NS",
    
    # --- Midcap & F&O High Volume (100) ---
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
    "COFORGE.NS", "TDPOWERSYS.NS", "BHEL.NS", "SAIL.NS", "NATIONALUM.NS",
    "BANDHANBNK.NS", "GUJGASLTD.NS", "IPCALAB.NS", "LAURUSLABS.NS", "TATAELXSI.NS",
    "DEEPAKNTR.NS", "CROMPTON.NS", "ACC.NS", "DALBHARAT.NS", "JSL.NS",
    "APLAPOLLO.NS", "MFSL.NS", "PETRONET.NS", "ZEEL.NS", "RAMCOCEM.NS",
    "NAVINFLUOR.NS", "SYNGENE.NS", "TRIDENT.NS", "SOLARINDS.NS", "RVNL.NS",
    
    # --- Emerging & Volatile (50) ---
    "IRFC.NS", "MAZDOCK.NS", "COCHINSHIP.NS", "FACT.NS", "SUZLON.NS",
    "IDEA.NS", "YESBANK.NS", "IDBI.NS", "UNIONBANK.NS", "IOB.NS",
    "UCOBANK.NS", "CENTRALBK.NS", "MAHABANK.NS", "BANKINDIA.NS", "BSE.NS",
    "CDSL.NS", "ANGELONE.NS", "MCX.NS", "MOTILALOFS.NS", "IEX.NS",
    "LUPIN.NS", "BIOCON.NS", "AUROPHARMA.NS", "GLENMARK.NS", "ZYDUSLIFE.NS",
    "GRANULES.NS", "ABFRL.NS", "BATAINDIA.NS", "RELAXO.NS", "PAGEIND.NS",
    "JUBLFOOD.NS", "DEVYANI.NS", "SAPPHIRE.NS", "KALYANKJIL.NS", "RAJESHEXPO.NS",
    "MANAPPURAM.NS", "M&MFIN.NS", "LICHSGFIN.NS", "POONAWALLA.NS", "SUNDARAMFIN.NS",
    "KPITTECH.NS", "CYIENT.NS", "BSOFT.NS", "SONACOMS.NS", "ZENSARTECH.NS",
    "OFSS.NS", "HONAUT.NS", "KEI.NS", "DIXON.NS", "AMBER.NS",
    
    # --- Extra Momentum Stocks (100) ---
    "KAYNES.NS", "DATAPATTNS.NS", "MTARTECH.NS", "PARAS.NS", "ASTRAMICRO.NS",
    "CENTUM.NS", "HBLPOWER.NS", "TITAGARH.NS", "TEXRAIL.NS", "JWL.NS",
    "RKFORGE.NS", "ELECTCAST.NS", "GABRIEL.NS", "PRICOLLTD.NS", "SUBROS.NS",
    "LUMAXIND.NS", "MINDA CORP.NS", "UNOMINDA.NS", "ENDURANCE.NS", "CRAFTSMAN.NS",
    "JAMNAAUTO.NS", "GNA.NS", "ROLEXRINGS.NS", "SFL.NS", "TIMKEN.NS",
    "SCHAEFFLER.NS", "SKFINDIA.NS", "AIAENG.NS", "THERMAX.NS", "TRIVENI.NS",
    "PRAJIND.NS", "BALRAMCHIN.NS", "EIDPARRY.NS", "RENUKA.NS", "TRIVENITURB.NS",
    "KIRLOSENG.NS", "ELGIEQUIP.NS", "INGERRAND.NS", "KSB.NS", "POWERINDIA.NS",
    "HITACHI.NS", "VOLTAS.NS", "BLUESTARCO.NS", "KAJARIACER.NS", "CERA.NS",
    "SOMANYCERA.NS", "GREENPANEL.NS", "CENTURYPLY.NS", "STYLAMIND.NS", "PRINCEPIPE.NS",
    "FINPIPE.NS", "JINDALSAW.NS", "WELCORP.NS", "MAHARSEAM.NS", "RATNAMANI.NS",
    "APLLTD.NS", "ALEMBICLTD.NS", "ERIS.NS", "AJANTPHARM.NS", "JBITHEM.NS",
    "NATCOPHARM.NS", "PFIZER.NS", "SANOFI.NS", "ABBOTINDIA.NS", "GLAXO.NS",
    "ASTERDM.NS", "NARAYANA.NS", "KIMS.NS", "RAINBOW.NS", "METROPOLIS.NS",
    "LALPATHLAB.NS", "THYROCARE.NS", "VIJAYA.NS", "FORTIS.NS", "MAXHEALTH.NS",
    "NH.NS", "HCG.NS", "POLYMED.NS", "LINDEINDIA.NS", "FLUOROCHEM.NS",
    "AETHER.NS", "CLEAN.NS", "FINEORG.NS", "VINATIORGA.NS", "ROSSARI.NS",
    "NOCIL.NS", "SUMICHEM.NS", "UPL.NS", "RALLIS.NS", "CHAMBLFERT.NS",
    "GNFC.NS", "GSFC.NS", "DEEPAKFERT.NS", "PARADEEP.NS", "IPL.NS"
]

@st.cache_data(ttl=900) # 15 मिनट कैश (ताकि 300 स्टॉक बार-बार लोड न हों)
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

# --- मुख्य ऐप लॉजिक ---
st.title("📊 Market Dashboard (300)")

if start_scan:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    valid_data = []
    entry_names = []
    exit_names = []
    
    # 300 स्टॉक्स स्कैन लूप
    for i, stock in enumerate(STOCKS):
        status_text.caption(f"Analyzing {i+1}/{len(STOCKS)}: {stock}...")
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
                # यहाँ हमने लॉजिक वापस BUY / HOLD कर दिया है
                if cmp < sl:
                    status = "EXIT NOW"
                    exit_names.append(data['symbol'])
                else:
                    status = "BUY / HOLD"
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
        # --- डैशबोर्ड मेट्रिक्स ---
        total_found = len(valid_data)
        total_buy = len(entry_names)
        total_exit = len(exit_names)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Stocks Found", value=total_found)
        with col2:
            st.metric(label="BUY / HOLD", value=total_buy, delta="Bullish")
        with col3:
            st.metric(label="EXIT ALERT", value=total_exit, delta="-Bearish", delta_color="inverse")
        
        st.write("---")

        # --- टिकर (High Contrast for both Black/White Modes) ---
        if entry_names:
            entry_str = " &nbsp; • &nbsp; ".join(entry_names)
            st.markdown(f"<div class='ticker-wrap-green'><marquee scrollamount='10'>🚀 <b>BUY / HOLD:</b> {entry_str}</marquee></div>", unsafe_allow_html=True)
            
        if exit_names:
            exit_str = " &nbsp; • &nbsp; ".join(exit_names)
            st.markdown(f"<div class='ticker-wrap-red'><marquee scrollamount='10'>🛑 <b>EXIT NOW:</b> {exit_str}</marquee></div>", unsafe_allow_html=True)

        # --- फाइनल टेबल ---
        df_result = pd.DataFrame(valid_data)
        
        def color_status(val):
            # यह रंग ऑटोमैटिक थीम के साथ भी अच्छे दिखेंगे
            if 'EXIT' in val: return 'background-color: #ff4b4b; color: white; font-weight: bold;'
            elif 'BUY' in val: return 'background-color: #2ecc71; color: black; font-weight: bold;'
            return ''

        st.dataframe(
            df_result.style.map(color_status, subset=['Status']).format({
                "CMP": "{:.2f}", "Entry": "{:.2f}", "Target": "{:.2f}", 
                "Stop Loss": "{:.2f}", "% Gain": "{:.2f}%"
            }),
            column_config={
                "Stock": st.column_config.TextColumn("Symbol"),
                "Chart": st.column_config.LinkColumn("View", display_text="Open Chart"),
            },
            use_container_width=True,
            height=800, # टेबल की हाइट बढ़ा दी है
            hide_index=True
        )
    else:
        st.warning("No active setups found in 300 stocks list.")

else:
    st.info("👈 Tap 'START SCAN' in the sidebar to analyze 300 stocks.")
