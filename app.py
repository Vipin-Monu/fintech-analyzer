import streamlit as st
import pdfplumber
import pandas as pd
import re
import io
import pytesseract
from PIL import Image
import difflib
from openai import OpenAI

# 🔐 OpenAI setup
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(layout="wide")

st.title("🚀 Fintech AI Analyzer (FINAL PRO)")

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

            d = desc.lower()

            if "upi" in d:
                category = "UPI"
            elif "bank" in d:
                category = "Bank Transfer"
            elif "atm" in d:
                category = "ATM"
            elif "amazon" in d or "flipkart" in d:
                category = "Shopping"
            else:
                category = "Other"

            transactions.append([date, desc, amount, txn_type, category])

    df = pd.DataFrame(transactions, columns=["Date", "Description", "Amount", "Type", "Category"])

    st.subheader("📊 Full Data")
    st.dataframe(df)

    # 🔎 SMART SEARCH
    st.subheader("🔎 Search by Name")

    search = st.text_input("Enter Name")

    filtered_df = pd.DataFrame()

    if search:
        results = []

        for _, row in df.iterrows():
            desc = row["Description"]

            similarity = difflib.SequenceMatcher(None, search.lower(), desc.lower()).ratio()

            if similarity > 0.4 or search.lower() in desc.lower():
                results.append(row)

        filtered_df = pd.DataFrame(results)

        st.subheader(f"📌 Data for: {search}")
        st.dataframe(filtered_df)

    # 📥 DOWNLOAD FILTERED
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Filtered Data",
            data=csv,
            file_name=f"{search}_data.csv",
            mime="text/csv"
        )

    # 🤖 GPT AI CHATBOT
    st.subheader("🤖 Ask AI (GPT Powered)")

    question = st.text_input("Ask anything about your data")

    if question and not df.empty:

        data_text = df.to_string(index=False)

        prompt = f"""
You are a financial assistant.

Here is bank transaction data:
{data_text}

User question:
{question}

Answer clearly and shortly.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        st.write("🤖 AI:", response.choices[0].message.content)
