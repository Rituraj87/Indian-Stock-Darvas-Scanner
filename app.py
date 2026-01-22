import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="Darvas AI Prime", 
    layout="wide", 
    page_icon="🦅",
    initial_sidebar_state="expanded"
)

# --- 2. SMART UI (DAY/NIGHT FRIENDLY) ---
st.markdown("""
<style>
    /* Global Font */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    /* SEARCH BAR */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #4CAF50;
        padding: 12px;
        font-size: 18px;
    }

    /* --- GLASSMORPHISM CARDS --- */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }

    /* SPECIAL AI CARDS (Restored) */
    .ai-card {
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.1) 0%, rgba(39, 174, 96, 0.1) 100%);
        border: 1px solid #2ecc71;
        border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 15px;
    }
    .level-card {
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.1) 0%, rgba(41, 128, 185, 0.1) 100%);
        border: 1px solid #3498db;
        border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 15px;
    }

    /* STATUS BADGES */
    .badge-buy { background-color: #d4edda; color: #155724; padding: 5px 10px; border-radius: 8px; font-weight: bold; border: 1px solid #c3e6cb; }
    .badge-sell { background-color: #f8d7da; color: #721c24; padding: 5px 10px; border-radius: 8px; font-weight: bold; border: 1px solid #f5c6cb; }
    .badge-hold { background-color: #fff3cd; color: #856404; padding: 5px 10px; border-radius: 8px; font-weight: bold; border: 1px solid #ffeeba; }

    /* TEXT SIZES */
    .big-value { font-size: 28px; font-weight: 800; }
    .label-text { font-size: 14px; opacity: 0.8; text-transform: uppercase; }
    
    /* BUTTONS */
    div.stButton > button {
        width: 100%; border-radius: 10px; height: 50px; font-weight: bold;
        background: linear-gradient(90deg, #0072ff 0%, #00c6ff 100%);
        color: white; border: none; font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. PASSWORD PROTECTION ---
MY_PASSWORD = "admin" 
def check_password():
    if "password_correct" not in st.session_state: st.session_state.password_correct = False
    if not st.session_state.password_correct:
        st.markdown("### 🔒 Login Required")
        pwd = st.text_input("Enter Password:", type="password")
        if st.button("Login"):
            if pwd == MY_PASSWORD: st.session_state.password_correct = True; st.rerun()
        return False
    return True
if not check_password(): st.stop()

# --- 4. DATA ENGINE (AI + FUNDAMENTALS) ---
@st.cache_data(ttl=900)
def get_stock_data(symbol):
    try:
        symbol = symbol.upper().strip()
        if not symbol.endswith(".NS"): symbol = f"{symbol}.NS"
        
        ticker = yf.Ticker(symbol)
        
        # 1. Historical Data (6 Months)
        df = ticker.history(period="6mo", interval="1d")
        if len(df) < 50: return None
        
        def get_val(s): return s.iloc[0] if isinstance(s, pd.Series) else s
        
        # 2. Technicals
        close = get_val(df['Close'].iloc[-1])
        high = get_val(df['High'].iloc[-1])
        low = get_val(df['Low'].iloc[-1])
        
        past = df.iloc[:-1]
        entry = get_val(past['High'].tail(20).max())
        sl = get_val(past['Low'].tail(20).min())
        
        avg_vol = get_val(past['Volume'].tail(20).mean())
        cur_vol = get_val(df['Volume'].iloc[-1])
        rvol = cur_vol / avg_vol if avg_vol > 0 else 0
        
        ema50 = get_val(df['Close'].ewm(span=50, adjust=False).mean().iloc[-1])
        trend_status = "UP 📈" if close > ema50 else "DOWN 📉"
        
        # 3. AI Score
        ai_score = 0
        reasons = []
        if close > entry: ai_score += 35; reasons.append("Box Breakout")
        if rvol > 1.5: ai_score += 25; reasons.append("Volume Blast")
        if close > ema50: ai_score += 20; reasons.append("Uptrend")
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = get_val(100 - (100 / (1 + rs)).iloc[-1])
        if 50 < rsi < 75: ai_score += 20; reasons.append("Momentum")
        
        # 4. Levels (Support/Resistance)
        risk = entry - sl
        target = entry + (risk * 2)
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        s1 = (2 * pivot) - high
        
        # 5. Fundamentals
        try:
            info = ticker.info
            mcap = info.get("marketCap", 0) / 10000000 # Crores
            pe = info.get("trailingPE", 0)
            sector = info.get("sector", "N/A")
            high52 = info.get("fiftyTwoWeekHigh", 0)
            book_val = info.get("bookValue", 0)
        except:
            mcap, pe, sector, high52, book_val = 0, 0, "N/A", 0, 0

        return {
            "symbol": symbol.replace(".NS", ""),
            "close": close, "entry": entry, "sl": sl, "target": target,
            "rvol": rvol, "rsi": rsi, "ema": ema50, "trend": trend_status,
            "ai_score": ai_score, "reasons": ", ".join(reasons),
            "mcap": mcap, "pe": pe, "sector": sector,
            "high52": high52, "book_val": book_val,
            "s1": s1, "r1": r1
        }
    except: return None

# --- 5. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn.pixabay.com/photo/2020/05/18/16/17/social-media-5187243_1280.png", caption="AI Powered", use_column_width=True)
    st.title("AI TERMINAL")
    st.markdown("---")
    try:
        nifty = yf.download("^NSEI", period="5d", interval="1d", progress=False)
        n_close = nifty['Close'].iloc[-1]
        n_open = nifty['Open'].iloc[-1]
        t_color = "green" if n_close > n_open else "red"
        t_text = "BULLISH" if n_close > n_open else "BEARISH"
        st.markdown(f"**MARKET MOOD:** <span style='color:{t_color}; font-weight:bold'>{t_text}</span>", unsafe_allow_html=True)
    except: pass
    st.markdown("---")
    start_scan = st.button("🚀 SCAN NIFTY 500")

# --- 6. MAIN SEARCH UI ---
st.title("🦅 Darvas AI Scanner Pro")
st.markdown("### 🔎 Universal AI Analysis")
search_symbol = st.text_input("Search Stock (e.g. ZOMATO, TATASTEEL)", "")

if search_symbol:
    with st.spinner(f"Running AI Models on {search_symbol}..."):
        data = get_stock_data(search_symbol)
        
        if data:
            # Determine Status
            if data['ai_score'] >= 80: 
                status_html = f"<span class='badge-buy'>💎 STRONG BUY ({data['ai_score']}/100)</span>"
                sentiment_text = "BULLISH 🐂"
            elif data['ai_score'] >= 50: 
                status_html = f"<span class='badge-hold'>⚖️ HOLD / WATCH ({data['ai_score']}/100)</span>"
                sentiment_text = "NEUTRAL / MILD 🐃"
            else: 
                status_html = f"<span class='badge-sell'>🛑 WEAK / EXIT ({data['ai_score']}/100)</span>"
                sentiment_text = "BEARISH 🐻"
            
            # --- HEADER ---
            st.markdown(f"""
            <div class="glass-card">
                <h1 style="margin:0;">{data['symbol']} {status_html}</h1>
                <p style="opacity:0.7;">Sector: {data['sector']} | 52W High: ₹{data['high52']}</p>
            </div>
            """, unsafe_allow_html=True)

            # --- TOP ROW: PRICE & FUNDAMENTALS ---
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""<div class="glass-card"><h4>💰 Price</h4><div class="big-value">₹{data['close']:.2f}</div><p class="label-text">Current Price</p></div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div class="glass-card"><h4>📊 Market Cap</h4><div class="big-value">₹{int(data['mcap']):,}Cr</div><p class="label-text">Valuation</p></div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div class="glass-card"><h4>📉 PE Ratio</h4><div class="big-value">{data['pe']:.1f}</div><p class="label-text">Price to Earnings</p></div>""", unsafe_allow_html=True)

            # --- SECOND ROW: RESTORED SPECIAL CARDS (SENTIMENT & LEVELS) ---
            c_ai, c_lvl = st.columns(2)
            
            with c_ai:
                st.markdown(f"""
                <div class="ai-card">
                    <h3>🤖 AI Technical Sentiment</h3>
                    <div style="font-size: 24px; font-weight: bold; margin: 10px 0;">{sentiment_text}</div>
                    <p><b>Trend:</b> {data['trend']} | <b>RSI:</b> {data['rsi']:.1f}</p>
                    <p><b>Vol Surge:</b> {data['rvol']:.1f}x</p>
                    <small><i>Logic: {data['reasons']}</i></small>
                </div>
                """, unsafe_allow_html=True)
                
            with c_lvl:
                st.markdown(f"""
                <div class="level-card">
                    <h3>📐 Auto Support & Resistance</h3>
                    <div style="display: flex; justify-content: space-around; margin-top: 15px;">
                        <div>
                            <span style="font-size: 20px; font-weight: bold; color: #c0392b;">R1 (Res)</span><br>
                            <span style="font-size: 18px;">₹{data['r1']:.2f}</span>
                        </div>
                        <div>
                            <span style="font-size: 20px; font-weight: bold; color: #27ae60;">S1 (Sup)</span><br>
                            <span style="font-size: 18px;">₹{data['s1']:.2f}</span>
                        </div>
                    </div>
                    <hr>
                    <p><b>Target:</b> ₹{data['target']:.2f} | <b>Stop Loss:</b> ₹{data['sl']:.2f}</p>
                </div>
                """, unsafe_allow_html=True)

            # --- TRADING VIEW LINK ---
            st.markdown(f"""
                <a href="https://in.tradingview.com/chart/?symbol=NSE:{data['symbol']}" target="_blank">
                    <button>📈 Open {data['symbol']} Chart on TradingView</button>
                </a>
            """, unsafe_allow_html=True)

        else:
            st.error("Stock not found. Check spelling (e.g., use TATAMOTORS).")

