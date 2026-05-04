import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Trading Journal Pro", layout="wide")

# ==============================
# 🎨 CUSTOM DARK THEME (TradeZella Inspired)
# ==============================
st.markdown("""
<style>
body {background-color: #0e1117;}
.stApp {background-color: #0e1117; color: #e6edf3;}
h1, h2, h3 {color: #58a6ff;}
div[data-testid="metric-container"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

DATA_FILE = "data.csv"

CONTRACT_VALUES = {
    "MNQ": 2, "NQ": 20, "ES": 50, "MES": 5,
    "USOIL": 100, "CL": 1000, "MCL": 100,
    "XAUUSD": 100, "GC": 100
}

ASSETS = list(CONTRACT_VALUES.keys())

# ==============================
# LOAD / SAVE
# ==============================
def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "Trade#", "Date", "Time", "Asset", "Direction", "Lots",
            "Entry", "SL", "TP",
            "Risk ($)", "Reward ($)", "RR",
            "Result", "P&L ($)",
            "Setup", "Strategy", "Emotion", "Notes"
        ])
        df.to_csv(DATA_FILE, index=False)
        return df
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# ==============================
# TITLE
# ==============================
st.title("📊 Trading Journal Pro")

# ==============================
# RESET
# ==============================
if st.button("➕ New Trade"):
    st.session_state.clear()
    st.rerun()

# ==============================
# FORM
# ==============================
with st.form("trade_form"):
    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("Date")
        time = st.text_input("Time (09:30 AM)")
        asset = st.selectbox("Asset", [""] + ASSETS)
        direction = st.selectbox("Direction", ["", "Long", "Short"])
        lots = st.number_input("Lot/s", min_value=0.0)

        entry = st.number_input("Entry")
        sl = st.number_input("Stop Loss")
        tp = st.number_input("Take Profit")

    with col2:
        result = st.selectbox("Result", ["", "Win", "Loss", "Break Even"])
        setup = st.text_input("Setup (Playbook)")
        strategy = st.text_input("Strategy")
        emotion = st.selectbox("Emotion", ["", "Calm", "FOMO", "Revenge", "Fear"])
        notes = st.text_area("Notes")

    submit = st.form_submit_button("Submit Trade")

    if submit:
        errors = []

        if not time: errors.append("Time required")
        if not asset: errors.append("Asset required")
        if not direction: errors.append("Direction required")
        if lots <= 0: errors.append("Lot size required")
        if entry == 0: errors.append("Entry required")
        if sl == 0: errors.append("SL required")
        if tp == 0: errors.append("TP required")
        if not result: errors.append("Result required")

        if errors:
            for e in errors:
                st.error(e)
        else:
            point = CONTRACT_VALUES.get(asset, 1)

            if result == "Win":
                pnl = (tp - entry) * point * lots if direction == "Long" else (entry - tp) * point * lots
            elif result == "Loss":
                pnl = (sl - entry) * point * lots if direction == "Long" else (entry - sl) * point * lots
            else:
                pnl = 0

            risk = abs(entry - sl)
            reward = abs(tp - entry)
            rr = round(reward / risk, 2) if risk else 0

            new_row = pd.DataFrame([{
                "Trade#": len(df) + 1,
                "Date": date,
                "Time": time,
                "Asset": asset,
                "Direction": direction,
                "Lots": lots,
                "Entry": entry,
                "SL": sl,
                "TP": tp,
                "Risk ($)": risk,
                "Reward ($)": reward,
                "RR": rr,
                "Result": result,
                "P&L ($)": pnl,
                "Setup": setup,
                "Strategy": strategy,
                "Emotion": emotion,
                "Notes": notes
            }])

            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)

            st.success("Trade Added")
            st.rerun()

# ==============================
# 📊 DASHBOARD
# ==============================
st.subheader("📊 Performance Dashboard")

if not df.empty:
    df["P&L ($)"] = pd.to_numeric(df["P&L ($)"], errors="coerce").fillna(0)

    total = len(df)
    wins = df[df["Result"] == "Win"]
    losses = df[df["Result"] == "Loss"]

    win_rate = len(wins) / total * 100
    profit = df["P&L ($)"].sum()

    avg_win = wins["P&L ($)"].mean() if not wins.empty else 0
    avg_loss = losses["P&L ($)"].mean() if not losses.empty else 0

    profit_factor = abs(wins["P&L ($)"].sum() / losses["P&L ($)"].sum()) if not losses.empty else 0

    expectancy = (win_rate/100 * avg_win) + ((1 - win_rate/100) * avg_loss)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Trades", total)
    col2.metric("Win Rate", f"{win_rate:.1f}%")
    col3.metric("Net Profit", f"${profit:.2f}")
    col4.metric("Profit Factor", f"{profit_factor:.2f}")
    col5.metric("Expectancy", f"${expectancy:.2f}")

    # Equity Curve
    st.subheader("📈 Equity Curve")
    df["Equity"] = df["P&L ($)"].cumsum()
    st.line_chart(df["Equity"])

    # Drawdown
    df["Peak"] = df["Equity"].cummax()
    df["Drawdown"] = df["Equity"] - df["Peak"]
    st.subheader("📉 Drawdown")
    st.line_chart(df["Drawdown"])

    # Playbook (Setup Performance)
    st.subheader("🧠 Setup Performance")
    st.bar_chart(df.groupby("Setup")["P&L ($)"].sum())

    # Emotion Analysis
    st.subheader("🧠 Emotion Impact")
    st.bar_chart(df.groupby("Emotion")["P&L ($)"].sum())

    # Asset Performance
    st.subheader("📊 Asset Performance")
    st.bar_chart(df.groupby("Asset")["P&L ($)"].sum())

    # Table
    st.subheader("📋 Trade History")
    st.dataframe(df, use_container_width=True)

else:
    st.info("No trades yet")
