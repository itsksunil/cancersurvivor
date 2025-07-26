import streamlit as st
import pandas as pd

# ---------- Load & Cache Data ----------
@st.cache_data
def load_data():
    df = pd.read_csv('cancer_survivor_data.csv')
    df.fillna('', inplace=True)
    # Convert 'Completion Date' to datetime
    df['Completion Date'] = pd.to_datetime(df['Completion Date'], errors='coerce')
    return df

df = load_data()

st.title("🧪 Cancer Clinical Trials Explorer & Outcome Comparator")

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

# Sidebar filters
selected_condition = st.sidebar.selectbox("Filter by Cancer Type:", ["All"] + conditions)
selected_intervention = st.sidebar.selectbox("Filter by Intervention/Drug:", ["All"] + interventions)
selected_phase = st.sidebar.selectbox("Filter by Phase:", ["All"] + phases)

# Date range filter
min_date = df['Completion Date'].min()
max_date = df['Completion Date'].max()

start_date, end_date = st.sidebar.date_input(
    "Filter by Completion Date Range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

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

# ---------- Filtered Results ----------
st.markdown(f"### 🎯 Showing {len(filtered_df)} studies after applying filters")

st.dataframe(filtered_df[['NCT Number', 'Study Title', 'Conditions', 'Interventions',
                          'Phases', 'Enrollment', 'Completion Date']])

st.markdown("---")

# ---------- Explore Related Cancer Types ----------
explore_conditions = get_unique_keywords(filtered_df['Conditions'])
explore_cond = st.selectbox("Explore Related Cancer Types:", options=["Select"] + explore_conditions)

if explore_cond != "Select":
    subset = df[df['Conditions'].str.contains(explore_cond, case=False, na=False)]
    st.markdown(f"### 📚 Trials related to **{explore_cond}** ({len(subset)})")
    st.dataframe(subset[['NCT Number', 'Study Title',
                         'Primary Outcome Measures',
                         'Secondary Outcome Measures',
                         'Other Outcome Measures']])

st.markdown("---")

# ---------- Outcome Comparison ----------
st.header("📊 Compare Clinical Trial Outcomes by Cancer Type")

selected_cancer_compare = st.selectbox("Select Cancer Type to Compare Trials:", ["Select"] + conditions)

if selected_cancer_compare != "Select":
    related_trials = df[df['Conditions'].str.contains(selected_cancer_compare, case=False, na=False)]
    st.markdown(f"### 🧬 Found {len(related_trials)} trials for **{selected_cancer_compare}**")

    comparison_columns = [
        'NCT Number', 'Study Title', 'Phases', 'Enrollment', 'Completion Date',
        'Primary Outcome Measures', 'Secondary Outcome Measures', 'Other Outcome Measures'
    ]
    st.dataframe(related_trials[comparison_columns].reset_index(drop=True))
