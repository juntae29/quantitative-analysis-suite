import streamlit as st
import pandas as pd
from scraper import run_web_scraper, scrape_text_from_url
from analyzer import process_dataframe_mining, generate_wordcloud_obj
from pypdf import PdfReader

st.set_page_config(layout="wide")
st.title("🌐 Multi-Source Text Data Mining Analyzer")

with st.sidebar:
    mode = st.selectbox("Mode", ["arXiv Web Scraping", "PDF Document Analysis", "Custom Text Input", "Web URL Analysis"])
    if mode == "arXiv Web Scraping":
        keyword = st.text_input("Keyword", "Artificial Intelligence")
        num = st.slider("Papers", 10, 50, 20)
    elif mode == "Web URL Analysis":
        url = st.text_input("URL")
    elif mode == "PDF Document Analysis":
        pdf_file = st.file_uploader("PDF", type=["pdf"])
    else:
        custom_text = st.text_area("Text", height=200)

if st.button("Launch Analysis"):
    df = None
    if mode == "arXiv Web Scraping":
        if run_web_scraper(keyword, num):
            df = pd.read_csv("scraped_data.csv")
    elif mode == "PDF Document Analysis" and pdf_file:
        reader = PdfReader(pdf_file)
        df = pd.DataFrame({"Abstract": ["".join([p.extract_text() for p in reader.pages])]})
    elif mode == "Web URL Analysis" and url:
        text = scrape_text_from_url(url)
        if text: df = pd.DataFrame({"Abstract": [text]})
    elif mode == "Custom Text Input" and custom_text:
        df = pd.DataFrame({"Abstract": [custom_text]})

    if df is not None and not df.empty:
        word_df, words = process_dataframe_mining(df)
        st.image(generate_wordcloud_obj(words).to_array())
        st.dataframe(df)