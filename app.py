import streamlit as st
import pandas as pd
from collections import Counter
import altair as alt

# Load data (cached for performance)
@st.cache_data
def load_data():
    df = pd.read_csv('cancer_survivor_data.csv')

    # Fill NAs with empty strings for relevant columns
    for col in ['Conditions', 'Interventions', 'Primary Outcome Measures', 'Secondary Outcome Measures', 'Other Outcome Measures', 'Brief Summary']:
        if col in df.columns:
            df[col] = df[col].fillna('')

    # Split pipe '|' separated lists into Python lists
    if 'Conditions' in df.columns:
        df['Conditions'] = df['Conditions'].apply(lambda x: [i.strip() for i in x.split('|')] if x else [])
    if 'Interventions' in df.columns:
        df['Interventions'] = df['Interventions'].apply(lambda x: [i.strip() for i in x.split('|')] if x else [])

    return df

df = load_data()

st.title("Clinical Trials Explorer — Cancer Survivors Data")

# Sidebar filters
st.sidebar.header("Filter clinical trials")

# Unique sorted filter options for conditions (cancer types) and interventions (drugs)
all_conditions = sorted({c for sublist in df['Conditions'] for c in sublist}) if 'Conditions' in df.columns else []
all_interventions = sorted({i for sublist in df['Interventions'] for i in sublist}) if 'Interventions' in df.columns else []

selected_conditions = st.sidebar.multiselect("Select Cancer Type(s) / Conditions", all_conditions)
selected_interventions = st.sidebar.multiselect("Select Drugs / Interventions", all_interventions)

# Optional: keyword search in Outcome Measures or Brief Summary
keyword_search = st.sidebar.text_input("Search keyword (cancer type, drug, symptom, etc.)")

def filter_trials(df, conditions, interventions, keyword):
    filtered = df.copy()
    if conditions:
        filtered = filtered[filtered['Conditions'].apply(lambda cond_list: any(c in cond_list for c in conditions))]
    if interventions:
        filtered = filtered[filtered['Interventions'].apply(lambda int_list: any(i in int_list for i in interventions))]
    if keyword:
        keyword_lower = keyword.lower()
        # Search keyword in multiple text columns if exist
        text_cols = []
        for col in ['Primary Outcome Measures', 'Secondary Outcome Measures', 'Other Outcome Measures', 'Brief Summary']:
            if col in df.columns:
                text_cols.append(col)
        if text_cols:
            mask = False
            for col in text_cols:
                mask = mask | df[col].str.lower().str.contains(keyword_lower)
            filtered = filtered[mask]
        else:
            # Fallback: search in 'Study Title'
            filtered = filtered[filtered['Study Title'].str.lower().str.contains(keyword_lower)]
    return filtered

filtered_df = filter_trials(df, selected_conditions, selected_interventions, keyword_search)

st.write(f"### Found {len(filtered_df)} clinical trials matching your filters")

# Show selected columns in a table
display_cols = ['NCT Number', 'Study Title', 'Study Status', 'Conditions', 'Interventions']
# Add outcome columns if exist
for col in ['Primary Outcome Measures', 'Secondary Outcome Measures', 'Other Outcome Measures']:
    if col in filtered_df.columns:
        display_cols.append(col)
filtered_df_display = filtered_df[display_cols].reset_index(drop=True)

st.dataframe(filtered_df_display)

# Visualize top cancer types and drugs in filtered data
def plot_top_keywords(df, column, title, top_n=10):
    if column not in df.columns:
        return
    all_items = [item for sublist in df[column] for item in sublist]
    counter = Counter(all_items)
    top_items = counter.most_common(top_n)
    if not top_items:
        return
    df_plot = pd.DataFrame(top_items, columns=[column[:-1], 'Count'])
    chart = alt.Chart(df_plot).mark_bar().encode(
        x=alt.X('Count', title='Count'),
        y=alt.Y(f'{column[:-1]}', sort='-x', title=title),
        tooltip=['Count']
    ).properties(width=700, height=300)
    st.altair_chart(chart)

st.markdown("### Top Cancer Types in Results")
plot_top_keywords(filtered_df, 'Conditions', 'Cancer Type')

st.markdown("### Top Interventions (Drugs) in Results")
plot_top_keywords(filtered_df, 'Interventions', 'Intervention')

# BONUS: Show connection network between Conditions and Interventions
# (Very basic co-occurrence count)

def build_cooccurrence(df):
    from collections import defaultdict
    cooccur = defaultdict(Counter)
    for _, row in df.iterrows():
        conds = row['Conditions'] if 'Conditions' in row else []
        ints = row['Interventions'] if 'Interventions' in row else []
        for c in conds:
            for i in ints:
                cooccur[c][i] += 1
    return cooccur

def show_cooccurrence_table(cooccur):
    data = []
    for cond, ints_counter in cooccur.items():
        for intervention, count in ints_counter.items():
            data.append({'Condition': cond, 'Intervention': intervention, 'Count': count})
    if not data:
        st.write("No Condition-Intervention co-occurrence data to display.")
        return
    cooccur_df = pd.DataFrame(data).sort_values(by='Count', ascending=False)
    st.markdown("### Condition-Intervention Co-occurrence Table")
    st.dataframe(cooccur_df.head(50))

cooccurrence = build_cooccurrence(filtered_df)
show_cooccurrence_table(cooccurrence)
