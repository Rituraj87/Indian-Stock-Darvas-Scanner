import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. पेज कॉन्फ़िगरेशन ---
st.set_page_config(
    page_title="Darvas AI Prime", 
    layout="wide", 
    page_icon="🦅",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED CSS (Same as requested) ---
st.markdown("""
<style>
    /* सर्च बार */
    .stTextInput > div > div > input {
        border-radius: 12px; border: 2px solid #2980b9; padding: 12px; font-size: 18px;
    }
    
    /* 3D Glassmorphism Cards (Main Result) */
    .dashboard-card {
        background: rgba(255, 255, 255, 0.95);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 20px;
        text-align: center;
        transition: 0.4s;
        margin-bottom: 20px;
    }
    .dashboard-card:hover { transform: translateY(-8px); box-shadow: 0 15px 30px rgba(0,0,0,0.3); }
    
    .card-value { font-size: 40px !important; font-weight: 800; margin: 0; background: -webkit-linear-gradient(#1e3c72, #2a5298); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .card-label { font-size: 16px !important; font-weight: 600; color: #555; text-transform: uppercase; }

    /* AI Score Badge */
    .ai-badge {
        background-color: #000; color: #00ff00; padding: 5px 15px; border-radius: 20px;
        font-weight: bold; font-family: 'Courier New', monospace; border: 1px solid #00ff00;
        box-shadow: 0 0 10px #00ff00;
    }

    /* --- THE MISSING CARDS (Restored) --- */
    /* Green AI Sentiment Card */
    .ai-box {
        background-color: #f1f8e9; 
        border-left: 6px solid #33691e;
        padding: 20px; 
        border-radius: 10px; 
        margin-top: 15px; 
        color: #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Blue Auto Levels Card */
    .levels-box {
        background-color: #e3f2fd; 
        border-left: 6px solid #1565c0;
        padding: 20px; 
        border-radius: 10px; 
        margin-top: 15px; 
        color: #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Market Mood Bar */
    .mood-box { padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; color: white; margin-bottom: 10px; }
    
    /* Advice Notification */
    .advice-box { background-color: #f0f8ff; border-left: 6px solid #2196F3; padding: 15px; border-radius: 5px; color: #0c5460; margin: 10px 0 20px 0; }

    /* Button */
    div.stButton > button { width: 100%; background: linear-gradient(90deg, #1cb5e0 0%, #000851 100%); color: white; font-weight: bold; padding: 14px; border-radius: 10px; border: none; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

# --- 3. पासवर्ड ---
MY_PASSWORD = "admin" 
def check_password():
    if "password_correct" not in st.session_state: st.session_state.password_correct = False
    if not st.session_state.password_correct:
        st.markdown("<h1 style='text-align:center;'>🦅 Darvas AI Prime</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Enter Access Key:", type="password")
        if st.button("AUTHENTICATE"):
            if pwd == MY_PASSWORD: st.session_state.password_correct = True; st.rerun()
        return False
    return True
if not check_password(): st.stop()

# --- 4. साइडबार & NIFTY TREND ---
def get_nifty_trend():
    try:
        df = yf.download("^NSEI", period="6mo", interval="1d", progress=False)
        close = df['Close'].iloc[-1]
        ema50 = df['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
        if isinstance(close, pd.Series): close = close.iloc[0]
        if isinstance(ema50, pd.Series): ema50 = ema50.iloc[0]
        
        if close > ema50: return "BULLISH 🐂", "#2ecc71" 
        else: return "BEARISH 🐻", "#e74c3c" 
    except: return "NEUTRAL 😐", "#95a5a6"

with st.sidebar:
    st.image("https://cdn.pixabay.com/photo/2020/05/18/16/17/social-media-5187243_1280.png", caption="AI Powered Analytics", use_column_width=True)
    st.title("DARVAS AI PRIME")
    mood, color = get_nifty_trend()
    st.markdown(f"<div class='mood-box' style='background-color: {color};'>MARKET MOOD: {mood}</div>", unsafe_allow_html=True)
    st.markdown("---")
    start_scan = st.button("🚀 RUN AI SCANNER", type="primary")
    st.caption("Advanced Calculation: ~4-6 mins")

# --- 5. ADVANCED DATA ENGINE ---
@st.cache_data(ttl=900)
def get_stock_data(symbol):
    try:
        symbol = symbol.upper().strip()
        if not symbol.endswith(".NS"): symbol = f"{symbol}.NS"
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="6mo", interval="1d") 
        if len(df) < 50: return None
        
        def get_val(s): return s.iloc[0] if isinstance(s, pd.Series) else s
        
        # Prices
        close = get_val(df['Close'].iloc[-1])
        high = get_val(df['High'].iloc[-1])
        low = get_val(df['Low'].iloc[-1])
        
        # Darvas
        past = df.iloc[:-1]
        entry = get_val(past['High'].tail(20).max())
        sl = get_val(past['Low'].tail(20).min())
        
        # Volume
        avg_vol = get_val(past['Volume'].tail(20).mean())
        cur_vol = get_val(df['Volume'].iloc[-1])
        rvol = cur_vol / avg_vol if avg_vol > 0 else 0
        
        # EMA 50
        ema50 = get_val(df['Close'].ewm(span=50, adjust=False).mean().iloc[-1])
        trend = "UP" if close > ema50 else "DOWN"
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = get_val(100 - (100 / (1 + rs)).iloc[-1])
        
        # AI Score
        ai_score = 0
        reasons = []
        if close > entry: ai_score += 40; reasons.append("Box Breakout")
        if rvol > 1.5: ai_score += 20; reasons.append("High Volume")
        if close > ema50: ai_score += 20; reasons.append("Uptrend")
        if 50 < rsi < 75: ai_score += 20; reasons.append("Momentum")
            
        risk = entry - sl
        target = entry + (risk * 2)
        
        # Pivot Points (Auto Support/Resistance)
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        s1 = (2 * pivot) - high
        
        # Fundamentals
        try:
            info = ticker.info
            mcap = info.get("marketCap", 0) / 10000000
            pe = info.get("trailingPE", 0)
            sector = info.get("sector", "N/A")
        except: mcap, pe, sector = 0, 0, "N/A"

        return {
            "symbol": symbol.replace(".NS", ""),
            "close": close, "entry": entry, "sl": sl, "target": target,
            "rvol": rvol, "rsi": rsi, "trend": trend, "ema": ema50,
            "ai_score": ai_score, "reasons": ", ".join(reasons),
            "mcap": mcap, "pe": pe, "sector": sector,
            "s1": s1, "r1": r1
        }
    except: return None

# --- 6. MAIN DASHBOARD ---
st.title("🦅 Darvas AI Prime Terminal")

# --- SECTION 1: AI SUPER SEARCH ---
st.markdown("### 🧠 AI Stock Analysis (Universal Search)")
search_symbol = st.text_input("Enter Stock (e.g. ZOMATO, TATASTEEL):", "")

if search_symbol:
    with st.spinner(f"AI Analyzing {search_symbol}..."):
        data = get_stock_data(search_symbol)
        
        if data:
            # Status Logic
            score = data['ai_score']
            if score >= 80: 
                status = "💎 STRONG BUY"; color = "#00c853"; sentiment = "BULLISH 🐂"
            elif score >= 60: 
                status = "🟢 BUY / HOLD"; color = "#006400"; sentiment = "MILDLY BULLISH 🐃"
            elif data['close'] < data['sl']:
                status = "🔴 EXIT / AVOID"; color = "#d50000"; sentiment = "BEARISH 🐻"
            else:
                status = "🟡 WAIT / WATCH"; color = "#ffab00"; sentiment = "NEUTRAL 😐"

            # 1. MAIN 3D CARD
            st.markdown(f"""
            <div style="background-color: white; border: 3px solid {color}; padding: 25px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.15);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h1 style="color: #333; margin: 0;">{data['symbol']}</h1>
                    <span class="ai-badge">AI SCORE: {score}/100</span>
                </div>
                <h2 style="color: {color}; margin-top: 10px;">{status}</h2>
                <hr>
                <div style="display: flex; justify-content: space-around; font-size: 18px; color: #333; font-weight: bold;">
                    <div>Price<br>₹{data['close']:.2f}</div>
                    <div>Entry<br>₹{data['entry']:.2f}</div>
                    <div>Target<br>₹{data['target']:.2f}</div>
                    <div>Stop Loss<br>₹{data['sl']:.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- 2. THE REQUESTED EXTRA CARDS (ADDED BACK) ---
            col_a, col_b = st.columns(2)
            
            with col_a:
                # Green AI Card
                st.markdown(f"""
                <div class="ai-box">
                    <h3 style="margin-top:0;">🤖 AI Technical Sentiment</h3>
                    <h2 style="margin:5px 0;">{sentiment}</h2>
                    <p><b>Vol Surge:</b> {data['rvol']:.1f}x (Normal is 1.0x)</p>
                    <p><b>Sector:</b> {data['sector']}</p>
                    <small><i>AI Logic: {data['reasons']}</i></small>
                </div>
                """, unsafe_allow_html=True)
                
            with col_b:
                # Blue Levels Card
                st.markdown(f"""
                <div class="levels-box">
                    <h3 style="margin-top:0;">📐 Auto Support & Resistance</h3>
                    <h2 style="margin:5px 0;">R1 (Res): ₹{data['r1']:.2f}</h2>
                    <h3 style="margin:5px 0;">S1 (Sup): ₹{data['s1']:.2f}</h3>
                    <p style="font-size: 14px;">*Based on Pivot Points Calculation</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"👉 [**View Live Chart**](https://in.tradingview.com/chart/?symbol=NSE:{data['symbol']})")
        else:
            st.error("Stock not found.")

st.markdown("---")

# --- SECTION 2: 500 STOCK SCANNER ---
STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "INFY.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS",
    "LT.NS", "BAJFINANCE.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS", "ADANIENT.NS", "KOTAKBANK.NS", "TITAN.NS", "ONGC.NS", "TATAMOTORS.NS",
    "NTPC.NS", "AXISBANK.NS", "ADANIPORTS.NS", "POWERGRID.NS", "ULTRACEMCO.NS", "M&M.NS", "WIPRO.NS", "BAJAJFINSV.NS", "COALINDIA.NS", "JSWSTEEL.NS",
    "TATASTEEL.NS", "LTIM.NS", "HINDALCO.NS", "SBILIFE.NS", "GRASIM.NS", "TECHM.NS", "ADANIGREEN.NS", "BRITANNIA.NS", "HAL.NS", "BAJAJ-AUTO.NS",
    "ADANIPOWER.NS", "SIEMENS.NS", "DLF.NS", "INDUSINDBK.NS", "DIVISLAB.NS", "DRREDDY.NS", "EICHERMOT.NS", "JIOFIN.NS", "BEL.NS", "VARROC.NS",
    "VBL.NS", "TRENT.NS", "ZOMATO.NS", "PIDILITIND.NS", "HAVELLS.NS", "NESTLEIND.NS", "BPCL.NS", "GAIL.NS", "SHRIRAMFIN.NS", "GODREJCP.NS",
    "IOC.NS", "TATACONSUM.NS", "CIPLA.NS", "DABUR.NS", "ABB.NS", "CHOLAFIN.NS", "AMBUJACEM.NS", "PNB.NS", "INDIGO.NS", "VEDL.NS",
    "BANKBARODA.NS", "TVSMOTOR.NS", "BOSCHLTD.NS", "MOTHERSON.NS", "HEROMOTOCO.NS", "RECLTD.NS", "MANKIND.NS", "APOLLOHOSP.NS", "TORNTPOWER.NS", "ICICIPRULI.NS",
    "LODHA.NS", "CANBK.NS", "PFC.NS", "JINDALSTEL.NS", "POLYCAB.NS", "IRCTC.NS", "CUMMINSIND.NS", "COLPAL.NS", "MCDOWELL-N.NS", "PERSISTENT.NS",
    "MUTHOOTFIN.NS", "ASHOKLEY.NS", "MRF.NS", "PIIND.NS", "IDFCFIRSTB.NS", "ASTRAL.NS", "TATACOMM.NS", "PHOENIXLTD.NS", "MPHASIS.NS", "SUPREMEIND.NS",
    "TIINDIA.NS", "LALPATHLAB.NS", "AUBANK.NS", "CONCOR.NS", "ABCAPITAL.NS", "TATACHEM.NS", "FEDERALBNK.NS", "OBEROIRLTY.NS", "LTTS.NS", "ATUL.NS",
    "COROMANDEL.NS", "GMRINFRA.NS", "WHIRLPOOL.NS", "ALKEM.NS", "COFORGE.NS", "TDPOWERSYS.NS", "BHEL.NS", "SAIL.NS", "NATIONALUM.NS", "BANDHANBNK.NS",
    "GUJGASLTD.NS", "IPCALAB.NS", "LAURUSLABS.NS", "TATAELXSI.NS", "DEEPAKNTR.NS", "CROMPTON.NS", "ACC.NS", "DALBHARAT.NS", "JSL.NS", "APLAPOLLO.NS",
    "MFSL.NS", "PETRONET.NS", "ZEEL.NS", "RAMCOCEM.NS", "NAVINFLUOR.NS", "SYNGENE.NS", "TRIDENT.NS", "SOLARINDS.NS", "RVNL.NS", "IRFC.NS",
    "MAZDOCK.NS", "COCHINSHIP.NS", "FACT.NS", "SUZLON.NS", "IDEA.NS", "YESBANK.NS", "IDBI.NS", "UNIONBANK.NS", "IOB.NS", "UCOBANK.NS",
    "CENTRALBK.NS", "MAHABANK.NS", "BANKINDIA.NS", "BSE.NS", "CDSL.NS", "ANGELONE.NS", "MCX.NS", "MOTILALOFS.NS", "IEX.NS", "LUPIN.NS",
    "BIOCON.NS", "AUROPHARMA.NS", "GLENMARK.NS", "ZYDUSLIFE.NS", "GRANULES.NS", "ABFRL.NS", "BATAINDIA.NS", "RELAXO.NS", "PAGEIND.NS", "JUBLFOOD.NS",
    "DEVYANI.NS", "SAPPHIRE.NS", "KALYANKJIL.NS", "RAJESHEXPO.NS", "MANAPPURAM.NS", "M&MFIN.NS", "LICHSGFIN.NS", "POONAWALLA.NS", "SUNDARAMFIN.NS", "KPITTECH.NS",
    "CYIENT.NS", "BSOFT.NS", "SONACOMS.NS", "ZENSARTECH.NS", "OFSS.NS", "HONAUT.NS", "KEI.NS", "DIXON.NS", "AMBER.NS", "KAYNES.NS",
    "DATAPATTNS.NS", "MTARTECH.NS", "PARAS.NS", "ASTRAMICRO.NS", "CENTUM.NS", "HBLPOWER.NS", "TITAGARH.NS", "TEXRAIL.NS", "JWL.NS", "RKFORGE.NS",
    "ELECTCAST.NS", "GABRIEL.NS", "PRICOLLTD.NS", "SUBROS.NS", "LUMAXIND.NS", "MINDA CORP.NS", "UNOMINDA.NS", "ENDURANCE.NS", "CRAFTSMAN.NS", "JAMNAAUTO.NS",
    "GNA.NS", "ROLEXRINGS.NS", "SFL.NS", "TIMKEN.NS", "SCHAEFFLER.NS", "SKFINDIA.NS", "AIAENG.NS", "THERMAX.NS", "TRIVENI.NS", "PRAJIND.NS",
    "BALRAMCHIN.NS", "EIDPARRY.NS", "RENUKA.NS", "TRIVENITURB.NS", "KIRLOSENG.NS", "ELGIEQUIP.NS", "INGERRAND.NS", "KSB.NS", "POWERINDIA.NS", "HITACHI.NS",
    "VOLTAS.NS", "BLUESTARCO.NS", "KAJARIACER.NS", "CERA.NS", "SOMANYCERA.NS", "GREENPANEL.NS", "CENTURYPLY.NS", "STYLAMIND.NS", "PRINCEPIPE.NS", "FINPIPE.NS",
    "JINDALSAW.NS", "WELCORP.NS", "MAHARSEAM.NS", "RATNAMANI.NS", "APLLTD.NS", "ALEMBICLTD.NS", "ERIS.NS", "AJANTPHARM.NS", "JBITHEM.NS", "NATCOPHARM.NS",
    "PFIZER.NS", "SANOFI.NS", "ABBOTINDIA.NS", "GLAXO.NS", "ASTERDM.NS", "NARAYANA.NS", "KIMS.NS", "RAINBOW.NS", "METROPOLIS.NS", "THYROCARE.NS",
    "VIJAYA.NS", "FORTIS.NS", "MAXHEALTH.NS", "NH.NS", "HCG.NS", "POLYMED.NS", "LINDEINDIA.NS", "FLUOROCHEM.NS", "AETHER.NS", "CLEAN.NS",
    "FINEORG.NS", "VINATIORGA.NS", "ROSSARI.NS", "NOCIL.NS", "SUMICHEM.NS", "UPL.NS", "RALLIS.NS", "CHAMBLFERT.NS", "GNFC.NS", "GSFC.NS",
    "DEEPAKFERT.NS", "PARADEEP.NS", "IPL.NS", "CASTROLIND.NS", "GULFOILLUB.NS", "BLS.NS", "REDINGTON.NS", "ECLERX.NS", "FSL.NS", "TANLA.NS",
    "ROUTE.NS", "MASTEK.NS", "INTELLECT.NS", "HAPPSTMNDS.NS", "LATENTVIEW.NS", "MAPMYINDIA.NS", "RATEGAIN.NS", "NAZARA.NS", "PBFINTECH.NS", "PAYTM.NS",
    "NYKAA.NS", "DELHIVERY.NS", "HONASA.NS", "RRKABEL.NS", "CAMS.NS", "KFINTECH.NS", "PRUDENT.NS", "ANANDRATHI.NS", "SHAREINDIA.NS", "GEJTL.NS",
    "STARCEMENT.NS", "JKCEMENT.NS", "JKLAKSHMI.NS", "BIRLACORPN.NS", "HEIDELBERG.NS", "NUVOCO.NS", "ORIENTCEM.NS", "SAGCEM.NS", "KCP.NS", "INDIACEM.NS",
    "PRISMJOHN.NS", "AARTIIND.NS", "SUDARSCHEM.NS", "LAOPALA.NS", "BORORENEW.NS", "ASAHIINDIA.NS", "VIPIND.NS", "SAFARI.NS", "TTKPRESTIG.NS", "HAWKINS.NS",
    "SYMPHONY.NS", "ORIENTELEC.NS", "VGUARD.NS", "IFBIND.NS", "JOHNSONCON.NS", "PGHH.NS", "GILLETTE.NS", "EMAMILTD.NS", "MARICO.NS", "JYOTHYLAB.NS",
    "WABAG.NS", "VAIBHAVGBL.NS", "PCJEWELLER.NS", "THANGAMAYL.NS", "SENCO.NS", "GOLDIAM.NS", "RADICO.NS", "UBL.NS", "SULA.NS", "GMMPFAUDLR.NS",
    "TEJASNET.NS", "ITI.NS", "HFCL.NS", "STERLITE.NS", "INDUSTOWER.NS", "GSPL.NS", "MGL.NS", "IGL.NS", "ATGL.NS", "OIL.NS",
    "HINDPETRO.NS", "CHENNPETRO.NS", "MRPL.NS", "AEGISLOG.NS", "CONFIPET.NS", "DEEPINDS.NS", "HOEC.NS", "SELAN.NS", "JINDALDRILL.NS", "SWSOLAR.NS",
    "BOROLTD.NS", "GREAVESCOT.NS", "KIRLOSIND.NS", "PTC.NS", "SJVN.NS", "NHPC.NS", "JPPOWER.NS", "RTNPOWER.NS", "RPOWER.NS", "ADANIPOWER.NS", "JSWENERGY.NS",
    "CESC.NS", "EXIDEIND.NS", "AMARAJABAT.NS", "HBLPOWER.NS", "HUDCO.NS", "NBCC.NS", "RITES.NS", "IRCON.NS", "RAILTEL.NS", "BEML.NS", "GPPL.NS",
    "SCI.NS", "DREDGECORP.NS", "RCF.NS", "NFL.NS", "AWL.NS", "PATANJALI.NS", "MANYAVAR.NS", "RHIM.NS", "POLICYBZR.NS", "STARHEALTH.NS",
    "MEDANTA.NS", "BIKAJI.NS", "CAMPUS.NS", "METROBRAND.NS", "RUSTOMJEE.NS", "KEYSTONE.NS", "SIGNATURE.NS", "SOBHA.NS", "PRESTIGE.NS", "BRIGADE.NS",
    "GODREJPROP.NS", "SUNTECK.NS", "MAHLIFE.NS", "PURVA.NS", "ASHOKA.NS", "PNCINFRA.NS", "KNRCON.NS", "GRINFRA.NS", "HGINFRA.NS", "DILIPBUILD.NS",
    "NCC.NS", "HCC.NS", "ITDCEM.NS", "MANINFRA.NS", "JKTYRE.NS", "CEATLTD.NS", "APOLLOTYRE.NS", "BALKRISIND.NS", "TVSSRICHAK.NS", "GOCOLORS.NS",
    "VMART.NS", "SHOPERSTOP.NS", "TCNSBRANDS.NS", "ARVIND.NS", "RAYMOND.NS", "WELSPUNIND.NS", "GARFIBRES.NS", "LUXIND.NS", "DOLLAR.NS", "RUPA.NS",
    "KPRMILL.NS", "GOKEX.NS", "SWANENERGY.NS", "TRITURBINE.NS", "ELECON.NS", "AIAENGINE.NS", "TIMKEN.NS", "SCHAEFFLER.NS", "GRINDWELL.NS", "CARBORUNIV.NS",
    "MMTC.NS", "STCINDIA.NS", "GMDC.NS", "MOIL.NS", "KIOCL.NS", "HINDCOPPER.NS", "HINDZINC.NS", "GPIL.NS", "JAYNECOIND.NS", "LLOYDSME.NS",
    "IMFA.NS", "MASTEK.NS", "FSL.NS", "ECLERX.NS", "HGS.NS", "DATAMATICS.NS", "CMSINFO.NS", "SIS.NS", "QUESS.NS", "TEAMLEASE.NS",
    "BLS.NS", "JUSTDIAL.NS", "AFFLE.NS", "INDIAMART.NS", "VAIBHAVGBL.NS", "CARTRADE.NS", "EASYTRIP.NS", "YATRA.NS", "RBA.NS", "WESTLIFE.NS",
    "BARBEQUE.NS", "SPECIALITY.NS", "CHALET.NS", "LEMONHOTEL.NS", "EIHOTEL.NS", "INDHOTEL.NS", "TAJGVK.NS", "MAHSEAMLES.NS", "APOLLOPIPE.NS", "SURYA.NS"
]

if start_scan:
    progress_bar = st.progress(0)
    status_text = st.empty()
    valid_data = []
    
    for i, stock in enumerate(STOCKS):
        status_text.caption(f"AI Scanning {i+1}/{len(STOCKS)}: {stock}")
        data = get_stock_data(stock) 
        progress_bar.progress((i + 1) / len(STOCKS))
        
        # --- SMART FILTERING ---
        if data:
            if data['close'] > data['entry']:
                
                status = "HOLD"
                if data['close'] < data['sl']: 
                    status = "EXIT NOW"
                elif data['ai_score'] >= 60: # AI Approved
                    status = "STRONG BUY"
                
                valid_data.append({
                    "Stock": data['symbol'],
                    "Price": data['close'],
                    "Entry": data['entry'],
                    "Target": data['target'],
                    "Stop Loss": data['sl'],
                    "Vol Surge": data['rvol'],
                    "RSI": data['rsi'],
                    "AI Score": data['ai_score'],
                    "Status": status
                })

    progress_bar.empty()
    status_text.empty()
    
    if valid_data:
        df = pd.DataFrame(valid_data)
        
        # 3D Cards
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"<div class='dashboard-card card-blue'><p class='card-value'>{len(df)}</p><p class='card-label'>Stocks Scanned</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='dashboard-card card-green'><p class='card-value'>{len(df[df['Status']=='STRONG BUY'])}</p><p class='card-label'>AI Approved Buys</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='dashboard-card card-red'><p class='card-value'>{len(df[df['Status']=='EXIT NOW'])}</p><p class='card-label'>Stop Loss Hits</p></div>", unsafe_allow_html=True)
        
        # Long Notification (Restored)
        st.markdown("""
        <div class="advice-box">
            <b>💡 TRADING RULES & NOTIFICATION:</b><br>
            ✅ <b>STRONG BUY:</b> Only enter if <b>Volume is > 1.5x</b> and Price Gain is between <b>0.5% to 3%</b> from Entry Price.<br>
            ⚠️ <b>AVOID/RISKY:</b> If stock has already moved <b>> 5%</b> from Entry (Chase mat karein).<br>
            🛑 <b>EXIT:</b> If price closes below the Stop Loss level immediately.
        </div>
        """, unsafe_allow_html=True)
        
        # Table with Formatting
        def color_row(val):
            if 'STRONG' in val: return 'background-color: #d4edda; color: green; font-weight: bold;'
            if 'EXIT' in val: return 'background-color: #f8d7da; color: red; font-weight: bold;'
            return ''
            
        st.dataframe(
            df.style.map(color_row, subset=['Status']).format({
                "Price": "{:.2f}", 
                "Entry": "{:.2f}", 
                "Target": "{:.2f}", 
                "Stop Loss": "{:.2f}",
                "Vol Surge": "{:.2f}x",
                "RSI": "{:.2f}",
                "AI Score": "{:.0f}/100"
            }),
            use_container_width=True, 
            height=600, 
            hide_index=True
        )
    else:
        st.warning("No high-probability setups found today.")
else:
    st.info("Click 'RUN AI SCANNER' to begin.")
