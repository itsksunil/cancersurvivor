import streamlit as st
import pandas as pd
import altair as alt

# Optional for word cloud
try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

st.set_page_config(page_title="Cancer Clinical Trials Explorer", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('cancer_survivor_data.csv')
    df.fillna('', inplace=True)
    return df

df = load_data()

st.title("Cancer Clinical Trials Explorer")

# Prepare filter options
all_conditions = set()
for cond_list in df['Conditions']:
    if cond_list:
        all_conditions.update([c.strip() for c in cond_list.split('|')])
conditions = sorted(all_conditions)

statuses = sorted(set(df['Study Status']))

# Filters UI
col1, col2 = st.columns(2)

with col1:
    selected_condition = st.selectbox("Filter by Cancer Type (Condition):", options=["All"] + conditions)

with col2:
    selected_status = st.selectbox("Filter by Study Status:", options=["All"] + statuses)

# Apply filters
filtered_df = df.copy()
if selected_condition != "All":
    filtered_df = filtered_df[filtered_df['Conditions'].str.contains(selected_condition, case=False, na=False)]
if selected_status != "All":
    filtered_df = filtered_df[filtered_df['Study Status'] == selected_status]

st.markdown(f"### Showing {len(filtered_df)} studies")

# Show key columns in a table
cols_to_show = [
    'NCT Number', 'Study Title', 'Study Status', 'Conditions', 'Interventions',
    'Primary Outcome Measures', 'Secondary Outcome Measures', 'Other Outcome Measures',
    'Enrollment', 'Phases', 'Completion Date'
]

st.dataframe(filtered_df[cols_to_show].reset_index(drop=True))

# Bar chart: count of studies by Phase
phase_counts = filtered_df['Phases'].value_counts().reset_index()
phase_counts.columns = ['Phase', 'Count']

if not phase_counts.empty:
    chart = alt.Chart(phase_counts).mark_bar(color='teal').encode(
        x=alt.X('Phase', sort='-y'),
        y='Count'
    ).properties(
        title="Number of Studies by Phase",
        width=600,
        height=400
    )
    st.altair_chart(chart)

# Word Cloud of Outcome Measures
if WORDCLOUD_AVAILABLE:
    all_outcomes = " ".join(filtered_df['Primary Outcome Measures']) + " " + \
                   " ".join(filtered_df['Secondary Outcome Measures']) + " " + \
                   " ".join(filtered_df['Other Outcome Measures'])

    if all_outcomes.strip():
        wc = WordCloud(width=800, height=400, background_color='white').generate(all_outcomes)
        st.write("### Common Outcome Measure Terms")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
else:
    st.info("To see word clouds of outcome measures, install `wordcloud` and `matplotlib` libraries.")

