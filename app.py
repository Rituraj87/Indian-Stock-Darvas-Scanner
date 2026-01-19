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

# --- 2. ADVANCED CSS (3D Cards, Big Fonts, Styling) ---
st.markdown("""
<style>
    /* सर्च बार स्टाइल */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #2980b9;
        padding: 12px;
        font-size: 18px; /* बड़ा फोंट */
    }

    /* --- 3D कार्ड स्टाइल (Shadows + Lift Effect) --- */
    .dashboard-card {
        box-shadow: 0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23); /* 3D Shadow */
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 25px;
        transform: translateY(-5px); /* थोड़ा उठा हुआ */
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
    }
    .dashboard-card:hover {
        box-shadow: 0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22);
        transform: translateY(-10px); /* होवर करने पर और ऊपर उठेगा */
    }

    /* कार्ड कलर्स */
    .card-blue { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); }
    .card-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .card-red { background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%); }

    /* कार्ड फोंट्स (बड़ा साइज़) */
    .card-value {
        font-size: 42px !important; /* बहुत बड़ा नंबर */
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .card-label {
        font-size: 18px !important; /* बड़ा लेबल */
        font-weight: 600;
        opacity: 0.95;
        margin-top: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* एडवाइस नोटिफिकेशन बॉक्स (LONG VERSION) */
    .advice-box {
        background-color: #f0f8ff;
        border-left: 6px solid #2196F3;
        padding: 15px;
        border-radius: 5px;
        color: #0c5460;
        margin-top: 10px;
        margin-bottom: 20px;
        font-size: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* फंडामेंटल बॉक्स */
    .fund-box {
        background-color: #ffffff; border-left: 5px solid #ff9800;
        padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-top: 15px; color: #333; font-size: 16px;
    }

    /* बटन स्टाइल */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #FF512F 0%, #DD2476 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 12px;
        border-radius: 8px;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. पासवर्ड सुरक्षा ---
MY_PASSWORD = "admin" 
def check_password():
    if "password_correct" not in st.session_state: st.session_state.password_correct = False
    if not st.session_state.password_correct:
        st.header("🔒 Login")
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
    
    # स्कैन बटन
    start_scan = st.button("🚀 SCAN FULL MARKET (500)", type="primary")
    st.caption("Scanning 500 stocks may take 3-5 mins.")

# --- 5. NIFTY 500 FULL LIST ---
STOCKS = [
    "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "ITC.NS", "TCS.NS", "L&T.NS", "AXISBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS", "HCLTECH.NS", "TITAN.NS", "SUNPHARMA.NS", "ULTRACEMCO.NS", "TATAMOTORS.NS", "M&M.NS", "NTPC.NS", "POWERGRID.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "ADANIENT.NS", "HINDUNILVR.NS", "GRASIM.NS", "COALINDIA.NS", "ONGC.NS", "TECHM.NS", "HINDALCO.NS", "WIPRO.NS", "DIVISLAB.NS", "CIPLA.NS", "SBILIFE.NS", "DRREDDY.NS", "BAJAJFINSV.NS", "BPCL.NS", "BRITANNIA.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "TATACONSUM.NS", "INDUSINDBK.NS", "APOLLOHOSP.NS", "UPL.NS", "LICI.NS", "ADANIPORTS.NS", "DMART.NS", "ZOMATO.NS", "HAL.NS", "BEL.NS", "JIOFIN.NS", "VBL.NS", "TRENT.NS", "SIEMENS.NS", "IOC.NS", "DLF.NS", "BANKBARODA.NS", "CHOLAFIN.NS", "GAIL.NS", "RECLTD.NS", "SHRIRAMFIN.NS", "PFC.NS",
    "ADANIPOWER.NS", "ABB.NS", "HAVELLS.NS", "AMBUJACEM.NS", "CANBK.NS", "TVSMOTOR.NS", "DABUR.NS", "VEDL.NS", "PNB.NS", "INDIGO.NS", "NAUKRI.NS", "ICICIPRULI.NS", "PIDILITIND.NS", "SBICARD.NS", "LODHA.NS", "JINDALSTEL.NS", "POLYCAB.NS", "IRCTC.NS", "CUMMINSIND.NS", "BOSCHLTD.NS", "MCDOWELL-N.NS", "PERSISTENT.NS", "MUTHOOTFIN.NS", "ASHOKLEY.NS", "MRF.NS", "PIIND.NS", "IDFCFIRSTB.NS", "ASTRAL.NS", "TATACOMM.NS", "PHOENIXLTD.NS", "MPHASIS.NS", "SUPREMEIND.NS", "TIINDIA.NS", "LALPATHLAB.NS", "AUBANK.NS", "CONCOR.NS", "ABCAPITAL.NS", "TATACHEM.NS", "FEDERALBNK.NS", "OBEROIRLTY.NS", "LTTS.NS", "ATUL.NS", "COROMANDEL.NS", "GMRINFRA.NS", "WHIRLPOOL.NS", "ALKEM.NS", "COFORGE.NS", "TDPOWERSYS.NS", "BHEL.NS", "SAIL.NS", "NATIONALUM.NS", "BANDHANBNK.NS", "GUJGASLTD.NS", "IPCALAB.NS", "LAURUSLABS.NS", "TATAELXSI.NS", "DEEPAKNTR.NS", "CROMPTON.NS", "ACC.NS", "DALBHARAT.NS", "JSL.NS", "APLAPOLLO.NS",
    "MFSL.NS", "PETRONET.NS", "ZEEL.NS", "RAMCOCEM.NS", "NAVINFLUOR.NS", "SYNGENE.NS", "TRIDENT.NS", "SOLARINDS.NS", "RVNL.NS", "IRFC.NS", "MAZDOCK.NS", "COCHINSHIP.NS", "FACT.NS", "SUZLON.NS", "IDEA.NS", "YESBANK.NS", "IDBI.NS", "UNIONBANK.NS", "IOB.NS", "UCOBANK.NS", "CENTRALBK.NS", "MAHABANK.NS", "BANKINDIA.NS", "BSE.NS", "CDSL.NS", "ANGELONE.NS", "MCX.NS", "MOTILALOFS.NS", "IEX.NS", "LUPIN.NS", "BIOCON.NS", "AUROPHARMA.NS", "GLENMARK.NS", "ZYDUSLIFE.NS", "GRANULES.NS", "ABFRL.NS", "BATAINDIA.NS", "RELAXO.NS", "PAGEIND.NS", "JUBLFOOD.NS", "DEVYANI.NS", "SAPPHIRE.NS", "KALYANKJIL.NS", "RAJESHEXPO.NS", "MANAPPURAM.NS", "M&MFIN.NS", "LICHSGFIN.NS", "POONAWALLA.NS", "SUNDARAMFIN.NS", "KPITTECH.NS", "CYIENT.NS", "BSOFT.NS", "SONACOMS.NS", "ZENSARTECH.NS", "OFSS.NS", "HONAUT.NS", "KEI.NS", "DIXON.NS", "AMBER.NS", "KAYNES.NS", "DATAPATTNS.NS", "MTARTECH.NS", "PARAS.NS", "ASTRAMICRO.NS", "CENTUM.NS",
    "HBLPOWER.NS", "TITAGARH.NS", "TEXRAIL.NS", "JWL.NS", "RKFORGE.NS", "ELECTCAST.NS", "GABRIEL.NS", "PRICOLLTD.NS", "SUBROS.NS", "LUMAXIND.NS", "MINDA CORP.NS", "UNOMINDA.NS", "ENDURANCE.NS", "CRAFTSMAN.NS", "JAMNAAUTO.NS", "GNA.NS", "ROLEXRINGS.NS", "SFL.NS", "TIMKEN.NS", "SCHAEFFLER.NS", "SKFINDIA.NS", "AIAENG.NS", "THERMAX.NS", "TRIVENI.NS", "PRAJIND.NS", "BALRAMCHIN.NS", "EIDPARRY.NS", "RENUKA.NS", "TRIVENITURB.NS", "KIRLOSENG.NS", "ELGIEQUIP.NS", "INGERRAND.NS", "KSB.NS", "POWERINDIA.NS", "HITACHI.NS", "VOLTAS.NS", "BLUESTARCO.NS", "KAJARIACER.NS", "CERA.NS", "SOMANYCERA.NS", "GREENPANEL.NS", "CENTURYPLY.NS", "STYLAMIND.NS", "PRINCEPIPE.NS", "FINPIPE.NS", "JINDALSAW.NS", "WELCORP.NS", "MAHARSEAM.NS", "RATNAMANI.NS", "APLLTD.NS", "ALEMBICLTD.NS", "ERIS.NS", "AJANTPHARM.NS", "JBITHEM.NS", "NATCOPHARM.NS", "PFIZER.NS", "SANOFI.NS", "ABBOTINDIA.NS", "GLAXO.NS", "ASTERDM.NS", "NARAYANA.NS", "KIMS.NS",
    "RAINBOW.NS", "METROPOLIS.NS", "LALPATHLAB.NS", "THYROCARE.NS", "VIJAYA.NS", "FORTIS.NS", "MAXHEALTH.NS", "NH.NS", "HCG.NS", "POLYMED.NS", "LINDEINDIA.NS", "FLUOROCHEM.NS", "AETHER.NS", "CLEAN.NS", "FINEORG.NS", "VINATIORGA.NS", "ROSSARI.NS", "NOCIL.NS", "SUMICHEM.NS", "UPL.NS", "RALLIS.NS", "CHAMBLFERT.NS", "GNFC.NS", "GSFC.NS", "DEEPAKFERT.NS", "PARADEEP.NS", "IPL.NS", "CASTROLIND.NS", "GULFOILLUB.NS", "BLS.NS", "REDINGTON.NS", "ECLERX.NS", "FSL.NS", "TANLA.NS", "ROUTE.NS", "MASTEK.NS", "INTELLECT.NS", "HAPPSTMNDS.NS", "LATENTVIEW.NS", "MAPMYINDIA.NS", "RATEGAIN.NS", "NAZARA.NS", "PBFINTECH.NS", "PAYTM.NS", "NYKAA.NS", "DELHIVERY.NS", "HONASA.NS", "RRKABEL.NS", "CAMS.NS", "KFINTECH.NS", "PRUDENT.NS", "ANANDRATHI.NS", "SHAREINDIA.NS", "GEJTL.NS", "STARCEMENT.NS", "JKCEMENT.NS", "JKLAKSHMI.NS", "BIRLACORPN.NS", "HEIDELBERG.NS", "NUVOCO.NS", "ORIENTCEM.NS", "SAGCEM.NS", "KCP.NS", "INDIACEM.NS",
    "PRISMJOHN.NS", "AARTIIND.NS", "ATUL.NS", "SUDARSCHEM.NS", "LAOPALA.NS", "BORORENEW.NS", "ASAHIINDIA.NS", "VIPIND.NS", "SAFARI.NS", "TTKPRESTIG.NS", "HAWKINS.NS", "SYMPHONY.NS", "ORIENTELEC.NS", "VGUARD.NS", "IFBIND.NS", "JOHNSONCON.NS", "AMBER.NS", "DIXON.NS", "PGHH.NS", "GILLETTE.NS", "EMAMILTD.NS", "MARICO.NS", "GODREJCP.NS", "JYOTHYLAB.NS", "VARROC.NS", "MOTHERSON.NS", "BOSCHLTD.NS", "WABAG.NS", "VAIBHAVGBL.NS", "PCJEWELLER.NS", "THANGAMAYL.NS", "SENCO.NS", "GOLDIAM.NS", "RADICO.NS", "UBL.NS", "SULA.NS", "GMMPFAUDLR.NS", "TEJASNET.NS", "ITI.NS", "HFCL.NS", "STERLITE.NS", "INDUSTOWER.NS", "BHARTIARTL.NS", "TATACOMM.NS", "GSPL.NS", "MGL.NS", "IGL.NS", "GUJGASLTD.NS", "ATGL.NS", "PETRONET.NS", "OIL.NS", "ONGC.NS", "HINDPETRO.NS", "BPCL.NS", "IOC.NS", "CHENNPETRO.NS", "MRPL.NS", "AEGISLOG.NS", "CONFIPET.NS", "DEEPINDS.NS", "HOEC.NS", "SELAN.NS", "JINDALDRILL.NS", "SWSOLAR.NS", "BOROLTD.NS",
    "GREAVESCOT.NS", "KIRLOSIND.NS", "PTC.NS", "SJVN.NS", "NHPC.NS", "TORNTPOWER.NS", "JPPOWER.NS", "RTNPOWER.NS", "RPOWER.NS", "ADANIPOWER.NS", "JSWENERGY.NS", "CESC.NS", "EXIDEIND.NS", "AMARAJABAT.NS", "HBLPOWER.NS", "HUDCO.NS", "NBCC.NS", "RITES.NS", "IRCON.NS", "RAILTEL.NS", "BEML.NS", "GPPL.NS", "SCI.NS", "DREDGECORP.NS", "RCF.NS", "NFL.NS", "FACT.NS", "CHAMBLFERT.NS", "GNFC.NS", "DEEPAKFERT.NS", "COROMANDEL.NS"
]

@st.cache_data(ttl=900)
def get_stock_data(symbol):
    try:
        # Fix: Remove spaces and ensure uppercase
        symbol = symbol.upper().strip()
        if not symbol.endswith(".NS"): symbol = f"{symbol}.NS"
        
        ticker = yf.Ticker(symbol)
        
        # Fast History Fetch
        df = ticker.history(period="3mo", interval="1d")
        if len(df) < 30: return None
        
        # Technicals
        def get_val(s): return s.iloc[0] if isinstance(s, pd.Series) else s
        close = get_val(df['Close'].iloc[-1])
        past = df.iloc[:-1]
        entry = get_val(past['High'].tail(20).max())
        sl = get_val(past['Low'].tail(20).min())
        avg_vol = get_val(past['Volume'].tail(20).mean())
        cur_vol = get_val(df['Volume'].iloc[-1])
        rvol = cur_vol / avg_vol if avg_vol > 0 else 0
        
        # Fundamentals (Safe Fetch)
        try:
            info = ticker.info
            mcap = info.get("marketCap", 0) / 10000000 # Crores
            pe = info.get("trailingPE", 0)
            sector = info.get("sector", "N/A")
            high52 = info.get("fiftyTwoWeekHigh", 0)
        except:
            mcap, pe, sector, high52 = 0, 0, "N/A", 0

        return {
            "symbol": symbol.replace(".NS", ""),
            "close": close, "entry": entry, "sl": sl, "rvol": rvol,
            "mcap": mcap, "pe": pe, "sector": sector, "high52": high52
        }
    except: return None

# --- 6. MAIN APP ---
st.title("🦅 Darvas Pro Market Scanner")

# --- SECTION 1: SEARCH BAR (Fixed & Fundamental) ---
st.markdown("### 🔍 Universal Search (With Fundamentals)")
st.caption("Type any stock name (e.g. ZOMATO, TATASTEEL, SUZLON)")
search_symbol = st.text_input("Enter Stock Symbol:", "")

if search_symbol:
    with st.spinner(f"Fetching details for {search_symbol}..."):
        data = get_stock_data(search_symbol)
        
        if data:
            # Logic
            status = "HOLD"
            color = "#856404"
            if data['close'] > data['entry']:
                if data['rvol'] > 1.5: status = "STRONG BUY 🚀"; color = "#155724"
                else: status = "BUY / HOLD 🟢"; color = "#006400"
            elif data['close'] < data['sl']:
                status = "EXIT 🔴"; color = "#721c24"
            
            # 3D Result Card
            st.markdown(f"""
            <div style="background-color: white; border: 3px solid {color}; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                <h1 style="color: {color}; margin: 0;">{data['symbol']}</h1>
                <h2 style="color: {color};">{status}</h2>
                <hr>
                <div style="display: flex; justify-content: space-around; font-size: 18px; color: #333;">
                    <div><b>Price:</b><br>₹{data['close']:.2f}</div>
                    <div><b>Entry:</b><br>₹{data['entry']:.2f}</div>
                    <div><b>Stop Loss:</b><br>₹{data['sl']:.2f}</div>
                    <div><b>Vol Surge:</b><br>{data['rvol']:.1f}x</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Fundamental Analysis Box
            st.markdown(f"""
            <div class="fund-box">
                <h4>📊 Fundamental Snapshot</h4>
                <p>
                <b>🏢 Sector:</b> {data['sector']} &nbsp;|&nbsp; 
                <b>💰 Market Cap:</b> ₹{int(data['mcap']):,} Cr &nbsp;|&nbsp; 
                <b>📉 PE Ratio:</b> {data['pe']:.2f}<br>
                <b>🚀 52-Week High:</b> ₹{data['high52']:.2f}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"👉 [**View Chart on TradingView**](https://in.tradingview.com/chart/?symbol=NSE:{data['symbol']})")

        else:
            st.error("Stock not found. Try checking the spelling (e.g. use TATAMOTORS instead of TATA MOTORS).")

st.markdown("---")

# --- SECTION 2: 500 STOCK SCANNER ---
st.markdown("### 📊 Full Market Scanner (Nifty 500)")

if start_scan:
    progress_bar = st.progress(0)
    status_text = st.empty()
    valid_data = []
    
    for i, stock in enumerate(STOCKS):
        status_text.caption(f"Analyzing {i+1}/{len(STOCKS)}: {stock}")
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
                "Vol Surge": data['rvol'], # --- कॉलम का नाम बदल दिया (User Request) ---
                "Status": status
            })

    progress_bar.empty()
    status_text.empty()
    
    if valid_data:
        df = pd.DataFrame(valid_data)
        
        # 3D Cards (Big Font)
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"<div class='dashboard-card card-blue'><p class='card-value'>{len(df)}</p><p class='card-label'>Stocks Scanned</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='dashboard-card card-green'><p class='card-value'>{len(df[df['Status']=='STRONG BUY'])}</p><p class='card-label'>Strong Buys</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='dashboard-card card-red'><p class='card-value'>{len(df[df['Status']=='EXIT NOW'])}</p><p class='card-label'>Exits</p></div>", unsafe_allow_html=True)
        
        # --- Notification Restored (Long Version) ---
        st.markdown("""
        <div class="advice-box">
            <b>💡 TRADING RULES & NOTIFICATION:</b><br>
            ✅ <b>STRONG BUY:</b> Only enter if <b>Volume is > 1.5x</b> and Price Gain is between <b>0.5% to 3%</b> from Entry Price.<br>
            ⚠️ <b>AVOID/RISKY:</b> If stock has already moved <b>> 5%</b> from Entry (Chase mat karein).<br>
            🛑 <b>EXIT:</b> If price closes below the Stop Loss level immediately.
        </div>
        """, unsafe_allow_html=True)
        
        # Table
        def color_row(val):
            if 'STRONG' in val: return 'background-color: #d4edda; color: green; font-weight: bold;'
            if 'EXIT' in val: return 'background-color: #f8d7da; color: red; font-weight: bold;'
            return ''
            
        st.dataframe(
            df.style.map(color_row, subset=['Status']).format({
                "Price": "{:.2f}", 
                "Entry": "{:.2f}", 
                "Target": "{:.2f}", 
                "Gain %": "{:.2f}%",
                "Vol Surge": "{:.1f}x" # --- कॉलम फॉर्मेटिंग ---
            }),
            use_container_width=True, 
            height=600, 
            hide_index=True
        )
    else:
        st.warning("No stocks matched the breakout criteria today.")
else:
    st.info("Click 'SCAN FULL MARKET' in sidebar to start.")
