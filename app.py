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

# ---------- Compare Trials for Mult
