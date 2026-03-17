import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO

st.title("💰 Fintech Analyzer")

uploaded_file = st.file_uploader("Upload Bank Statement (PDF)", type=["pdf"])

def clean_text(text):
    return text.lower().replace(" ", "").strip()

if uploaded_file:
    text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    lines = text.split("\n")
    data = []

    for line in lines:
        match = re.search(r"(\d{2}-\d{2}-\d{4}).*(\d+\.\d{2})", line)

        if match:
            date = match.group(1)
            amount = float(match.group(2))

            name = " ".join(re.findall(r"[A-Za-z]+", line))

            if "sent" in line.lower() or "paid" in line.lower():
                txn_type = "Debit"
            else:
                txn_type = "Credit"

            data.append([date, name, amount, txn_type])

    df = pd.DataFrame(data, columns=["Date", "Name", "Amount", "Type"])

    search_name = st.text_input("🔍 Enter Name")

    if search_name:
        search_clean = clean_text(search_name)
        df["clean_name"] = df["Name"].apply(clean_text)

        filtered_df = df[df["clean_name"].str.contains(search_clean)]

        # 🔴 Debit
        debit_df = filtered_df[filtered_df["Type"] == "Debit"]

        # 🟢 Credit
        credit_df = filtered_df[filtered_df["Type"] == "Credit"]

        # Show separately
        st.subheader("🔴 Debit Transactions")
        st.dataframe(debit_df)

        st.subheader("🟢 Credit Transactions")
        st.dataframe(credit_df)

        # Summary
        st.write("### 💰 Summary")
        st.write("Total Debit:", debit_df["Amount"].sum())
        st.write("Total Credit:", credit_df["Amount"].sum())

        # Excel download
        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            debit_df.to_excel(writer, sheet_name='Debit', index=False)
            credit_df.to_excel(writer, sheet_name='Credit', index=False)

        st.download_button(
            label="📥 Download Excel",
            data=output.getvalue(),
            file_name="transactions.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
