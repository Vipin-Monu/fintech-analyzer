import streamlit as st
import pdfplumber
import pandas as pd
import re

st.title("💰 Fintech Analyzer (FINAL FIX)")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
search_name = st.text_input("Search Name (optional)")

if uploaded_file:

    full_text = ""

    # 🔥 Step 1: पूरे PDF का text जोड़ो
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    # 🔥 Step 2: multi-line को single line में convert
    lines = full_text.split("\n")

    merged_lines = []
    temp = ""

    for line in lines:
        if re.match(r"\d{2}-\d{2}-\d{4}", line):
            if temp:
                merged_lines.append(temp)
            temp = line
        else:
            temp += " " + line

    if temp:
        merged_lines.append(temp)

    # 🔥 Step 3: parse सही तरीके से
    data = []
    prev_balance = None

    for line in merged_lines:

        amounts = re.findall(r"\d+\.\d+", line)

        if len(amounts) >= 2:
            try:
                date = re.search(r"\d{2}-\d{2}-\d{4}", line).group()

                amount = float(amounts[-2])
                balance = float(amounts[-1])

                # 🔥 name clean
                name = re.sub(r"\d{2}-\d{2}-\d{4}", "", line)
                name = re.sub(r"\d+\.\d+", "", name)
                name = re.sub(r"UPI/.*?/", "", name)
                name = re.sub(r"/.*", "", name)
                name = name.strip()

                debit = 0
                credit = 0

                if prev_balance is not None:
                    if balance > prev_balance:
                        credit = amount
                    else:
                        debit = amount

                prev_balance = balance

                data.append({
                    "Date": date,
                    "Name": name,
                    "Credit": credit,
                    "Debit": debit
                })

            except:
                continue

    df = pd.DataFrame(data)

    if search_name:
        df = df[df["Name"].str.contains(search_name, case=False, na=False)]

    st.dataframe(df)

    st.success(f"Total Credit: {df['Credit'].sum()}")
    st.error(f"Total Debit: {df['Debit'].sum()}")

    df.to_excel("transactions.xlsx", index=False)

    with open("transactions.xlsx", "rb") as f:
        st.download_button("Download Excel", f, "transactions.xlsx")
