import streamlit as st
import pdfplumber
import pandas as pd
import re

# 🔥 BANK DETECTION
def detect_bank(text):
    text = text.lower()

    if "axis bank" in text:
        return "AXIS"
    elif "state bank of india" in text:
        return "SBI"
    elif "hdfc bank" in text:
        return "HDFC"
    else:
        return "UNKNOWN"


# 🔥 AXIS PARSER (FINAL STABLE)
def parse_axis(text):

    lines = text.split("\n")
    data = []

    for line in lines:

        # Date detect
        date_match = re.search(r"\d{2}-\d{2}-\d{4}", line)
        if not date_match:
            continue

        date = date_match.group()

        # Amounts extract
        amounts = re.findall(r"\d+\.\d+", line)
        if len(amounts) < 2:
            continue

        amount = float(amounts[-2])

        # Credit / Debit detect
        line_lower = line.lower()

        if "cr" in line_lower:
            credit = amount
            debit = 0
        elif "dr" in line_lower:
            credit = 0
            debit = amount
        else:
            # fallback
            credit = 0
            debit = amount

        # Name cleaning
        name = line

        name = re.sub(r"\d{2}-\d{2}-\d{4}", "", name)
        name = re.sub(r"\d+\.\d+", "", name)
        name = re.sub(r"cr|dr", "", name, flags=re.IGNORECASE)
        name = re.sub(r"UPI/.*?/", "", name)
        name = re.sub(r"/.*", "", name)
        name = name.strip()

        if len(name) < 3:
            continue

        data.append({
            "Date": date,
            "Name": name,
            "Credit": credit,
            "Debit": debit
        })

    return data


# 🔥 STREAMLIT APP
st.title("🚀 Fintech Analyzer (Pro Version)")

uploaded_file = st.file_uploader("Upload Bank Statement PDF", type=["pdf"])

search_name = st.text_input("Search Name (optional)")

if uploaded_file:

    full_text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"

    bank = detect_bank(full_text)
    st.success(f"Detected Bank: {bank}")

    if bank == "AXIS":
        data = parse_axis(full_text)
    else:
        st.error("Bank not supported yet")
        data = []

    df = pd.DataFrame(data)

    # 🔍 NAME FILTER (STRONG)
    if search_name:
        df = df[df["Name"].str.lower().str.contains(search_name.lower())]

    st.dataframe(df)

    # totals
    total_credit = df["Credit"].sum() if not df.empty else 0
    total_debit = df["Debit"].sum() if not df.empty else 0

    st.success(f"Total Credit: {total_credit}")
    st.error(f"Total Debit: {total_debit}")

    # Excel
    df.to_excel("transactions.xlsx", index=False)

    with open("transactions.xlsx", "rb") as f:
        st.download_button("Download Excel", f, "transactions.xlsx")
