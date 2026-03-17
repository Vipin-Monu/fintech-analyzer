import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO

st.title("💰 Fintech Analyzer (Accurate Version)")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    lines = text.split("\n")
    data = []

    for line in lines:

        # Proper pattern: Date + Debit + Credit
        match = re.search(
            r"(\d{2}-\d{2}-\d{4}).*?(\d+\.\d{2})?\s*(\d+\.\d{2})?\s*(\d+\.\d{2})",
            line
        )

        if match:
            date = match.group(1)

            debit = match.group(2)
            credit = match.group(3)
            balance = match.group(4)

            # Extract clean name
            name = re.findall(r"/([A-Za-z ]+)", line)
            name = name[0] if name else "Unknown"

            if debit:
                data.append([date, name.strip(), float(debit), "Debit"])

            if credit:
                data.append([date, name.strip(), float(credit), "Credit"])

    df = pd.DataFrame(data, columns=["Date", "Name", "Amount", "Type"])

    search_name = st.text_input("🔍 Enter Name")

    if search_name:
        filtered_df = df[df["Name"].str.contains(search_name, case=False)]

        debit_df = filtered_df[filtered_df["Type"] == "Debit"]
        credit_df = filtered_df[filtered_df["Type"] == "Credit"]

        st.subheader("🔴 Debit")
        st.dataframe(debit_df)

        st.subheader("🟢 Credit")
        st.dataframe(credit_df)

        st.write("### 💰 Summary")
        st.write("Total Debit:", debit_df["Amount"].sum())
        st.write("Total Credit:", credit_df["Amount"].sum())
        st.write("Net:", credit_df["Amount"].sum() - debit_df["Amount"].sum())

        # Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            debit_df.to_excel(writer, sheet_name='Debit', index=False)
            credit_df.to_excel(writer, sheet_name='Credit', index=False)

        st.download_button(
            "📥 Download Excel",
            output.getvalue(),
            "transactions.xlsx"
        )
