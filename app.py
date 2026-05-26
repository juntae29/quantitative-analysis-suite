import streamlit as st
import pandas as pd
from scraper import run_web_scraper, scrape_text_from_url
from analyzer import process_dataframe_mining, generate_wordcloud_obj
from pypdf import PdfReader

st.set_page_config(page_title="Text Data Mining Analyzer", layout="wide")
st.title("🌐 Multi-Source Text Data Mining Analyzer")

with st.sidebar:
    st.header("⚙️ Configuration")
    mode = st.selectbox("Select Mode", ["arXiv Search", "Custom Text Input", "CSV Upload", "PDF Analysis", "Web URL"])
    
    df = None
    if mode == "arXiv Search":
        st.info("Operators: AND, OR, \" \" (e.g. \"Deep Learning\" AND medicine)")
        keyword = st.text_input("Query", value='"Artificial Intelligence" AND medicine')
        num = st.slider("Results", 10, 100, 30)
        if st.button("Fetch Data"):
            with st.spinner("Fetching from arXiv..."):
                if run_web_scraper(keyword, num):
                    df = pd.read_csv("scraped_data.csv")
                else:
                    st.error("No data found or connection failed. Try a broader query.")
            
    elif mode == "Custom Text Input":
        text_input = st.text_area("Paste your text here", height=200)
        if st.button("Analyze Text"):
            if text_input: df = pd.DataFrame({"Abstract": [text_input]})

    elif mode == "CSV Upload":
        f = st.file_uploader("Upload CSV", type=["csv"])
        if f: df = pd.read_csv(f)
        
    elif mode == "PDF Analysis":
        f = st.file_uploader("Upload PDF", type=["pdf"])
        if f:
            reader = PdfReader(f)
            text = "".join([p.extract_text() for p in reader.pages])
            df = pd.DataFrame({"Abstract": [text]})
            
    elif mode == "Web URL":
        u = st.text_input("Enter URL")
        if st.button("Fetch"):
            text = scrape_text_from_url(u)
            if text: df = pd.DataFrame({"Abstract": [text]})
            else: st.error("Failed to fetch from URL.")



if df is not None and not df.empty:
    st.success("Analysis Ready!")
    word_df, words = process_dataframe_mining(df)
    col1, col2 = st.columns(2)
    with col1: st.image(generate_wordcloud_obj(words).to_array())
    with col2: st.bar_chart(word_df.set_index("Word"))
    st.dataframe(df)
else:
    st.info("Please configure your input and launch analysis.")