import streamlit as st
import pandas as pd

# Load and cache the data
@st.cache_data
def load_data():
    df = pd.read_csv('cancer_survivor_data.csv')
    df.fillna('', inplace=True)
    df['Completion Date'] = pd.to_datetime(df['Completion Date'], errors='coerce')
    return df

df = load_data()

st.title("🧬 Cancer Clinical Trials Explorer and Outcome Comparator")

# Utility: extract unique keywords from pipe-separated fields
def get_unique_keywords(series):
    keywords = set()
    for val in series:
        if val:
            keywords.update([x.strip() for x in val.split('|')])
    return sorted(keywords)

# Prepare filter values
conditions = get_unique_keywords(df['Conditions'])
interventions = get_unique_keywords(df['Interventions'])
phases = sorted([p for p in df['Phases'].unique() if p])

# Sidebar filters
st.sidebar.header("🔍 Filter Trials")

selected_condition = st.sidebar.selectbox("Cancer Type", ["All"] + conditions)
selected_intervention = st.sidebar.selectbox("Intervention/Drug", ["All"] + interventions)
selected_phase = st.sidebar.selectbox("Phase", ["All"] + phases)

# 📅 Date Range filter
min_date = df['Completion Date'].min()
max_date = df['Completion Date'].max()
start_date, end_date = st.sidebar.date_input(
    "Completion Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)

# Apply filters
filtered_df = df.copy()

if selected_condition != "All":
    filtered_df = filtered_df[filtered_df['Conditions'].str.contains(selected_condition, case=False, na=False)]
if selected_intervention != "All":
    filtered_df = filtered_df[filtered_df['Interventions'].str.contains(selected_intervention, case=False, na=False)]
if selected_phase != "All":
    filtered_df = filtered_df[filtered_df['Phases'] == selected_phase]

# Filter by date range
filtered_df = filtered_df[
    (filtered_df['Completion Date'] >= pd.to_datetime(start_date)) &
    (filtered_df['Completion Date'] <= pd.to_datetime(end_date))
]

st.markdown(f"### 🎯 {len(filtered_df)} trials found")

# Main table showing key trial data
st.dataframe(filtered_df[[
    'NCT Number', 'Study Title', 'Conditions', 'Interventions', 
    'Phases', 'Enrollment', 'Completion Date'
]])

st.markdown("---")

# 🔗 Explore related cancer types dropdown
st.subheader("🔎 Explore Related Cancer Types")
explore_conditions = get_unique_keywords(filtered_df['Conditions'])
explore_cond = st.selectbox("Explore Cancer Type Trials:", options=["Select"] + explore_conditions)

if explore_cond != "Select":
    subset = df[df['Conditions'].str.contains(explore_cond, case=False, na=False)]
    st.markdown(f"### Trials related to **{explore_cond}** ({len(subset)})")
    st.dataframe(subset[[
        'NCT Number', 'Study Title', 'Primary Outcome Measures',
        'Secondary Outcome Measures', 'Other Outcome Measures'
    ]])

st.markdown("---")

# 📊 Compare trials for a selected cancer type
st.subheader("📈 Compare Clinical Trial Outcomes by Cancer Type")

selected_compare = st.selectbox("Select Cancer Type to Compare Trials:", ["Select"] + conditions)

if selected_compare != "Select":
    compare_df = df[df['Conditions'].str.contains(selected_compare, case=False, na=False)]
    st.markdown(f"### Comparing outcomes for **{selected_compare}** ({len(compare_df)} trials)")

    st.dataframe(compare_df[[
        'NCT Number', 'Study Title', 'Phases', 'Enrollment', 'Completion Date',
        'Primary Outcome Measures', 'Secondary Outcome Measures', 'Other Outcome Measures'
    ]].reset_index(drop=True))
