import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. पेज कॉन्फ़िगरेशन ---
st.set_page_config(
    page_title="Darvas Pro 3D", 
    layout="wide", 
    page_icon="🦅",
    initial_sidebar_state="expanded"
)

# --- 2. 3D ADVANCED CSS (New Styles) ---
st.markdown("""
<style>
    /* 1. 3D Search Bar Style */
    .stTextInput > div > div > input {
        border-radius: 15px;
        border: none;
        padding: 15px;
        font-size: 18px;
        background: #f0f2f6;
        box-shadow: inset 5px 5px 10px #bebebe, inset -5px -5px 10px #ffffff; /* Neumorphic 3D Look */
        color: #333;
        font-weight: bold;
    }

    /* 2. 3D Dashboard Cards */
    .dashboard-card {
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 25px;
        transition: transform 0.3s;
        /* Deep 3D Shadow */
        box-shadow: 0 10px 20px rgba(0,0,0,0.25), 0 6px 6px rgba(0,0,0,0.22);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .dashboard-card:hover {
        transform: translateY(-5px); /* Hover Effect */
    }

    /* Gradients for Cards */
    .card-blue { background: linear-gradient(135deg, #0061ff 0%, #60efff 100%); }
    .card-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .card-red { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); }

    /* 3. Big Font Size */
    .card-value {
        font-size: 48px; /* Very Big Font */
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4); /* Text Shadow */
    }
    .card-label {
        font-size: 18px;
        font-weight: 600;
        opacity: 0.95;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* 4. Table Header Style */
    thead tr th:first-child { display:none }
    tbody th { display:none }
    
    /* बटन स्टाइल */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #FF512F 0%, #DD2476 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 15px;
        border-radius: 12px;
        font-size: 18px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. पासवर्ड सुरक्षा ---
MY_PASSWORD = "admin" 
def check_password():
    if "password_correct" not in st.session_state: st.session_state.password_correct = False
    if not st.session_state.password_correct:
        st.header("🔒 Secure Login")
        pwd = st.text_input("Password:", type="password")
        if st.button("LOGIN"):
            if pwd == MY_PASSWORD: st.session_state.password_correct = True; st.rerun()
        return False
    return True
if not check_password(): st.stop()

# --- 4. साइडबार ---
with st.sidebar:
    st.image("https://cdn.pixabay.com/photo/2020/05/18/16/17/social-media-5187243_1280.png", caption="Bullish Momentum", use_column_width=True)
    st.title("NSE MARKET PRO")
    st.markdown("---")
    start_scan = st.button("🚀 SCAN NIFTY 500", type="primary")
    st.caption("Scanning 500+ stocks (approx 3 mins)")

# --- 5. FULL STOCK LIST (500+) ---
STOCKS = [
    "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "TCS.NS", "L&T.NS", "AXISBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS", "HCLTECH.NS", "TITAN.NS", "SUNPHARMA.NS", "ULTRACEMCO.NS", "TATAMOTORS.NS", "M&M.NS", "NTPC.NS", "POWERGRID.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "ADANIENT.NS", "HINDUNILVR.NS", "GRASIM.NS", "COALINDIA.NS", "ONGC.NS", "TECHM.NS", "HINDALCO.NS", "WIPRO.NS", "DIVISLAB.NS", "CIPLA.NS", "SBILIFE.NS", "DRREDDY.NS", "BAJAJFINSV.NS", "BPCL.NS", "BRITANNIA.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "TATACONSUM.NS", "INDUSINDBK.NS", "APOLLOHOSP.NS", "UPL.NS", "LICI.NS", "ADANIPORTS.NS", "DMART.NS", "ZOMATO.NS", "HAL.NS", "BEL.NS", "JIOFIN.NS", "VBL.NS", "TRENT.NS", "SIEMENS.NS", "IOC.NS", "DLF.NS", "BANKBARODA.NS", "CHOLAFIN.NS", "GAIL.NS", "RECLTD.NS", "SHRIRAMFIN.NS", "PFC.NS",
    "ADANIPOWER.NS", "ABB.NS", "HAVELLS.NS", "AMBUJACEM.NS", "CANBK.NS", "TVSMOTOR.NS", "DABUR.NS", "VEDL.NS", "PNB.NS", "INDIGO.NS", "NAUKRI.NS", "ICICIPRULI.NS", "PIDILITIND.NS", "SBICARD.NS", "LODHA.NS", "JINDALSTEL.NS", "POLYCAB.NS", "IRCTC.NS", "CUMMINSIND.NS", "BOSCHLTD.NS", "MCDOWELL-N.NS", "PERSISTENT.NS", "MUTHOOTFIN.NS", "ASHOKLEY.NS", "MRF.NS", "PIIND.NS", "IDFCFIRSTB.NS", "ASTRAL.NS", "TATACOMM.NS", "PHOENIXLTD.NS", "MPHASIS.NS", "SUPREMEIND.NS", "TIINDIA.NS", "LALPATHLAB.NS", "AUBANK.NS", "CONCOR.NS", "ABCAPITAL.NS", "TATACHEM.NS", "FEDERALBNK.NS", "OBEROIRLTY.NS", "LTTS.NS", "ATUL.NS", "COROMANDEL.NS", "GMRINFRA.NS", "WHIRLPOOL.NS", "ALKEM.NS", "COFORGE.NS", "TDPOWERSYS.NS", "BHEL.NS", "SAIL.NS", "NATIONALUM.NS", "BANDHANBNK.NS", "GUJGASLTD.NS", "IPCALAB.NS", "LAURUSLABS.NS", "TATAELXSI.NS", "DEEPAKNTR.NS", "CROMPTON.NS", "ACC.NS", "DALBHARAT.NS", "JSL.NS", "APLAPOLLO.NS",
    "MFSL.NS", "PETRONET.NS", "ZEEL.NS", "RAMCOCEM.NS", "NAVINFLUOR.NS", "SYNGENE.NS", "TRIDENT.NS", "SOLARINDS.NS", "RVNL.NS", "IRFC.NS", "MAZDOCK.NS", "COCHINSHIP.NS", "FACT.NS", "SUZLON.NS", "IDEA.NS", "YESBANK.NS", "IDBI.NS", "UNIONBANK.NS", "IOB.NS", "UCOBANK.NS", "CENTRALBK.NS", "MAHABANK.NS", "BANKINDIA.NS", "BSE.NS", "CDSL.NS", "ANGELONE.NS", "MCX.NS", "MOTILALOFS.NS", "IEX.NS", "LUPIN.NS", "BIOCON.NS", "AUROPHARMA.NS", "GLENMARK.NS", "ZYDUSLIFE.NS", "GRANULES.NS", "ABFRL.NS", "BATAINDIA.NS", "RELAXO.NS", "PAGEIND.NS", "JUBLFOOD.NS", "DEVYANI.NS", "SAPPHIRE.NS", "KALYANKJIL.NS", "RAJESHEXPO.NS", "MANAPPURAM.NS", "M&MFIN.NS", "LICHSGFIN.NS", "POONAWALLA.NS", "SUNDARAMFIN.NS", "KPITTECH.NS", "CYIENT.NS", "BSOFT.NS", "SONACOMS.NS", "ZENSARTECH.NS", "OFSS.NS", "HONAUT.NS", "KEI.NS", "DIXON.NS", "AMBER.NS", "KAYNES.NS", "DATAPATTNS.NS", "MTARTECH.NS", "PARAS.NS", "ASTRAMICRO.NS", "CENTUM.NS",
    "HBLPOWER.NS", "TITAGARH.NS", "TEXRAIL.NS", "JWL.NS", "RKFORGE.NS", "ELECTCAST.NS", "GABRIEL.NS", "PRICOLLTD.NS", "SUBROS.NS", "LUMAXIND.NS", "MINDA CORP.NS", "UNOMINDA.NS", "ENDURANCE.NS", "CRAFTSMAN.NS", "JAMNAAUTO.NS", "GNA.NS", "ROLEXRINGS.NS", "SFL.NS", "TIMKEN.NS", "SCHAEFFLER.NS", "SKFINDIA.NS", "AIAENG.NS", "THERMAX.NS", "TRIVENI.NS", "PRAJIND.NS", "BALRAMCHIN.NS", "EIDPARRY.NS", "RENUKA.NS", "TRIVENITURB.NS", "KIRLOSENG.NS", "ELGIEQUIP.NS", "INGERRAND.NS", "KSB.NS", "POWERINDIA.NS", "HITACHI.NS", "VOLTAS.NS", "BLUESTARCO.NS", "KAJARIACER.NS", "CERA.NS", "SOMANYCERA.NS", "GREENPANEL.NS", "CENTURYPLY.NS", "STYLAMIND.NS", "PRINCEPIPE.NS", "FINPIPE.NS", "JINDALSAW.NS", "WELCORP.NS", "MAHARSEAM.NS", "RATNAMANI.NS", "APLLTD.NS", "ALEMBICLTD.NS", "ERIS.NS", "AJANTPHARM.NS", "JBITHEM.NS", "NATCOPHARM.NS", "PFIZER.NS", "SANOFI.NS", "ABBOTINDIA.NS", "GLAXO.NS", "ASTERDM.NS", "NARAYANA.NS", "KIMS.NS",
    "RAINBOW.NS", "METROPOLIS.NS", "LALPATHLAB.NS", "THYROCARE.NS", "VIJAYA.NS", "FORTIS.NS", "MAXHEALTH.NS", "NH.NS", "HCG.NS", "POLYMED.NS", "LINDEINDIA.NS", "FLUOROCHEM.NS", "AETHER.NS", "CLEAN.NS", "FINEORG.NS", "VINATIORGA.NS", "ROSSARI.NS", "NOCIL.NS", "SUMICHEM.NS", "UPL.NS", "RALLIS.NS", "CHAMBLFERT.NS", "GNFC.NS", "GSFC.NS", "DEEPAKFERT.NS", "PARADEEP.NS", "IPL.NS", "CASTROLIND.NS", "GULFOILLUB.NS", "BLS.NS", "REDINGTON.NS", "ECLERX.NS", "FSL.NS", "TANLA.NS", "ROUTE.NS", "MASTEK.NS", "INTELLECT.NS", "HAPPSTMNDS.NS", "LATENTVIEW.NS", "MAPMYINDIA.NS", "RATEGAIN.NS", "NAZARA.NS", "PBFINTECH.NS", "PAYTM.NS", "NYKAA.NS", "DELHIVERY.NS", "HONASA.NS", "RRKABEL.NS", "CAMS.NS", "KFINTECH.NS", "PRUDENT.NS", "ANANDRATHI.NS", "SHAREINDIA.NS", "GEJTL.NS", "STARCEMENT.NS", "JKCEMENT.NS", "JKLAKSHMI.NS", "BIRLACORPN.NS", "HEIDELBERG.NS", "NUVOCO.NS", "ORIENTCEM.NS", "SAGCEM.NS", "KCP.NS", "INDIACEM.NS",
    "PRISMJOHN.NS", "AARTIIND.NS", "ATUL.NS", "SUDARSCHEM.NS", "LAOPALA.NS", "BORORENEW.NS", "ASAHIINDIA.NS", "VIPIND.NS", "SAFARI.NS", "TTKPRESTIG.NS", "HAWKINS.NS", "SYMPHONY.NS", "ORIENTELEC.NS", "VGUARD.NS", "IFBIND.NS", "JOHNSONCON.NS", "AMBER.NS", "DIXON.NS", "PGHH.NS", "GILLETTE.NS", "EMAMILTD.NS", "MARICO.NS", "GODREJCP.NS", "JYOTHYLAB.NS", "VARROC.NS", "MOTHERSON.NS", "BOSCHLTD.NS", "WABAG.NS", "VAIBHAVGBL.NS", "PCJEWELLER.NS", "THANGAMAYL.NS", "SENCO.NS", "GOLDIAM.NS", "RADICO.NS", "UBL.NS", "SULA.NS", "GMMPFAUDLR.NS", "TEJASNET.NS", "ITI.NS", "HFCL.NS", "STERLITE.NS", "INDUSTOWER.NS", "BHARTIARTL.NS", "TATACOMM.NS", "GSPL.NS", "MGL.NS", "IGL.NS", "GUJGASLTD.NS", "ATGL.NS", "PETRONET.NS", "OIL.NS", "ONGC.NS", "HINDPETRO.NS", "BPCL.NS", "IOC.NS", "CHENNPETRO.NS", "MRPL.NS", "AEGISLOG.NS", "CONFIPET.NS", "DEEPINDS.NS", "HOEC.NS", "SELAN.NS", "JINDALDRILL.NS", "SWSOLAR.NS", "BOROLTD.NS",
    "GREAVESCOT.NS", "KIRLOSIND.NS", "PTC.NS", "SJVN.NS", "NHPC.NS", "TORNTPOWER.NS", "JPPOWER.NS", "RTNPOWER.NS", "RPOWER.NS", "ADANIPOWER.NS", "JSWENERGY.NS", "CESC.NS", "EXIDEIND.NS", "AMARAJABAT.NS", "HBLPOWER.NS", "HUDCO.NS", "NBCC.NS", "RITES.NS", "IRCON.NS", "RAILTEL.NS", "BEML.NS", "GPPL.NS", "SCI.NS", "DREDGECORP.NS", "RCF.NS", "NFL.NS"
]

@st.cache_data(ttl=900)
def get_stock_data(symbol):
    try:
        # Fix: .NS logic handled here
        if not symbol.endswith(".NS"): symbol = f"{symbol}.NS"
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="3mo", interval="1d")
        if len(df) < 30: return None
        
        def get_val(s): return s.iloc[0] if isinstance(s, pd.Series) else s
        
        close = get_val(df['Close'].iloc[-1])
        past = df.iloc[:-1]
        entry = get_val(past['High'].tail(20).max())
        sl = get_val(past['Low'].tail(20).min())
        
        avg_vol = get_val(past['Volume'].tail(20).mean())
        cur_vol = get_val(df['Volume'].iloc[-1])
        rvol = cur_vol / avg_vol if avg_vol > 0 else 0
        
        # Fundamentals
        info = ticker.info
        mcap = info.get("marketCap", 0) / 10000000 
        pe = info.get("trailingPE", 0)
        sector = info.get("sector", "N/A")
        
        return {
            "symbol": symbol.replace(".NS", ""),
            "close": close, "entry": entry, "sl": sl, "rvol": rvol,
            "mcap": mcap, "pe": pe, "sector": sector
        }
    except: return None

# --- 6. मुख्य ऐप ---
st.title("🦅 Darvas Pro 3D")

# --- सेक्शन 1: UNIVERSAL SEARCH (FIXED) ---
st.markdown("### 🔍 3D Search Stock")
st.caption("Search ANY stock (e.g. YESBANK, SUZLON, TATASTEEL)")

# 3D सर्च बार इनपुट
search_query = st.text_input("", placeholder="Enter Stock Symbol...", label_visibility="collapsed").upper().strip()

if search_query:
    # Logic: अगर .NS नहीं है तो लगाओ
    full_symbol = search_query if search_query.endswith(".NS") else f"{search_query}.NS"
    
    with st.spinner(f"Searching {full_symbol}..."):
        data = get_stock_data(full_symbol)
        
        if data:
            status = "HOLD"
            color_code = "#b38f00" # Gold
            
            if data['close'] > data['entry']:
                if data['rvol'] > 1.5: 
                    status = "STRONG BUY 🚀"
                    color_code = "#28a745" # Green
                else: 
                    status = "BUY / HOLD 🟢"
                    color_code = "#218838"
            elif data['close'] < data['sl']:
                status = "EXIT 🔴"
                color_code = "#dc3545" # Red
            
            # Individual 3D Card for Search
            st.markdown(f"""
            <div style="background-color: #fff; padding: 25px; border-radius: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); border-left: 10px solid {color_code}; text-align: center; color: #333;">
                <h1 style="margin:0; font-size: 40px; color: #333;">{data['symbol']}</h1>
                <h2 style="color: {color_code}; font-weight: 800; font-size: 30px;">{status}</h2>
                <hr>
                <div style="display: flex; justify-content: space-around; font-size: 18px; font-weight: bold;">
                    <div>Current Price<br><span style="color:#007bff">₹{data['close']:.2f}</span></div>
                    <div>Entry Level<br><span style="color:#28a745">₹{data['entry']:.2f}</span></div>
                    <div>Stop Loss<br><span style="color:#dc3545">₹{data['sl']:.2f}</span></div>
                    <div>Volume<br><span style="color:#6c757d">{data['rvol']:.1f}x</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Chart Link
            st.markdown(f"<br><center><a href='https://in.tradingview.com/chart/?symbol=NSE:{data['symbol']}' target='_blank' style='background-color:#007bff; color:white; padding:10px 20px; text-decoration:none; border-radius:10px; font-weight:bold;'>📈 Open Live Chart</a></center><hr>", unsafe_allow_html=True)
            
        else:
            st.error(f"❌ Stock '{full_symbol}' not found. Please check spelling.")

# --- सेक्शन 2: ऑटोमैटिक स्कैनर ---
st.markdown("### 📊 Nifty 500 Dashboard")

if start_scan:
    progress_bar = st.progress(0)
    status_text = st.empty()
    valid_data = []
    
    for i, stock in enumerate(STOCKS):
        status_text.caption(f"Analysing {i+1}/{len(STOCKS)}")
        data = get_stock_data(stock) 
        progress_bar.progress((i + 1) / len(STOCKS))
        
        if data and data['close'] > data['entry']:
            risk = data['entry'] - data['sl']
            target = data['entry'] + (risk * 2)
            pct_change = ((data['close'] - data['entry']) / data['entry']) * 100
            
            status = "HOLD"
            if data['close'] < data['sl']: status = "EXIT NOW"
            elif data['rvol'] > 1.5: status = "STRONG BUY"
            
            valid_data.append({
                "Stock": data['symbol'],
                "Price": data['close'],
                "Entry": data['entry'],
                "Target": data['target'] if 'target' in data else target, 
                "Stop Loss": data['sl'],
                "Gain %": pct_change,
                "Status": status
            })

    progress_bar.empty()
    status_text.empty()
    
    if valid_data:
        df = pd.DataFrame(valid_data)
        
        # 3D CARDS
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"<div class='dashboard-card card-blue'><p class='card-value'>{len(df)}</p><p class='card-label'>Stocks Found</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='dashboard-card card-green'><p class='card-value'>{len(df[df['Status']=='STRONG BUY'])}</p><p class='card-label'>Strong Buys</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='dashboard-card card-red'><p class='card-value'>{len(df[df['Status']=='EXIT NOW'])}</p><p class='card-label'>Exit Alerts</p></div>", unsafe_allow_html=True)
        
        # RULES BOX
        st.markdown("""
        <div style="background-color: #e3f2fd; border-left: 5px solid #2196F3; padding: 15px; border-radius: 10px; margin: 20px 0;">
            <b>💡 TRADING RULES:</b> Only buy if <b>Status is STRONG BUY</b> (Volume > 1.5x) and Gain is < 3%.
        </div>
        """, unsafe_allow_html=True)
        
        # STYLISH TABLE (No content change)
        def color_row(val):
            if 'STRONG' in val: return 'background-color: #d1e7dd; color: #0f5132; font-weight: bold;'
            if 'EXIT' in val: return 'background-color: #f8d7da; color: #842029; font-weight: bold;'
            return ''
            
        st.dataframe(
            df.style.map(color_row, subset=['Status']).format({
                "Price": "{:.2f}", 
                "Entry": "{:.2f}", 
                "Target": "{:.2f}", 
                "Gain %": "{:.2f}%"
            }),
            use_container_width=True, 
            height=600, 
            hide_index=True
        )
    else:
        st.warning("No stocks matched criteria today.")
else:
    st.info("Click 'SCAN NIFTY 500' to start.")
