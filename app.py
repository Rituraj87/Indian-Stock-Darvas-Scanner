import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. पेज कॉन्फ़िगरेशन (App Mode) ---
st.set_page_config(
    page_title="Darvas Pro Elite", 
    layout="wide", 
    page_icon="🦅",
    initial_sidebar_state="expanded"
)

# --- 2. PREMIUM APP UI (CSS) ---
st.markdown("""
<style>
    /* पूरे ऐप का फॉन्ट और बैकग्राउंड */
    .stApp { background-color: #f4f6f9; }
    
    /* सर्च बार को सुंदर बनाएं */
    .stTextInput > div > div > input {
        border-radius: 15px; border: 2px solid #3b82f6; padding: 15px; font-size: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* --- GLASS CARD STYLE (विवरण देखने के लिए) --- */
    .glass-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0f2f5 100%);
        border: 1px solid white;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        backdrop-filter: blur(4px);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        transition: transform 0.3s;
    }
    .glass-card:hover { transform: translateY(-5px); }

    /* हेडलाइंस */
    .section-title { font-size: 24px; font-weight: bold; color: #1e293b; margin-bottom: 10px; }
    .sub-text { font-size: 14px; color: #64748b; }

    /* स्टेटस बैज */
    .badge { padding: 5px 12px; border-radius: 12px; font-weight: bold; color: white; display: inline-block; }
    .bg-green { background-color: #10b981; }
    .bg-red { background-color: #ef4444; }
    .bg-yellow { background-color: #f59e0b; }

    /* बटन्स */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #7c3aed 100%);
        color: white; border: none; padding: 15px; border-radius: 12px;
        font-size: 18px; font-weight: bold; box-shadow: 0 4px 12px rgba(37,99,235,0.3);
    }
    div.stButton > button:hover { background: linear-gradient(90deg, #1d4ed8 0%, #6d28d9 100%); }
</style>
""", unsafe_allow_html=True)

# --- 3. पासवर्ड ---
MY_PASSWORD = "admin" 
def check_password():
    if "password_correct" not in st.session_state: st.session_state.password_correct = False
    if not st.session_state.password_correct:
        st.markdown("<h2 style='text-align:center;'>🔒 Login Required</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Enter App Password:", type="password")
        if st.button("UNLOCK APP"):
            if pwd == MY_PASSWORD: st.session_state.password_correct = True; st.rerun()
        return False
    return True
if not check_password(): st.stop()

# --- 4. साइडबार (Market Mood) ---
def get_nifty_mood():
    try:
        df = yf.download("^NSEI", period="6mo", interval="1d", progress=False)
        close = df['Close'].iloc[-1].item()
        ema50 = df['Close'].ewm(span=50, adjust=False).mean().iloc[-1].item()
        return ("🟢 BULLISH", "#dcfce7", "#166534") if close > ema50 else ("🔴 BEARISH", "#fee2e2", "#991b1b")
    except: return ("⚪ NEUTRAL", "#f3f4f6", "#1f2937")

