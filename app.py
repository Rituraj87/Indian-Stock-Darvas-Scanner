import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. पेज सेटिंग्स ---
st.set_page_config(
    page_title="Darvas Elite Terminal", 
    layout="wide", 
    page_icon="🦅",
    initial_sidebar_state="expanded"
)

# --- 2. PROFESSIONAL STYLING (CSS) ---
st.markdown("""
<style>
    /* सर्च बार */
    .stTextInput > div > div > input {
        border-radius: 10px; border: 2px solid #2980b9; padding: 12px; font-size: 18px;
    }
    
    /* 3D Cards */
    .dashboard-card {
        box-shadow: 0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23);
        padding: 20px; border-radius: 12px; text-align: center; color: white;
        margin-bottom: 20px; transform: translateY(-5px); transition: 0.3s;
    }
    .dashboard-card:hover { transform: translateY(-8px); }
    
    .card-blue { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); }
    .card-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .card-red { background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%); }
    
    .card-value { font-size: 40px !important; font-weight: 800; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .card-label { font-size: 16px !important; font-weight: 600; opacity: 0.9; text-transform: uppercase; }

    /* Market Trend Bar */
    .trend-box {
        padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 20px; color: white; margin-bottom: 20px;
    }
    
    /* Notification */
    .advice-box { 
        background-color: #e8f5e9; border-left: 6px solid #2e7d32; 
        padding: 15px; border-radius: 5px; color: #1b5e20; margin: 10px 0; font-size: 15px;
    }
    
    /* Button */
    div.stButton > button { 
        width: 100%; background: linear-gradient(90deg, #FF512F 0%, #DD2476 100%); 
        color: white; font-weight: bold; padding: 12px; border-radius: 8px; border: none; font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. पासवर्ड ---
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
    st.image("https://cdn.pixabay.com/photo/2020/05/18/16/17/social-media-5187243_1280.png", caption="Darvas System", use_column_width=True)
    st.title("DARVAS ELITE")
    st.markdown("---")
    start_scan = st.button("🚀 SCAN NIFTY 500", type="primary")
    st.caption("Darvas Rule: Buy only in Uptrend.")

# --- 5. DATA ENGINE (Advanced) ---
@st.cache_data(ttl=900)
def get_market_trend():
    # Darvas Rule 1: Check General Market (Nifty 50)
    try:
        nifty = yf.Ticker("^NSEI")
        hist = nifty.history(period="5d")
        close = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        
        # Simple MA check (Close > 50 SMA is ideal, but here we check momentum)
        trend = "UPTREND 🐂" if close > prev_close else "DOWNTREND 🐻"
        color = "#2ecc71" if close > prev_close else "#e74c3c"
        return trend, color, close
    except:
        return "NEUTRAL 😐", "#95a5a6", 0

@st.cache_data(ttl=900)
def get_stock_data(symbol):
    try:
        symbol = symbol.upper().strip()
        if not symbol.endswith(".NS"): symbol = f"{symbol}.NS"
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="3mo", interval="1d")
        if len(df) < 30: return None
        
        def get_val(s): return s.iloc[0] if isinstance(s, pd.Series) else s
        
        close = get_val(df['Close'].iloc[-1])
        
        # Darvas Box Calculation
        past = df.iloc[:-1]
        box_high = get_val(past['High'].tail(20).max()) # Upper Box Limit
        box_low = get_val(past['Low'].tail(20).min())   # Lower Box Limit / Stop Loss
        
        # Volume Check
        avg_vol = get_val(past['Volume'].tail(20).mean())
        cur_vol = get_val(df['Volume'].iloc[-1])
        rvol = cur_vol / avg_vol if avg_vol > 0 else 0
        
        # Darvas Fundamentals (Basic Check)
        try:
            info = ticker.info
            mcap = info.get("marketCap", 0) / 10000000 
            pe = info.get("trailingPE", 0)
            sector = info.get("sector", "N/A")
            high52 = info.get("fiftyTwoWeekHigh", 0)
        except:
            mcap, pe, sector, high52 = 0, 0, "N/A", 0

        # Relative Strength (Simple: Is it near 52W High?)
        is_near_high = close >= (high52 * 0.85) # Darvas liked stocks near ATH

        return {
            "symbol": symbol.replace(".NS", ""),
            "close": close, "entry": box_high, "sl": box_low, 
            "rvol": rvol, "mcap": mcap, "pe": pe, "sector": sector, 
            "high52": high52, "near_high": is_near_high
        }
    except: return None

# --- 6. MAIN INTERFACE ---
st.title("🦅 Darvas Elite Terminal")

# --- Step 1: Market Trend Check (Darvas Rule #1) ---
trend, trend_color, nifty_price = get_market_trend()
st.markdown(f"""
<div class="trend-box" style="background-color: {trend_color};">
    MARKET MOOD: {trend} (Nifty: {nifty_price:.2f})<br>
    <span style="font-size:14px;">Darvas Principle: "I never buy a stock if the general market is falling."</span>
</div>
""", unsafe_allow_html=True)

# --- Step 2: Universal Search ---
st.markdown("### 🔍 Stock Analyzer (Darvas Method)")
search_symbol = st.text_input("Enter Symbol (e.g. TRENT, BEL):", "")

if search_symbol:
    with st.spinner(f"Applying Darvas Theory on {search_symbol}..."):
        data = get_stock_data(search_symbol)
        
        if data:
            # Darvas Logic
            status = "HOLD / WAIT"
            color = "#f39c12" # Orange
            msg = "Stock is inside the box. No action."
            
            if data['close'] > data['entry']:
                if data['rvol'] > 1.5 and data['near_high']:
                    status = "DARVAS BUY 🚀"
                    color = "#27ae60" # Green
                    msg = "Box Breakout + High Volume + Near 52W High (Perfect Setup)"
                elif data['rvol'] > 1.5:
                    status = "BUY (Weak) ⚠️"
                    color = "#82e0aa"
                    msg = "Breakout with Volume, but not near All Time Highs."
                else:
                    status = "FAKE BREAKOUT?"
                    color = "#d35400"
                    msg = "Price broke out, but Volume is low. Be careful."
            elif data['close'] < data['sl']:
                status = "EXIT NOW 🛑"
                color = "#c0392b"
                msg = "Price fell below the Box. Darvas Rule: Sell immediately."
            
            # Display Card
            st.markdown(f"""
            <div style="background-color: white; border: 3px solid {color}; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                <h1 style="color: {color}; margin: 0;">{data['symbol']}</h1>
                <h2 style="color: {color}; margin-top:5px;">{status}</h2>
                <p style="color: #555; font-style: italic;">"{msg}"</p>
                <hr>
                <div style="display: flex; justify-content: space-around; font-size: 18px; color: #333;">
                    <div><b>Price:</b><br>₹{data['close']:.2f}</div>
                    <div><b>Box Top (Buy):</b><br>₹{data['entry']:.2f}</div>
                    <div><b>Box Low (SL):</b><br>₹{data['sl']:.2f}</div>
                    <div><b>Vol Surge:</b><br>{data['rvol']:.2f}x</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"👉 [**View Chart**](https://in.tradingview.com/chart/?symbol=NSE:{data['symbol']})")
        else:
            st.error("Stock not found.")

