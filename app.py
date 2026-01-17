import streamlit as st
import yfinance as yf
import pandas as pd

# --- पेज सेटिंग ---
st.set_page_config(page_title="Darvas Pro Scanner (Nifty 500)", layout="wide", page_icon="📈")

# --- पासवर्ड सुरक्षा (वही पुराना पासवर्ड) ---
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

# --- NIFTY 500 के टॉप 100 एक्टिव स्टॉक्स (ताकि स्कैन फास्ट हो) ---
# अगर आप पूरे 500 चाहते हैं, तो इस लिस्ट को अपडेट कर सकते हैं
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
    "IDFCFIRSTB.NS", "ASTRAL.NS", "TATACOMM.NS", "PHOENIXLTD.NS", "MPHASIS.NS"
]

@st.cache_data(ttl=300)
def get_stock_data(symbol):
    try:
        # डेटा डाउनलोड करें
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if len(df) < 30: return None
        
        # वैल्यू निकालना
        def get_val(series):
            return series.iloc[0] if isinstance(series, pd.Series) else series

        current_close = get_val(df['Close'].iloc[-1])
        
        # पिछले दिन का डेटा (बॉक्स के लिए)
        past_data = df.iloc[:-1] # आज को छोड़कर
        
        box_high = get_val(past_data['High'].tail(20).max())
        box_low = get_val(past_data['Low'].tail(20).min())
        
        # वॉल्यूम लॉजिक
        avg_vol = get_val(past_data['Volume'].tail(20).mean())
        current_vol = get_val(df['Volume'].iloc[-1])
        
        # Relative Volume (RVol) - आज वॉल्यूम कितना गुना है
        rvol = current_vol / avg_vol if avg_vol > 0 else 0

        return {
            "symbol": symbol.replace(".NS", ""),
            "close": current_close,
            "box_high": box_high,
            "box_low": box_low,
            "volume": current_vol,
            "avg_volume": avg_vol,
            "rvol": rvol
        }
    except:
        return None

def main():
    st.title("🚀 Darvas Pro Scanner (Advanced)")
    st.caption("Scanning Top 100 High-Liquidity Stocks from Nifty 500")

    if st.button("Start Scan", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        valid_stocks = []
        
        # टेबल के लिए खाली जगह
        table_placeholder = st.empty()
        
        for i, stock in enumerate(STOCKS):
            status_text.text(f"Scanning {i+1}/{len(STOCKS)}: {stock}...")
            data = get_stock_data(stock)
            progress_bar.progress((i + 1) / len(STOCKS))
            
            if data:
                cmp = data['close']
                entry = data['box_high']
                sl = data['box_low']
                rvol = data['rvol']
                
                # --- शर्तें ---
                is_above_box = cmp > entry
                volume_ok = rvol > 1.5 # 1.5 गुना ज्यादा वॉल्यूम
                
                if is_above_box:
                    risk = entry - sl
                    target = entry + (risk * 2)
                    pct_change = ((cmp - entry) / entry) * 100
                    
                    if cmp < sl:
                        status = "EXIT"
                    else:
                        status = "HOLD"

                    # TradingView Link बनाना
                    tv_link = f"https://in.tradingview.com/chart/?symbol=NSE:{data['symbol']}"

                    valid_stocks.append({
                        "Stock": data['symbol'],
                        "Chart": tv_link, # लिंक कॉलम
                        "CMP": cmp,
                        "Entry": entry,
                        "Target": target,
                        "Stop Loss": sl,
                        "RVol (x)": rvol, # वॉल्यूम गुना
                        "% Gain": pct_change / 100, # प्रतिशत (Decimal format के लिए)
                        "Status": status
                    })

        progress_bar.empty()
        status_text.empty()

        if valid_stocks:
            df_result = pd.DataFrame(valid_stocks)
            
            st.success(f"Scan Complete! Found {len(valid_stocks)} stocks.")
            
            # --- ADVANCED COLUMN CONFIGURATION ---
            # यहाँ हम दशमलव (Decimals) और लिंक्स को कंट्रोल करेंगे
            st.dataframe(
                df_result,
                column_config={
                    "Stock": st.column_config.TextColumn("Stock Name", help="Name of the company"),
                    
                    "Chart": st.column_config.LinkColumn(
                        "Chart 🔗", 
                        help="Click to open TradingView", 
                        display_text="Open View"
                    ),
                    
                    "CMP": st.column_config.NumberColumn(
                        "CMP (₹)", format="%.2f"  # सिर्फ 2 दशमलव
                    ),
                    "Entry": st.column_config.NumberColumn(
                        "Entry Price (₹)", format="%.2f"
                    ),
                    "Target": st.column_config.NumberColumn(
                        "Target (₹)", format="%.2f"
                    ),
                    "Stop Loss": st.column_config.NumberColumn(
                        "Stop Loss (₹)", format="%.2f"
                    ),
                    "RVol (x)": st.column_config.NumberColumn(
                        "Vol Surge", format="%.1fx" # जैसे 2.5x
                    ),
                    "% Gain": st.column_config.NumberColumn(
                        "% Gain", format="%.2f%%" # प्रतिशत फॉर्मेट
                    ),
                    "Status": st.column_config.TextColumn(
                        "Action",
                    ),
                },
                use_container_width=True,
                height=600,
                hide_index=True # S.No. (Index) को छुपाने के लिए
            )
        else:
            st.warning("No stocks found matching criteria.")

if __name__ == "__main__":
    main()
