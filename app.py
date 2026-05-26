import streamlit as st
import pandas as pd
from scraper import scrape_text_from_url
from analyzer import process_dataframe_mining, generate_wordcloud_obj
from pypdf import PdfReader

st.set_page_config(page_title="Data Analyzer", layout="wide")
st.title("Data Mining Analyzer")

with st.sidebar:
    st.header("Configuration")
    mode = st.selectbox("Select Mode", ["CSV Upload", "PDF Document", "Custom Text Input", "Web URL"])
    
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
        u = st.text_input("Enter URL")
        if st.button("Fetch"):
            text = scrape_text_from_url(u)
            if text: df = pd.DataFrame({"Abstract": [text]})
            else: st.error("Fetch failed.")

if df is not None and not df.empty:
    st.success("Ready")
    word_df, words = process_dataframe_mining(df)
    col1, col2 = st.columns(2)
    with col1: st.image(generate_wordcloud_obj(words).to_array())
    with col2: st.bar_chart(word_df.set_index("Word"))
    st.dataframe(df)