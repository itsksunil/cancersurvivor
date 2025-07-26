import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import json

# ---------- Load & Cache Data ----------
@st.cache_data
def load_data():
    df = pd.read_csv('cancer_survivor_data.csv')
    df.fillna('', inplace=True)
    df['Completion Date'] = pd.to_datetime(df['Completion Date'], errors='coerce')
    return df

df = load_data()

st.title("🧪 Cancer Clinical Trials Explorer & Comparator")

# ---------- Utility to extract keywords ----------
def get_unique_keywords(series):
    keywords = set()
    for val in series:
        if val:
            keywords.update([x.strip() for x in val.split('|')])
    return sorted(keywords)

# ---------- Sidebar Filters ----------
st.sidebar.header("🔎 Filters")

conditions = get_unique_keywords(df['Conditions'])
interventions = get_unique_keywords(df['Interventions'])
phases = sorted([p for p in df['Phases'].unique() if p])

selected_condition = st.sidebar.selectbox("Filter by Cancer Type:", ["All"] + conditions)
selected_intervention = st.sidebar.selectbox("Filter by Intervention/Drug:", ["All"] + interventions)
selected_phase = st.sidebar.selectbox("Filter by Phase:", ["All"] + phases)

min_date = df['Completion Date'].min()
max_date = df['Completion Date'].max()
start_date, end_date = st.sidebar.date_input("Filter by Completion Date Range:", value=(min_date, max_date))

# ---------- Apply Filters ----------
filtered_df = df.copy()

if selected_condition != "All":
    filtered_df = filtered_df[filtered_df['Conditions'].str.contains(selected_condition, case=False, na=False)]
if selected_intervention != "All":
    filtered_df = filtered_df[filtered_df['Interventions'].str.contains(selected_intervention, case=False, na=False)]
if selected_phase != "All":
    filtered_df = filtered_df[filtered_df['Phases'] == selected_phase]
if start_date and end_date:
    filtered_df = filtered_df[
        (filtered_df['Completion Date'] >= pd.to_datetime(start_date)) &
        (filtered_df['Completion Date'] <= pd.to_datetime(end_date))
    ]

# ---------- Show Filtered Data ----------
st.markdown(f"### 🎯 Showing {len(filtered_df)} studies after applying filters")
st.dataframe(filtered_df[['NCT Number', 'Study Title', 'Conditions', 'Interventions',
                          'Phases', 'Enrollment', 'Completion Date']])

# ---------- Compare Trials for Multiple Cancer Types ----------
st.subheader("📈 Compare Clinical Trial Outcomes by Cancer Types")
compare_conditions = st.multiselect("Select Cancer Types to Compare:", conditions)

if compare_conditions:
    pattern = '|'.join(compare_conditions)
    compare_df = df[df['Conditions'].str.contains(pattern, case=False, na=False)]

    tabs = st.tabs(compare_conditions)

    for i, cancer_type in enumerate(compare_conditions):
        with tabs[i]:
            cancer_df = compare_df[compare_df['Conditions'].str.contains(cancer_type, case=False, na=False)]
            st.markdown(f"### {cancer_type} ({len(cancer_df)} trials)")
            st.dataframe(cancer_df[['NCT Number', 'Study Title', 'Phases', 'Enrollment', 'Completion Date',
                                    'Primary Outcome Measures', 'Secondary Outcome Measures', 'Other Outcome Measures']])

            # ---------- Outcome Pie Chart ----------
            st.markdown("#### 📊 Outcome Type Distribution")
            outcome_types = []
            for i, row in cancer_df.iterrows():
                if row['Primary Outcome Measures']: outcome_types.append("Primary")
                if row['Secondary Outcome Measures']: outcome_types.append("Secondary")
                if row['Other Outcome Measures']: outcome_types.append("Other")
            outcome_series = pd.Series(outcome_types)
            fig, ax = plt.subplots()
            outcome_series.value_counts().plot.pie(autopct='%1.1f%%', startangle=90, ax=ax)
            ax.set_ylabel('')
            st.pyplot(fig)

# ---------- Export Section ----------
st.markdown("---")
st.header("📤 Export Filtered Results")

export_df = filtered_df.copy()

# Export as Excel
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    export_df.to_excel(writer, index=False, sheet_name='Filtered_Trials')

st.download_button(
    label="📥 Download as Excel",
    data=excel_buffer.getvalue(),
    file_name="filtered_trials
