import streamlit as st
import pandas as pd
from collections import Counter
import numpy as np

st.set_page_config(page_title="Adaptive Super-AI v2.0", layout="wide")
st.title("🧠 Adaptive Super-AI v2.0")

sample_text = """DS:23 FD:45 GD:67 GL:89 DB:12 SG:34
DS:34 FD:56 GD:78 GL:90 DB:23 SG:45
DS:12 FD:78 GD:34 GL:56 DB:89 SG:67
DS:56 FD:89 GD:23 GL:45 DB:67 SG:12"""

recent_failures = st.sidebar.text_area(
    "पिछले 4 दिन के actual results डालें (हर दिन नई लाइन में):",
    value=sample_text
)

uploaded_file = st.sidebar.file_uploader("Historical Data", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(".xlsx") else pd.read_csv(uploaded_file)
    st.write(df.head())
else:
    st.warning("Sidebar में historical data upload करें")
