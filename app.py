import streamlit as st
import pdfplumber
import pandas as pd
import re

st.title("⚡ Fintech Analyzer (Fast & Accurate)")

uploaded_file = st.file_uploader("Upload Bank Statement PDF", type=["pdf"])
search_name = st.text_input("Search Name (optional)")

if uploaded_file:

    data = []
    prev_balance = None

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if not text:
                continue

            lines = text.split("\n")

            for line in lines:

                # match date + numbers
                if re.search(r"\d{2}-\d{2}-\d{4}", line):

                    amounts = re.findall(r"\d+\.\d+", line)

                    if len(amounts) >= 2:
                        try:
                            date = re.search(r"\d{2}-\d{2}-\d{4}", line).group()
                            amount = float(amounts[-2])
                            balance = float(amounts[-1])

                            # clean name
                            name = line
                            name = re.sub(r"\d{2}-\d{2}-\d{4}", "", name)
                            name = re.sub(r"\d+\.\d+", "", name)
                            name = re.sub(r"UPI/.*?/", "", name)
                            name = re.sub(r"/.*", "", name)
                            name = name.strip()

                            debit = 0
                            credit = 0

                            # 🔥 balance logic (core)
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

    # search filter
    if search_name:
        df = df[df["Name"].str.contains(search_name, case=False, na=False)]

    st.dataframe(df, use_container_width=True)

    total_credit = df["Credit"].sum()
    total_debit = df["Debit"].sum()

    st.success(f"Total Credit: {total_credit}")
    st.error(f"Total Debit: {total_debit}")

    # download excel
    df.to_excel("transactions.xlsx", index=False)

    with open("transactions.xlsx", "rb") as f:
        st.download_button("📥 Download Excel", f, "transactions.xlsx")
