import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
from datetime import timedelta

# Page Config
st.set_page_config(page_title="Adaptive Super-AI v2.0", layout="wide")

st.title("🧠 Adaptive Super-AI v2.0: Learning from Failures")
st.write("यह मॉडल पिछले 4-7 दिनों की गलतियों से सीखकर आज की प्रेडिक्शन को एडजस्ट (Adjust) करेगा।")

# 1. Master Patterns
master_patterns = [0, -18, -16, -26, -32, -1, -4, -11, -15, -10, -51, -50, 15, 5, -5, -55, 1, 10, 11, 51, 55, -40]
shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

uploaded_file = st.sidebar.file_uploader("Upload Data File", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        # File Loading
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Date Processing
        if 'DATE' in df.columns:
            df['DATE'] = pd.to_datetime(df['DATE']).dt.date
            available_dates = df['DATE'].dropna().unique()
            selected_date = st.sidebar.selectbox("Base Date चुनें:", options=reversed(available_dates))
            base_idx = df[df['DATE'] == selected_date].index[0]
            tomorrow = selected_date + timedelta(days=1)
        else:
            st.error("फाइल में 'DATE' कॉलम होना ज़रूरी है।")
            st.stop()

        # Numeric Clean
        for s in shifts:
            if s in df.columns:
                df[s] = pd.to_numeric(df[s], errors='coerce')

        # --- STEP 1: ADAPTIVE LEARNING ENGINE ---
        # पिछले 7 दिनों में कौन से पैटर्न सबसे ज्यादा पास हुए?
        lookback = st.sidebar.slider("लर्निंग विंडो (पिछले कितने दिन देखें?)", 3, 10, 7)
        recent_hits = []
        
        for i in range(max(1, base_idx - lookback), base_idx + 1):
            prev_day = set(df.iloc[i-1][shifts].dropna().values)
            curr_day = set(df.iloc[i][shifts].dropna().values)
            # Check which master patterns worked in history
            for v in prev_day:
                for p in master_patterns:
                    if (v + p) % 100 in curr_day:
                        recent_hits.append(p)
        
        pattern_loyalty = Counter(recent_hits)

        # --- STEP 2: SCORING WITH ADAPTIVE WEIGHTS ---
        scores = np.zeros(100)
        today_nums = df.loc[base_idx, [s for s in shifts if s in df.columns]].dropna().to_dict()
        
        for val in today_nums.values():
            for p in master_patterns:
                target = int((val + p) % 100)
                # Base score 1 + Bonus based on recent performance
                bonus = pattern_loyalty.get(p, 0)
                scores[target] += (1 + bonus)

        # --- STEP 3: DISPLAY ADAPTIVE WINNERS ---
        st.info(f"📅 **विश्लेषण तिथि:** {selected_date} | 🎯 **कल की प्रेडिक्शन:** {tomorrow}")
        
        with st.expander("📊 Recent Pattern Performance (लर्निंग डेटा)"):
            perf_df = pd.DataFrame(pattern_loyalty.items(), columns=['Pattern', 'Recent Hits']).sort_values('Recent Hits', ascending=False)
            st.write("पिछले दिनों में इन पैटर्न्स ने सबसे अच्छा काम किया:")
            st.table(perf_df.head(5))

        col1, col2 = st.columns(2)
        
        with col1:
            st.header("✅ Adaptive Winners")
            winners = []
            for n in range(100):
                if scores[n] >= 3:
                    conf = min(99.0, (scores[n] / (len(today_nums) * 2)) * 100)
                    winners.append({"Number": n, "Power Score": round(scores[n], 1), "Confidence %": f"{conf:.1f}%"})
            
            if winners:
                w_df = pd.DataFrame(winners).sort_values("Power Score", ascending=False)
                st.table(w_df.head(12))
            else:
                st.write("आज के ट्रेंड में कोई बहुत मजबूत नंबर नहीं मिला।")

        with col2:
            st.header("❌ Adaptive Losers (Avoid)")
            # Those that failed to hit any active trend
            losers = [n for n in range(100) if scores[n] <= 1]
            st.error(f"इन {len(losers)} नंबरों के आने के चांस बहुत कम हैं:")
            st.write(sorted(losers))

        # --- STEP 4: SHIFT-WISE ADAPTIVE PICK ---
        st.divider()
        st.header("🎰 Shift-Wise Prediction (Adaptive)")
        valid_shifts = [s for s in shifts if s in df.columns]
        tabs = st.tabs(valid_shifts)
        
        for i, s_name in enumerate(valid_shifts):
            with tabs[i]:
                s_val = today_nums.get(s_name)
                if s_val is not None:
                    st.subheader(f"{s_name} (आज का नंबर: {int(s_val)})")
                    s_preds = []
                    for p in master_patterns:
                        num = int((s_val + p) % 100)
                        s_preds.append({
                            "Number": num,
                            "Reliability": pattern_loyalty.get(p, 0),
                            "Total Conf %": f"{min(99.0, (scores[num]/(len(today_nums)*2))*100):.1f}%"
                        })
                    # Sort by Reliability (how often this pattern hit recently)
                    st.table(pd.DataFrame(s_preds).sort_values("Reliability", ascending=False).drop_duplicates('Number').head(5))

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("शुरू करने के लिए अपनी एक्सेल/CSV फाइल अपलोड करें।")
                    
