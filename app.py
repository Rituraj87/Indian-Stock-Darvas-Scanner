import streamlit as st
import yfinance as yf
import pandas as pd

# --- पेज कॉन्फ़िगरेशन ---
st.set_page_config(page_title="Private Darvas Scanner", layout="wide", page_icon="🔒")

# --- 🔒 पासवर्ड सुरक्षा (PASSWORD PROTECTION) ---
# अपना पासवर्ड यहाँ बदलें (जैसे "Rituraj123")
MY_PASSWORD = "Rituraj87" 

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == MY_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # पासवर्ड को सेव न रखें
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # पहली बार रन होने पर पासवर्ड इनपुट दिखाएं
        st.text_input(
            "कृपया एक्सेस के लिए पासवर्ड डालें:", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # गलत पासवर्ड होने पर
        st.text_input(
            "गलत पासवर्ड। दोबारा कोशिश करें:", type="password", on_change=password_entered, key="password"
        )
        st.error("⛔ एक्सेस अस्वीकृत")
        return False
    else:
        # पासवर्ड सही है
        return True

if not check_password():
    st.stop()  # अगर पासवर्ड गलत है, तो यहीं रुक जाएं और आगे का कोड न दिखाएं

# ==============================================================================
# --- यहाँ से आपका असली ऐप शुरू होता है (Main App Logic) ---
# ==============================================================================

st.toast("Login Successful! Welcome back.", icon="✅")

# --- CSS स्टाइल ---
st.markdown("""
<style>
    .stDataFrame {font-size: 14px;}
    div[data-testid="stMetricValue"] {font-size: 20px;}
</style>
""", unsafe_allow_html=True)

# --- स्टॉक लिस्ट (आप इसे बढ़ा सकते हैं) ---
STOCKS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
    "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "LICI.NS", "HINDUNILVR.NS",
    "LT.NS", "BAJFINANCE.NS", "MARUTI.NS", "TATAMOTORS.NS", "SUNPHARMA.NS",
    "TITAN.NS", "ADANIENT.NS", "KOTAKBANK.NS", "AXISBANK.NS", "NTPC.NS",
    "ULTRACEMCO.NS", "POWERGRID.NS", "M&M.NS", "ONGC.NS", "WIPRO.NS",
    "ADANIPORTS.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "COALINDIA.NS", "HCLTECH.NS",
    "ASIANPAINT.NS", "SBILIFE.NS", "BAJAJFINSV.NS", "TECHM.NS", "BPCL.NS",
    "GRASIM.NS", "EICHERMOT.NS", "DRREDDY.NS", "CIPLA.NS", "INDUSINDBK.NS",
    "APOLLOHOSP.NS", "TATACONSUM.NS", "BRITANNIA.NS", "NESTLEIND.NS", "HEROMOTOCO.NS"]

@st.cache_data(ttl=300)
def get_stock_data(symbol):
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if len(df) < 30: return None
        
        # Data Cleaning
        def get_val(series):
            return series.iloc[0] if isinstance(series, pd.Series) else series

        current_close = get_val(df['Close'].iloc[-1])
        current_vol = get_val(df['Volume'].iloc[-1])
        
        past_data = df.iloc[:-2]
        box_high = get_val(past_data['High'].tail(20).max())
        box_low = get_val(past_data['Low'].tail(20).min())
        avg_vol = get_val(past_data['Volume'].tail(20).mean())

        return {
            "symbol": symbol,
            "close": current_close,
            "box_high": box_high,
            "box_low": box_low,
            "volume": current_vol,
            "avg_volume": avg_vol
        }
    except:
        return None

def main():
    st.title("🕵️ Private Darvas Scanner")
    st.write(f"Logged in securely. Ready to scan {len(STOCKS)} stocks.")

    if st.button("🚀 Scan Market Now"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        valid_stocks = []
        
        for i, stock in enumerate(STOCKS):
            status_text.text(f"Analyzing {stock}...")
            data = get_stock_data(stock)
            progress_bar.progress((i + 1) / len(STOCKS))
            
            if data:
                cmp = data['close']
                entry = data['box_high']
                sl = data['box_low']
                
                # Logic
                is_above_box = cmp > entry
                volume_ok = data['volume'] > (data['avg_volume'] * 1.5)
                
                if is_above_box:
                    risk = entry - sl
                    target = entry + (risk * 2)
                    pct_change = ((cmp - entry) / entry) * 100
                    
                    if cmp < sl:
                        status = "🔴 EXIT NOW"
                    else:
                        status = "🟢 HOLD (Riding)"

                    valid_stocks.append({
                        "Stock Name": stock.replace(".NS", ""),
                        "CMP (₹)": round(cmp, 2),
                        "Entry Price": round(entry, 2),
                        "Target Price": round(target, 2),
                        "Stop Loss": round(sl, 2),
                        "Status": status,
                        "% Gain": f"{pct_change:.2f}%"
                    })

        progress_bar.empty()
        status_text.empty()

        if valid_stocks:
            df_result = pd.DataFrame(valid_stocks)
            df_result.insert(0, 'S.No.', range(1, 1 + len(df_result)))
            st.success(f"Scan Complete! Found {len(valid_stocks)} opportunities.")
            
            st.dataframe(
                df_result.style.applymap(
                    lambda x: 'color: #ff4b4b; font-weight: bold' if 'EXIT' in str(x) else ('color: #2ecc71; font-weight: bold' if 'HOLD' in str(x) else ''),
                    subset=['Status']
                ),
                use_container_width=True,
                height=600
            )
        else:
            st.info("No active setups found right now.")

if __name__ == "__main__":
    main()
