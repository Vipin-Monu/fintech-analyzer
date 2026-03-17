import streamlit as st
import pandas as pd
import pdfplumber
import re

st.set_page_config(page_title="Fintech Analyzer", layout="wide")

st.title("💰 Universal Fintech Analyzer")

uploaded_file = st.file_uploader("Upload Bank Statement PDF", type=["pdf"])
search_name = st.text_input("🔍 Enter Name")


def match_name(line, search_name):
    line = re.sub(r'[^a-zA-Z]', '', line).lower()
    search_name = re.sub(r'[^a-zA-Z]', '', search_name).lower()
    return search_name in line


# ✅ ONLY RUN WHEN BOTH EXIST
if uploaded_file and search_name:

    all_text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"

    lines = all_text.split("\n")

    cleaned_lines = []
    temp = ""

    for line in lines:
        line = line.strip()

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

        if match_name(line, search_name):

            date_match = re.search(r"\d{2}-\d{2}-\d{4}", line)
            date = date_match.group() if date_match else ""

            amounts = re.findall(r"\d+\.\d{2}", line)

            debit = 0
            credit = 0

            if len(amounts) >= 2:
                amt = float(amounts[-2])

                if "sent" in line.lower() or "paid" in line.lower() or "upi/p2a" in line.lower():
                    debit = amt
                else:
                    credit = amt

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

        total_credit = df["Credit"].sum()
        total_debit = df["Debit"].sum()

        st.subheader("💰 Summary")
        st.write(f"🟢 Total Credit: {total_credit}")
        st.write(f"🔴 Total Debit: {total_debit}")
        st.write(f"📊 Net: {total_credit - total_debit}")

        df.to_excel("filtered.xlsx", index=False)

        with open("filtered.xlsx", "rb") as f:
            st.download_button("⬇️ Download Excel", f, file_name="filtered.xlsx")

    else:
        st.warning("No data found for this name")

# 👇 THIS IS NEW
elif uploaded_file and not search_name:
    st.info("👉 Please enter a name to search transactions")
