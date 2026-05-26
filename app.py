import streamlit as st
import pandas as pd
from analyzer import process_dataframe_mining, generate_wordcloud_obj
from pypdf import PdfReader
from scraper import scrape_text_from_url

st.set_page_config(page_title="Multi-Source Analyzer", layout="wide")
st.title("🌐 Multi-Source Text Data Mining Analyzer")

with st.sidebar:
    st.header("⚙️ Data Input Mode")
    mode = st.selectbox("Select Source", ["CSV File Upload (Recommended)", "PDF Document", "Custom Text", "Web URL"])
    
    df = None
    if mode == "CSV File Upload (Recommended)":
        f = st.file_uploader("Upload CSV (must have 'Abstract' column)", type=["csv"])
        if f: df = pd.read_csv(f)
    elif mode == "PDF Document":
        f = st.file_uploader("Upload PDF", type=["pdf"])
        if f:
            reader = PdfReader(f)
            text = "".join([p.extract_text() for p in reader.pages])
            df = pd.DataFrame({"Abstract": [text]})
    elif mode == "Custom Text":
        t = st.text_area("Paste text")
        if st.button("Process Text"): df = pd.DataFrame({"Abstract": [t]})
    elif mode == "Web URL":
        u = st.text_input("Enter URL")
        if st.button("Fetch URL"):
            text = scrape_text_from_url(u)
            if text: df = pd.DataFrame({"Abstract": [text]})

if df is not None and not df.empty:
    st.success("Data loaded successfully!")
    word_df, words = process_dataframe_mining(df)
    st.image(generate_wordcloud_obj(words).to_array())
    st.dataframe(df)
else:
    st.info("Please upload a file or enter data to begin.")