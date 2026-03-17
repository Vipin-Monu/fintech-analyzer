import streamlit as st
import pandas as pd
import pdfplumber
import re
from io import BytesIO

st.title("💰 Universal Fintech Analyzer")

uploaded_file = st.file_uploader("Upload Bank Statement PDF", type=["pdf"])


# 🔹 Extract name from line
def extract_name(text):
    # try common patterns
    match = re.search(r"/([A-Za-z ]{3,})", text)
    if match:
        return match.group(1).strip()

    words = re.findall(r"[A-Za-z]+", text)
    return " ".join(words[:3]) if words else "Unknown"


if uploaded_file:
    all_rows = []

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:

            # -----------------------
            # 🔹 METHOD 1: TABLE
            # -----------------------
            tables = page.extract_tables()

            if tables:
                for table in tables:
                    df = pd.DataFrame(table)

                    if len(df.columns) >= 5:
                        for row in df.values:
                            try:
                                date = str(row[0])

                                if re.search(r"\d{2}-\d{2}-\d{4}", date):

                                    particulars = str(row[2])

                                    debit = pd.to_numeric(row[3], errors="coerce")
                                    credit = pd.to_numeric(row[4], errors="coerce")

                                    name = extract_name(particulars)

                                    all_rows.append([
                                        date,
                                        name,
                                        credit if pd.notna(credit) else 0,
                                        debit if pd.notna(debit) else 0
                                    ])
                            except:
                                pass

            # -----------------------
            # 🔹 METHOD 2: TEXT (fallback)
            # -----------------------
            else:
                text = page.extract_text()
                if text:
                    lines = text.split("\n")

                    for line in lines:
                        if re.search(r"\d{2}-\d{2}-\d{4}", line):

                            nums = re.findall(r"\d+\.\d{2}", line)

                            if len(nums) >= 2:
                                amount = float(nums[-2])  # ignore balance

                                name = extract_name(line)
                                date = re.search(r"\d{2}-\d{2}-\d{4}", line).group()

                                # detect type
                                if "cr" in line.lower() or "deposit" in line.lower() or "imps" in line.lower():
                                    credit = amount
                                    debit = 0
                                else:
                                    debit = amount
                                    credit = 0

                                all_rows.append([date, name, credit, debit])

    if all_rows:
        df = pd.DataFrame(all_rows, columns=["Date", "Name", "Credit", "Debit"])

        # 🔍 Name filter
        search = st.text_input("🔍 Search Name")

        if search:
            df = df[df["Name"].str.contains(search, case=False, na=False)]

        st.subheader("📊 Transactions")
        st.dataframe(df)

        # 💰 Summary
        total_credit = df["Credit"].sum()
        total_debit = df["Debit"].sum()

        st.write("### 💰 Summary")
        st.write("🟢 Total Credit:", total_credit)
        st.write("🔴 Total Debit:", total_debit)
        st.write("📈 Net:", total_credit - total_debit)

        # 📥 Excel
        output = BytesIO()
        df.to_excel(output, index=False)

        st.download_button(
            "📥 Download Excel",
            output.getvalue(),
            "transactions.xlsx"
        )

    else:
        st.error("❌ No data detected")
