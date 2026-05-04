import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Trading Journal", layout="wide")

DATA_FILE = "data.csv"

# Initialize file if not exists
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        "Trade#", "Date", "Time", "Account", "Asset", "Setup", "Strategy",
        "Entry", "SL", "TP", "Risk ($)", "Reward ($)", "RR",
        "Result", "P&L ($)", "Emotion", "Notes", "Lesson"
    ])
    df.to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)

st.title("📊 Trading Journal Dashboard")

# ==============================
# ➕ ADD TRADE
# ==============================
st.sidebar.header("Add New Trade")

with st.sidebar.form("trade_form"):
    trade_num = len(df) + 1
    date = st.date_input("Date")
    time = st.time_input("Time")
    account = st.selectbox("Account", ["A1", "A2", "A3", "A4"])
    asset = st.selectbox("Asset", ["Nasdaq Micro", "Oil Micro", "Gold Micro"])
    setup = st.text_input("Setup")
    strategy = st.text_input("Strategy")

    entry = st.number_input("Entry")
    sl = st.number_input("Stop Loss")
    tp = st.number_input("Take Profit")

    risk = abs(entry - sl)
    reward = abs(tp - entry)
    rr = round(reward / risk, 2) if risk != 0 else 0

    result = st.selectbox("Result", ["Win", "Loss", "BE"])
    pnl = st.number_input("P&L ($)")
    emotion = st.selectbox("Emotion", ["Calm", "FOMO", "Revenge", "Fear"])

    notes = st.text_area("Notes")
    lesson = st.text_area("Lesson")

    submit = st.form_submit_button("Add Trade")

    if submit:
        new_row = pd.DataFrame([{
            "Trade#": trade_num,
            "Date": date,
            "Time": time,
            "Account": account,
            "Asset": asset,
            "Setup": setup,
            "Strategy": strategy,
            "Entry": entry,
            "SL": sl,
            "TP": tp,
            "Risk ($)": risk,
            "Reward ($)": reward,
            "RR": rr,
            "Result": result,
            "P&L ($)": pnl,
            "Emotion": emotion,
            "Notes": notes,
            "Lesson": lesson
        }])

        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.success("Trade Added!")

# ==============================
# 📊 DASHBOARD METRICS
# ==============================

st.subheader("Performance Overview")

col1, col2, col3, col4 = st.columns(4)

total_trades = len(df)
wins = len(df[df["Result"] == "Win"])
losses = len(df[df["Result"] == "Loss"])
win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
net_profit = df["P&L ($)"].sum()

col1.metric("Total Trades", total_trades)
col2.metric("Win Rate %", f"{win_rate:.2f}")
col3.metric("Net Profit ($)", f"{net_profit:.2f}")
col4.metric("Wins / Losses", f"{wins} / {losses}")

# ==============================
# 📈 EQUITY CURVE
# ==============================

st.subheader("Equity Curve")

if total_trades > 0:
    df["Cumulative P&L"] = df["P&L ($)"].cumsum()
    st.line_chart(df["Cumulative P&L"])

# ==============================
# 📊 ANALYSIS
# ==============================

st.subheader("Performance by Asset")
st.bar_chart(df.groupby("Asset")["P&L ($)"].sum())

st.subheader("Performance by Account")
st.bar_chart(df.groupby("Account")["P&L ($)"].sum())

# ==============================
# 📋 DATA TABLE
# ==============================

st.subheader("Trade History")
st.dataframe(df, use_container_width=True)