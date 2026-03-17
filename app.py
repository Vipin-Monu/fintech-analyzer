import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO

st.title("💰 Fintech Analyzer (Final Working)")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    lines = text.split("\n")
    data = []

    for line in lines:

        # check valid transaction line
        if re.search(r"\d{2}-\d{2}-\d{4}", line):

            parts = line.split()

            # find all numbers
            numbers = re.findall(r"\d+\.\d{2}", line)

            if len(numbers) >= 2:
                amount = float(numbers[-2])   # debit or credit
                balance = float(numbers[-1])  # last is always balance

                date = parts[0]

                # detect type
                if "sent" in line.lower() or "paid" in line.lower() or "upi" in line.lower():
                    txn_type = "Debit"
                else:
                    txn_type = "Credit"

                # extract name better
                name_match = re.search(r"/([A-Za-z ]+)", line)
                name = name_match.group(1).strip() if name_match else "Unknown"

                data.append([date, name, amount, txn_type])

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

        # Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            debit_df.to_excel(writer, sheet_name='Debit', index=False)
            credit_df.to_excel(writer, sheet_name='Credit', index=False)

        st.download_button("📥 Download Excel", output.getvalue(), "transactions.xlsx")
