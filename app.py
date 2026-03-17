import streamlit as st
import pdfplumber
import pandas as pd
import re

# 🔥 BANK DETECTION
def detect_bank(text):
    text = text.lower()

    if "axis bank" in text:
        return "AXIS"
    elif "state bank of india" in text:
        return "SBI"
    elif "hdfc bank" in text:
        return "HDFC"
    else:
        return "UNKNOWN"


# 🔥 AXIS PARSER
def parse_axis(text):

    lines = text.split("\n")

    data = []

    for line in lines:

        date_match = re.search(r"\d{2}-\d{2}-\d{4}", line)

        if not date_match:
            continue

        date = date_match.group()

        amounts = re.findall(r"\d+\.\d+", line)

        if len(amounts) < 2:
            continue

        amount = float(amounts[-2])

        if "cr" in line.lower():
            credit = amount
            debit = 0
        elif "dr" in line.lower():
            credit = 0
            debit = amount
        else:
            credit = 0
            debit = amount

        name = re.sub(r"\d{2}-\d{2}-\d{4}", "", line)
        name = re.sub(r"\d+\.\d+", "", name)
        name = re.sub(r"cr|dr", "", name, flags=re.IGNORECASE)
        name = re.sub(r"UPI/.*?/", "", name)
        name = re.sub(r"/.*", "", name)
        name = name.strip()

        data.append({
            "Date": date,
            "Name": name,
            "Credit": credit,
            "Debit": debit
        })

    return data
