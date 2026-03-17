import streamlit as st
import pandas as pd
import pdfplumber
import re

st.set_page_config(page_title="Fintech Analyzer", layout="wide")

st.title("💰 Universal Fintech Analyzer")

# Upload PDF
uploaded_file = st.file_uploader("Upload Bank Statement PDF", type=["pdf"])

# Name search
search_name = st.text_input("🔍 Enter Name")

# Name matching function (STRONG)
def match_name(line, search_name):
    line = line.lower()
    search_name = search_name.lower()

    parts = search_name.split()

    for part in parts:
        if part in line:
            return True

    return False


if uploaded_file:

    # Extract text from PDF
    all_text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"

    # Split lines
    lines = all_text.split("\n")

    # Merge broken lines (IMPORTANT FIX)
    cleaned_lines = []
    temp = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if re.match(r"\d{2}-\d{2}-\d{4}", line):
            if temp:
                cleaned_lines.append(temp)
            temp = line
        else:
            temp += " " + line

    if temp:
        cleaned_lines.append(temp)

    data = []

    for line in cleaned_lines:

        if search_name and match_name(line, search_name):

            # Extract date
            date_match = re.search(r"\d{2}-\d{2}-\d{4}", line)
            date = date_match.group() if date_match else ""

            # Extract amounts
            amounts = re.findall(r"\d+\.\d{2}", line)

            debit = 0
            credit = 0

            if len(amounts) >= 2:
                debit = float(amounts[0])
                credit = float(amounts[1])
            elif len(amounts) == 1:
                debit = float(amounts[0])

            data.append({
                "Date": date,
                "Name": search_name,
                "Credit": credit,
                "Debit": debit
            })

    if data:
        df = pd.DataFrame(data)

        st.subheader("📊 Transactions")
        st.dataframe(df, use_container_width=True)

        # Summary
        total_credit = df["Credit"].sum()
        total_debit = df["Debit"].sum()

        st.subheader("💰 Summary")
        st.write(f"🟢 Total Credit: {total_credit}")
        st.write(f"🔴 Total Debit: {total_debit}")
        st.write(f"📊 Net: {total_credit - total_debit}")

        # Excel download
        excel_file = "filtered_transactions.xlsx"
        df.to_excel(excel_file, index=False)

        with open(excel_file, "rb") as f:
            st.download_button(
                "⬇️ Download Excel",
                f,
                file_name=excel_file
            )

    else:
        st.warning("⚠️ No data found for this name")
