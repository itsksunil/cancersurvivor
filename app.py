import streamlit as st
import pandas as pd
import altair as alt

@st.cache_data
def load_data():
    df = pd.read_csv('cancer_survivor_data.csv')
    df.fillna('', inplace=True)
    return df

df = load_data()

st.title("Cancer Clinical Trials Explorer - Connected Search")

# Helper to get unique keywords from pipe '|' separated fields
def get_unique_keywords(series):
    keywords = set()
    for val in series:
        if val:
            keywords.update([x.strip() for x in val.split('|')])
    return sorted(keywords)

# Extract keyword lists
conditions = get_unique_keywords(df['Conditions'])
interventions = get_unique_keywords(df['Interventions'])
phases = sorted(df['Phases'].unique())

# Filters UI
selected_condition = st.selectbox("Filter by Cancer Type:", ["All"] + conditions)
selected_intervention = st.selectbox("Filter by Intervention/Drug:", ["All"] + interventions)
selected_phase = st.selectbox("Filter by Phase:", ["All"] + [p for p in phases if p])

# Filter DataFrame based on selections
filtered_df = df.copy()
if selected_condition != "All":
    filtered_df = filtered_df[filtered_df['Conditions'].str.contains(selected_condition, case=False, na=False)]
if selected_intervention != "All":
    filtered_df = filtered_df[filtered_df['Interventions'].str.contains(selected_intervention, case=False, na=False)]
if selected_phase != "All":
    filtered_df = filtered_df[filtered_df['Phases'] == selected_phase]

st.markdown(f"### Showing {len(filtered_df)} studies after filtering")

# Show clickable keywords from filtered data — e.g., conditions again for exploration
explore_conditions = get_unique_keywords(filtered_df['Conditions'])
st.write("### Explore related Cancer Types")
for cond in explore_conditions:
    if st.button(cond):
        # When clicked, show trials for this condition
        subset = df[df['Conditions'].str.contains(cond, case=False, na=False)]
        st.write(f"Trials related to **{cond}** ({len(subset)})")
        st.dataframe(subset[['NCT Number', 'Study Title', 'Primary Outcome Measures']])

# Display filtered trial table
st.write("### Filtered Clinical Trials")
st.dataframe(filtered_df[['NCT Number', 'Study Title', 'Conditions', 'Interventions', 'Primary Outcome Measures', 'Secondary Outcome Measures']])

