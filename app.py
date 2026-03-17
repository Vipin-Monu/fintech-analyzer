import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

st.title("🚀 Fintech Bank Statement Analyzer (AI Pro)")

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

            # Credit / Debit
            if amount > 5000:
                txn_type = "Credit"
            else:
                txn_type = "Debit"

            # Category
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

    df = pd.DataFrame(transactions, columns=["Date", "Description", "Amount", "Type", "Category"])

    st.write("### 📋 Full Data")
    st.dataframe(df)

    # Summary
    if not df.empty:
        total = df["Amount"].sum()
        credit = df[df["Type"] == "Credit"]["Amount"].sum()
        debit = df[df["Type"] == "Debit"]["Amount"].sum()

        st.write("### 💰 Total:", total)
        st.write("### 🟢 Credit:", credit)
        st.write("### 🔴 Debit:", debit)

        st.write("### 📊 Category Chart")
        st.bar_chart(df.groupby("Category")["Amount"].sum())

    # 🔍 Search
    st.write("## 🔎 Search / Filter by Name")
    search = st.text_input("Enter Name (e.g. Vipin Kumar)")

    if search:
        filtered_df = df[df["Description"].str.contains(search, case=False, na=False)]

        st.write(f"### 📌 Data for: {search}")
        st.dataframe(filtered_df)

        if not filtered_df.empty:
            total_filtered = filtered_df["Amount"].sum()
            st.write("### 💰 Total for this:", total_filtered)

            # 🤖 AI Insight
            st.write("### 🤖 AI Insight")

            if total_filtered > 50000:
                st.success("High transaction detected 🚀")
            else:
                st.info("Normal transaction activity")

            # 📥 ADVANCED EXCEL REPORT
            output = io.BytesIO()

            with pd.ExcelWriter(output, engine='openpyxl') as writer:

                df.to_excel(writer, index=False, sheet_name="All Data")

                category_summary = df.groupby("Category")["Amount"].sum().reset_index()
                category_summary.to_excel(writer, index=False, sheet_name="Category Summary")

                filtered_df.to_excel(writer, index=False, sheet_name="Filtered Data")

            excel_data = output.getvalue()

            st.download_button(
                label="📥 Download Advanced Report",
                data=excel_data,
                file_name=f"{search}_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        else:
            st.warning("No data found ❌")
