import streamlit as st
import pdfplumber
import pandas as pd
from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("💰 AI Fintech Analyzer")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
search_name = st.text_input("Enter Name (optional)")

if uploaded_file:

    text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"

    st.success("PDF Loaded")

    # 🔥 STRONG PROMPT
    response = client.responses.create(
        model="gpt-4o-mini",
        input=f"""
You are expert in bank statements.

Extract ALL transactions STRICTLY.

Understand table format.

IMPORTANT RULES:
- If amount is in debit column → debit
- If amount is in credit column → credit
- NEVER put both 0
- NEVER miss credit
- Identify correctly

Return ONLY JSON:

[
  {{
    "date": "DD-MM-YYYY",
    "name": "clean name",
    "credit": number,
    "debit": number
  }}
]

TEXT:
{text}
"""
    )

    try:
        output = response.output_text.strip()

        start = output.find("[")
        end = output.rfind("]") + 1
        clean_json = output[start:end]

        data = json.loads(clean_json)

        df = pd.DataFrame(data)

        df["credit"] = pd.to_numeric(df["credit"], errors="coerce").fillna(0)
        df["debit"] = pd.to_numeric(df["debit"], errors="coerce").fillna(0)

        # ❗ REMOVE WRONG ROWS
        df = df[(df["credit"] != 0) | (df["debit"] != 0)]

        if search_name:
            df = df[df["name"].str.contains(search_name, case=False, na=False)]

        st.dataframe(df)

        st.write("Total Credit:", df["credit"].sum())
        st.write("Total Debit:", df["debit"].sum())

        df.to_excel("output.xlsx", index=False)

        with open("output.xlsx", "rb") as f:
            st.download_button("Download Excel", f, "transactions.xlsx")

    except Exception as e:
        st.error("Error")
        st.text(str(e))
