import streamlit as st
import pdfplumber
import pandas as pd
import re

st.title("Fintech Bank Statement Analyzer")

file = st.file_uploader("Upload Bank Statement PDF")

if file:

    transactions = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if text:
                lines = text.split("\n")

                for line in lines:

                    match = re.search(
                        r'(\d{2}[-/]\d{2}[-/]\d{4})\s+(.*?)\s+([\d,]+\.\d{2})',
                        line
                    )

                    if match:
                        date = match.group(1)
                        desc = match.group(2)
                        amount = float(match.group(3).replace(",", ""))

                        transactions.append([date, desc, amount])

    df = pd.DataFrame(transactions, columns=["Date", "Description", "Amount"])

    st.dataframe(df)

    if not df.empty:
        st.write("### Total Amount:", df["Amount"].sum())
