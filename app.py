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

    data = []

    for line in lines:

        amounts = re.findall(r"\d[\d,]*\.\d{2}", line)

        if len(amounts) >= 2:

            data.append({
                "transaction": line,
                "amount": float(amounts[-2].replace(",",""))
            })

    df = pd.DataFrame(data)

    st.dataframe(df)

    if not df.empty:

        st.write("Total:", df["amount"].sum())