st.markdown("---")

# --- Step 3: Nifty 500 Scanner ---
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
    "BOROLTD.NS", "GREAVESCOT.NS", "KIRLOSIND.NS", "PTC.NS", "SJVN.NS", "NHPC.NS", "JPPOWER.NS", "RTNPOWER.NS", "RPOWER.NS", "JSWENERGY.NS",
    "CESC.NS", "EXIDEIND.NS", "AMARAJABAT.NS", "HUDCO.NS", "NBCC.NS", "RITES.NS", "IRCON.NS", "RAILTEL.NS", "BEML.NS", "GPPL.NS",
    "SCI.NS", "DREDGECORP.NS", "RCF.NS", "NFL.NS", "FACT.NS", "CHAMBLFERT.NS", "GNFC.NS", "DEEPAKFERT.NS", "COROMANDEL.NS"
]

st.markdown("### 📊 Nifty 500 Scanner (Darvas Filter)")

if start_scan:
    progress_bar = st.progress(0)
    status_text = st.empty()
    valid_data = []
    
    for i, stock in enumerate(STOCKS):
        status_text.caption(f"Checking {stock}...")
        data = get_stock_data(stock) 
        progress_bar.progress((i + 1) / len(STOCKS))
        
        if data and data['close'] > data['entry']:
            risk = data['entry'] - data['sl']
            pct_change = ((data['close'] - data['entry']) / data['entry']) * 100
            
            # Darvas Logic Filters
            status = "HOLD"
            if data['close'] < data['sl']: 
                status = "EXIT NOW"
            elif data['rvol'] > 1.5: 
                status = "STRONG BUY"
            
            # Formatting (2 Decimals enforced)
            valid_data.append({
                "Stock": data['symbol'],
                "Price": data['close'],
                "Box Top": data['entry'],
                "Stop Loss": data['sl'],
                "Gain %": pct_change,
                "Vol Surge": data['rvol'],
                "Status": status
            })

    progress_bar.empty()
    status_text.empty()
    
    if valid_data:
        df = pd.DataFrame(valid_data)
        
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"<div class='dashboard-card card-blue'><p class='card-value'>{len(df)}</p><p class='card-label'>Matches</p></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='dashboard-card card-green'><p class='card-value'>{len(df[df['Status']=='STRONG BUY'])}</p><p class='card-label'>Strong Buys</p></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='dashboard-card card-red'><p class='card-value'>{len(df[df['Status']=='EXIT NOW'])}</p><p class='card-label'>Exits</p></div>", unsafe_allow_html=True)
        
        # Darvas Notification
        st.markdown("""
        <div class="advice-box">
            <b>📜 DARVAS RULES (Strict):</b><br>
            1. <b>Market Check:</b> Only buy if Nifty is UPTREND.<br>
            2. <b>Volume:</b> 'Vol Surge' must be > 1.5x.<br>
            3. <b>Box Theory:</b> Buy exactly when Price crosses 'Box Top'. Stop Loss is 'Box Low'.
        </div>
        """, unsafe_allow_html=True)
        
        def color_row(val):
            if 'STRONG' in val: return 'background-color: #d4edda; color: green; font-weight: bold;'
            if 'EXIT' in val: return 'background-color: #f8d7da; color: red; font-weight: bold;'
            return ''
            
        st.dataframe(
            df.style.map(color_row, subset=['Status']).format({
                "Price": "{:.2f}", 
                "Box Top": "{:.2f}", 
                "Stop Loss": "{:.2f}", 
                "Gain %": "{:.2f}%",
                "Vol Surge": "{:.2f}x"
            }),
            use_container_width=True, 
            height=600, 
            hide_index=True
        )
    else:
        st.warning("No stocks matched the breakout criteria today.")
else:
    st.info("Click 'SCAN NIFTY 500' to start.")
            
