import streamlit as st
import pdfplumber
import pandas as pd
import re
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("💰 Smart Fintech Analyzer")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
search_name = st.text_input("Enter Name (optional)")

if uploaded_file:

    data = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()

            if table:
                for row in table:
                    try:
                        date = row[0]
                        particulars = row[2]
                        debit = row[3]
                        credit = row[4]

                        if date and particulars:

                            debit = float(debit) if debit else 0
                            credit = float(credit) if credit else 0

                            data.append({
                                "Date": date,
                                "Name": particulars,
                                "Credit": credit,
                                "Debit": debit
                            })

                    except:
                        continue

    df = pd.DataFrame(data)

    # 🔥 AI for name cleaning only
    def clean_name(name):
        try:
            response = client.responses.create(
                model="gpt-4o-mini",
                input=f"Extract only person or merchant name from: {name}"
            )
            return response.output_text.strip()
        except:
            return name

    df["Name"] = df["Name"].apply(clean_name)

    if search_name:
        df = df[df["Name"].str.contains(search_name, case=False, na=False)]

    st.dataframe(df)

    st.write("Total Credit:", df["Credit"].sum())
    st.write("Total Debit:", df["Debit"].sum())

    df.to_excel("output.xlsx", index=False)

    with open("output.xlsx", "rb") as f:
        st.download_button("Download Excel", f, "transactions.xlsx")
