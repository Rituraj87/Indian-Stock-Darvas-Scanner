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

# --- NIFTY 500 (Top 200 Most Active Stocks for Speed & Stability) ---
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
    "COFORGE.NS", "TDPOWERSYS.NS", "BHEL.NS", "SAIL.NS", "NATIONALUM.NS",
    "BANDHANBNK.NS", "GUJGASLTD.NS", "IPCALAB.NS", "LAURUSLABS.NS", "TATAELXSI.NS",
    "DEEPAKNTR.NS", "CROMPTON.NS", "ACC.NS", "DALBHARAT.NS", "JSL.NS",
    "APLAPOLLO.NS", "MFSL.NS", "PETRONET.NS", "ZEEL.NS", "RAMCOCEM.NS",
    "NAVINFLUOR.NS", "SYNGENE.NS", "TRIDENT.NS", "SOLARINDS.NS", "RVNL.NS",
    "IRFC.NS", "MAZDOCK.NS", "COCHINSHIP.NS", "FACT.NS", "SUZLON.NS",
    "IDEA.NS", "YESBANK.NS", "IDBI.NS", "UNIONBANK.NS", "IOB.NS",
    "UCOBANK.NS", "CENTRALBK.NS", "MAHABANK.NS", "BANKINDIA.NS", "BSE.NS",
    "CDSL.NS", "ANGELONE.NS", "MCX.NS", "MOTILALOFS.NS", "IEX.NS"
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
