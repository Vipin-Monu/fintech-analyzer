import streamlit as st
import pdfplumber
import pandas as pd
from openai import OpenAI
import os
import json

# ---------- API ----------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Fintech Analyzer", layout="wide")

st.title("💰 Universal AI Fintech Analyzer")

# ---------- Upload ----------
uploaded_file = st.file_uploader("Upload Bank Statement PDF", type=["pdf"])

search_name = st.text_input("🔍 Enter Name (optional)")

# ---------- PROCESS ----------
if uploaded_file:

    full_text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    st.success("✅ PDF Loaded Successfully")

    # ---------- AI CALL ----------
    with st.spinner("🤖 AI is analyzing transactions..."):

        response = client.responses.create(
            model="gpt-4o-mini",
            input=f"""
You are a bank statement analyzer.

Extract ALL transactions from this text.

Return ONLY JSON array like:
[
  {{"date": "DD-MM-YYYY", "name": "string", "credit": number, "debit": number}}
]

Rules:
- Detect ALL banks (SBI, HDFC, Axis, ICICI, etc.)
- If money added → credit
- If money deducted → debit
- Name must be clean (person or entity)
- No explanation, only JSON

TEXT:
{full_text}
"""
        )

    try:
        output = response.output_text.strip()

        # Fix if extra text comes
        start = output.find("[")
        end = output.rfind("]") + 1
        clean_json = output[start:end]

        data = json.loads(clean_json)

        df = pd.DataFrame(data)

        # ---------- CLEAN ----------
        df["credit"] = pd.to_numeric(df["credit"], errors="coerce").fillna(0)
        df["debit"] = pd.to_numeric(df["debit"], errors="coerce").fillna(0)

        # ---------- FILTER ----------
        if search_name:
            df = df[df["name"].str.contains(search_name, case=False, na=False)]

        # ---------- DISPLAY ----------
        st.subheader("📊 Transactions")
        st.dataframe(df, use_container_width=True)

        # ---------- SUMMARY ----------
        total_credit = df["credit"].sum()
        total_debit = df["debit"].sum()

        st.subheader("💰 Summary")
        st.success(f"Total Credit: {total_credit}")
        st.error(f"Total Debit: {total_debit}")
        st.info(f"Net: {total_credit - total_debit}")

        # ---------- DOWNLOAD ----------
        df.to_excel("output.xlsx", index=False)

        with open("output.xlsx", "rb") as f:
            st.download_button("⬇️ Download Excel", f, "transactions.xlsx")

    except Exception as e:
        st.error("❌ Error parsing AI response")
        st.text(str(e))
