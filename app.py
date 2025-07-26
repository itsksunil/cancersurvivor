import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import openai

openai.api_key = "YOUR_OPENAI_API_KEY"

@st.cache_data
def load_data():
    df = pd.read_csv('cancer_survivor_data.csv')
    df.fillna('', inplace=True)
    # Combine relevant text fields for semantic search
    df['combined_text'] = df['Study Title'] + " " + df['Brief Summary'] + " " + df['Primary Outcome Measures'] + " " + df['Interventions']
    return df

@st.cache_data
def build_faiss_index(texts):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts, show_progress_bar=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index, embeddings, model

def semantic_search(query, index, embeddings, model, df, top_k=5):
    query_vec = model.encode([query])
    D, I = index.search(query_vec, top_k)
    return df.iloc[I[0]]

def query_llm(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300,
        temperature=0.7
    )
    return response.choices[0].text.strip()

df = load_data()
index, embeddings, model = build_faiss_index(df['combined_text'].tolist())

st.title("Clinical Trials Semantic Search + LLM Query")

query = st.text_input("Enter your research question:")

if query:
    st.write("Searching relevant clinical trials...")
    results = semantic_search(query, index, embeddings, model, df)
    st.write("Top relevant trials:")

    for i, row in results.iterrows():
        st.markdown(f"**{row['NCT Number']} - {row['Study Title']}**")
        st.write(f"Summary: {row['Brief Summary']}")
        st.write(f"Interventions: {row['Interventions']}")
        st.write("---")

    # Construct prompt for LLM using top trials summaries
    context = "\n\n".join(results['Brief Summary'].tolist())
    prompt = f"Based on the following clinical trial summaries, answer the question:\n{query}\n\nContext:\n{context}\n\nAnswer:"

    answer = query_llm(prompt)
    st.markdown("### LLM Answer:")
    st.write(answer)

