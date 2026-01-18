import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. पेज सेटिंग (Page Config) ---
st.set_page_config(
    page_title="Darvas Elite Pro", 
    layout="wide", 
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# --- 2. स्मार्ट CSS (Card Style & Design) ---
st.markdown("""
<style>
    /* कार्ड स्टाइल (Cards) */
    .metric-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        transition: 0.3s;
        margin-bottom: 20px;
        color: black;
    }
    .metric-card:hover {
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
        transform: scale(1.02);
    }
    
    /* डार्क मोड सपोर्ट के लिए कार्ड टेक्स्ट */
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background-color: #262730;
            color: white;
            box-shadow: 0 4px 8px 0 rgba(255,255,255,0.1);
        }
    }

    /* टिकर स्टाइल */
    .ticker-green {
        background: linear-gradient(90deg, #155724 0%, #28a745 100%);
        color: white;
        padding: 10px;
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .ticker-red {
        background: linear-gradient(90deg, #721c24 0%, #dc3545 100%);
        color: white;
        padding: 10px;
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* बटन डिज़ाइन */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(45deg, #1e3c72, #2a5298);
        color: white;
        font-weight: bold;
        border: none;
        padding: 12px;
        border-radius: 8px;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. लॉगिन सिस्टम (ID & Password) ---
# अपना यूजरनेम और पासवर्ड यहाँ सेट करें
VALID_USERNAME = "Rituraj87"
VALID_PASSWORD = "16Aug&1987"

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.markdown("<h2 style='text-align: center;'>🔐 Secure Login</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("User ID")
            password = st.text_input("Password", type="password")
            
            if st.button("Login"):
                if username == VALID_USERNAME and password == VALID_PASSWORD:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ गलत User ID या Password")
        return False
    return True

if not check_login():
    st.stop()

# --- 4. साइडबार (फोटो और कंट्रोल) ---
with st.sidebar:
    # --- नई ट्रेडिंग फोटो ---
    # यह एक प्रोफेशनल ट्रेडिंग डेस्क की फोटो है
    st.image("https://images.unsplash.com/photo-1642543492481-44e81e3914a7?q=80&w=1000&auto=format&fit=crop", use_column_width=True)
    
    st.markdown("---")
    st.title("DARVAS PRO")
    st.caption("Scanning 300+ Stocks")
    
    # स्कैन बटन
    start_scan = st.button("🚀 SCAN MARKET NOW", type="primary")

# --- 5. STOCK LIST (Updated to 300+ Unique Stocks) ---
STOCKS = [
    # Nifty 50
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "L&T.NS", "HINDUNILVR.NS",
    "KOTAKBANK.NS", "AXISBANK.NS", "HCLTECH.NS", "TITAN.NS", "ASIANPAINT.NS", "BAJFINANCE.NS", "MARUTI.NS", "ULTRACEMCO.NS", "SUNPHARMA.NS", "TATAMOTORS.NS",
    "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "JSWSTEEL.NS", "ADANIENT.NS", "TATASTEEL.NS", "M&M.NS", "HINDALCO.NS", "GRASIM.NS", "COALINDIA.NS",
    "WIPRO.NS", "TECHM.NS", "BAJAJFINSV.NS", "DRREDDY.NS", "CIPLA.NS", "BRITANNIA.NS", "ADANIPORTS.NS", "SBILIFE.NS", "APOLLOHOSP.NS", "INDUSINDBK.NS",
    "TATACONSUM.NS", "DIVISLAB.NS", "EICHERMOT.NS", "BPCL.NS", "HEROMOTOCO.NS", "UPL.NS", "LICI.NS", "JIOFIN.NS", "VBL.NS", "ZOMATO.NS",
    
    # Nifty Next 50 & Midcap High Liquidity
    "HAL.NS", "DLF.NS", "BEL.NS", "SIEMENS.NS", "TRENT.NS", "IOC.NS", "PIDILITIND.NS", "BANKBARODA.NS", "CHOLAFIN.NS", "GAIL.NS",
    "RECLTD.NS", "SHRIRAMFIN.NS", "PFC.NS", "ADANIPOWER.NS", "ABB.NS", "HAVELLS.NS", "AMBUJACEM.NS", "CANBK.NS", "TVSMOTOR.NS", "DABUR.NS",
    "VEDL.NS", "PNB.NS", "INDIGO.NS", "NAUKRI.NS", "ICICIPRULI.NS", "SBICARD.NS", "LODHA.NS", "JINDALSTEL.NS", "POLYCAB.NS", "IRCTC.NS",
    "CUMMINSIND.NS", "BOSCHLTD.NS", "MCDOWELL-N.NS", "PERSISTENT.NS", "MUTHOOTFIN.NS", "ASHOKLEY.NS", "MRF.NS", "PIIND.NS", "IDFCFIRSTB.NS", "ASTRAL.NS",
    "TATACOMM.NS", "PHOENIXLTD.NS", "MPHASIS.NS", "SUPREMEIND.NS", "TIINDIA.NS", "LALPATHLAB.NS", "AUBANK.NS", "CONCOR.NS", "ABCAPITAL.NS", "TATACHEM.NS",
    
    # F&O & Active Stocks
    "FEDERALBNK.NS", "OBEROIRLTY.NS", "LTTS.NS", "ATUL.NS", "COROMANDEL.NS", "GMRINFRA.NS", "WHIRLPOOL.NS", "ALKEM.NS", "COFORGE.NS", "TDPOWERSYS.NS",
    "BHEL.NS", "SAIL.NS", "NATIONALUM.NS", "BANDHANBNK.NS", "GUJGASLTD.NS", "IPCALAB.NS", "LAURUSLABS.NS", "TATAELXSI.NS", "DEEPAKNTR.NS", "CROMPTON.NS",
    "ACC.NS", "DALBHARAT.NS", "JSL.NS", "APLAPOLLO.NS", "MFSL.NS", "PETRONET.NS", "ZEEL.NS", "RAMCOCEM.NS", "NAVINFLUOR.NS", "SYNGENE.NS",
    "TRIDENT.NS", "SOLARINDS.NS", "RVNL.NS", "IRFC.NS", "MAZDOCK.NS", "COCHINSHIP.NS", "FACT.NS", "SUZLON.NS", "IDEA.NS", "YESBANK.NS",
    "IDBI.NS", "UNIONBANK.NS", "IOB.NS", "UCOBANK.NS", "CENTRALBK.NS", "MAHABANK.NS", "BANKINDIA.NS", "BSE.NS", "CDSL.NS", "ANGELONE.NS",
    
    # Mid & Small Cap Momentum
    "MCX.NS", "MOTILALOFS.NS", "IEX.NS", "LUPIN.NS", "BIOCON.NS", "AUROPHARMA.NS", "GLENMARK.NS", "ZYDUSLIFE.NS", "GRANULES.NS", "ABFRL.NS",
    "BATAINDIA.NS", "RELAXO.NS", "PAGEIND.NS", "JUBLFOOD.NS", "DEVYANI.NS", "SAPPHIRE.NS", "KALYANKJIL.NS", "RAJESHEXPO.NS", "MANAPPURAM.NS", "M&MFIN.NS",
    "LICHSGFIN.NS", "POONAWALLA.NS", "SUNDARAMFIN.NS", "KPITTECH.NS", "CYIENT.NS", "BSOFT.NS", "SONACOMS.NS", "ZENSARTECH.NS", "OFSS.NS", "HONAUT.NS",
    "KEI.NS", "DIXON.NS", "AMBER.NS", "KAYNES.NS", "DATAPATTNS.NS", "MTARTECH.NS", "PARAS.NS", "ASTRAMICRO.NS", "CENTUM.NS", "HBLPOWER.NS",
    "TITAGARH.NS", "TEXRAIL.NS", "JWL.NS", "RKFORGE.NS", "ELECTCAST.NS", "GABRIEL.NS", "PRICOLLTD.NS", "SUBROS.NS", "LUMAXIND.NS", "MINDA CORP.NS",
    "UNOMINDA.NS", "ENDURANCE.NS", "CRAFTSMAN.NS", "JAMNAAUTO.NS", "GNA.NS", "ROLEXRINGS.NS", "SFL.NS", "TIMKEN.NS", "SCHAEFFLER.NS", "SKFINDIA.NS",
    "AIAENG.NS", "THERMAX.NS", "TRIVENI.NS", "PRAJIND.NS", "BALRAMCHIN.NS", "EIDPARRY.NS", "RENUKA.NS", "TRIVENITURB.NS", "KIRLOSENG.NS", "ELGIEQUIP.NS",
    "INGERRAND.NS", "KSB.NS", "POWERINDIA.NS", "HITACHI.NS", "VOLTAS.NS", "BLUESTARCO.NS", "KAJARIACER.NS", "CERA.NS", "SOMANYCERA.NS", "GREENPANEL.NS",
    "CENTURYPLY.NS", "STYLAMIND.NS", "PRINCEPIPE.NS", "FINPIPE.NS", "JINDALSAW.NS", "WELCORP.NS", "MAHARSEAM.NS", "RATNAMANI.NS", "APLLTD.NS", "ALEMBICLTD.NS",
    "ERIS.NS", "AJANTPHARM.NS", "JBITHEM.NS", "NATCOPHARM.NS", "PFIZER.NS", "SANOFI.NS", "ABBOTINDIA.NS", "GLAXO.NS", "ASTERDM.NS", "NARAYANA.NS",
    "KIMS.NS", "RAINBOW.NS", "METROPOLIS.NS", "THYROCARE.NS", "VIJAYA.NS", "FORTIS.NS", "MAXHEALTH.NS", "NH.NS", "HCG.NS", "POLYMED.NS", "LINDEINDIA.NS",
    "FLUOROCHEM.NS", "AETHER.NS", "CLEAN.NS", "FINEORG.NS", "VINATIORGA.NS", "ROSSARI.NS", "NOCIL.NS", "SUMICHEM.NS", "RALLIS.NS", "CHAMBLFERT.NS",
    "GNFC.NS", "GSFC.NS", "DEEPAKFERT.NS", "PARADEEP.NS", "IPL.NS", "CASTROLIND.NS", "OIL.NS", "GSPL.NS", "IGL.NS", "MGL.NS", "GUJGASLTD.NS",
    "PETRONET.NS", "AEGISCHEM.NS", "CONFIPET.NS", "HINDPETRO.NS", "BPCL.NS", "IOC.NS", "CHENNPETRO.NS", "MRPL.NS", "BORORENEW.NS", "SWANENERGY.NS",
    "KPIGREEN.NS", "INOXWIND.NS", "SJVN.NS", "NHPC.NS", "NBCC.NS", "HUDCO.NS", "RITES.NS", "IRCON.NS", "RAILTEL.NS", "GMDC.NS", "MOIL.NS",
    "NMDC.NS", "KIOCL.NS", "GPIL.NS", "JAICORPLTD.NS", "MSUMI.NS", "MOTHERSON.NS", "SAMVARDHANA.NS", "VARROC.NS", "AUTOAXLES.NS", "BANCOINDIA.NS", "RICOAUTO.NS"
]

@st.cache_data(ttl=900)
def get_stock_data(symbol):
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if len(df) < 30: return None
        def get_val(s): return s.iloc[0] if isinstance(s, pd.Series) else s
        
        current_close = get_val(df['Close'].iloc[-1])
        past_data = df.iloc[:-1]
        box_high = get_val(past_data['High'].tail(20).max())
        box_low = get_val(past_data['Low'].tail(20).min())
        avg_vol = get_val(past_data['Volume'].tail(20).mean())
        current_vol = get_val(df['Volume'].iloc[-1])
        rvol = current_vol / avg_vol if avg_vol > 0 else 0
        
        return {"symbol": symbol.replace(".NS", ""), "close": current_close, "box_high": box_high, "box_low": box_low, "rvol": rvol}
    except: return None

# --- 6. मुख्य स्कैनिंग और कार्ड डिस्प्ले ---
st.title("📊 Market Dashboard")

if start_scan:
    progress_bar = st.progress(0)
    status_text = st.empty()
    valid_data, entry_names, exit_names = [], [], []
    
    for i, stock in enumerate(STOCKS):
        status_text.caption(f"Analyzing {i+1}/{len(STOCKS)}: {stock}...")
        data = get_stock_data(stock)
        progress_bar.progress((i + 1) / len(STOCKS))
        
        if data:
            cmp = data['close']
            entry = data['box_high']
            sl = data['box_low']
            rvol = data['rvol']
            
            if cmp > entry:
                risk = entry - sl
                target = entry + (risk * 2)
                pct_change = ((cmp - entry) / entry) * 100
                
                status = ""
                if cmp < sl:
                    status = "EXIT NOW"
                    exit_names.append(data['symbol'])
                elif rvol > 1.5:
                    status = "🚀 STRONG BUY"
                    entry_names.append(data['symbol'])
                else:
                    status = "🟢 HOLD"
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
        # --- NEW: CARD STYLE METRICS (HTML/CSS) ---
        total_found = len(valid_data)
        total_buy = len(entry_names)
        total_exit = len(exit_names)

        # यहाँ हम कार्ड्स बना रहे हैं
        st.markdown(f"""
        <div style="display: flex; gap: 20px; justify-content: center; margin-bottom: 20px;">
            <div class="metric-card" style="flex: 1; border-top: 5px solid #2980b9;">
                <h3 style="margin:0; font-size: 18px; color:gray;">Total Scanned</h3>
                <h1 style="margin:0; font-size: 36px; color:#2980b9;">{total_found}</h1>
                <p>Stocks Found</p>
            </div>
            <div class="metric-card" style="flex: 1; border-top: 5px solid #2ecc71;">
                <h3 style="margin:0; font-size: 18px; color:gray;">Buy / Hold</h3>
                <h1 style="margin:0; font-size: 36px; color:#2ecc71;">{total_buy}</h1>
                <p>Bullish Trend</p>
            </div>
            <div class="metric-card" style="flex: 1; border-top: 5px solid #e74c3c;">
                <h3 style="margin:0; font-size: 18px; color:gray;">Exit Signals</h3>
                <h1 style="margin:0; font-size: 36px; color:#e74c3c;">{total_exit}</h1>
                <p>Stop Loss Hit</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")

        # Ticker
        if entry_names:
            st.markdown(f"<div class='ticker-green'><marquee>🚀 <b>STRONG BUY / HOLD:</b> {' • '.join(entry_names)}</marquee></div>", unsafe_allow_html=True)
        if exit_names:
            st.markdown(f"<div class='ticker-red'><marquee>🛑 <b>EXIT NOW:</b> {' • '.join(exit_names)}</marquee></div>", unsafe_allow_html=True)

        # Table
        df_result = pd.DataFrame(valid_data)
        def color_status(val):
            if 'EXIT' in val: return 'background-color: #ff4b4b; color: white; font-weight: bold;'
            elif 'STRONG BUY' in val: return 'background-color: #2ecc71; color: black; font-weight: bold;'
            elif 'HOLD' in val: return 'background-color: #d4edda; color: green; font-weight: bold;'
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
            use_container_width=True, height=800, hide_index=True
        )
    else:
        st.warning("No active setups found.")
else:
    st.info("👈 Please login and click 'START SCAN' in the sidebar.")
