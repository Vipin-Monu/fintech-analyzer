import streamlit as st
import pdfplumber
import pandas as pd
import re

st.title("Fintech Bank Statement Analyzer")

file = st.file_uploader("Upload Bank Statement PDF")

if file:
    lines = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines.extend(text.split("\n"))

    transactions = []

    for line in lines:
        match = re.search(r"(\d{2}-\d{2}-\d{4})\s+(.*)\s+([\d,]+\.\d{2})", line)

        if match:
            date = match.group(1)
            desc = match.group(2).strip()
            amount = float(match.group(3).replace(",", ""))

            # Debit / Credit logic
            if amount > 5000:
                txn_type = "Credit"
            else:
                txn_type = "Debit"

            # Category logic
            desc_lower = desc.lower()

            if "upi" in desc_lower:
                category = "UPI"
            elif "bank" in desc_lower:
                category = "Bank Transfer"
            elif "atm" in desc_lower:
                category = "ATM"
            elif "salary" in desc_lower:
                category = "Salary"
            elif "amazon" in desc_lower or "flipkart" in desc_lower:
                category = "Shopping"
            else:
                category = "Other"

            transactions.append([date, desc, amount, txn_type, category])

    # Create DataFrame
    df = pd.DataFrame(transactions, columns=["Date", "Description", "Amount", "Type", "Category"])

    st.dataframe(df)

    if not df.empty:
        total = df["Amount"].sum()
        credit = df[df["Type"] == "Credit"]["Amount"].sum()
        debit = df[df["Type"] == "Debit"]["Amount"].sum()

        st.write("### 💰 Total:", total)
        st.write("### 🟢 Credit:", credit)
        st.write("### 🔴 Debit:", debit)

        # Category-wise summary
        st.write("### 📊 Category Summary")
        category_summary = df.groupby("Category")["Amount"].sum()
        st.bar_chart(category_summary)
