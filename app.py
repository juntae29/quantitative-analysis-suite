import streamlit as st
import pandas as pd
from scraper import scrape_text_from_url
from analyzer import process_advanced_mining, generate_wordcloud_obj, map_taxonomy
from pypdf import PdfReader

st.set_page_config(layout="wide", page_title="Data Mining Analyzer")
st.title("Advanced Data Mining Analyzer")

# 1. Sidebar Configuration
with st.sidebar:
    st.header("1. Input Method")
    mode = st.radio("Select Source", ["CSV Upload", "PDF Document", "Custom Text Input", "Web URL"])
    st.divider()
    st.header("2. Taxonomy Settings")
    cat_name = st.text_input("Category Label", "Methodology")
    cat_words = st.text_input("Target Keywords (comma separated)", "regression, analysis, model")

# 2. Data Loading Logic
df = None
if mode == "CSV Upload":
    f = st.file_uploader("Upload CSV", type=["csv"])
    if f: df = pd.read_csv(f)
elif mode == "PDF Document":
    f = st.file_uploader("Upload PDF", type=["pdf"])
    if f:
        reader = PdfReader(f)
        text = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
        df = pd.DataFrame({"Content": [text]})
elif mode == "Custom Text Input":
    t = st.text_area("Paste Text Here", height=150)
    if st.button("Load Text"):
        if t: df = pd.DataFrame({"Content": [t]})
elif mode == "Web URL":
    u = st.text_input("URL")
    q = st.text_input("Query")
    if st.button("Fetch"):
        text = scrape_text_from_url(u, q)
        if text: df = pd.DataFrame({"Content": [text]})

# 3. Interactive Analysis Dashboard
if df is not None and not df.empty:
    selected_col = st.selectbox("Select Column to Analyze:", df.columns)
    
    # Trigger Analysis Automatically
    word_df, word_dict = process_advanced_mining(df, selected_col)
    
    # Create Tabs for Professional Layout
    tab1, tab2, tab3 = st.tabs(["Dashboard Visualization", "Taxonomy Mapping", "Raw Data Preview"])
    
    with tab1:
        st.subheader("Key Insight: TF-IDF Importance")
        col1, col2 = st.columns([1, 1])
        with col1: st.image(generate_wordcloud_obj(word_dict).to_array(), use_column_width=True)
        with col2: st.bar_chart(word_df.set_index("Word"))
        
    with tab2:
        st.subheader(f"Taxonomy Classification: {cat_name}")
        tax_list = [w.strip().lower() for w in cat_words.split(",")]
        mapping = map_taxonomy(word_dict.keys(), {cat_name: tax_list})
        st.info(f"Found {len(mapping[cat_name])} matches: {', '.join(mapping[cat_name])}")
        
    with tab3:
        st.dataframe(df, use_container_width=True)
else:
    st.info("Please load data via the sidebar to initiate analysis.")