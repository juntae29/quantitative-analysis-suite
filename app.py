import streamlit as st
import pandas as pd
import os
from scraper import run_web_scraper, scrape_text_from_url
from analyzer import process_dataframe_mining, generate_wordcloud_obj
from pypdf import PdfReader

st.set_page_config(page_title="Text Data Mining Analyzer", layout="wide", page_icon="🌐")

st.title("🌐 Multi-Source Text Data Mining Analyzer")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configuration")
    analysis_mode = st.selectbox("Select Analysis Mode", ["arXiv Web Scraping", "PDF Document Analysis", "Custom Text Input", "Web URL Analysis"])
    
    if analysis_mode == "arXiv Web Scraping":
        keyword = st.text_input("Research Keyword", value="Artificial Intelligence")
        num_papers = st.slider("Number of Papers", 10, 100, 30)
        mode_data = {"type": "web", "keyword": keyword, "num": num_papers}
    elif analysis_mode == "Web URL Analysis":
        url_input = st.text_input("Website URL")
        keyword_input = st.text_input("Focus Keyword (Optional)")
        mode_data = {"type": "url", "url": url_input, "keyword": keyword_input}
    elif analysis_mode == "PDF Document Analysis":
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
        mode_data = {"type": "pdf", "file": uploaded_file}
    else:
        custom_text = st.text_area("Paste text here", height=200)
        mode_data = {"type": "text", "content": custom_text}

if st.button("Launch Analysis"):
    df = None
    with st.spinner("Analyzing... Please wait."):
        if mode_data["type"] == "web":
            # 스크래핑 시도 후 성공 여부 확인
            if run_web_scraper(mode_data["keyword"], mode_data["num"]):
                # 파일이 존재하고 데이터가 있는지 확인
                if os.path.exists("scraped_data.csv") and os.path.getsize("scraped_data.csv") > 0:
                    df = pd.read_csv("scraped_data.csv")
                else:
                    st.error("Data collected but the file is empty. Please try again.")
            else:
                st.error("Failed to generate analysis data. Please check your input or connection.")
        
        elif mode_data["type"] == "pdf" and mode_data["file"] is not None:
            reader = PdfReader(mode_data["file"])
            text = "".join([page.extract_text() for page in reader.pages])
            df = pd.DataFrame({"Abstract": [text]})
            
        elif mode_data["type"] == "url" and mode_data["url"]:
            full_text = scrape_text_from_url(mode_data["url"])
            if full_text:
                text = full_text
                if mode_data["keyword"]:
                    sentences = [s.strip() for s in full_text.split('.') if mode_data["keyword"].lower() in s.lower()]
                    text = " ".join(sentences) if sentences else full_text
                df = pd.DataFrame({"Abstract": [text]})
            else:
                st.error("Could not extract text from the provided URL.")
        
        elif mode_data["type"] == "text" and mode_data["content"]:
            df = pd.DataFrame({"Abstract": [mode_data["content"]]})

    if df is not None and not df.empty:
        word_df, words = process_dataframe_mining(df)
        wc = generate_wordcloud_obj(words)
        tab1, tab2 = st.tabs(["📊 Visualization", "📋 Raw Data"])
        with tab1:
            col1, col2 = st.columns(2)
            with col1: st.image(wc.to_array(), use_column_width=True)
            with col2: st.bar_chart(word_df.set_index("Word"))
        with tab2: st.dataframe(df)