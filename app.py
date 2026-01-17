import streamlit as st
import yfinance as yf
import pandas as pd

# --- पेज सेटिंग ---
st.set_page_config(page_title="Darvas Pro 500", layout="wide", page_icon="⚡")

# --- कस्टम CSS (पट्टी और टेबल को सुंदर बनाने के लिए) ---
st.markdown("""
<style>
    /* टेबल का फॉन्ट और स्टाइल */
    .stDataFrame {font-size: 14px;}
    
    /* टॉप टिकर स्टाइल */
    .ticker-wrap-green {
        width: 100%;
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        margin-bottom: 5px;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        font-weight: bold;
    }
    .ticker-wrap-red {
        width: 100%;
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        margin-bottom: 20px;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- पासवर्ड सुरक्षा ---
MY_PASSWORD = "Rituraj87" 

def check_password():
    def password_entered():
        if st.session_state["password"] == MY_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("पासवर्ड डालें:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("गलत पासवर्ड। फिर से डालें:", type="password", on_change=password_entered, key="password")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- NIFTY 500 of indian market ---
STOCKS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS",
        "KOTAKBANK.NS", "L&T.NS", "HCLTECH.NS", "AXISBANK.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS",
        "BAJFINANCE.NS", "ULTRACEMCO.NS", "TATASTEEL.NS", "NTPC.NS", "M&M.NS", "POWERGRID.NS", "TATAMOTORS.NS",
        "ADANIENT.NS", "HINDUNILVR.NS", "COALINDIA.NS", "ONGC.NS", "JSWSTEEL.NS", "ADANIPORTS.NS", "GRASIM.NS",
        "BPCL.NS", "HINDALCO.NS", "DRREDDY.NS", "CIPLA.NS", "TECHM.NS", "WIPRO.NS", "BRITANNIA.NS",
        "HEROMOTOCO.NS", "APOLLOHOSP.NS", "EICHERMOT.NS", "DIVISLAB.NS", "SBILIFE.NS", "BAJAJFINSV.NS",
        "TATACONSUM.NS", "NESTLEIND.NS", "INDUSINDBK.NS", "HDFCLIFE.NS", "BHEL.NS", "ZOMATO.NS", "DLF.NS",
        "HAL.NS", "BEL.NS", "VBL.NS", "TRENT.NS", "SIEMENS.NS", "ABB.NS", "JIOFIN.NS", "PFC.NS", "RECLTD.NS",
        "IRFC.NS", "RVNL.NS", "IRCON.NS", "RAILTEL.NS", "IRCTC.NS", "TITAGARH.NS", "JUPITERIN.NS",
        "MAZDOCK.NS", "COCHINSHIP.NS", "GRSE.NS", "BDL.NS", "ASTRAMICRO.NS", "SOLARINDS.NS",
        "VEDL.NS", "HINDZINC.NS", "JINDALSTEL.NS", "SAIL.NS", "NMDC.NS", "NATIONALUM.NS",
        "PIDILITIND.NS", "ASTRAL.NS", "SRF.NS", "PIIND.NS", "UPL.NS", "DEEPAKNTR.NS", "NAVINFLUOR.NS",
        "IGL.NS", "MGL.NS", "GAIL.NS", "PETRONET.NS", "OIL.NS", "IOC.NS", "HPCL.NS",
        "BANKBARODA.NS", "CANBK.NS", "PNB.NS", "UNIONBANK.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS", "INDHOTEL.NS",
        "CUMMINSIND.NS", "POLYCAB.NS", "OFSS.NS", "PERSISTENT.NS", "LTIM.NS", "LTTS.NS", "KPITTECH.NS",
        "COFORGE.NS", "MPHASIS.NS", "LUPIN.NS", "ALKEM.NS", "AUROPHARMA.NS", "TORNTPHARM.NS", "MANKIND.NS",
        "GLENMARK.NS", "ABBOTINDIA.NS", "BIOCON.NS", "SYNGENE.NS", "SANOFI.NS", "PFIZER.NS", "GMRINFRA.NS",
        "OBEROIRLTY.NS", "GODREJPROP.NS", "PRESTIGE.NS", "PHOENIXLTD.NS", "BRIGADE.NS", "SOBHA.NS",
        "MRF.NS", "BOSCHLTD.NS", "MOTHERSON.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "BHARATFORG.NS", "BALKRISIND.NS",
        "APOLLOTYRE.NS", "CEATLTD.NS", "ENDURANCE.NS", "SONACOMS.NS", "TIINDIA.NS", "UNO.NS",
        "HAVELLS.NS", "CROMPTON.NS", "VOLTAS.NS", "BLUESTARCO.NS", "WHIRLPOOL.NS", "DIXON.NS", "AMBER.NS",
        "PAGEIND.NS", "ABFRL.NS", "BATAINDIA.NS", "RELAXO.NS", "MANYAVAR.NS", "KALYANKJIL.NS", "TITAN.NS",
        "DABUR.NS", "MARICO.NS", "COLPAL.NS", "GODREJCP.NS", "BERGEPAINT.NS", "KANSAINER.NS", "UBL.NS",
        "MCDOWELL-N.NS", "RADICO.NS", "VBL.NS", "JUBLFOOD.NS", "DEVYANI.NS", "SAPPHIRE.NS", "WESTLIFE.NS",
        "PVRINOX.NS", "SUNTV.NS", "ZEEL.NS", "NAUKRI.NS", "POLICYBZR.NS", "PAYTM.NS", "NYKAA.NS", "DELHIVERY.NS",
        "MUTHOOTFIN.NS", "MANAPPURAM.NS", "CHOLAFIN.NS", "SHRIRAMFIN.NS", "BAJAJHLDNG.NS", "M&MFIN.NS",
        "LICI.NS", "GICRE.NS", "NIACL.NS", "ABCAPITAL.NS", "POONAWALLA.NS", "SUNDARMFIN.NS", "CREDITACC.NS",
        "ACC.NS", "AMBUJACEM.NS", "SHREECEM.NS", "DALBHARAT.NS", "JKCEMENT.NS", "RAMCOCEM.NS", "STARCEMENT.NS",
        "TATACHEM.NS", "COROMANDEL.NS", "FACT.NS", "CHAMBLFERT.NS", "GSFC.NS", "GNFC.NS", "RCF.NS",
        "IDEA.NS", "INDUSTOWER.NS", "HFCL.NS", "ITI.NS", "TEJASNET.NS", "TATACOMM.NS", "BHARTIARTL.NS",
        "ADANIPOWER.NS", "ADANIENSOL.NS", "ADANIGREEN.NS", "ATGL.NS", "AWL.NS", "ADANIENT.NS", "ADANIPORTS.NS",
        "SJVN.NS", "NHPC.NS", "SUZLON.NS", "INOXWIND.NS", "TORNTPOWER.NS", "CESC.NS", "JSL.NS", "JINDALSAW.NS",
        "WELCORP.NS", "APLAPOLLO.NS", "RATNAMANI.NS", "AIAENG.NS", "TIMKEN.NS", "SCHAEFFLER.NS", "SKFINDIA.NS",
        "CARBORUNIV.NS", "GRINDWELL.NS", "THERMAX.NS", "KEC.NS", "KALPATPOWR.NS", "TRITURBINE.NS", "ELGIEQUIP.NS",
        "KAJARIACER.NS", "CERA.NS", "CENTURYPLY.NS", "GREENPANEL.NS", "ASTRAL.NS", "FINCABLES.NS", "KEI.NS",
        "LALPATHLAB.NS", "METROPOLIS.NS", "MEDANTA.NS", "NH.NS", "FORTIS.NS", "MAXHEALTH.NS", "KIMS.NS",
        "RAINBOW.NS", "ASTERDM.NS", "POLYMED.NS", "GLAND.NS", "LAURUSLABS.NS", "GRANULES.NS", "JBCHEPHARM.NS",
        "ERIS.NS", "IPCALAB.NS", "AJANTPHARM.NS", "NATCOPHARM.NS", "PFIZER.NS", "SANOFI.NS", "GSK.NS",
        "FSL.NS", "ZENSARTECH.NS", "REDINGTON.NS", "CYIENT.NS", "BISOFT.NS", "SONATSOFTW.NS", "INTELLECT.NS",
        "TANLA.NS", "ROUTE.NS", "AFFLE.NS", "HAPPSTMNDS.NS", "DATAPATTNS.NS", "MTARTECH.NS", "PARAS.NS",
        "IEX.NS", "MCX.NS", "BSE.NS", "CDSL.NS", "CAMS.NS", "KFINTECH.NS", "ANGELONE.NS", "MOTILALOFS.NS",
        "ISEC.NS", "360ONE.NS", "NAM-INDIA.NS", "UTIAMC.NS", "HDFCAMC.NS", "BIRLAMONEY.NS", "GEOJIT.NS",
        "CRISIL.NS", "ICRA.NS", "CAREERP.NS", "TEAMLEASE.NS", "SIS.NS", "QUESS.NS", "BLS.NS", "ECLERX.NS",
        "JUSTDIAL.NS", "INDIAMART.NS", "EASEMYTRIP.NS", "YATRA.NS", "MAPMYINDIA.NS", "RATEGAIN.NS", "ZOMATO.NS",
        "SFL.NS", "RHIM.NS", "VRLLOG.NS", "TCIEXP.NS", "MAHLOG.NS", "ALLCARGO.NS", "GPPL.NS", "SCI.NS",
        "GESHIP.NS", "DREDGECORP.NS", "RITES.NS", "HUDCO.NS", "NBCC.NS", "NCC.NS", "PNCINFRA.NS", "KNRCON.NS",
        "GRINFRA.NS", "HGINFRA.NS", "ASHOKA.NS", "DILIPBUILD.NS", "IRB.NS", "MANINFRA.NS", "AHLUCONT.NS",
        "JKPAPER.NS", "WESTCOASTP.NS", "ANDHRAPAP.NS", "SESHAPAPER.NS", "CENTURYTEX.NS", "RAYMOND.NS", "TRIDENT.NS",
        "WELSPUNLIV.NS", "KPRMILL.NS", "GOKEX.NS", "LUXIND.NS", "RUPA.NS", "DOLLAR.NS", "TCNSBRANDS.NS",
        "GOCOLORS.NS", "VMART.NS", "SHOPPERS.NS", "ETHOSLTD.NS", "CAMPUS.NS", "METROBRAND.NS", "REDTAPE.NS",
        "BIKAJI.NS", "MRSBECTORS.NS", "AVANTIFEED.NS", "VENKEYS.NS", "HATSUN.NS", "DODLA.NS", "HERITGFOOD.NS",
        "VADILALIND.NS", "TASTYBITE.NS", "ZYDUSWELL.NS", "GILLETTE.NS", "PGHH.NS", "AKZOINDIA.NS", "INDIGOPNTS.NS",
        "SIRCA.NS", "SHALPAINTS.NS", "CASTROLIND.NS", "GULFOILLUB.NS", "TIDEWATER.NS", "BLAL.NS", "INDIGO.NS",
        "SPICEJET.NS", "JETAIRWAYS.NS", "EMAMILTD.NS", "JYOTHYLAB.NS", "BAJAJCON.NS", "HONAUT.NS", "3MINDIA.NS"
    ]

@st.cache_data(ttl=600) # 10 मिनट कैश ताकि बार बार लोड न हो
def get_stock_data(symbol):
    try:
        # डेटा डाउनलोड (3 महीने का)
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if len(df) < 30: return None
        
        # वैल्यू क्लीनिंग
        def get_val(series):
            return series.iloc[0] if isinstance(series, pd.Series) else series

        current_close = get_val(df['Close'].iloc[-1])
        past_data = df.iloc[:-1] # आज को छोड़कर
        
        box_high = get_val(past_data['High'].tail(20).max())
        box_low = get_val(past_data['Low'].tail(20).min())
        
        avg_vol = get_val(past_data['Volume'].tail(20).mean())
        current_vol = get_val(df['Volume'].iloc[-1])
        
        # वॉल्यूम चेक (लॉजिक है, पर डिस्प्ले नहीं करेंगे)
        rvol = current_vol / avg_vol if avg_vol > 0 else 0

        return {
            "symbol": symbol.replace(".NS", ""),
            "close": current_close,
            "box_high": box_high,
            "box_low": box_low,
            "rvol": rvol
        }
    except:
        return None

def main():
    st.title("⚡ Darvas Pro 500 Scanner")
    st.caption(f"Scanning {len(STOCKS)} High-Volume Stocks from Nifty 500")

    if st.button("🚀 Start Nifty 500 Scan", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        valid_data = []
        entry_names = []
        exit_names = []
        
        # स्कैनिंग लूप
        for i, stock in enumerate(STOCKS):
            status_text.text(f"Analyzing {i+1}/{len(STOCKS)}: {stock}...")
            data = get_stock_data(stock)
            progress_bar.progress((i + 1) / len(STOCKS))
            
            if data:
                cmp = data['close']
                entry = data['box_high']
                sl = data['box_low']
                rvol = data['rvol']
                
                # --- शर्तें (Conditions) ---
                is_above_box = cmp > entry
                volume_ok = rvol > 1.5
                
                if is_above_box: # अगर बॉक्स के ऊपर है
                    risk = entry - sl
                    target = entry + (risk * 2)
                    pct_change = ((cmp - entry) / entry) * 100
                    
                    status = ""
                    if cmp < sl:
                        status = "EXIT NOW"
                        exit_names.append(data['symbol'])
                    else:
                        status = "BUY / HOLD"
                        entry_names.append(data['symbol'])

                    # TradingView Link
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

        # --- 1. टिकर पट्टी (Ticker Tape) ---
        if entry_names:
            entry_str = "  &nbsp;&nbsp;&nbsp; • &nbsp;&nbsp;&nbsp;  ".join(entry_names)
            st.markdown(f"""
            <div class='ticker-wrap-green'>
                <marquee direction="left" scrollamount="8">
                    🚀 <b>ENTRY / HOLD SIGNALS:</b> {entry_str}
                </marquee>
            </div>
            """, unsafe_allow_html=True)
            
        if exit_names:
            exit_str = "  &nbsp;&nbsp;&nbsp; • &nbsp;&nbsp;&nbsp;  ".join(exit_names)
            st.markdown(f"""
            <div class='ticker-wrap-red'>
                <marquee direction="left" scrollamount="8">
                    🛑 <b>EXIT SIGNALS:</b> {exit_str}
                </marquee>
            </div>
            """, unsafe_allow_html=True)

        # --- 2. डेटा टेबल ---
        if valid_data:
            df_result = pd.DataFrame(valid_data)
            
            st.success(f"Scan Complete! Found {len(valid_data)} stocks.")
            
            # स्टाइलिंग (कलरफुल बैकग्राउंड)
            def color_status(val):
                if 'EXIT' in val:
                    return 'background-color: #ffcccc; color: red; font-weight: bold;'
                elif 'HOLD' in val or 'BUY' in val:
                    return 'background-color: #ccffcc; color: green; font-weight: bold;'
                return ''

            # कॉलम कॉन्फ़िगरेशन (दशमलव और लिंक)
            st.dataframe(
                df_result.style.map(color_status, subset=['Status']).format({
                    "CMP": "{:.2f}",
                    "Entry": "{:.2f}",
                    "Target": "{:.2f}",
                    "Stop Loss": "{:.2f}",
                    "% Gain": "{:.2f}%"
                }),
                column_config={
                    "Stock": st.column_config.TextColumn("Stock Name"),
                    "Chart": st.column_config.LinkColumn("Chart", display_text="Open View"),
                },
                use_container_width=True,
                height=600,
                hide_index=True  # S.No हटा दिया
            )
        else:
            st.warning("No stocks matching criteria right now.")

if __name__ == "__main__":
    main()
