import streamlit as st
import pandas as pd
import altair as alt

@st.cache_data
def load_data():
    df = pd.read_csv('cancer_survivor_data.csv')

    df['Conditions'] = df['Conditions'].fillna('')
    df['Interventions'] = df['Interventions'].fillna('')
    df['Study Status'] = df['Study Status'].fillna('Unknown')

    df['Conditions'] = df['Conditions'].apply(lambda x: [i.strip() for i in x.split('|')] if x else [])
    df['Interventions'] = df['Interventions'].apply(lambda x: [i.strip() for i in x.split('|')] if x else [])

    return df

df = load_data()

st.title("Clinical Trials Explorer")

st.sidebar.header("Filter Trials")

all_conditions = sorted({c for sublist in df['Conditions'] for c in sublist})
all_interventions = sorted({i for sublist in df['Interventions'] for i in sublist})
all_status = df['Study Status'].unique().tolist()

selected_conditions = st.sidebar.multiselect("Cancer Types / Conditions", all_conditions)
selected_interventions = st.sidebar.multiselect("Interventions (Drugs/Treatments)", all_interventions)
selected_status = st.sidebar.multiselect("Study Status", all_status)

def filter_trials(df, conditions, interventions, status):
    filtered = df.copy()
    if conditions:
        filtered = filtered[filtered['Conditions'].apply(lambda cond_list: any(c in cond_list for c in conditions))]
    if interventions:
        filtered = filtered[filtered['Interventions'].apply(lambda int_list: any(i in int_list for i in interventions))]
    if status:
        filtered = filtered[filtered['Study Status'].isin(status)]
    return filtered

filtered_df = filter_trials(df, selected_conditions, selected_interventions, selected_status)

st.write(f"### Showing {len(filtered_df)} trials matching your filters")

st.dataframe(filtered_df[['NCT Number', 'Study Title', 'Study Status', 'Conditions', 'Interventions']].reset_index(drop=True))

def plot_top_conditions(df, top_n=10):
    all_conds = [c for cond_list in df['Conditions'] for c in cond_list]
    cond_counts = pd.Series(all_conds).value_counts().reset_index()
    cond_counts.columns = ['Condition', 'Count']
    cond_counts = cond_counts.head(top_n)

    chart = alt.Chart(cond_counts).mark_bar().encode(
        x=alt.X('Condition', sort='-y'),
        y='Count',
        tooltip=['Condition', 'Count']
    ).properties(width=700, height=400)

    st.altair_chart(chart)

plot_top_conditions(filtered_df)

