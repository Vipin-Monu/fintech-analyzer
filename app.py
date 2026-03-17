import streamlit as st
import pdfplumber
import pandas as pd
import re
import pytesseract
from PIL import Image
import difflib

st.set_page_config(layout="wide")

st.title("🚀 Fintech Analyzer (SMART VERSION)")

# 📂 Upload
file = st.file_uploader("Upload Bank Statement (PDF/Image)")

# 📄 Extract text
def extract_text(file):
    text_data = ""

    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_data += text + "\n"
    else:
        image = Image.open(file)
        text_data = pytesseract.image_to_string(image)

    return text_data


if file:
    full_text = extract_text(file)
    lines = full_text.split("\n")

    transactions = []

    for i, line in enumerate(lines):
        match = re.search(r"(\d{2}-\d{2}-\d{4}).*?([\d,]+\.\d{2})", line)

        if match:
            date = match.group(1)
            amount = float(match.group(2).replace(",", ""))

            desc_parts = []
            for j in range(max(0, i-2), min(len(lines), i+3)):
                desc_parts.append(lines[j])

            desc = " ".join(desc_parts)
            desc = re.sub(r"\s+", " ", desc)

            txn_type = "Credit" if amount > 5000 else "Debit"

            transactions.append([date, desc, amount, txn_type])

    df = pd.DataFrame(transactions, columns=["Date", "Description", "Amount", "Type"])

    st.subheader("📊 Full Data")
    st.dataframe(df)

    # 🔎 SEARCH SECTION
    st.subheader("🔎 Search by Name")

    search = st.text_input("Enter Name")

    if search:
        results = []

        for _, row in df.iterrows():
            desc = row["Description"]

            similarity = difflib.SequenceMatcher(None, search.lower(), desc.lower()).ratio()

            if similarity > 0.4 or search.lower() in desc.lower():
                results.append(row)

        filtered_df = pd.DataFrame(results)

        if not filtered_df.empty:
            st.subheader(f"📌 Results for: {search}")

            # 💳 CREDIT / DEBIT अलग
            credit_df = filtered_df[filtered_df["Type"] == "Credit"]
            debit_df = filtered_df[filtered_df["Type"] == "Debit"]

            col1, col2 = st.columns(2)

            with col1:
                st.success("💰 Credit Transactions")
                st.dataframe(credit_df)
                st.write("Total Credit:", credit_df["Amount"].sum())

            with col2:
                st.error("💸 Debit Transactions")
                st.dataframe(debit_df)
                st.write("Total Debit:", debit_df["Amount"].sum())

            # 📥 Download
            csv = filtered_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Download This Data",
                data=csv,
                file_name=f"{search}_transactions.csv",
                mime="text/csv"
            )

        else:
            st.warning("No matching data found")

    # 📊 OVERALL SUMMARY
    st.subheader("📊 Overall Summary")

    total_credit = df[df["Type"] == "Credit"]["Amount"].sum()
    total_debit = df[df["Type"] == "Debit"]["Amount"].sum()

    st.write("💰 Total Credit:", total_credit)
    st.write("💸 Total Debit:", total_debit)
