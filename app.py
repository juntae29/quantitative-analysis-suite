import streamlit as st
import pandas as pd
from scraper import scrape_text_from_url
from analyzer import process_dataframe_mining, generate_wordcloud_obj, map_taxonomy
from pypdf import PdfReader

st.set_page_config(page_title="Data Mining Analyzer", layout="wide")
st.title("Data Mining Analyzer")

with st.sidebar:
    st.header("Configuration")
    mode = st.selectbox("Select Mode", ["CSV Upload", "PDF Document", "Custom Text Input", "Web URL"])
    st.divider()
    st.header("Taxonomy Settings")
    cat_name = st.text_input("Category Name", "Methodology")
    cat_words = st.text_input("Keywords (comma separated)", "regression, analysis, model")

df = None
if mode == "CSV Upload":
    f = st.file_uploader("Upload CSV", type=["csv"])
    if f: df = pd.read_csv(f)
elif mode == "PDF Document":
    f = st.file_uploader("Upload PDF", type=["pdf"])
    if f:
        reader = PdfReader(f)
        text = "".join([p.extract_text() for p in reader.pages])
        df = pd.DataFrame({"Abstract": [text]})
elif mode == "Custom Text Input":
    t = st.text_area("Input Text", height=200)
    if st.button("Analyze"):
        if t: df = pd.DataFrame({"Abstract": [t]})
elif mode == "Web URL":
    u = st.text_input("URL")
    q = st.text_input("Query")
    if st.button("Fetch"):
        text = scrape_text_from_url(u, q)
        if text: df = pd.DataFrame({"Abstract": [text]})
        else: st.error("Fetch failed.")

if df is not None and not df.empty:
    selected_col = st.selectbox("Select Column to Analyze", df.columns)
    if st.button("Start Analysis"):
        st.success("Ready")
        word_df, words = process_dataframe_mining(df, selected_col)
        
        col1, col2 = st.columns(2)
        with col1: st.image(generate_wordcloud_obj(words).to_array())
        with col2: st.bar_chart(word_df.set_index("Word"))
        
        st.divider()
        st.header("Taxonomy Mapping Result")
        tax_dict = {cat_name: [w.strip().lower() for w in cat_words.split(",")]}
        mapping = map_taxonomy(words.keys(), tax_dict)
        st.write(f"Words mapped to **{cat_name}**:", mapping[cat_name])
        st.dataframe(df)