st.markdown("---")

# --- 7. SCANNER SECTION ---
st.markdown("### 📡 Live Market Scanner (500 Stocks)")

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
        status_text.caption(f"Scanning {i+1}/{len(STOCKS)}: {stock}")
        data = get_stock_data(stock) 
        progress_bar.progress((i + 1) / len(STOCKS))
        
        if data and data['close'] > data['entry']:
            status = "HOLD"
            if data['close'] < data['sl']: status = "EXIT NOW"
            elif data['ai_score'] >= 60: status = "STRONG BUY"
            
            valid_data.append({
                "Stock": data['symbol'],
                "Price": data['close'],
                "Entry": data['entry'],
                "Target": data['target'],
                "Stop Loss": data['sl'],
                "Vol Surge": data['rvol'],
                "AI Score": data['ai_score'],
                "Status": status
            })

    progress_bar.empty()
    status_text.empty()
    
    if valid_data:
        df = pd.DataFrame(valid_data)
        
        # Display Metrics
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='glass-card'><h3>Found</h3><div class='big-value'>{len(df)}</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='glass-card'><h3>Buy</h3><div class='big-value'>{len(df[df['Status']=='STRONG BUY'])}</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='glass-card'><h3>Exit</h3><div class='big-value'>{len(df[df['Status']=='EXIT NOW'])}</div></div>", unsafe_allow_html=True)
        
        # Advice Box (Long)
        st.markdown("""
        <div style="background-color: #f0f8ff; border-left: 6px solid #2196F3; padding: 15px; border-radius: 5px; color: #0c5460; margin: 20px 0;">
            <b>💡 TRADING RULES & NOTIFICATION:</b><br>
            ✅ <b>STRONG BUY:</b> Only enter if <b>Volume is > 1.5x</b> and Price Gain is between <b>0.5% to 3%</b> from Entry Price.<br>
            ⚠️ <b>AVOID/RISKY:</b> If stock has already moved <b>> 5%</b> from Entry (Chase mat karein).<br>
            🛑 <b>EXIT:</b> If price closes below the Stop Loss level immediately.
        </div>
        """, unsafe_allow_html=True)
        
        def color_row(val):
            if 'STRONG' in val: return 'background-color: #d4edda; color: green; font-weight: bold;'
            if 'EXIT' in val: return 'background-color: #f8d7da; color: red; font-weight: bold;'
            return ''
            
        st.dataframe(
            df.style.map(color_row, subset=['Status']).format({
                "Price": "{:.2f}", "Entry": "{:.2f}", "Target": "{:.2f}", 
                "Stop Loss": "{:.2f}", "Vol Surge": "{:.2f}x", "AI Score": "{:.0f}"
            }),
            use_container_width=True, height=600, hide_index=True
        )
    else:
        st.warning("No breakout stocks found today.")
else:
    st.info("Click 'SCAN NIFTY 500' to start.")
