import streamlit as st
import pdfplumber
import pandas as pd
import re

st.title("🔥 Fintech Analyzer")

uploaded_file = st.file_uploader("Upload Bank Statement PDF")

def parse_axis(text):
    lines = text.split("\n")
    data = []

    for line in lines:
        date_match = re.search(r"\d{2}-\d{2}-\d{4}", line)

        if not date_match:
            continue

        date = date_match.group()

        amounts = re.findall(r"\d+\.?\d*", line)

        if len(amounts) < 2:
            continue

        debit = float(amounts[-2])
        credit = float(amounts[-1])

        # name निकालने की कोशिश
        name = line.replace(date, "").strip()

        data.append({
            "Date": date,
            "Name": name[:30],
            "Credit": credit,
            "Debit": debit
        })

    return data


if uploaded_file:
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"

        st.success("PDF Loaded ✅")

        data = parse_axis(full_text)

        if len(data) == 0:
            st.warning("No transactions found ⚠️")
        else:
            df = pd.DataFrame(data)

            st.dataframe(df)

            st.success(f"Total Credit: {df['Credit'].sum()}")
            st.error(f"Total Debit: {df['Debit'].sum()}")

            df.to_excel("transactions.xlsx", index=False)

            with open("transactions.xlsx", "rb") as f:
                st.download_button("Download Excel", f, "transactions.xlsx")

    except Exception as e:
        st.error(f"ERROR: {e}")
