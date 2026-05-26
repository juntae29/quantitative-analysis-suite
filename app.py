import streamlit as st
import pandas as pd
from scraper import run_web_scraper
from analyzer import process_dataframe_mining, generate_wordcloud_obj
from pypdf import PdfReader

st.set_page_config(page_title="Multi-Source Text Data Mining Analyzer", layout="wide", page_icon="🌐")

st.title("🌐 Multi-Source Text Data Mining Analyzer")
st.caption("Advanced text mining from academic web sources, PDF documents, and custom text inputs.")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Global Control Panel")
    analysis_mode = st.selectbox(
        "Select Analysis Mode", 
        ["arXiv Web Scraping", "PDF Document Analysis", "Custom Text Input"]
    )
    
    # 모드별 동적 UI
    if analysis_mode == "arXiv Web Scraping":
        keyword = st.text_input("Enter Research Keyword", value="Artificial Intelligence")
        num_papers = st.slider("Number of Papers to Fetch", 10, 100, 30)
        launch_btn = st.button("Launch Analysis")
        mode_data = {"type": "web", "keyword": keyword, "num": num_papers}
        
    elif analysis_mode == "PDF Document Analysis":
        uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])
        launch_btn = st.button("Analyze PDF")
        mode_data = {"type": "pdf", "file": uploaded_file}
        
    else: # Custom Text Input
        custom_text = st.text_area("Paste your text here for analysis", height=200)
        launch_btn = st.button("Analyze Text")
        mode_data = {"type": "text", "content": custom_text}

# 분석 실행 로직
if launch_btn:
    df = None
    with st.spinner("Processing..."):
        if mode_data["type"] == "web":
            if run_web_scraper(mode_data["keyword"], mode_data["num"]):
                df = pd.read_csv("scraped_data.csv")
        
        elif mode_data["type"] == "pdf" and mode_data["file"] is not None:
            reader = PdfReader(mode_data["file"])
            text = "".join([page.extract_text() for page in reader.pages])
            df = pd.DataFrame({"Abstract": [text]})
            
        elif mode_data["type"] == "text" and mode_data["content"]:
            df = pd.DataFrame({"Abstract": [mode_data["content"]]})
            
    if df is not None and not df.empty:
        word_df, words = process_dataframe_mining(df)
        wc = generate_wordcloud_obj(words)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Word Cloud Visualization")
            st.image(wc.to_array(), use_column_width=True)
        with col2:
            st.subheader("Top 10 Keywords")
            st.bar_chart(word_df.set_index("Word"))
        st.subheader("Data Preview")
        st.dataframe(df.head(10))
    else:
        st.error("Data processing failed. Please ensure content is provided.")