with st.sidebar:
    st.image("https://cdn.pixabay.com/photo/2020/05/18/16/17/social-media-5187243_1280.png", caption="Pro Analytics", use_column_width=True)
    mood_text, bg_col, txt_col = get_nifty_mood()
    st.markdown(f"""
    <div style='background-color: {bg_col}; color: {txt_col}; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold;'>
        MARKET TREND: {mood_text}
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    start_scan = st.button("🚀 SCAN 500 STOCKS", type="primary")

# --- 5. DATA ENGINE (Full Details) ---
@st.cache_data(ttl=900)
def get_stock_details(symbol):
    try:
        symbol = symbol.upper().strip()
        if not symbol.endswith(".NS"): symbol = f"{symbol}.NS"
        
        ticker = yf.Ticker(symbol)
        
        # 1. Historical Data (Fast)
        df = ticker.history(period="6mo", interval="1d")
        if len(df) < 50: return None
        
        # Values
        close = df['Close'].iloc[-1]
        
        # Darvas & Technicals
        past = df.iloc[:-1]
        entry = past['High'].tail(20).max()
        sl = past['Low'].tail(20).min()
        
        avg_vol = past['Volume'].tail(20).mean()
        cur_vol = df['Volume'].iloc[-1]
        rvol = cur_vol / avg_vol if avg_vol > 0 else 0
        
        # Indicators
        ema50 = df['Close'].ewm(span=50, adjust=False).mean().iloc[-1]
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]

        # 2. Fundamentals (Detailed) - Using Try/Except blocks for safety
        info = ticker.info
        
        details = {
            "symbol": symbol.replace(".NS", ""),
            "close": close, "entry": entry, "sl": sl,
            "target": entry + ((entry-sl)*2),
            "rvol": rvol, "rsi": rsi, "ema50": ema50,
            
            # --- FULL DETAILS RESTORED ---
            "name": info.get("longName", symbol),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "mcap": info.get("marketCap", 0) / 10000000, # Crores
            "pe": info.get("trailingPE", 0),
            "book_val": info.get("bookValue", 0),
            "div_yield": info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0,
            "high52": info.get("fiftyTwoWeekHigh", 0),
            "low52": info.get("fiftyTwoWeekLow", 0),
            "website": info.get("website", "#")
        }
        
        # AI Score logic
        score = 0
        if close > entry: score += 40
        if rvol > 1.5: score += 20
        if close > ema50: score += 20
        if 50 < rsi < 70: score += 20
        details['score'] = score
        
        return details
    except: return None

# --- 6. MAIN APP INTERFACE ---
st.title("🦅 Darvas Pro Elite")

# === SECTION A: UNIVERSAL SEARCH (DETAILED) ===
st.markdown("### 🔍 Stock Analyzer (Full Detail)")
search_query = st.text_input("Search Stock (e.g. ZOMATO, TATASTEEL):", "")

if search_query:
    with st.spinner(f"Fetching full report for {search_query}..."):
        data = get_stock_details(search_query)
        
        if data:
            # Color Logic
            if data['score'] >= 80: status = "STRONG BUY 🚀"; color = "green"
            elif data['score'] >= 60: status = "BUY / HOLD 🟢"; color = "orange"
            elif data['close'] < data['sl']: status = "EXIT NOW 🔴"; color = "red"
            else: status = "NEUTRAL ⚪"; color = "grey"

            # --- 1. HEADER CARD ---
            st.markdown(f"""
            <div class="glass-card" style="border-left: 5px solid {color};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h1 style="margin:0; color:#1e293b;">{data['name']}</h1>
                        <p class="sub-text">{data['sector']} | {data['industry']}</p>
                    </div>
                    <div style="text-align:right;">
                        <h2 style="margin:0; color:{color};">{status}</h2>
                        <span style="font-size:24px; font-weight:bold;">₹{data['close']:.2f}</span>
                    </div>
                </div>
                <hr>
                <div style="display:flex; justify-content:space-between; text-align:center;">
                    <div><b>Target</b><br>₹{data['target']:.2f}</div>
                    <div><b>Stop Loss</b><br>₹{data['sl']:.2f}</div>
                    <div><b>Entry</b><br>₹{data['entry']:.2f}</div>
                    <div><b>Vol Surge</b><br>{data['rvol']:.1f}x</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- 2. DETAILS GRID (FUNDAMENTALS) ---
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown("""<div class="glass-card"><h4>📊 Fundamental Data</h4>""", unsafe_allow_html=True)
                st.markdown(f"""
                - **Market Cap:** ₹{int(data['mcap']):,} Cr
                - **P/E Ratio:** {data['pe']:.2f}
                - **Book Value:** ₹{data['book_val']:.2f}
                - **Div Yield:** {data['div_yield']:.2f}%
                """)
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown("""<div class="glass-card"><h4>📈 Technical Levels</h4>""", unsafe_allow_html=True)
                st.markdown(f"""
                - **52W High:** ₹{data['high52']:.2f}
                - **52W Low:** ₹{data['low52']:.2f}
                - **RSI (14):** {data['rsi']:.2f}
                - **Trend (EMA50):** {"UP 🟢" if data['close']>data['ema50'] else "DOWN 🔴"}
                """)
                st.markdown("</div>", unsafe_allow_html=True)

            # --- 3. EXTERNAL LINK ---
            st.markdown(f"""
            <a href="https://in.tradingview.com/chart/?symbol=NSE:{data['symbol']}" target="_blank" style="text-decoration:none;">
                <div style="background:#2962ff; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">
                    Open Advanced Chart on TradingView ↗
                </div>
            </a>
            """, unsafe_allow_html=True)

        else:
            st.error("Stock not found. Please check the spelling.")

st.markdown("---")

# === SECTION B: 500 STOCK SCANNER (FAST LIST) ===
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

st.markdown("### 📊 Nifty 500 Scanner")

if start_scan:
    progress_bar = st.progress(0)
    status_text = st.empty()
    valid_data = []
    
    for i, stock in enumerate(STOCKS):
        status_text.caption(f"Scanning {i+1}/{len(STOCKS)}: {stock}")
        # Note: Scanner uses lighter logic to stay fast
        try:
            ticker = yf.Ticker(stock)
            df = ticker.history(period="3mo", interval="1d")
            if len(df) > 20:
                close = df['Close'].iloc[-1]
                entry = df['High'].iloc[:-1].tail(20).max()
                sl = df['Low'].iloc[:-1].tail(20).min()
                
                # Check Darvas Condition
                if close > entry:
                    # Calculate minimal details for table
                    avg_vol = df['Volume'].iloc[:-1].tail(20).mean()
                    cur_vol = df['Volume'].iloc[-1]
                    rvol = cur_vol / avg_vol if avg_vol > 0 else 0
                    
                    status = "STRONG BUY" if rvol > 1.5 else "HOLD"
                    if close < sl: status = "EXIT NOW"
                    
                    valid_data.append({
                        "Symbol": stock.replace(".NS",""),
                        "Price": close,
                        "Entry": entry,
                        "Target": entry + ((entry-sl)*2),
                        "Stop Loss": sl,
                        "Vol Surge": rvol,
                        "Status": status
                    })
        except: pass
        progress_bar.progress((i + 1) / len(STOCKS))

    progress_bar.empty()
    status_text.empty()
    
    if valid_data:
        df = pd.DataFrame(valid_data)
        
        # Advice Box (Long)
        st.markdown("""
        <div style="background-color:#eff6ff; padding:15px; border-radius:10px; border-left:5px solid #3b82f6; margin-bottom:20px;">
            <b>💡 TRADING RULES:</b><br>
            ✅ <b>STRONG BUY:</b> Only enter if Volume > 1.5x & Gain < 3%.<br>
            🛑 <b>EXIT:</b> If price closes below Stop Loss immediately.
        </div>
        """, unsafe_allow_html=True)
        
        # Color Function
        def color_row(val):
            if 'STRONG' in val: return 'background-color: #dcfce7; color: #166534; font-weight: bold;'
            if 'EXIT' in val: return 'background-color: #fee2e2; color: #991b1b; font-weight: bold;'
            return ''
            
        st.dataframe(
            df.style.map(color_row, subset=['Status']).format({
                "Price": "{:.2f}", "Entry": "{:.2f}", "Target": "{:.2f}", 
                "Stop Loss": "{:.2f}", "Vol Surge": "{:.2f}x"
            }),
            use_container_width=True, height=600, hide_index=True
        )
        
        # Download Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results (CSV)", csv, "scan_results.csv", "text/csv")
    else:
        st.warning("No breakout stocks found right now.")

else:
    st.info("Click 'SCAN 500 STOCKS' in sidebar to start.")
        
