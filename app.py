import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Trading Journal", layout="wide")

DATA_FILE = "data.csv"
ACCOUNTS_FILE = "accounts.csv"

# ==============================
# CONTRACT VALUES (PER POINT)
# ==============================
CONTRACT_VALUES = {
    "MNQ": 2,
    "NQ": 20,
    "US100": 1,
    "ES": 50,
    "MES": 5,
    "USOIL": 100,
    "CL": 1000,
    "MCL": 100,
    "XAUUSD": 100,
    "GC": 100
}

ASSETS = list(CONTRACT_VALUES.keys())

# ==============================
# LOAD FUNCTIONS
# ==============================
def load_csv(file, columns):
    if not os.path.exists(file):
        df = pd.DataFrame(columns=columns)
        df.to_csv(file, index=False)
        return df
    try:
        df = pd.read_csv(file)
        if df.empty:
            return pd.DataFrame(columns=columns)
        return df
    except:
        return pd.DataFrame(columns=columns)

def save_csv(df, file):
    df.to_csv(file, index=False)

# ==============================
# LOAD DATA
# ==============================
trade_columns = [
    "Trade#", "Date", "Time", "Account", "Asset", "Direction", "Lots",
    "Entry", "SL", "TP",
    "Risk ($)", "Reward ($)", "RR",
    "Result", "P&L ($)",
    "Setup", "Strategy", "Emotion", "Notes", "Lesson"
]

df = load_csv(DATA_FILE, trade_columns)
accounts_df = load_csv(ACCOUNTS_FILE, ["Account"])
accounts = accounts_df["Account"].dropna().tolist()

# ==============================
# TITLE
# ==============================
st.title("📊 Trading Journal")

# ==============================
# ACCOUNT MANAGEMENT (INLINE)
# ==============================
st.subheader("🏦 Account")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    account = st.selectbox("Select Account", [""] + accounts, key="account_select")

with col2:
    new_account = st.text_input("Add Account", key="add_account")

    if st.button("Add"):
        if new_account.strip():
            if new_account not in accounts:
                accounts_df = pd.concat(
                    [accounts_df, pd.DataFrame({"Account": [new_account.strip()]})],
                    ignore_index=True
                )
                save_csv(accounts_df, ACCOUNTS_FILE)
                st.success("Added")
                st.rerun()
            else:
                st.warning("Exists")

with col3:
    if account:
        if st.button("Delete"):
            accounts_df = accounts_df[accounts_df["Account"] != account]
            save_csv(accounts_df, ACCOUNTS_FILE)
            st.warning("Deleted")
            st.rerun()

# Rename inline
if account:
    new_name = st.text_input("Rename Account")

    if st.button("Rename"):
        if new_name.strip() and new_name not in accounts:
            accounts_df.loc[
                accounts_df["Account"] == account, "Account"
            ] = new_name.strip()
            save_csv(accounts_df, ACCOUNTS_FILE)
            st.success("Renamed")
            st.rerun()

# ==============================
# RESET BUTTON
# ==============================
if st.button("➕ Add New Trade"):
    st.session_state.clear()
    st.rerun()

# ==============================
# TRADE FORM
# ==============================
with st.form("trade_form"):

    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("Date")
        time = st.text_input("Time (e.g. 09:30 AM)")

        asset = st.selectbox("Asset", [""] + ASSETS)
        direction = st.selectbox("Direction", ["", "Long", "Short"])
        lots = st.number_input("Lot/s", min_value=0.0)

        entry = st.number_input("Entry")
        sl = st.number_input("Stop Loss")
        tp = st.number_input("Take Profit")

    with col2:
        setup = st.text_input("Setup")
        strategy = st.text_input("Strategy")
        emotion = st.selectbox("Emotion", ["", "Calm", "FOMO", "Revenge", "Fear"])

        notes = st.text_area("Notes")
        lesson = st.text_area("Lesson")

    submit = st.form_submit_button("Submit Trade")

    # ==============================
    # VALIDATION
    # ==============================
    if submit:
        errors = []

        if not time.strip():
            errors.append("Time required")
        if account == "":
            errors.append("Account required")
        if asset == "":
            errors.append("Asset required")
        if direction == "":
            errors.append("Direction required")
        if lots <= 0:
            errors.append("Lot size required")
        if entry == 0:
            errors.append("Entry required")
        if sl == 0:
            errors.append("SL required")
        if tp == 0:
            errors.append("TP required")

        if errors:
            for e in errors:
                st.error(e)
        else:
            try:
                point_value = CONTRACT_VALUES.get(asset, 1)

                # ==============================
                # RESULT LOGIC
                # ==============================
                if direction == "Long":
                    if tp > entry:
                        result = "Win"
                    elif sl < entry:
                        result = "Loss"
                    else:
                        result = "BE"

                    pnl = (tp - entry) * point_value * lots if result == "Win" else \
                          (sl - entry) * point_value * lots if result == "Loss" else 0

                else:  # Short
                    if tp < entry:
                        result = "Win"
                    elif sl > entry:
                        result = "Loss"
                    else:
                        result = "BE"

                    pnl = (entry - tp) * point_value * lots if result == "Win" else \
                          (entry - sl) * point_value * lots if result == "Loss" else 0

                risk = abs(entry - sl)
                reward = abs(tp - entry)
                rr = round(reward / risk, 2) if risk != 0 else 0

                trade_num = len(df) + 1

                new_row = pd.DataFrame([{
                    "Trade#": trade_num,
                    "Date": date,
                    "Time": time,
                    "Account": account,
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
                    "Notes": notes,
                    "Lesson": lesson
                }])

                df = pd.concat([df, new_row], ignore_index=True)
                save_csv(df, DATA_FILE)

                st.success(f"✅ Trade Saved ({result})")
                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

# ==============================
# DASHBOARD
# ==============================
st.subheader("📊 Dashboard")

if not df.empty:
    df["P&L ($)"] = pd.to_numeric(df["P&L ($)"], errors="coerce").fillna(0)

    total = len(df)
    wins = len(df[df["Result"] == "Win"])
    losses = len(df[df["Result"] == "Loss"])
    win_rate = (wins / total * 100) if total else 0
    profit = df["P&L ($)"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Trades", total)
    col2.metric("Win Rate", f"{win_rate:.2f}%")
    col3.metric("Net Profit", f"${profit:.2f}")
    col4.metric("Wins/Losses", f"{wins}/{losses}")

    st.subheader("Equity Curve")
    df["Cumulative"] = df["P&L ($)"].cumsum()
    st.line_chart(df["Cumulative"])

    st.subheader("By Asset")
    st.bar_chart(df.groupby("Asset")["P&L ($)"].sum())

    st.subheader("By Account")
    st.bar_chart(df.groupby("Account")["P&L ($)"].sum())

    st.subheader("Trade History")
    st.dataframe(df, use_container_width=True)

else:
    st.info("No trades yet")
